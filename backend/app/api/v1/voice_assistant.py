from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, Response, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user_optional
from app.services.voice_assistant_service import VoiceAssistantService
from app.models.voice_callback import VoiceCallbackRequest, PropertyInquiry


router = APIRouter()


class CallbackRequestPayload(BaseModel):
    property_id: int
    phone_number: str


class InquiryPayload(BaseModel):
    property_id: int
    phone_number: str
    question_or_request: str
    session_id: Optional[str] = None


@router.post("/request-callback")
def request_ai_callback(
    payload: CallbackRequestPayload,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Request an automated voice callback from the Gemini AI Property Assistant.
    Validates phone number and initiates outbound telephone call via Twilio.
    """
    user_id = current_user.id if current_user else None
    result = VoiceAssistantService.initiate_voice_callback(
        property_id=payload.property_id,
        phone_number=payload.phone_number,
        user_id=user_id,
        db=db
    )
    return result


@router.get("/callback-status/{session_id}")
def get_callback_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Poll live status of an AI callback session (calling, connected, completed, failed)."""
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


@router.api_route("/twiml/{session_id}", methods=["GET", "POST"])
def get_twiml_stream(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Return TwiML XML to Twilio instructing it to bridge audio into WebSocket media stream."""
    req = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.session_id == session_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Invalid callback session.")

    twiml_xml = VoiceAssistantService.generate_twiml_xml(session_id)
    return Response(content=twiml_xml, media_type="application/xml")


@router.post("/status-callback/{session_id}")
async def twilio_status_callback(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Twilio call status webhook (ringing, in-progress, completed, busy, failed)."""
    req = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.session_id == session_id).first()
    if not req:
        return {"status": "ignored"}

    form_data = await request.form()
    call_status = form_data.get("CallStatus", "").lower()

    if call_status in ["in-progress", "answered"]:
        req.status = "connected"
    elif call_status in ["completed"]:
        req.status = "completed"
    elif call_status in ["busy", "no-answer", "failed", "canceled"]:
        req.status = "failed"
        req.error_message = f"Call terminated with status: {call_status}"

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
