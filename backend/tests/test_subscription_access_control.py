import hmac
import hashlib
import json
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.property import Property
from app.models.subscription import Subscription
from app.services.subscription_service import SubscriptionService


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="module")
def test_property_id(db: Session):
    prop = db.query(Property).first()
    if not prop:
        prop = Property(
            title="Bengaluru Test Villa",
            price=12500000.0,
            area_sqft=1850.0,
            bhk=3,
            locality="Whitefield",
            city="Bengaluru",
            latitude=12.9698,
            longitude=77.7499,
            status="active"
        )
        db.add(prop)
        db.commit()
        db.refresh(prop)
    return prop.id


@pytest.fixture(scope="module")
def free_user(db: Session):
    user = db.query(User).filter(User.email == "test_free_user@example.com").first()
    if not user:
        user = User(
            email="test_free_user@example.com",
            full_name="Free Tier User",
            hashed_password=get_password_hash("FreePassword123!"),
            role="USER",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    # Ensure no active subscription
    db.query(Subscription).filter(Subscription.user_id == user.id).delete()
    db.commit()
    return user


@pytest.fixture(scope="module")
def free_user_token(free_user: User):
    return create_access_token(subject=free_user.id)


@pytest.fixture(scope="module")
def pro_user(db: Session):
    user = db.query(User).filter(User.email == "test_pro_user@example.com").first()
    if not user:
        user = User(
            email="test_pro_user@example.com",
            full_name="PropPulse Pro User",
            hashed_password=get_password_hash("ProPassword123!"),
            role="USER",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Set active Pro subscription
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=30)
    if not sub:
        sub = Subscription(
            user_id=user.id,
            plan="PRO",
            plan_name="PROPULSE_PRO_299",
            subscription_status="ACTIVE",
            status="ACTIVE",
            plan_amount=299.0,
            currency="INR",
            start_date=now,
            end_date=future,
            razorpay_payment_id="pay_test_active_123"
        )
        db.add(sub)
    else:
        sub.plan = "PRO"
        sub.subscription_status = "ACTIVE"
        sub.status = "ACTIVE"
        sub.start_date = now
        sub.end_date = future
        sub.razorpay_payment_id = "pay_test_active_123"
    db.commit()
    return user


@pytest.fixture(scope="module")
def pro_user_token(pro_user: User):
    return create_access_token(subject=pro_user.id)


@pytest.fixture(scope="module")
def admin_token(db: Session):
    admin = db.query(User).filter(User.role == "ADMIN").first()
    if not admin:
        admin = User(
            email=settings.PRIVATE_ADMIN_EMAIL,
            full_name="Platform Admin",
            hashed_password=get_password_hash(settings.PRIVATE_ADMIN_PASSWORD),
            role="ADMIN",
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    return create_access_token(subject=admin.id)


# ============================================================================
# 1. PROPERTY BROWSING FOR FREE USERS (UNRESTRICTED)
# ============================================================================
def test_free_user_can_browse_properties(client: TestClient, free_user_token: str):
    """FREE users must have unrestricted access to search and property listings."""
    res = client.get("/api/v1/properties/", headers={"Authorization": f"Bearer {free_user_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "items" in data or isinstance(data, list)

    res_public = client.get("/api/v1/properties/")
    assert res_public.status_code == 200


# ============================================================================
# 2. FREE USER BLOCKED FROM PREMIUM AI & SHAP ENDPOINT
# ============================================================================
def test_free_user_blocked_from_premium_ai_endpoint(client: TestClient, free_user_token: str, test_property_id: int):
    """FREE users must be blocked from AI multimodal valuation and SHAP analysis with 403 PRO_REQUIRED."""
    res = client.get(
        f"/api/v1/ai/analyze-property/{test_property_id}",
        headers={"Authorization": f"Bearer {free_user_token}"}
    )
    assert res.status_code == 403
    payload = res.json()
    detail = payload.get("detail", payload)
    assert detail.get("code") == "PRO_REQUIRED"
    assert "PropPulse Pro" in detail.get("message", "")


# ============================================================================
# 3. FREE USER BLOCKED FROM AI VOICE CALLBACK
# ============================================================================
def test_free_user_blocked_from_ai_voice_callback(client: TestClient, free_user_token: str, test_property_id: int):
    """FREE users must be blocked from requesting automated outbound AI calls."""
    res = client.post(
        "/api/v1/voice-assistant/request-callback",
        headers={"Authorization": f"Bearer {free_user_token}"},
        json={
            "property_id": test_property_id,
            "phone_number": "+919876543210"
        }
    )
    assert res.status_code == 403
    payload = res.json()
    detail = payload.get("detail", payload)
    assert detail.get("code") == "PRO_REQUIRED"


# ============================================================================
# 4. FREE USER BLOCKED FROM LOAN COMPARISON
# ============================================================================
def test_free_user_blocked_from_loan_comparison(client: TestClient, free_user_token: str, test_property_id: int):
    """FREE users must be blocked from multi-bank comparison with 403 PRO_REQUIRED."""
    res = client.post(
        "/api/v1/loans/compare",
        headers={"Authorization": f"Bearer {free_user_token}"},
        json={
            "property_id": test_property_id,
            "full_name": "Test User",
            "mobile_number": "9876543210",
            "age": 30,
            "monthly_income": 120000,
            "employment_type": "Salaried",
            "existing_monthly_emi": 0,
            "property_price": 5000000,
            "down_payment": 1000000,
            "desired_loan_amount": 4000000,
            "preferred_tenure_years": 20
        }
    )
    assert res.status_code == 403
    payload = res.json()
    detail = payload.get("detail", payload)
    assert detail.get("code") == "PRO_REQUIRED"


# ============================================================================
# 5. PRO ACTIVE USER CAN ACCESS PREMIUM AI VALUATION
# ============================================================================
def test_pro_active_user_can_access_ai_endpoint(client: TestClient, pro_user_token: str, test_property_id: int):
    """PRO users with ACTIVE status must successfully receive multimodal valuations."""
    res = client.get(
        f"/api/v1/ai/analyze-property/{test_property_id}",
        headers={"Authorization": f"Bearer {pro_user_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "property" in data
    assert "safety_guard" in data or "image_ai" in data or "text_ai" in data


# ============================================================================
# 6. PRO ACTIVE USER CAN INITIATE AI VOICE CALLBACK
# ============================================================================
def test_pro_active_user_can_use_ai_voice_callback(client: TestClient, pro_user_token: str, test_property_id: int):
    """PRO users must not be blocked by the subscription guard when requesting voice callbacks."""
    res = client.post(
        "/api/v1/voice-assistant/request-callback",
        headers={"Authorization": f"Bearer {pro_user_token}"},
        json={
            "property_id": test_property_id,
            "phone_number": "+919876543210"
        }
    )
    # The subscription check passed! Must NEVER be 403 PRO_REQUIRED.
    assert res.status_code != 403


# ============================================================================
# 7. UNCONFIGURED GATEWAY TEST
# ============================================================================
def test_unconfigured_gateway_returns_503(client: TestClient, free_user_token: str, monkeypatch):
    """When Razorpay is unconfigured, verify-payment must return 503 instead of pretending success."""
    monkeypatch.setattr(settings, "RAZORPAY_KEY_SECRET", "")
    res = client.post(
        "/api/v1/subscriptions/verify-payment",
        headers={"Authorization": f"Bearer {free_user_token}"},
        json={
            "razorpay_order_id": "ord_unconf",
            "razorpay_payment_id": "pay_unconf",
            "razorpay_signature": "sig_unconf"
        }
    )
    assert res.status_code == 503
    detail = res.json().get("detail", res.json())
    assert "Payment gateway not configured" in str(detail)


# ============================================================================
# 8. INVALID PAYMENT SIGNATURE REJECTED
# ============================================================================
def test_invalid_payment_signature_rejected(client: TestClient, free_user_token: str, monkeypatch):
    """Tampered or fraudulent payment signatures must strictly return HTTP 400."""
    monkeypatch.setattr(settings, "RAZORPAY_KEY_SECRET", "test_rzp_secret_key_12345")
    monkeypatch.setattr(settings, "RAZORPAY_KEY_ID", "rzp_test_12345")

    res = client.post(
        "/api/v1/subscriptions/verify-payment",
        headers={"Authorization": f"Bearer {free_user_token}"},
        json={
            "razorpay_order_id": "order_fake_12345",
            "razorpay_payment_id": "pay_fake_67890",
            "razorpay_signature": "invalid_forged_hex_signature"
        }
    )
    assert res.status_code == 400
    detail = res.json().get("detail", res.json())
    assert "Invalid signature" in str(detail)


# ============================================================================
# 9. INVALID WEBHOOK SIGNATURE REJECTED
# ============================================================================
def test_invalid_webhook_rejected(client: TestClient, monkeypatch):
    """Razorpay webhooks with missing or mismatched HMAC signatures must be rejected."""
    monkeypatch.setattr(settings, "RAZORPAY_WEBHOOK_SECRET", "test_wh_secret_12345")

    # Missing signature header
    res_no_sig = client.post(
        "/api/v1/subscriptions/webhook",
        json={"event": "payment.captured"}
    )
    assert res_no_sig.status_code == 400

    # Forged signature
    res_bad_sig = client.post(
        "/api/v1/subscriptions/webhook",
        headers={"X-Razorpay-Signature": "bad_hex_signature_abcdef"},
        json={"event": "payment.captured"}
    )
    assert res_bad_sig.status_code == 400


# ============================================================================
# 10. SUCCESSFUL VERIFIED PAYMENT ACTIVATES PRO
# ============================================================================
def test_successful_verified_payment_activates_pro(client: TestClient, db: Session, monkeypatch):
    """A mathematically valid HMAC-SHA256 signature must transition the user to ACTIVE PRO."""
    test_secret = "test_rzp_secret_key_12345"
    monkeypatch.setattr(settings, "RAZORPAY_KEY_SECRET", test_secret)
    monkeypatch.setattr(settings, "RAZORPAY_KEY_ID", "rzp_test_12345")

    # Create distinct checkout user
    user = User(
        email=f"checkout_user_{datetime.now().timestamp()}@example.com",
        full_name="Checkout Verified User",
        hashed_password=get_password_hash("CheckoutPass123!"),
        role="USER",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id)
    order_id = f"order_real_{user.id}"
    payment_id = f"pay_real_{user.id}"

    # Generate genuine HMAC-SHA256 signature using current settings secret
    secret = test_secret.encode("utf-8")
    msg = f"{order_id}|{payment_id}".encode("utf-8")
    valid_signature = hmac.new(secret, msg, hashlib.sha256).hexdigest()

    # Pre-create pending order subscription in DB
    sub = Subscription(
        user_id=user.id,
        plan="FREE",
        subscription_status="PENDING",
        razorpay_order_id=order_id,
        plan_amount=299.0,
        currency="INR"
    )
    db.add(sub)
    db.commit()

    # Verify payment through API
    res = client.post(
        "/api/v1/subscriptions/verify-payment",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": valid_signature
        }
    )
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["status"] == "ok"
    assert res_json["plan"] == "PRO"
    assert res_json["subscription_status"] == "ACTIVE"

    # Verify persisted in database
    db.refresh(sub)
    assert sub.subscription_status == "ACTIVE"
    assert sub.plan == "PRO"
    assert sub.razorpay_payment_id == payment_id
    assert sub.end_date is not None


# ============================================================================
# 11. EXPIRED SUBSCRIPTION BECOMES INACCESSIBLE
# ============================================================================
def test_expired_subscription_becomes_inaccessible(client: TestClient, db: Session, test_property_id: int):
    """An expired end_date must immediately lock access with 403 PRO_REQUIRED."""
    user = User(
        email=f"expired_user_{datetime.now().timestamp()}@example.com",
        full_name="Expired Sub User",
        hashed_password=get_password_hash("ExpiredPass123!"),
        role="USER",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    now = datetime.now(timezone.utc)
    expired_end = now - timedelta(days=2) # 2 days in the past
    sub = Subscription(
        user_id=user.id,
        plan="PRO",
        subscription_status="ACTIVE",
        start_date=now - timedelta(days=32),
        end_date=expired_end,
        plan_amount=299.0,
        currency="INR"
    )
    db.add(sub)
    db.commit()

    token = create_access_token(subject=user.id)
    res = client.get(
        f"/api/v1/ai/analyze-property/{test_property_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403
    detail = res.json().get("detail", res.json())
    assert detail.get("code") == "PRO_REQUIRED"


# ============================================================================
# 12. CANCELLED SUBSCRIPTION BECOMES INACCESSIBLE
# ============================================================================
def test_cancelled_subscription_becomes_inaccessible(client: TestClient, db: Session, test_property_id: int):
    """A CANCELLED subscription status must reject premium access with 403 PRO_REQUIRED."""
    user = User(
        email=f"cancelled_user_{datetime.now().timestamp()}@example.com",
        full_name="Cancelled User",
        hashed_password=get_password_hash("CancelledPass123!"),
        role="USER",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    sub = Subscription(
        user_id=user.id,
        plan="PRO",
        subscription_status="CANCELLED",
        plan_amount=299.0,
        currency="INR"
    )
    db.add(sub)
    db.commit()

    token = create_access_token(subject=user.id)
    res = client.get(
        f"/api/v1/ai/analyze-property/{test_property_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403
    detail = res.json().get("detail", res.json())
    assert detail.get("code") == "PRO_REQUIRED"


# ============================================================================
# 13. USER ISOLATION: USER A CANNOT ACCESS/MODIFY USER B SUBSCRIPTION
# ============================================================================
def test_user_a_cannot_access_user_b_subscription(client: TestClient, db: Session):
    """Subscription queries must strictly isolate to authenticated JWT subject identity."""
    user_a = User(
        email=f"user_a_{datetime.now().timestamp()}@example.com",
        full_name="User Alpha",
        hashed_password=get_password_hash("PassAlpha123!"),
        role="USER",
        is_active=True
    )
    user_b = User(
        email=f"user_b_{datetime.now().timestamp()}@example.com",
        full_name="User Bravo",
        hashed_password=get_password_hash("PassBravo123!"),
        role="USER",
        is_active=True
    )
    db.add_all([user_a, user_b])
    db.commit()

    # Give User B an active Pro subscription
    sub_b = Subscription(
        user_id=user_b.id,
        plan="PRO",
        subscription_status="ACTIVE",
        razorpay_payment_id="pay_user_b_private_ref",
        plan_amount=299.0,
        currency="INR",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=30)
    )
    db.add(sub_b)
    db.commit()

    token_a = create_access_token(subject=user_a.id)

    # User A requests /subscriptions/me -> Must NOT see User B's PRO plan
    res_a = client.get("/api/v1/subscriptions/me", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.status_code == 200
    data_a = res_a.json()
    assert data_a["user_id"] == user_a.id
    assert data_a["plan"] == "FREE"
    assert data_a["is_active"] is False
    assert data_a["razorpay_payment_id"] != "pay_user_b_private_ref"


# ============================================================================
# 14. PRIVATE ADMIN DASHBOARD SUBSCRIPTION VISIBILITY
# ============================================================================
def test_admin_dashboard_subscription_visibility(client: TestClient, admin_token: str, free_user_token: str):
    """Admin dashboard must list subscriptions without exposing Razorpay secrets; Non-admins blocked."""
    # Free user cannot access admin subscriptions
    res_free = client.get("/api/v1/admin/subscriptions", headers={"Authorization": f"Bearer {free_user_token}"})
    assert res_free.status_code == 403

    # Admin successfully retrieves subscriptions
    res_admin = client.get("/api/v1/admin/subscriptions", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    data = res_admin.json()
    assert "subscriptions" in data
    assert "total" in data

    # Verify no secret keys exist in payload
    raw_text = res_admin.text
    assert "RAZORPAY_KEY_SECRET" not in raw_text
    assert "WEBHOOK_SECRET" not in raw_text
