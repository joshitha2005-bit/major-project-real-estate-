import os
import io
import re
import json
import uuid
import base64
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

try:
    import audioop
except ImportError:
    try:
        import audioop_lts as audioop
    except ImportError:
        audioop = None

from sqlalchemy.orm import Session
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status

from app.core.config import settings
from app.models.property import Property
from app.models.voice_callback import VoiceCallbackRequest, PropertyInquiry
from app.models.admin_lead import AILead, SiteVisit, PrivateOwnerContact
from app.services.price_prediction_service import PricePredictionService
from app.services.safety_service import SafetyGuardService
from app.services.text_ai_service import TextAIService
from app.services.image_ai_service import ImageAIService
from app.services.image_provenance import ImageProvenanceService
from app.services.voice_conversation_engine import VoiceConversationEngine, VoiceConversationSession


class VoiceAssistantService:

    @staticmethod
    def validate_and_format_phone(phone: str) -> str:
        """Validate phone number and format into standard E.164 representation."""
        if not phone or not isinstance(phone, str) or not phone.strip():
            raise ValueError("Invalid phone number: Phone number is required.")

        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone.strip())
        
        # Indian standard mobile check: 10 digits starting with 6, 7, 8, 9
        if re.match(r'^[6-9]\d{9}$', cleaned):
            return f"+91{cleaned}"
        
        # E.164 format with country code (+ followed by 10 to 15 digits)
        if re.match(r'^\+\d{10,15}$', cleaned):
            return cleaned

        # 12 digits starting with 91
        if re.match(r'^91[6-9]\d{9}$', cleaned):
            return f"+{cleaned}"

        raise ValueError("Invalid phone number format. Please provide a valid 10-digit mobile number or standard E.164 format.")

    @staticmethod
    def check_rate_limit(phone_number: str, db: Session, max_calls: int = 3, window_minutes: int = 10) -> None:
        """Ensure users cannot spam outbound telephone calls."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        recent_count = db.query(VoiceCallbackRequest).filter(
            VoiceCallbackRequest.phone_number == phone_number,
            VoiceCallbackRequest.created_at >= cutoff
        ).count()

        if recent_count >= max_calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {max_calls} callback requests allowed per {window_minutes} minutes."
            )

    @classmethod
    def get_telephony_diagnostics(cls) -> Dict[str, Any]:
        """
        Return comprehensive diagnostic information regarding Twilio telephony and webhook reachability.
        Never exposes sensitive tokens.
        """
        from dotenv import dotenv_values
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        env_vals = dotenv_values(env_file) if os.path.exists(env_file) else {}

        # Prefer settings if set or explicitly patched, fallback to .env/os.environ
        if hasattr(settings, "TWILIO_ACCOUNT_SID"):
            twilio_sid = settings.TWILIO_ACCOUNT_SID.strip() if settings.TWILIO_ACCOUNT_SID is not None else ""
        else:
            twilio_sid = (env_vals.get("TWILIO_ACCOUNT_SID") or os.getenv("TWILIO_ACCOUNT_SID") or "").strip()

        if hasattr(settings, "TWILIO_AUTH_TOKEN"):
            twilio_token = settings.TWILIO_AUTH_TOKEN.strip() if settings.TWILIO_AUTH_TOKEN is not None else ""
        else:
            twilio_token = (env_vals.get("TWILIO_AUTH_TOKEN") or os.getenv("TWILIO_AUTH_TOKEN") or "").strip()

        if hasattr(settings, "TWILIO_PHONE_NUMBER"):
            twilio_from = settings.TWILIO_PHONE_NUMBER.strip() if settings.TWILIO_PHONE_NUMBER is not None else ""
        else:
            twilio_from = (env_vals.get("TWILIO_PHONE_NUMBER") or os.getenv("TWILIO_PHONE_NUMBER") or "").strip()

        if hasattr(settings, "VOICE_PUBLIC_BASE_URL") and settings.VOICE_PUBLIC_BASE_URL:
            base_url = settings.VOICE_PUBLIC_BASE_URL.strip().rstrip('/')
        else:
            base_url = (env_vals.get("VOICE_PUBLIC_BASE_URL") or os.getenv("VOICE_PUBLIC_BASE_URL") or "").strip().rstrip('/')

        is_twilio_configured = bool(
            twilio_sid and twilio_token and twilio_from and
            twilio_sid.startswith("AC") and len(twilio_sid) >= 30
        )
        
        # Check if base_url is public HTTPS
        is_public_webhook = bool(
            base_url and
            base_url.startswith("https://") and
            not ("localhost" in base_url or "127.0.0.1" in base_url or "0.0.0.0" in base_url)
        )

        masked_phone = None
        if twilio_from:
            cleaned = re.sub(r'\s+', '', twilio_from)
            if len(cleaned) > 4:
                masked_phone = f"{cleaned[:3]}****{cleaned[-4:]}"
            else:
                masked_phone = "***"

        gemini_key = (os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY or "").strip()
        if not gemini_key:
            from dotenv import dotenv_values
            env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
            if os.path.exists(env_file):
                gemini_key = (dotenv_values(env_file).get("GEMINI_API_KEY") or "").strip()
        has_gemini = bool(gemini_key and len(gemini_key) >= 10)

        return {
            "twilio_configured": is_twilio_configured,
            "twilio_account_sid_present": bool(twilio_sid),
            "twilio_auth_token_present": bool(twilio_token),
            "twilio_phone_number_present": bool(twilio_from),
            "twilio_phone_masked": masked_phone,
            "public_webhook_configured": is_public_webhook,
            "webhook_base_url": base_url,
            "uses_localhost": "localhost" in base_url or "127.0.0.1" in base_url,
            "gemini_configured": has_gemini,
            "ready_for_real_calls": is_twilio_configured and is_public_webhook
        }

    @classmethod
    def build_property_knowledge_context(cls, prop: Property, db: Session) -> str:
        """
        Compile truthful, verified property attributes into a structured knowledge base.
        Never fabricates information or owner details.
        """
        ctx_dict = VoiceConversationEngine.build_property_context(prop, db)
        
        desc_text = (prop.description or "Prime residential listing in Bengaluru.").replace("\n", " ").strip()
        if len(desc_text) > 300:
            desc_text = desc_text[:300] + "..."

        context = f"""
PROPERTY SPECIFICATIONS:
- Property ID: BLR-{prop.id}
- Title: {ctx_dict['title']}
- Locality: {ctx_dict['locality']}, Bengaluru, Karnataka
- Full Address: {ctx_dict['address']}
- Layout & Type: {ctx_dict['bhk_str']} {ctx_dict['property_type']}
- Built-up Area: {ctx_dict['area_sqft']} sq.ft.
- Parking: {ctx_dict['parking']}
- Facing Direction: {ctx_dict['facing']}
- Furnishing Status: {ctx_dict['furnishing']}
- Listed Asking Price: {ctx_dict['price_formatted']}
- Available Amenities: {ctx_dict['amenities']}
- Listing Description: {desc_text}
"""
        return context.strip()

    @classmethod
    def get_system_instruction(cls, property_context: str) -> str:
        """Generate authoritative system instructions for AI voice session."""
        return f"""You are an AI property assistant for the Cloud-Based Real Estate Analysis platform.
You are NOT the property owner.
You are assisting a user on a live telephone call who is asking questions about one specific property.
Use ONLY the verified property information supplied below.

CRITICAL RULES:
1. Never invent property details, prices, amenities, distances, availability, owner information, or negotiation terms.
2. If information is unavailable, clearly state: "I don't have that information available for this property."
3. Keep spoken answers short, natural, courteous, and conversational (1 to 2 sentences maximum per turn).
4. If the user asks whether the price is negotiable, state that negotiation must be confirmed directly with the owner or listing agent.
5. If the user gives unrelated or nonsensical speech, politely clarify without inferring answers.
6. Ask whether they would like to schedule an in-person site visit.
7. Always identify yourself as an AI assistant.

==================================================
VERIFIED PROPERTY KNOWLEDGE BASE:
==================================================
{property_context}
"""

    @classmethod
    def initiate_voice_callback(
        cls,
        property_id: int,
        phone_number: str,
        user_id: Optional[int],
        db: Session
    ) -> Dict[str, Any]:
        """
        Validate, create callback record, and initiate REAL outbound telephone call via Twilio.
        STRICT: Never simulates fake Call SIDs or fake success.
        If Twilio credentials are missing or invalid, truthfully returns TELEPHONY_NOT_CONFIGURED.
        """
        # 1. Validate property existence
        prop = db.query(Property).filter(Property.id == property_id).first()
        if not prop:
            raise HTTPException(status_code=404, detail="Property listing not found.")

        # 2. Validate and format phone number
        try:
            formatted_phone = cls.validate_and_format_phone(phone_number)
        except ValueError as val_err:
            raise HTTPException(status_code=400, detail=str(val_err))

        # 3. Rate limiting check
        cls.check_rate_limit(formatted_phone, db, max_calls=3, window_minutes=10)

        # 4. Generate unique session ID
        session_id = f"vcs_{uuid.uuid4().hex[:16]}"

        # 5. Check telephony configuration diagnostics
        diag = cls.get_telephony_diagnostics()
        is_twilio_configured = diag["twilio_configured"]
        is_public_webhook = diag.get("public_webhook_configured", not diag.get("uses_localhost", False))
        base_url = diag.get("webhook_base_url", diag.get("webhook_url", ""))

        # 6. Create database record
        callback_req = VoiceCallbackRequest(
            property_id=property_id,
            user_id=user_id,
            phone_number=formatted_phone,
            session_id=session_id,
            status="requested",
            call_sid=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(callback_req)
        db.commit()
        db.refresh(callback_req)

        # If Twilio is NOT configured: TRUTHFULLY return TELEPHONY_NOT_CONFIGURED (NO FAKE CALL SID)
        if not is_twilio_configured:
            callback_req.status = "telephony_not_configured"
            callback_req.error_message = (
                "Telephony not configured: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, or TWILIO_PHONE_NUMBER "
                "is missing or invalid in server environment."
            )
            db.commit()

            return {
                "success": False,
                "status": "TELEPHONY_NOT_CONFIGURED",
                "message": (
                    "Telephony provider is not configured. Real outbound telephone calls require active Twilio credentials. "
                    "No simulated call was placed."
                ),
                "diagnostics": {
                    "twilio_configured": False,
                    "twilio_api_request": False,
                    "call_sid": None,
                    "call_status": "TELEPHONY_NOT_CONFIGURED",
                    "public_webhook_configured": is_public_webhook,
                    "webhook_base_url": base_url,
                    "failure_code": "TELEPHONY_NOT_CONFIGURED",
                    "failure_message": "Twilio credentials not configured in server environment."
                },
                "session_id": session_id,
                "call_sid": None,
                "phone_number": formatted_phone,
                "property_id": property_id,
                "property_title": prop.title
            }

        # Twilio is configured: Attempt real Twilio REST API outbound call
        twilio_sid = settings.TWILIO_ACCOUNT_SID.strip()
        twilio_token = settings.TWILIO_AUTH_TOKEN.strip()
        twilio_from = settings.TWILIO_PHONE_NUMBER.strip()

        try:
            from twilio.rest import Client
            client = Client(twilio_sid, twilio_token)

            twiml_url = f"{base_url}/api/v1/voice-assistant/twiml/{session_id}"
            status_callback_url = f"{base_url}/api/v1/voice-assistant/status-callback/{session_id}"

            call = client.calls.create(
                to=formatted_phone,
                from_=twilio_from,
                url=twiml_url,
                status_callback=status_callback_url,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed']
            )

            call_sid = call.sid
            callback_req.call_sid = call_sid
            callback_req.status = "calling"
            callback_req.call_started_at = datetime.now(timezone.utc)
            db.commit()

            return {
                "success": True,
                "status": "CALLING",
                "message": f"Real outbound call initiated via Twilio to {formatted_phone}. Your phone will ring shortly.",
                "diagnostics": {
                    "twilio_configured": True,
                    "twilio_api_request": True,
                    "call_sid": call_sid,
                    "call_status": (call.status or "CALLING").upper(),
                    "public_webhook_configured": is_public_webhook,
                    "webhook_base_url": base_url,
                    "failure_code": None,
                    "failure_message": None
                },
                "session_id": session_id,
                "call_sid": call_sid,
                "phone_number": formatted_phone,
                "property_id": property_id,
                "property_title": prop.title
            }

        except Exception as twilio_err:
            error_text = str(twilio_err)
            callback_req.status = "failed"
            callback_req.error_message = error_text
            db.commit()

            failure_code = getattr(twilio_err, "code", "TWILIO_DISPATCH_ERROR")

            return {
                "success": False,
                "status": "CALL_FAILED",
                "message": f"Twilio API request failed: {error_text}",
                "diagnostics": {
                    "twilio_configured": True,
                    "twilio_api_request": True,
                    "call_sid": None,
                    "call_status": "FAILED",
                    "public_webhook_configured": is_public_webhook,
                    "webhook_base_url": base_url,
                    "failure_code": str(failure_code),
                    "failure_message": error_text
                },
                "session_id": session_id,
                "call_sid": None,
                "phone_number": formatted_phone,
                "property_id": property_id,
                "property_title": prop.title
            }

    @staticmethod
    def generate_gather_twiml(session_id: str, spoken_text: str, is_first: bool = False) -> str:
        """
        Generate TwiML XML instructing Twilio to speak the AI response and gather the user's speech.
        """
        base_url = settings.VOICE_PUBLIC_BASE_URL.rstrip('/')
        action_url = f"{base_url}/api/v1/voice-assistant/twiml-gather/{session_id}"

        # Clean text for XML safe content
        clean_text = spoken_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="{action_url}" method="POST" speechTimeout="auto" timeout="4" language="en-IN">
        <Say voice="Polly.Aditi">{clean_text}</Say>
    </Gather>
    <Say voice="Polly.Aditi">I didn't receive a response. Our team will follow up with you. Have a great day!</Say>
    <Hangup/>
</Response>"""

    @staticmethod
    def generate_hangup_twiml(closing_text: str) -> str:
        """Generate final concluding TwiML XML with factual summary and hangup."""
        clean_text = closing_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi">{clean_text}</Say>
    <Hangup/>
</Response>"""

    @staticmethod
    def generate_twiml_xml(session_id: str) -> str:
        """Generate TwiML XML for media stream bridge if WebSocket mode is used."""
        base_url = settings.VOICE_PUBLIC_BASE_URL.rstrip('/')
        ws_url = base_url.replace("https://", "wss://").replace("http://", "ws://")
        stream_url = f"{ws_url}/api/v1/voice-assistant/stream/{session_id}"

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi">Connecting you to the AI Property Assistant.</Say>
    <Connect>
        <Stream url="{stream_url}" />
    </Connect>
</Response>"""

    @staticmethod
    def mulaw_to_pcm16(mulaw_bytes: bytes, in_rate: int = 8000, out_rate: int = 16000) -> bytes:
        if not audioop:
            return mulaw_bytes
        pcm_data = audioop.ulaw2lin(mulaw_bytes, 2)
        if in_rate != out_rate:
            pcm_data, _ = audioop.ratecv(pcm_data, 2, 1, in_rate, out_rate, None)
        return pcm_data

    @staticmethod
    def pcm_to_mulaw(pcm_bytes: bytes, in_rate: int = 24000, out_rate: int = 8000) -> bytes:
        if not audioop:
            return pcm_bytes
        if in_rate != out_rate:
            pcm_bytes, _ = audioop.ratecv(pcm_bytes, 2, 1, in_rate, out_rate, None)
        return audioop.lin2ulaw(pcm_bytes, 2)

    @classmethod
    async def handle_media_stream(cls, websocket: WebSocket, session_id: str, db: Session) -> None:
        """Bidirectional WebSocket handler for real-time Twilio media streaming."""
        await websocket.accept()

        req = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.session_id == session_id).first()
        if not req:
            await websocket.close(code=4004, reason="Callback request session not found")
            return

        prop = db.query(Property).filter(Property.id == req.property_id).first()
        if not prop:
            await websocket.close(code=4004, reason="Property not found")
            return

        stream_sid = None
        has_gemini_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())

        if has_gemini_key:
            try:
                from google import genai
                from google.genai import types

                system_instruction = cls.get_system_instruction(cls.build_property_knowledge_context(prop, db))
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                
                live_config = types.LiveConnectConfig(
                    response_modalities=["AUDIO"],
                    system_instruction=types.Content(parts=[types.Part.from_text(text=system_instruction)]),
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                        )
                    )
                )

                async with client.aio.live.connect(model=settings.GEMINI_LIVE_MODEL, config=live_config) as gemini_session:
                    await gemini_session.send(
                        input=f"Hello, I am calling regarding {prop.title}. Is now a good time to talk?",
                        end_of_turn=True
                    )

                    async def gemini_to_twilio():
                        nonlocal stream_sid
                        try:
                            async for response in gemini_session.receive():
                                server_content = response.server_content
                                if server_content:
                                    if getattr(server_content, 'interrupted', False) and stream_sid:
                                        await websocket.send_text(json.dumps({
                                            "event": "clear",
                                            "streamSid": stream_sid
                                        }))

                                    model_turn = server_content.model_turn
                                    if model_turn:
                                        for part in model_turn.parts:
                                            if part.inline_data and part.inline_data.data and stream_sid:
                                                mulaw_chunk = cls.pcm_to_mulaw(part.inline_data.data, in_rate=24000)
                                                payload = base64.b64encode(mulaw_chunk).decode('ascii')
                                                await websocket.send_text(json.dumps({
                                                    "event": "media",
                                                    "streamSid": stream_sid,
                                                    "media": {"payload": payload}
                                                }))
                        except asyncio.CancelledError:
                            pass
                        except Exception as e:
                            print(f"Error in gemini_to_twilio: {e}")

                    async def twilio_to_gemini():
                        nonlocal stream_sid
                        try:
                            while True:
                                data = await websocket.receive_text()
                                msg = json.loads(data)
                                event = msg.get("event")

                                if event == "start":
                                    stream_sid = msg.get("start", {}).get("streamSid") or msg.get("streamSid")

                                elif event == "media":
                                    payload = msg.get("media", {}).get("payload")
                                    if payload:
                                        mulaw_raw = base64.b64decode(payload)
                                        pcm_16k = cls.mulaw_to_pcm16(mulaw_raw)
                                        await gemini_session.send(
                                            input=types.LiveClientRealtimeInput(
                                                media_chunks=[types.Blob(data=pcm_16k, mime_type="audio/pcm;rate=16000")]
                                            ),
                                            end_of_turn=False
                                        )

                                elif event == "stop":
                                    break
                        except (WebSocketDisconnect, asyncio.CancelledError):
                            pass
                        except Exception as e:
                            print(f"Error in twilio_to_gemini: {e}")

                    consumer_task = asyncio.create_task(gemini_to_twilio())
                    producer_task = asyncio.create_task(twilio_to_gemini())

                    done, pending = await asyncio.wait(
                        [consumer_task, producer_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    for t in pending:
                        t.cancel()

            except Exception as gemini_err:
                print(f"Gemini Live connection error: {gemini_err}")
                req.error_message = str(gemini_err)
                db.commit()
        else:
            try:
                while True:
                    data = await websocket.receive_text()
                    msg = json.loads(data)
                    if msg.get("event") == "stop":
                        break
            except (WebSocketDisconnect, asyncio.CancelledError):
                pass

        req.status = "completed"
        req.call_completed_at = datetime.now(timezone.utc)
        req.updated_at = datetime.now(timezone.utc)
        db.commit()

    @classmethod
    def record_owner_inquiry(
        cls,
        property_id: int,
        phone_number: str,
        question: str,
        user_id: Optional[int],
        session_id: Optional[str],
        db: Session
    ) -> PropertyInquiry:
        """Record an official owner/agent inquiry callback request."""
        inquiry = PropertyInquiry(
            property_id=property_id,
            user_id=user_id,
            phone_number=phone_number,
            session_id=session_id,
            question_or_request=question,
            status="PENDING",
            created_at=datetime.now(timezone.utc)
        )
        db.add(inquiry)
        db.commit()
        db.refresh(inquiry)
        return inquiry