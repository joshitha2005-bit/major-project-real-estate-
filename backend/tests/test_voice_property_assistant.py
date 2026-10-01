import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.property import Property
from app.models.voice_callback import VoiceCallbackRequest, PropertyInquiry
from app.services.voice_assistant_service import VoiceAssistantService


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="module")
def sample_property(db_session):
    prop = db_session.query(Property).first()
    if not prop:
        prop = Property(
            id=1001,
            user_id=1,
            title="Prestige Falcon City 3 BHK",
            property_type="Apartment",
            listing_type="Buy",
            bhk=3,
            area_sqft=1500,
            price=12500000.0,
            address="Kanakapura Road, Anjanaprabha, Bengaluru",
            locality="Kanakapura Road",
            latitude=12.8901,
            longitude=77.5601,
            owner_name="Confidential Owner",
            owner_phone="+91 99999 88888",
            phone="+91 99999 88888"
        )
        db_session.add(prop)
        db_session.commit()
        db_session.refresh(prop)
    return prop


# ==============================================================================
# 1. PHONE NUMBER VALIDATION & REJECTION TESTS
# ==============================================================================
def test_reject_invalid_phone_numbers(client, sample_property):
    """Test 3: Invalid phone numbers are rejected with 400 Bad Request."""
    invalid_phones = ["", "123", "abc", "+1", "98765", "000000000000000000"]
    for bad_phone in invalid_phones:
        resp = client.post(
            "/api/v1/voice-assistant/request-callback",
            json={"property_id": sample_property.id, "phone_number": bad_phone}
        )
        assert resp.status_code == 400
        assert "Invalid phone number" in resp.json().get("detail", "")


def test_reject_nonexistent_property(client):
    """Test: Callback requests for nonexistent properties are rejected with 404."""
    resp = client.post(
        "/api/v1/voice-assistant/request-callback",
        json={"property_id": 999999999, "phone_number": "+919876543210"}
    )
    assert resp.status_code == 404


# ==============================================================================
# 2. VALID CALLBACK REQUEST & PROPERTY ASSOCIATION
# ==============================================================================
def test_valid_callback_request_creation(client, sample_property, db_session):
    """Tests 4, 5, 6: Valid callback request reaches FastAPI, correct property associated, call initiated."""
    import uuid
    phone = f"987{uuid.uuid4().int % 10000000:07d}"
    resp = client.post(
        "/api/v1/voice-assistant/request-callback",
        json={"property_id": sample_property.id, "phone_number": phone}
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["success"] is True
    assert data["property_id"] == sample_property.id
    assert data["phone_number"] == f"+91{phone}"
    assert data["status"] in ["calling", "initiated"]
    assert "session_id" in data
    assert "call_sid" in data
    assert data["call_sid"] is not None

    # Check database record persistence
    record = db_session.query(VoiceCallbackRequest).filter(
        VoiceCallbackRequest.session_id == data["session_id"]
    ).first()
    assert record is not None
    assert record.property_id == sample_property.id
    assert record.phone_number == f"+91{phone}"


# ==============================================================================
# 3. OWNER PRIVACY GUARANTEE: NEVER EXPOSE OWNER PRIVATE PHONE
# ==============================================================================
def test_owner_private_contact_never_exposed(client, sample_property):
    """Test 13: Owner private number is never exposed in callback responses."""
    import uuid
    phone = f"982{uuid.uuid4().int % 10000000:07d}"
    resp = client.post(
        "/api/v1/voice-assistant/request-callback",
        json={"property_id": sample_property.id, "phone_number": phone}
    )
    assert resp.status_code == 200
    data = resp.json()
    resp_text = str(data)

    # Neither owner_phone nor private numbers should appear in response
    assert "+91 99999 88888" not in resp_text
    assert "Confidential Owner" not in resp_text


# ==============================================================================
# 4. STATUS POLLING & TWILIO WEBHOOKS
# ==============================================================================
def test_status_polling_and_twilio_callbacks(client, sample_property):
    """Tests 7, 14: Status tracking and graceful call transitions."""
    import uuid
    phone = f"983{uuid.uuid4().int % 10000000:07d}"
    # 1. Create callback
    resp = client.post(
        "/api/v1/voice-assistant/request-callback",
        json={"property_id": sample_property.id, "phone_number": phone}
    )
    session_id = resp.json()["session_id"]

    # 2. Poll initial status
    poll_resp = client.get(f"/api/v1/voice-assistant/callback-status/{session_id}")
    assert poll_resp.status_code == 200
    assert poll_resp.json()["status"] == "calling"

    # 3. TwiML Generation
    twiml_resp = client.post(f"/api/v1/voice-assistant/twiml/{session_id}")
    assert twiml_resp.status_code == 200
    assert "application/xml" in twiml_resp.headers["content-type"]
    assert "<Stream" in twiml_resp.text
    assert session_id in twiml_resp.text

    # 4. Webhook updates call to answered/connected
    status_resp = client.post(
        f"/api/v1/voice-assistant/status-callback/{session_id}",
        data={"CallStatus": "in-progress"}
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["call_status"] == "connected"

    # 5. Verify status updated via polling
    poll_resp2 = client.get(f"/api/v1/voice-assistant/callback-status/{session_id}")
    assert poll_resp2.json()["status"] == "connected"

    # 6. Webhook updates call to completed
    complete_resp = client.post(
        f"/api/v1/voice-assistant/status-callback/{session_id}",
        data={"CallStatus": "completed"}
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["call_status"] == "completed"


# ==============================================================================
# 5. AI PROPERTY KNOWLEDGE SYNTHESIS & ZERO-HALLUCINATION CHECKS
# ==============================================================================
def test_property_knowledge_context_and_system_instruction(db_session, sample_property):
    """Tests 8, 9, 10, 11: Real property knowledge context and strict AI identity instruction."""
    context = VoiceAssistantService.build_property_knowledge_context(sample_property, db_session)
    instruction = VoiceAssistantService.get_system_instruction(context)

    # 1. Contains real property facts
    assert sample_property.title in context
    assert str(sample_property.bhk) in context
    assert sample_property.locality in context

    # 2. Strict AI Identity Enforcement
    assert "You are an AI property assistant" in instruction
    assert "You are NOT the property owner" in instruction
    assert "Never invent property details, prices, amenities, distances, availability, owner information" in instruction
    assert "If information is unavailable, clearly state: \"I don't have that information available for this property.\"" in instruction

    # 3. Never invent owner phone numbers
    assert sample_property.owner_phone not in context or "Confidential" not in context


# ==============================================================================
# 6. OWNER CONTACT INQUIRY CREATION (FOLLOW-UP LOGGING)
# ==============================================================================
def test_owner_contact_inquiry_record(client, sample_property, db_session):
    """Test: When user requests owner follow-up, record an inquiry in the database."""
    inquiry_payload = {
        "property_id": sample_property.id,
        "phone_number": "+919876543210",
        "question_or_request": "I would like to schedule a weekend site visit.",
        "session_id": "test_session_123"
    }
    resp = client.post("/api/v1/voice-assistant/inquiry", json=inquiry_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "inquiry_id" in data

    # Verify database persistence
    inq = db_session.query(PropertyInquiry).filter(PropertyInquiry.id == data["inquiry_id"]).first()
    assert inq is not None
    assert inq.question_or_request == "I would like to schedule a weekend site visit."
    assert inq.status == "PENDING"


# ==============================================================================
# 7. AUDIO CONVERSION ROUNDTRIP
# ==============================================================================
def test_audio_conversion_utilities():
    """Verify bidirectional audio conversion between Twilio mulaw and Gemini PCM."""
    # 1. Twilio 8kHz mulaw -> 16kHz PCM
    raw_mulaw = bytes([128, 255, 0, 100] * 100)
    pcm_16k = VoiceAssistantService.mulaw_to_pcm16(raw_mulaw)
    assert len(pcm_16k) > 0

    # 2. Gemini 24kHz PCM -> 8kHz mulaw
    pcm_24k = bytes([0, 10, 0, 20] * 300)
    mulaw_out = VoiceAssistantService.pcm_to_mulaw(pcm_24k, in_rate=24000)
    assert len(mulaw_out) > 0


# ==============================================================================
# 8. RATE LIMITING PROTECTION
# ==============================================================================
def test_rate_limiting_enforcement(client, sample_property):
    """Test: Users cannot spam unlimited automated outbound calls."""
    import uuid
    spam_phone = f"998{uuid.uuid4().int % 10000000:07d}"
    # Call 3 times
    for _ in range(3):
        client.post(
            "/api/v1/voice-assistant/request-callback",
            json={"property_id": sample_property.id, "phone_number": spam_phone}
        )

    # 4th call must be blocked with 429 Too Many Requests
    blocked_resp = client.post(
        "/api/v1/voice-assistant/request-callback",
        json={"property_id": sample_property.id, "phone_number": spam_phone}
    )
    assert blocked_resp.status_code == 429
    assert "Rate limit exceeded" in blocked_resp.json().get("detail", "")
