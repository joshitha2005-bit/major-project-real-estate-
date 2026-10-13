import time
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import verify_password
from app.models.user import User


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


def test_standard_demo_user_exists_and_can_login(client: TestClient, db: Session):
    """Verify demo user exists, has active account and can log in with standard demo password."""
    demo_email = "demo@cloudrealestate.ai"
    user = db.query(User).filter(User.email == demo_email).first()
    assert user is not None, f"Demo user {demo_email} must exist in the database"
    assert user.is_active is True
    assert user.role == "USER"
    assert verify_password("DemoUser@2026", user.hashed_password) is True

    # Test login via API
    resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": demo_email, "password": "DemoUser@2026"}
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == demo_email


def test_login_with_incorrect_password_rejected(client: TestClient):
    """Verify login fails with HTTP 401 when password does not match."""
    resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "demo@cloudrealestate.ai", "password": "WrongPassword!999"}
    )
    assert resp.status_code == 401
    assert "Incorrect email or password" in resp.json().get("detail", "")


def test_user_registration_login_and_profile_flow(client: TestClient, db: Session):
    """Verify complete registration -> password hashing -> login -> profile retrieval flow."""
    unique_email = f"flow_user_{int(time.time() * 1000)}@example.com"
    plain_password = "ValidPassword@2026"

    # 1. Register
    reg_resp = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": unique_email,
            "password": plain_password,
            "full_name": "Flow Test User"
        }
    )
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert "access_token" in reg_data

    # 2. Verify hashed password in DB is not plaintext
    created_user = db.query(User).filter(User.email == unique_email).first()
    assert created_user is not None
    assert created_user.hashed_password != plain_password
    assert created_user.hashed_password.startswith("$2b$") or created_user.hashed_password.startswith("$2a$")
    assert verify_password(plain_password, created_user.hashed_password) is True

    # 3. Log in with credentials
    login_resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": unique_email, "password": plain_password}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # 4. Access profile with token
    profile_resp = client.get(
        f"{settings.API_V1_STR}/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert profile_resp.status_code == 200
    prof = profile_resp.json()
    assert prof["email"] == unique_email
    assert prof["full_name"] == "Flow Test User"


def test_admin_account_synchronization_and_login(client: TestClient, db: Session):
    """Verify administrator account exists and can log in through both auth and admin login endpoints."""
    admin_user = db.query(User).filter(User.email == settings.PRIVATE_ADMIN_EMAIL).first()
    assert admin_user is not None
    assert admin_user.role == "ADMIN"
    assert verify_password(settings.PRIVATE_ADMIN_PASSWORD, admin_user.hashed_password) is True

    # Admin portal login
    admin_resp = client.post(
        f"{settings.API_V1_STR}/admin/login",
        json={
            "identifier": settings.PRIVATE_ADMIN_EMAIL,
            "password": settings.PRIVATE_ADMIN_PASSWORD
        }
    )
    assert admin_resp.status_code == 200
    assert "access_token" in admin_resp.json()
