from typing import Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, WebSocket, Response, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.property import Property
from app.api.deps import get_current_user_optional
from app.dependencies.subscriptions import require_pro_subscription
from app.services.voice_assistant_service import VoiceAssistantService
from app.services.voice_conversation_engine import VoiceConversationEngine, VoiceConversationSession
from app.services.lead_management_service import LeadManagementService
from app.models.voice_callback import VoiceCallbackRequest, PropertyInquiry
from app.models.admin_lead import AILead

router = APIRouter()

# In-memory registry for active multi-turn phone sessions
_ACTIVE_VOICE_SESSIONS: Dict[str, VoiceConversationSession] = {}


class CallbackRequestPayload(BaseModel):
    property_id: int
    phone_number: str


class InquiryPayload(BaseModel):
    property_id: int
    phone_number: str
    question_or_request: str
    session_id: Optional[str] = None


@router.get("/telephony-status")
def get_telephony_status():
    """
    Diagnostic endpoint reporting live Twilio configuration and public webhook reachability.
    Never exposes sensitive secrets.
    """
    diag = VoiceAssistantService.get_telephony_diagnostics()
    return {
        "status": "ok",
        "telephony": diag
    }


@router.post("/request-callback")
def request_ai_callback(
    payload: CallbackRequestPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pro_subscription)
):
    """
    Request an automated voice callback from the AI Property Assistant.
    Validates phone number and initiates REAL outbound telephone call via Twilio.
    Strictly returns TELEPHONY_NOT_CONFIGURED if credentials are not configured.
    """
    user_id = current_user.id if current_user else None
    result = VoiceAssistantService.initiate_voice_callback(
        property_id=payload.property_id,
        phone_number=payload.phone_number,
        user_id=user_id,
        db=db
    )

    # Register lead in private lead management system
    try:
        LeadManagementService.create_or_process_call_lead(
            db=db,
            phone=payload.phone_number,
            property_id=payload.property_id,
            session_id=result.get("session_id")
        )
    except Exception as e:
        print(f"Warning: Failed to create lead for voice callback: {e}")

    return result


@router.get("/callback-status/{session_id}")
def get_callback_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Poll live status of an AI callback session (requested, calling, connected, completed, failed, telephony_not_configured)."""
    req = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.session_id == session_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Callback session not found.")

    return {
        "session_id": req.session_id,
        "call_sid": req.call_sid,
        "status": req.status,
        "property_id": req.property_id,
        "phone_number": req.phone_number,
        "error_message": req.error_message,
        "created_at": req.created_at,
        "updated_at": req.updated_at
    }


def _get_or_create_voice_session(session_id: str, db: Session) -> Optional[VoiceConversationSession]:
    """Retrieve active conversational session or reconstruct from database."""
    if session_id in _ACTIVE_VOICE_SESSIONS:
        return _ACTIVE_VOICE_SESSIONS[session_id]

    req = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.session_id == session_id).first()
    if not req:
        return None

    prop = db.query(Property).filter(Property.id == req.property_id).first()
    if not prop:
        return None

    prop_ctx = VoiceConversationEngine.build_property_context(prop, db)
    conv_sess = VoiceConversationSession(
        session_id=session_id,
        property_id=prop.id,
        user_phone=req.phone_number,
        prop_context=prop_ctx
    )
    _ACTIVE_VOICE_SESSIONS[session_id] = conv_sess
    return conv_sess


@router.api_route("/twiml/{session_id}", methods=["GET", "POST"])
def get_twiml_initial(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Initial TwiML webhook invoked by Twilio when the user answers their phone.
    Greets the user naturally and prompts for voice response via Gather.
    """
    req = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.session_id == session_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Invalid callback session.")

    conv_sess = _get_or_create_voice_session(session_id, db)
    if not conv_sess:
        raise HTTPException(status_code=404, detail="Could not initialize conversation session.")

    greeting = conv_sess.get_initial_greeting()
    twiml_xml = VoiceAssistantService.generate_gather_twiml(session_id, greeting, is_first=True)
    return Response(content=twiml_xml, media_type="application/xml")


@router.post("/twiml-gather/{session_id}")
async def handle_twiml_gather(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Twilio Speech-to-Text webhook callback.
    Receives user utterance, extracts lead entities, answers property questions,
    handles rubbish gracefully, and returns the next natural conversational turn.
    """
    req = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.session_id == session_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Invalid callback session.")

    form_data = await request.form()
    speech_result = form_data.get("SpeechResult", "").strip()

    conv_sess = _get_or_create_voice_session(session_id, db)
    if not conv_sess:
        raise HTTPException(status_code=404, detail="Session not found.")

    if not speech_result:
        # User was silent
        twiml_xml = VoiceAssistantService.generate_gather_twiml(
            session_id,
            "I couldn't hear your response clearly. May I know your name and approximate budget?"
        )
        return Response(content=twiml_xml, media_type="application/xml")

    # Process conversational turn
    reply = conv_sess.process_user_utterance(speech_result)

    if conv_sess.is_completed:
        # Finalize and persist structured lead to database
        try:
            conv_sess.finalize_and_persist(db, call_sid=req.call_sid)
            req.status = "completed"
            req.call_completed_at = datetime.now(timezone.utc)
            db.commit()
        except Exception as e:
            print(f"Error persisting finalized lead: {e}")

        twiml_xml = VoiceAssistantService.generate_hangup_twiml(reply)
        # Clean up session from active memory
        _ACTIVE_VOICE_SESSIONS.pop(session_id, None)
        return Response(content=twiml_xml, media_type="application/xml")

    else:
        # Prompt next missing question
        twiml_xml = VoiceAssistantService.generate_gather_twiml(session_id, reply)
        return Response(content=twiml_xml, media_type="application/xml")


@router.post("/status-callback/{session_id}")
async def twilio_status_callback(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Twilio call status webhook (initiated, ringing, in-progress/answered, completed, busy, failed)."""
    req = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.session_id == session_id).first()
    if not req:
        return {"status": "ignored"}

    form_data = await request.form()
    call_status = form_data.get("CallStatus", "").lower()
    call_duration = form_data.get("CallDuration")

    if call_status in ["in-progress", "answered"]:
        req.status = "connected"
        if not req.call_started_at:
            req.call_started_at = datetime.now(timezone.utc)
    elif call_status in ["completed"]:
        req.status = "completed"
        req.call_completed_at = datetime.now(timezone.utc)
        if call_duration and call_duration.isdigit():
            req.duration_seconds = int(call_duration)
            
        # Finalize active session if not yet persisted
        if session_id in _ACTIVE_VOICE_SESSIONS:
            sess = _ACTIVE_VOICE_SESSIONS.pop(session_id)
            if not sess.is_completed:
                sess.is_completed = True
                try:
                    sess.finalize_and_persist(db, call_sid=req.call_sid)
                except Exception as e:
                    print(f"Error finalizing lead on status completed: {e}")

    elif call_status in ["busy", "no-answer", "failed", "canceled"]:
        req.status = "failed"
        req.error_message = f"Call terminated with status: {call_status}"

    req.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "updated", "call_status": req.status}


@router.websocket("/stream/{session_id}")
async def twilio_media_stream(
    websocket: WebSocket,
    session_id: str,
    db: Session = Depends(get_db)
):
    """Bidirectional WebSocket endpoint for Twilio Media Streams connected to Gemini Live API."""
    await VoiceAssistantService.handle_media_stream(websocket, session_id, db)


@router.post("/inquiry")
def submit_owner_inquiry(
    payload: InquiryPayload,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Record an owner/agent inquiry request made during or following an AI voice call."""
    user_id = current_user.id if current_user else None
    inquiry = VoiceAssistantService.record_owner_inquiry(
        property_id=payload.property_id,
        phone_number=payload.phone_number,
        question=payload.question_or_request,
        user_id=user_id,
        session_id=payload.session_id,
        db=db
    )
    return {
        "success": True,
        "inquiry_id": inquiry.id,
        "message": "Your inquiry has been recorded. The owner or agent will contact you shortly.",
        "status": inquiry.status
    }