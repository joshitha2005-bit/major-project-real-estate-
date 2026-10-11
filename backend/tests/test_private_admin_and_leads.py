import random
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.property import Property
from app.models.admin_lead import AILead, PrivateOwnerContact, SiteVisit, AdminAuditLog
from app.services.lead_management_service import LeadManagementService


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def admin_token():
    session = SessionLocal()
    try:
        admin = session.query(User).filter(User.role == "ADMIN").first()
        if not admin:
            admin = User(
                email=settings.PRIVATE_ADMIN_EMAIL,
                full_name="Test Administrator",
                hashed_password=get_password_hash(settings.PRIVATE_ADMIN_PASSWORD),
                role="ADMIN",
                is_active=True
            )
            session.add(admin)
            session.commit()
            session.refresh(admin)
        token = create_access_token(subject=admin.id)
        return token
    finally:
        session.close()


@pytest.fixture
def normal_user_token():
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.role == "USER").first()
        if not user:
            user = User(
                email="regular.user@example.com",
                full_name="Regular Public User",
                hashed_password=get_password_hash("UserPass@1234"),
                role="USER",
                is_active=True
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        token = create_access_token(subject=user.id)
        return token
    finally:
        session.close()


# ==============================================================
# 1. ADMIN AUTHENTICATION TESTS
# ==============================================================
def test_admin_login_success(client: TestClient):
    """Test admin authentication with valid environment credentials."""
    session = SessionLocal()
    try:
        admin = session.query(User).filter(User.email == settings.PRIVATE_ADMIN_EMAIL).first()
        if not admin:
            admin = session.query(User).filter(User.role == "ADMIN").first()
        if not admin:
            admin = User(
                email=settings.PRIVATE_ADMIN_EMAIL,
                full_name="Administrator",
                hashed_password=get_password_hash(settings.PRIVATE_ADMIN_PASSWORD),
                role="ADMIN",
                is_active=True
            )
            session.add(admin)
            session.commit()
        else:
            admin.email = settings.PRIVATE_ADMIN_EMAIL
            admin.hashed_password = get_password_hash(settings.PRIVATE_ADMIN_PASSWORD)
            session.commit()
    finally:
        session.close()

    resp = client.post(
        f"{settings.API_V1_STR}/admin/login",
        json={"identifier": settings.PRIVATE_ADMIN_EMAIL, "password": settings.PRIVATE_ADMIN_PASSWORD}
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "ADMIN"
    assert "password" not in str(data)  # Never expose password


def test_admin_login_wrong_password(client: TestClient):
    """Test admin login rejection on bad credentials."""
    resp = client.post(
        f"{settings.API_V1_STR}/admin/login",
        json={"identifier": settings.PRIVATE_ADMIN_EMAIL, "password": "WrongPassword@999"}
    )
    assert resp.status_code == 401
    assert "Invalid administrative credentials" in resp.json()["detail"]


def test_public_user_access_blocked(client: TestClient, normal_user_token: str):
    """Test normal public user receives 403 Forbidden on private admin endpoint."""
    resp = client.get(
        f"{settings.API_V1_STR}/admin/stats",
        headers={"Authorization": f"Bearer {normal_user_token}"}
    )
    assert resp.status_code == 403
    assert "Access denied" in resp.json()["detail"]


def test_unauthenticated_access_blocked(client: TestClient):
    """Test unauthenticated user receives 401 Unauthorized on private admin endpoint."""
    resp = client.get(f"{settings.API_V1_STR}/admin/stats")
    assert resp.status_code == 401


# ==============================================================
# 2. PRIVATE DASHBOARD STATS (10 KPI CARDS)
# ==============================================================
def test_private_dashboard_kpis(client: TestClient, admin_token: str):
    """Test live summary stats from database (zero fake numbers)."""
    resp = client.get(
        f"{settings.API_V1_STR}/admin/stats",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    expected_keys = [
        "total_properties", "public_properties", "private_properties",
        "total_leads", "new_requests", "owner_callbacks", "site_visit_requests",
        "pending_review", "contacted", "closed", "spam_leads"
    ]
    for key in expected_keys:
        assert key in data
        assert isinstance(data[key], int)
        assert data[key] >= 0


# ==============================================================
# 3. PROPERTY PUBLIC / PRIVATE VISIBILITY CONTROL
# ==============================================================
def test_property_visibility_toggle_and_privacy_filter(client: TestClient, admin_token: str, db: Session):
    """
    Test making property PRIVATE:
    1. Verify property disappears from public listings
    2. Verify public user cannot access it (404)
    3. Verify admin can still view it in private dashboard
    4. Make it PUBLIC again and verify public access is restored.
    """
    prop = db.query(Property).first()
    assert prop is not None
    prop_id = prop.id

    # 1. Make property PRIVATE
    patch_resp = client.patch(
        f"{settings.API_V1_STR}/admin/properties/{prop_id}/visibility",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"visibility_status": "PRIVATE"}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["visibility_status"] == "PRIVATE"

    # 2. Verify property disappears from public property listings
    list_resp = client.get(f"{settings.API_V1_STR}/properties/?limit=100")
    assert list_resp.status_code == 200
    public_ids = [p["id"] for p in list_resp.json()["items"]]
    assert prop_id not in public_ids, f"Private property #{prop_id} should not appear in public listings"

    # 3. Verify public direct GET receives 404
    get_resp = client.get(f"{settings.API_V1_STR}/properties/{prop_id}")
    assert get_resp.status_code == 404

    # 4. Verify admin CAN still access it through admin endpoint
    admin_get = client.get(
        f"{settings.API_V1_STR}/admin/properties/{prop_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_get.status_code == 200
    assert admin_get.json()["property"]["visibility_status"] == "PRIVATE"

    # 5. Restore property to PUBLIC
    restore_resp = client.patch(
        f"{settings.API_V1_STR}/admin/properties/{prop_id}/visibility",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"visibility_status": "PUBLIC"}
    )
    assert restore_resp.status_code == 200
    assert restore_resp.json()["visibility_status"] == "PUBLIC"

    # 6. Verify public access restored
    restored_get = client.get(f"{settings.API_V1_STR}/properties/{prop_id}")
    assert restored_get.status_code == 200


# ==============================================================
# 4. PRIVATE OWNER CONTACT INTEGRITY
# ==============================================================
def test_private_owner_contact_isolation(client: TestClient, admin_token: str, db: Session):
    """
    Verify private owner contacts are visible only to admin and never exposed publicly.
    """
    # Select a property that is associated with an existing PrivateOwnerContact
    owner_contact = db.query(PrivateOwnerContact).first()
    assert owner_contact is not None, "Authoritative database must contain at least one PrivateOwnerContact"
    prop = db.query(Property).filter(Property.id == owner_contact.property_id).first()
    assert prop is not None, f"Property #{owner_contact.property_id} associated with owner contact must exist"
    # Admin accesses property detail with owner contact
    admin_resp = client.get(
        f"{settings.API_V1_STR}/admin/properties/{prop.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_resp.status_code == 200
    contact = admin_resp.json()["private_contact"]
    assert contact is not None
    assert "contact_name" in contact
    assert "phone" in contact

    # Public property endpoint must NOT contain private owner fields
    public_resp = client.get(f"{settings.API_V1_STR}/properties/{prop.id}")
    assert public_resp.status_code == 200
    public_data = public_resp.json()
    assert "private_contact" not in public_data


# ==============================================================
# 5. AI CALL REQUEST & LEAD CREATION
# ==============================================================
def test_voice_call_request_and_lead_storage(client: TestClient, db: Session):
    """
    Test Contact Owner with AI flow:
    - User phone + consent creates VoiceCallbackRequest and AILead
    """
    prop = db.query(Property).first()
    test_phone = "+919876543999"
    resp = client.post(
        f"{settings.API_V1_STR}/voice/call-request",
        json={
            "property_id": prop.id,
            "user_phone": test_phone,
            "consent": True,
            "inquiry_text": "Looking for a 3 BHK near tech park, budget around 90 lakhs."
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["call_status"] in ["REQUESTED", "TELEPHONY_NOT_CONFIGURED", "CALLING", "CALL_FAILED"]
    assert data["consent"] is True

    # Check lead created in database
    lead = db.query(AILead).filter(AILead.id == data["lead_id"]).first()
    assert lead is not None
    assert lead.phone == test_phone
    assert lead.property_id == prop.id
    assert lead.validation_status == "VALID"
    assert "90 lakhs" in lead.call_summary or "Tech park" in lead.call_summary or "inquired" in lead.call_summary


# ==============================================================
# 6. RUBBISH / SPAM DETECTION
# ==============================================================
def test_rubbish_conversation_handling(client: TestClient, db: Session):
    """
    Test user saying unrelated/rubbish information ('My dog is sleeping'):
    - Flags as INVALID / SPAM
    - Does NOT count as valid lead
    """
    prop = db.query(Property).first()
    resp = client.post(
        f"{settings.API_V1_STR}/voice/call-request",
        json={
            "property_id": prop.id,
            "user_phone": "+919999900001",
            "consent": True,
            "inquiry_text": "My dog is sleeping and the weather is nice"
        }
    )
    assert resp.status_code == 200
    lead_id = resp.json()["lead_id"]
    lead = db.query(AILead).filter(AILead.id == lead_id).first()
    assert lead.validation_status == "INVALID"
    assert lead.lead_status == "SPAM"


# ==============================================================
# 7. DUPLICATE LEAD DETECTION
# ==============================================================
def test_duplicate_lead_detection(client: TestClient, db: Session):
    """
    Test duplicate submission within 7 days flags is_duplicate=True.
    """
    prop = db.query(Property).first()
    dup_phone = f"+919888{random.randint(100000, 999999)}"
    
    # First request
    resp1 = client.post(
        f"{settings.API_V1_STR}/voice/call-request",
        json={
            "property_id": prop.id,
            "user_phone": dup_phone,
            "consent": True,
            "inquiry_text": "First inquiry about 3BHK pricing."
        }
    )
    assert resp1.status_code == 200
    lead1_id = resp1.json()["lead_id"]

    # Second request with same phone & property
    resp2 = client.post(
        f"{settings.API_V1_STR}/voice/call-request",
        json={
            "property_id": prop.id,
            "user_phone": dup_phone,
            "consent": True,
            "inquiry_text": "Second inquiry, follow up."
        }
    )
    assert resp2.status_code == 200
    lead2_id = resp2.json()["lead_id"]

    lead2 = db.query(AILead).filter(AILead.id == lead2_id).first()
    assert lead2.is_duplicate is True
    assert lead2.duplicate_of_id == lead1_id


# ==============================================================
# 8. HUMAN REVIEW & SEND TO OWNER
# ==============================================================
def test_lead_approval_and_honest_owner_send(client: TestClient, admin_token: str, db: Session):
    """
    Test admin review workflow:
    1. Admin approves lead
    2. Attempt send to owner -> correctly reports NOT_CONFIGURED without false claims
    """
    lead = db.query(AILead).filter(AILead.validation_status == "VALID").first()
    assert lead is not None

    # Ensure a verified owner contact exists so notification configuration is tested
    contact = db.query(PrivateOwnerContact).filter(PrivateOwnerContact.property_id == lead.property_id).first()
    if not contact:
        contact = PrivateOwnerContact(
            property_id=lead.property_id,
            contact_name="Verified Owner",
            phone="+919876543210",
            contact_type="OWNER",
            verification_status="VERIFIED"
        )
        db.add(contact)
        db.commit()
    elif contact.verification_status != "VERIFIED":
        contact.verification_status = "VERIFIED"
        db.commit()

    # Approve
    appr_resp = client.post(
        f"{settings.API_V1_STR}/admin/leads/{lead.id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert appr_resp.status_code == 200
    assert appr_resp.json()["success"] is True

    # Send to owner
    send_resp = client.post(
        f"{settings.API_V1_STR}/admin/leads/{lead.id}/send-owner",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert send_resp.status_code == 200
    send_data = send_resp.json()
    # Since OWNER_NOTIFICATION_PROVIDER is empty, must report NOT_CONFIGURED honestly
    assert send_data["status"] == "NOT_CONFIGURED"
    assert "not configured" in send_data["message"].lower()


# ==============================================================
# 9. PDF LEAD REPORT GENERATION
# ==============================================================
def test_download_lead_pdf_report(client: TestClient, admin_token: str, db: Session):
    """
    Verify downloadable PDF report:
    - Generated with ReportLab
    - Begins with PDF magic bytes (%PDF)
    - Protected strictly for admin
    """
    lead = db.query(AILead).filter(AILead.validation_status == "VALID").first()
    resp = client.get(
        f"{settings.API_V1_STR}/admin/leads/{lead.id}/report-pdf",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF")
    assert len(resp.content) > 1000


# ==============================================================
# 10. SITE VISIT APPOINTMENT MANAGEMENT
# ==============================================================
def test_site_visit_status_lifecycle(client: TestClient, admin_token: str, db: Session):
    """
    Test site visit status transitions: REQUESTED -> CONFIRMED -> COMPLETED
    """
    visit = db.query(SiteVisit).first()
    if not visit:
        visit = SiteVisit(
            appointment_code="VISIT-TEST-01",
            lead_id=1,
            property_id=1,
            user_name="Test Visitor",
            user_phone="+919876543210",
            visit_date="2026-10-15",
            visit_time="10:00 AM",
            status="REQUESTED"
        )
        db.add(visit)
        db.commit()
        db.refresh(visit)

    # 1. Confirm site visit
    confirm_resp = client.patch(
        f"{settings.API_V1_STR}/admin/site-visits/{visit.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "CONFIRMED", "admin_notes": "Confirmed with building security desk."}
    )
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["status"] == "CONFIRMED"

    # 2. Complete site visit
    complete_resp = client.patch(
        f"{settings.API_V1_STR}/admin/site-visits/{visit.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "COMPLETED", "admin_notes": "Client visited property successfully."}
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "COMPLETED"
