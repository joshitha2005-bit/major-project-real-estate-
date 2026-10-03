import os
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal, get_db
from app.core.config import settings
from app.models.property import Property
from app.models.admin_lead import AILead, SiteVisit, PrivateOwnerContact
from app.models.voice_callback import VoiceCallbackRequest
from app.services.voice_assistant_service import VoiceAssistantService
from app.services.voice_conversation_engine import VoiceConversationEngine, VoiceConversationSession
from app.services.lead_management_service import LeadManagementService

client = TestClient(app)


@pytest.fixture
def db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@pytest.fixture(autouse=True)
def clean_test_rate_limits(db: Session):
    """Clear callback records to prevent cross-test rate limit collision."""
    db.query(VoiceCallbackRequest).delete()
    db.commit()


@pytest.fixture
def sample_property(db: Session):
    """Ensure a verified sample property exists in test database."""
    prop = db.query(Property).first()
    if not prop:
        prop = Property(
            title="Sobha Classic Residency",
            locality="Harlur",
            address="Outer Ring Road, Harlur, Bengaluru",
            price=15000000.0,
            bhk=3,
            property_type="Apartment",
            area_sqft=1850,
            parking="Covered",
            furnishing="Semi-Furnished",
            facing="East",
            amenities=["Gym", "Swimming Pool", "Power Backup", "Security", "Covered Parking"],
            description="Premium 3 BHK apartment with verified amenities and excellent connectivity."
        )
        db.add(prop)
        db.commit()
        db.refresh(prop)
    return prop


# ==============================================================================
# 1 & 2. CALL REQUEST & CONSENT
# ==============================================================================
def test_call_request_requires_consent(sample_property):
    """Calling without consent must be rejected with 400 Bad Request."""
    res = client.post("/api/v1/admin/private/voice/call-request", json={
        "property_id": sample_property.id,
        "user_phone": "+919876543210",
        "consent": False
    })
    assert res.status_code == 400
    assert "consent" in res.json()["detail"].lower()


def test_call_request_with_consent_registers_lead(sample_property, db: Session):
    """Valid call request with consent creates record in database."""
    phone = "+919876543210"
    res = client.post("/api/v1/admin/private/voice/call-request", json={
        "property_id": sample_property.id,
        "user_phone": phone,
        "consent": True,
        "inquiry_text": "Interested in site visit."
    })
    assert res.status_code == 200
    data = res.json()
    assert data["session_id"] is not None
    assert data["consent"] is True

    # Verify callback request in database
    cb = db.query(VoiceCallbackRequest).filter(VoiceCallbackRequest.session_id == data["session_id"]).first()
    assert cb is not None
    assert cb.consent is True


# ==============================================================================
# 3. PROPERTY CONTEXT LOADING
# ==============================================================================
def test_property_context_loading_verified_only(sample_property, db: Session):
    """Context compiler must strictly extract verified facts and never invent missing data."""
    ctx = VoiceConversationEngine.build_property_context(sample_property, db)
    assert ctx["property_id"] == sample_property.id
    assert ctx["title"] == sample_property.title
    assert "₹" in ctx["price_formatted"]
    assert ctx["bhk"] == sample_property.bhk
    assert ctx["property_type"] == sample_property.property_type

    knowledge_text = VoiceAssistantService.build_property_knowledge_context(sample_property, db)
    assert sample_property.title in knowledge_text
    assert "PROPERTY SPECIFICATIONS:" in knowledge_text


# ==============================================================================
# 4 & 5. TWILIO REAL CALL CREATION & FAILURE HANDLING (NO FAKE SIDs)
# ==============================================================================
def test_twilio_unconfigured_returns_truthful_status_without_fake_sid(sample_property, db: Session):
    """
    STRICT REQUIREMENT 1: When Twilio credentials are not configured,
    truthfully return TELEPHONY_NOT_CONFIGURED. NEVER return fake SIM_ Call SID.
    """
    mock_diag = {
        "twilio_configured": False,
        "gemini_configured": True,
        "uses_localhost": False,
        "ready_for_real_calls": False,
        "webhook_url": "http://localhost:8000/api/v1/voice-assistant/twiml"
    }
    with patch("app.services.voice_assistant_service.VoiceAssistantService.get_telephony_diagnostics", return_value=mock_diag):
        with patch.object(settings, "TWILIO_ACCOUNT_SID", ""):
            with patch.object(settings, "TWILIO_PHONE_NUMBER", ""):
                res = VoiceAssistantService.initiate_voice_callback(
                    property_id=sample_property.id,
                    phone_number="+919876543210",
                    user_id=None,
                    db=db
                )
                assert res["success"] is False
                assert res["status"] == "TELEPHONY_NOT_CONFIGURED"
                assert res["call_sid"] is None  # NO FAKE SID
                assert res["diagnostics"]["twilio_configured"] is False
                assert res["diagnostics"]["twilio_api_request"] is False
                assert res["diagnostics"]["call_sid"] is None


def test_twilio_configured_creates_real_call(sample_property, db: Session):
    """When credentials exist, Twilio calls.create is invoked and returns real Call SID."""
    mock_call = MagicMock()
    mock_call.sid = "CA1234567890abcdef1234567890abcdef"
    mock_call.status = "queued"

    mock_client_instance = MagicMock()
    mock_client_instance.calls.create.return_value = mock_call

    with patch.object(settings, "TWILIO_ACCOUNT_SID", "AC" + "1" * 32), \
         patch.object(settings, "TWILIO_AUTH_TOKEN", "auth_token_mock_12345"), \
         patch.object(settings, "TWILIO_PHONE_NUMBER", "+12025550199"), \
         patch("twilio.rest.Client", return_value=mock_client_instance):

        res = VoiceAssistantService.initiate_voice_callback(
            property_id=sample_property.id,
            phone_number="+919876543210",
            user_id=None,
            db=db
        )
        assert res["success"] is True
        assert res["status"] == "CALLING"
        assert res["call_sid"] == "CA1234567890abcdef1234567890abcdef"
        assert res["diagnostics"]["twilio_configured"] is True
        assert res["diagnostics"]["twilio_api_request"] is True
        assert mock_client_instance.calls.create.called


def test_twilio_api_failure_handled_truthfully(sample_property, db: Session):
    """If Twilio throws an API exception, failure code and message are captured truthfully."""
    mock_client_instance = MagicMock()
    mock_client_instance.calls.create.side_effect = Exception("21211 - The 'To' number is not a valid phone number.")

    with patch.object(settings, "TWILIO_ACCOUNT_SID", "AC" + "1" * 32), \
         patch.object(settings, "TWILIO_AUTH_TOKEN", "auth_token_mock_12345"), \
         patch.object(settings, "TWILIO_PHONE_NUMBER", "+12025550199"), \
         patch("twilio.rest.Client", return_value=mock_client_instance):

        res = VoiceAssistantService.initiate_voice_callback(
            property_id=sample_property.id,
            phone_number="+919876543299",
            user_id=None,
            db=db
        )
        assert res["success"] is False
        assert res["status"] == "CALL_FAILED"
        assert res["call_sid"] is None
        assert "21211" in res["diagnostics"]["failure_message"]


# ==============================================================================
# 6. PUBLIC HTTPS WEBHOOK DIAGNOSTIC
# ==============================================================================
def test_public_webhook_diagnostics():
    """Diagnoses whether webhook base URL is localhost or public HTTPS."""
    # Test localhost detection
    with patch.object(settings, "VOICE_PUBLIC_BASE_URL", "http://localhost:8000"):
        diag = VoiceAssistantService.get_telephony_diagnostics()
        assert diag["uses_localhost"] is True
        assert diag["public_webhook_configured"] is False

    # Test public HTTPS tunnel URL
    with patch.object(settings, "VOICE_PUBLIC_BASE_URL", "https://realestate-ai.ngrok-free.app"):
        diag = VoiceAssistantService.get_telephony_diagnostics()
        assert diag["uses_localhost"] is False
        assert diag["public_webhook_configured"] is True


def test_telephony_status_api_endpoint():
    """GET /api/v1/voice-assistant/telephony-status returns diagnostic object."""
    res = client.get("/api/v1/voice-assistant/telephony-status")
    assert res.status_code == 200
    data = res.json()
    assert "telephony" in data
    assert "twilio_configured" in data["telephony"]
    assert "public_webhook_configured" in data["telephony"]


# ==============================================================================
# 7, 8, 9, 10, 11. AI CONVERSATION & NATURAL EXTRACTION
# ==============================================================================
def test_ai_greeting_introduces_assistant(sample_property, db: Session):
    """AI must introduce itself clearly with property title and location."""
    prop_ctx = VoiceConversationEngine.build_property_context(sample_property, db)
    sess = VoiceConversationSession("sess_001", sample_property.id, "+919876543210", prop_ctx)
    greeting = sess.get_initial_greeting()

    assert "AI property assistant" in greeting
    assert sample_property.title in greeting
    assert "Is now a good time to talk?" in greeting


def test_natural_extraction_single_utterance(sample_property, db: Session):
    """
    User: 'My name is Joshitha and my budget is around 1.5 crore.'
    AI should extract: full_name=Joshitha, budget=1.5 Crore and continue with next missing field.
    """
    prop_ctx = VoiceConversationEngine.build_property_context(sample_property, db)
    sess = VoiceConversationSession("sess_002", sample_property.id, "+919876543210", prop_ctx)
    sess.get_initial_greeting()

    reply = sess.process_user_utterance("My name is Joshitha and my budget is around 1.5 crore.")
    
    assert sess.full_name == "Joshitha"
    assert "Crore" in (sess.budget or "")
    # Should NOT ask name or budget again!
    assert "your name" not in reply.lower()
    assert "approximate budget" not in reply.lower()
    # Should ask loan or site visit
    assert ("loan" in reply.lower() or "visit" in reply.lower())


def test_budget_extraction_patterns():
    """Verify various monetary budget expressions."""
    assert "Crore" in (VoiceConversationEngine.parse_budget_from_text("My budget is 1.5 cr") or "")
    assert "Crore" in (VoiceConversationEngine.parse_budget_from_text("around 2 crore") or "")
    assert "Lakh" in (VoiceConversationEngine.parse_budget_from_text("85 lakhs") or "")
    assert "Lakh" in (VoiceConversationEngine.parse_budget_from_text("about 60 lac") or "")


def test_mid_call_property_question_answering(sample_property, db: Session):
    """
    USER: 'Is there parking?'
    AI: Answers from verified property context ('Yes, the listing indicates parking is available.'),
    then continues with lead collection.
    """
    prop_ctx = VoiceConversationEngine.build_property_context(sample_property, db)
    sess = VoiceConversationSession("sess_003", sample_property.id, "+919876543210", prop_ctx)
    sess.get_initial_greeting()

    reply = sess.process_user_utterance("Is there parking?")
    assert "parking" in reply.lower()
    assert "name" in reply.lower() or "budget" in reply.lower()


def test_price_negotiation_question_answered_honestly(sample_property, db: Session):
    """AI must state price negotiation requires confirmation from owner/agent."""
    prop_ctx = VoiceConversationEngine.build_property_context(sample_property, db)
    ans = VoiceConversationEngine.answer_property_question("Is the price negotiable?", prop_ctx)
    assert ans is not None
    assert "negotiation must be confirmed" in ans.lower() or "owner" in ans.lower()


# ==============================================================================
# 12 & 13. RUBBISH / UNRELATED SPEECH HANDLING
# ==============================================================================
def test_rubbish_response_clarified_politely(sample_property, db: Session):
    """
    User: 'My dog is sleeping'
    AI must politely clarify without hallucinating or inferring answers.
    """
    prop_ctx = VoiceConversationEngine.build_property_context(sample_property, db)
    sess = VoiceConversationSession("sess_004", sample_property.id, "+919876543210", prop_ctx)
    sess.get_initial_greeting()

    reply = sess.process_user_utterance("My dog is sleeping")
    assert "didn't quite catch that" in reply.lower()
    assert sess.rubbish_count == 1
    assert sess.budget is None  # Did not infer fake budget


def test_repeated_rubbish_marks_lead_needs_review(sample_property, db: Session):
    """Repeated rubbish marks validation_status as NEEDS_REVIEW without fabricating data."""
    prop_ctx = VoiceConversationEngine.build_property_context(sample_property, db)
    sess = VoiceConversationSession("sess_005", sample_property.id, "+919876543210", prop_ctx)
    sess.get_initial_greeting()

    sess.process_user_utterance("My dog is sleeping")
    reply2 = sess.process_user_utterance("blabla gibberish")
    
    assert sess.rubbish_count >= 2
    assert sess.validation_status == "NEEDS_REVIEW"
    assert sess.lead_status == "SPAM_REVIEW"
    assert "skip" in reply2.lower()


# ==============================================================================
# 14. SITE VISIT EXTRACTION & SITEVISIT RECORD
# ==============================================================================
def test_site_visit_extraction_and_persistence(sample_property, db: Session):
    """AI extracts site visit request and creates SiteVisit record with status REQUESTED."""
    prop_ctx = VoiceConversationEngine.build_property_context(sample_property, db)
    sess = VoiceConversationSession("sess_006", sample_property.id, "+919876543210", prop_ctx)
    sess.get_initial_greeting()

    sess.process_user_utterance("My name is Ramesh")
    sess.process_user_utterance("My budget is 1.2 crore")
    sess.process_user_utterance("No loan required")
    reply = sess.process_user_utterance("Yes, I would like to schedule a site visit for Saturday at 11 am")

    assert sess.site_visit_requested is True
    assert sess.preferred_site_visit_date == "Saturday"
    assert "11:00 AM" in (sess.preferred_site_visit_time or "")

    # Finalize and persist
    lead = sess.finalize_and_persist(db, call_sid="CA_TEST_123")
    assert lead.id is not None
    assert lead.site_visit_requested is True

    # Verify SiteVisit record
    sv = db.query(SiteVisit).filter(SiteVisit.lead_id == lead.id).first()
    assert sv is not None
    assert sv.status == "REQUESTED"
    assert "Saturday" in sv.visit_date


# ==============================================================================
# 15. DUPLICATE LEAD DETECTION
# ==============================================================================
def test_duplicate_lead_detection(sample_property, db: Session):
    """Multiple calls from the same phone number for the same property flag duplicate."""
    import uuid
    phone = f"+919{uuid.uuid4().hex[:9]}"
    lead1 = LeadManagementService.create_or_process_call_lead(
        db=db,
        phone=phone,
        property_id=sample_property.id,
        inquiry_text="First inquiry"
    )
    assert lead1.is_duplicate is False

    lead2 = LeadManagementService.create_or_process_call_lead(
        db=db,
        phone=phone,
        property_id=sample_property.id,
        inquiry_text="Second inquiry"
    )
    assert lead2.is_duplicate is True
    assert lead2.duplicate_of_id == lead1.id


# ==============================================================================
# 16. DATABASE PERSISTENCE
# ==============================================================================
def test_complete_lead_database_persistence(sample_property, db: Session):
    """Verify all structured lead fields, call_sid, duration, and transcript are persisted."""
    prop_ctx = VoiceConversationEngine.build_property_context(sample_property, db)
    sess = VoiceConversationSession("sess_007", sample_property.id, "+919876543299", prop_ctx)
    sess.get_initial_greeting()
    sess.process_user_utterance("My name is Priya, budget 90 lakhs, yes loan required, visit tomorrow evening")
    
    lead = sess.finalize_and_persist(db, call_sid="CA_PERSIST_TEST")
    db_lead = db.query(AILead).filter(AILead.id == lead.id).first()

    assert db_lead is not None
    assert db_lead.name == "Priya"
    assert "90 Lakh" in db_lead.budget
    assert db_lead.loan_required == "YES"
    assert db_lead.site_visit_requested is True
    assert db_lead.call_sid == "CA_PERSIST_TEST"
    assert db_lead.call_status == "COMPLETED"
    assert db_lead.transcript is not None
    assert len(db_lead.transcript) > 20


# ==============================================================================
# 17. ADMIN DASHBOARD METRICS & DRAWER
# ==============================================================================
def test_admin_dashboard_stats_endpoint(db: Session):
    """GET /api/v1/admin/private/stats returns telephony and lead KPI counts."""
    # Obtain admin token
    from app.core.security import create_access_token
    from app.models.user import User

    admin_user = db.query(User).filter(User.role == "ADMIN").first()
    token = create_access_token(subject=admin_user.id if admin_user else 1)

    res = client.get(
        "/api/v1/admin/private/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "total_calls" in data
    assert "completed_calls" in data
    assert "failed_calls" in data
    assert "new_leads" in data
    assert "site_visit_requests" in data
    assert "leads_needing_review" in data


# ==============================================================================
# 18. PDF GENERATION
# ==============================================================================
def test_lead_pdf_report_generation(sample_property, db: Session):
    """PDF report must generate valid binary content with metadata."""
    prop_ctx = VoiceConversationEngine.build_property_context(sample_property, db)
    sess = VoiceConversationSession("sess_pdf", sample_property.id, "+919876543288", prop_ctx)
    sess.get_initial_greeting()
    sess.process_user_utterance("My name is Ananya, budget 1.4 crore, loan yes, visit Sunday")
    lead = sess.finalize_and_persist(db, call_sid="CA_PDF_TEST")

    pdf_bytes = LeadManagementService.generate_lead_pdf(db, lead.id)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    assert pdf_bytes[:4] == b"%PDF"


# ==============================================================================
# 19. OWNER NOTIFICATION & PRIVACY PROTECTION
# ==============================================================================
def test_owner_private_contact_protection(sample_property, db: Session):
    """Owner phone number must NEVER be exposed publicly or in AI voice conversation."""
    owner = db.query(PrivateOwnerContact).filter(PrivateOwnerContact.property_id == sample_property.id).first()
    if not owner:
        owner = PrivateOwnerContact(
            property_id=sample_property.id,
            contact_name="Verified Landlord",
            phone="+919999988888",
            email="landlord@private.com",
            verification_status="VERIFIED"
        )
        db.add(owner)
        db.commit()

    # Verify context given to AI does NOT contain owner private phone
    prop_ctx = VoiceConversationEngine.build_property_context(sample_property, db)
    prop_ctx_str = str(prop_ctx)
    assert owner.phone not in prop_ctx_str
    assert "landlord@private.com" not in prop_ctx_str

    # Spoken AI answers must not leak owner phone
    ans = VoiceConversationEngine.answer_property_question("What is the owner's phone number?", prop_ctx)
    if ans:
        assert owner.phone not in ans