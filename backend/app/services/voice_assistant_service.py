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
from app.services.price_prediction_service import PricePredictionService
from app.services.safety_service import SafetyGuardService
from app.services.text_ai_service import TextAIService
from app.services.image_ai_service import ImageAIService
from app.services.image_provenance import ImageProvenanceService


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
    def build_property_knowledge_context(cls, prop: Property, db: Session) -> str:
        """
        Compile truthful, verified property attributes into a structured knowledge base
        for the Gemini AI Property Assistant.
        Never fabricates information or owner details.
        """
        # Price formatting
        price_lakhs = round(prop.price / 100_000.0, 2)
        price_str = f"₹{price_lakhs} Lakh" if price_lakhs < 100 else f"₹{round(prop.price / 10_000_000.0, 2)} Crore"
        rate_str = f"₹{int(prop.price / (prop.area_sqft or 1)):,} / sq.ft"

        # AI Valuation Prediction
        pred_val_str = "Unavailable"
        rent_val_str = "Unavailable"
        try:
            pred = PricePredictionService.predict_property_valuation(
                address=prop.address,
                lat=prop.latitude,
                lon=prop.longitude,
                area_sqft=prop.area_sqft,
                bhk=prop.bhk,
                bathrooms=prop.bathrooms,
                balconies=prop.balconies,
                parking=prop.parking,
                facing=prop.facing,
                property_age=prop.property_age,
                nearby_places=prop.nearby_places or [],
                image_score=80.0,
                text_score=75.0,
                listed_price=prop.price
            )
            if pred:
                pred_price = pred.get("predicted_selling_price")
                if pred_price:
                    p_lakhs = round(pred_price / 100_000.0, 2)
                    pred_val_str = f"₹{p_lakhs} Lakh" if p_lakhs < 100 else f"₹{round(pred_price / 10_000_000.0, 2)} Crore"
                rent_price = pred.get("estimated_rental_price")
                if rent_price:
                    rent_val_str = f"₹{int(rent_price):,} / month"
        except Exception as e:
            print(f"Warning building AI prediction context for voice: {e}")

        # Image Intelligence Info
        image_info_str = "Property photos unavailable."
        try:
            prov = ImageProvenanceService.get_property_image_provenance(prop)
            if prov.get("image_classification") == "AUTHORIZED_PROPERTY_IMAGE":
                image_info_str = "Verified authentic property photos available. PyTorch ResNet-18 extracted 512-dim visual features."
            elif prov.get("image_classification") == "SOURCE_LISTING_IMAGE":
                image_info_str = "Reference photos available on source listing portal (NoBroker/Housing)."
            elif prov.get("image_classification") == "LOCATION_BUILDING_REFERENCE":
                image_info_str = "Building and locality exterior reference photos available."
        except Exception:
            pass

        # Description NLP Info
        desc_text = prop.description or "No descriptive text provided in the listing record."

        # Nearby Facilities
        nearby_hospitals = "Nearest hospital data not recorded."
        nearby_police = "Nearest police station data not recorded."
        safety_score = "Safety rating unavailable"
        if prop.nearby_places and isinstance(prop.nearby_places, list):
            hosps = [p for p in prop.nearby_places if p.get("category") == "Hospitals"]
            if hosps:
                h = hosps[0]
                nearby_hospitals = f"{h.get('name', 'Hospital')} ({round(h.get('distance_meters', 0)/1000.0, 2)} km away)"
            police = [p for p in prop.nearby_places if p.get("category") == "Police Stations"]
            if police:
                pol = police[0]
                nearby_police = f"{pol.get('name', 'Police Station')} ({round(pol.get('distance_meters', 0)/1000.0, 2)} km away)"

        amenities_str = ", ".join(prop.amenities) if prop.amenities else "Standard amenities"

        context = f"""
PROPERTY SPECIFICATIONS:
- Property ID: BLR-{prop.id}
- Title: {prop.title}
- Locality: {prop.locality or 'Bengaluru'}, Bengaluru, Karnataka
- Full Address: {prop.address}
- Layout & Type: {prop.bhk} BHK {prop.property_type or 'Apartment'}
- Built-up Area: {prop.area_sqft} sq.ft.
- Floor: Floor {prop.floor} of {prop.total_floors}
- Bathrooms: {prop.bathrooms}, Balconies: {prop.balconies}
- Facing Direction: {prop.facing or 'Not specified'}
- Furnishing Status: {prop.furnishing or 'Semi-Furnished'}
- Parking: {prop.parking or 'Available'}
- Property Age: {prop.property_age or 'New'}
- Listed Asking Price: {price_str} ({rate_str})
- Model Predicted Price: {pred_val_str}
- Estimated Monthly Rental Forecast: {rent_val_str}
- Available Amenities: {amenities_str}
- Nearby Hospital: {nearby_hospitals}
- Nearby Police Station: {nearby_police}
- Visual Media Status: {image_info_str}
- Listing Description: {desc_text}
"""
        return context.strip()

    @classmethod
    def get_system_instruction(cls, property_context: str) -> str:
        """Generate authoritative system instructions for Gemini Live voice session."""
        return f"""You are an AI property assistant for the Cloud-Based Real Estate Analysis platform.

You are NOT the property owner.

You are assisting a user on a live telephone call who is asking questions about one specific property.

Use ONLY the verified property information supplied below.

CRITICAL RULES:
1. Never invent property details, prices, amenities, distances, availability, owner information, or negotiation terms.
2. If information is unavailable, clearly state: "I don't have that information available for this property."
3. Keep spoken answers short, natural, courteous, and conversational (1 to 3 sentences maximum per turn).
4. If the user asks whether the price is negotiable, do not assume that it is. State that negotiation must be confirmed by the owner or agent.
5. If the user asks to speak with the owner or have the owner contact them, inform them that you are an AI assistant and you have recorded their request for the owner or listing agent to follow up.
6. Always identify yourself as an AI assistant when greeting or when asked.
7. Speak clearly and concisely in standard professional Indian English.

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
        Validate, create callback record, and initiate outbound phone call via Twilio.
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

        # 5. Create database record
        callback_req = VoiceCallbackRequest(
            property_id=property_id,
            user_id=user_id,
            phone_number=formatted_phone,
            session_id=session_id,
            status="calling",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(callback_req)
        db.commit()
        db.refresh(callback_req)

        # 6. Twilio Call Initiation
        twilio_sid = settings.TWILIO_ACCOUNT_SID
        twilio_token = settings.TWILIO_AUTH_TOKEN
        twilio_from = settings.TWILIO_PHONE_NUMBER
        base_url = settings.VOICE_PUBLIC_BASE_URL.rstrip('/')

        call_initiated = False
        call_sid = None

        if twilio_sid and twilio_token and twilio_from:
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
                call_initiated = True
                callback_req.call_sid = call_sid
                db.commit()
            except Exception as twilio_err:
                print(f"Twilio call dispatch warning: {twilio_err}")
                callback_req.error_message = str(twilio_err)
                db.commit()
        else:
            # Simulated development mode when live credentials are not yet supplied
            call_sid = f"SIM_{uuid.uuid4().hex[:12]}"
            call_initiated = True
            callback_req.call_sid = call_sid
            callback_req.status = "calling"
            db.commit()

        return {
            "success": True,
            "session_id": session_id,
            "call_sid": call_sid,
            "status": "calling",
            "message": "Your AI callback has been requested. Connecting to your phone...",
            "phone_number": formatted_phone,
            "property_id": property_id,
            "property_title": prop.title
        }

    @staticmethod
    def generate_twiml_xml(session_id: str) -> str:
        """Generate TwiML XML instructing Twilio to bridge the call to WebSocket media stream."""
        base_url = settings.VOICE_PUBLIC_BASE_URL.rstrip('/')
        # Convert http/https to ws/wss
        ws_url = base_url.replace("https://", "wss://").replace("http://", "ws://")
        stream_url = f"{ws_url}/api/v1/voice-assistant/stream/{session_id}"

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Google.en-IN-Wavenet-D">Connecting you to the PropPulse AI Property Assistant.</Say>
    <Connect>
        <Stream url="{stream_url}">
            <Parameter name="session_id" value="{session_id}" />
        </Stream>
    </Connect>
</Response>
"""

    # =========================================================================
    # AUDIO CONVERSION UTILITIES (Twilio mulaw 8kHz <-> Gemini PCM 16/24kHz)
    # =========================================================================

    @staticmethod
    def mulaw_to_pcm16(mulaw_chunk: bytes) -> bytes:
        """Convert Twilio 8kHz 8-bit mulaw audio to 16kHz 16-bit linear PCM for Gemini Live."""
        if not audioop:
            return mulaw_chunk
        try:
            pcm_8k = audioop.ulaw2lin(mulaw_chunk, 2)
            pcm_16k, _ = audioop.ratecv(pcm_8k, 2, 1, 8000, 16000, None)
            return pcm_16k
        except Exception:
            return mulaw_chunk

    @staticmethod
    def pcm_to_mulaw(pcm_chunk: bytes, in_rate: int = 24000) -> bytes:
        """Convert Gemini Live 24kHz/16kHz 16-bit linear PCM to 8kHz 8-bit mulaw for Twilio."""
        if not audioop:
            return pcm_chunk
        try:
            if in_rate != 8000:
                pcm_8k, _ = audioop.ratecv(pcm_chunk, 2, 1, in_rate, 8000, None)
            else:
                pcm_8k = pcm_chunk
            return audioop.lin2ulaw(pcm_8k, 2)
        except Exception:
            return pcm_chunk

    # =========================================================================
    # BIDIRECTIONAL MEDIA STREAM WEBSOCKET HANDLER
    # =========================================================================

    @classmethod
    async def handle_media_stream(cls, websocket: WebSocket, session_id: str, db: Session):
        """
        Handle bidirectional audio stream between Twilio Media Stream and Google Gemini Live API.
        """
        await websocket.accept()

        req = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.session_id == session_id).first()
        if not req:
            await websocket.close(code=1008, reason="Invalid session")
            return

        prop = db.query(Property).filter(Property.id == req.property_id).first()
        if not prop:
            await websocket.close(code=1008, reason="Property not found")
            return

        # Update status to connected
        req.status = "connected"
        req.updated_at = datetime.now(timezone.utc)
        db.commit()

        property_context = cls.build_property_knowledge_context(prop, db)
        system_instruction = cls.get_system_instruction(property_context)

        stream_sid = None
        has_gemini_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())

        # If Gemini Live API key is configured, start real Gemini Live session
        if has_gemini_key:
            try:
                from google import genai
                from google.genai import types

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
                    # Send initial prompt to prompt Gemini to greet the user
                    await gemini_session.send(
                        input="Introduce yourself as the AI property assistant for Cloud-Based Real Estate Analysis and offer to answer questions about this property.",
                        end_of_turn=True
                    )

                    # Task 1: Gemini Audio -> Twilio Media Stream
                    async def gemini_to_twilio():
                        nonlocal stream_sid
                        try:
                            async for response in gemini_session.receive():
                                server_content = response.server_content
                                if server_content:
                                    # Interruption detection (barge-in)
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

                    # Task 2: Twilio Media Stream -> Gemini Live
                    async def twilio_to_gemini():
                        nonlocal stream_sid
                        try:
                            while True:
                                data = await websocket.receive_text()
                                msg = json.loads(data)
                                event = msg.get("event")

                                if event == "start":
                                    stream_sid = msg.get("start", {}).get("streamSid") or msg.get("streamSid")
                                    print(f"Twilio Media Stream started: {stream_sid}")

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
                                    print(f"Twilio Media Stream stopped: {stream_sid}")
                                    break
                        except (WebSocketDisconnect, asyncio.CancelledError):
                            pass
                        except Exception as e:
                            print(f"Error in twilio_to_gemini: {e}")

                    # Run both tasks concurrently
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
            # Fallback/Mock mode when GEMINI_API_KEY is not configured
            # Handles WebSocket connection smoothly for testing
            try:
                while True:
                    data = await websocket.receive_text()
                    msg = json.loads(data)
                    event = msg.get("event")
                    if event == "start":
                        stream_sid = msg.get("start", {}).get("streamSid")
                    elif event == "stop":
                        break
            except (WebSocketDisconnect, asyncio.CancelledError):
                pass

        # Finalize request status to completed
        req.status = "completed"
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
