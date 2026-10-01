import pytest
import io
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.property import Property, PropertyImage
from app.models.user import User
from app.models.market_reference import MarketReference
from app.services.listing_service import ListingService
from app.services.image_provenance import ImageProvenanceService
from app.providers.authorized_provider_template import AuthorizedProviderTemplate
from app.providers.proppulse_direct_provider import PropPulseDirectProvider

from sqlalchemy.pool import StaticPool

# Test SQLite in-memory DB setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create dummy users: 1 regular user (owner) and 1 admin user
    owner_user = User(
        email="direct_owner@proppulse.com",
        full_name="Bengaluru Owner Direct",
        hashed_password="hashed_password_123",
        is_active=True,
        role="USER"
    )
    admin_user = User(
        email="admin@proppulse.com",
        full_name="PropPulse Platform Admin",
        hashed_password="admin_password_123",
        is_active=True,
        role="ADMIN"
    )
    db.add_all([owner_user, admin_user])
    db.commit()

    # Seed 1 Historical property
    p_hist = Property(
        user_id=owner_user.id,
        title="Historical Whitefield Flat",
        property_type="Apartment",
        listing_type="Buy",
        bhk=2,
        area_sqft=1200.0,
        price=6400000.0,
        address="Whitefield, Bengaluru",
        locality="Whitefield",
        latitude=12.9696,
        longitude=77.7497,
        source_type="HISTORICAL_MARKET_DATA",
        source="Bengaluru_House_Data.csv",
        source_name="Bengaluru_House_Data.csv",
        listing_status="HISTORICAL",
        verification_status="Historical Dataset",
        coordinate_quality="LOCALITY_APPROXIMATE",
        owner_name="Historical Dataset",
        owner_phone="Contact information unavailable"
    )

    # Seed 1 Market Reference property
    m_ref = MarketReference(
        provider_name="99acres Market Observation",
        source_listing_id="OBS-99A-101",
        locality="HSR Layout",
        property_type="Plot",
        bhk=0,
        area_sqft=1500.0,
        price_inr=15000000.0,
        price_per_sqft=10000.0,
        listing_url="https://www.99acres.com/reference-101",
        reference_status="OBSERVED"
    )

    db.add_all([p_hist, m_ref])
    db.commit()

    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# Helper to generate test JPEG bytes
def create_dummy_jpeg_bytes(width=600, height=450, color=(100, 150, 200)):
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# =====================================================================
# PHASE C TEST SUITE (20+ Scenarios)
# =====================================================================

def test_1_direct_listing_creation(db_session):
    user = db_session.query(User).filter(User.role == "USER").first()
    p = Property(
        user_id=user.id,
        title="Direct Indiranagar Villa",
        property_type="Villa",
        listing_type="Buy",
        bhk=4,
        area_sqft=3200.0,
        price=45000000.0,
        address="100 Feet Road, Indiranagar, Bengaluru",
        locality="Indiranagar",
        latitude=12.9719,
        longitude=77.6412,
        source_type="PROPPULSE_DIRECT",
        source="PropPulse Direct",
        source_name="PropPulse Direct",
        listing_status="PENDING",
        verification_status="Pending Verification",
        coordinate_quality="EXACT",
        owner_name=user.full_name,
        owner_phone="+91 98860 11223"
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    assert p.id is not None
    assert p.source_type == "PROPPULSE_DIRECT"
    assert p.verification_status == "Pending Verification"
    assert p.listing_status == "PENDING"


def test_2_price_per_sqft_calculation():
    rate = ListingService.calculate_price_per_sqft(45000000.0, 3200.0)
    assert rate == 14062.5


def test_3_real_image_upload_and_provenance(db_session):
    prop = db_session.query(Property).filter(Property.locality == "Indiranagar").first()
    img_bytes = create_dummy_jpeg_bytes(800, 600, (50, 100, 150))

    res = ImageProvenanceService.process_and_store_owner_upload(
        db=db_session,
        image_bytes=img_bytes,
        filename="living_room.jpg",
        property_id=prop.id,
        user_id=prop.user_id,
        is_primary=True
    )

    assert res["success"] is True
    assert res["image_provenance"] == "OWNER_UPLOADED"
    assert res["quality_score"] > 0

    prov_info = ImageProvenanceService.get_property_image_provenance(prop)
    assert prov_info["has_genuine_image"] is True
    assert prov_info["image_provenance"] == "OWNER_UPLOADED"
    assert prov_info["provenance_badge"] == "OWNER UPLOADED IMAGE"


def test_4_duplicate_image_detection(db_session):
    prop = db_session.query(Property).filter(Property.locality == "Indiranagar").first()
    img_bytes = create_dummy_jpeg_bytes(800, 600, (50, 100, 150)) # Identical bytes!

    res = ImageProvenanceService.process_and_store_owner_upload(
        db=db_session,
        image_bytes=img_bytes,
        filename="living_room_duplicate.jpg",
        property_id=prop.id,
        user_id=prop.user_id,
        is_primary=False
    )

    assert res["success"] is False
    assert "Duplicate image detected" in res["error"]
    assert res["validation_status"] == "Duplicate"


def test_5_current_listing_verification_lifecycle(db_session):
    prop = db_session.query(Property).filter(Property.locality == "Indiranagar").first()
    assert prop.verification_status == "Pending Verification"

    # Transition to Verified
    prop.verification_status = "Verified"
    prop.verified = True
    prop.listing_status = "CURRENT"
    db_session.commit()
    db_session.refresh(prop)

    assert prop.verification_status == "Verified"
    assert prop.listing_status == "CURRENT"


def test_6_listing_expiry(db_session):
    user = db_session.query(User).filter(User.role == "USER").first()
    p_exp = Property(
        user_id=user.id,
        title="Expired Koramangala Flat",
        property_type="Apartment",
        bhk=2,
        area_sqft=1100.0,
        price=8000000.0,
        locality="Koramangala",
        address="Koramangala 4th Block",
        latitude=12.9357,
        longitude=77.6240,
        source_type="PROPPULSE_DIRECT",
        verification_status="Expired",
        listing_status="EXPIRED",
        verified=False
    )
    db_session.add(p_exp)
    db_session.commit()

    assert p_exp.listing_status == "EXPIRED"
    assert p_exp.verification_status == "Expired"


def test_7_current_only_search_filter(db_session, client):
    res = client.get("/api/v1/properties/?current_only=true")
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert item["source_type"] in ["PROPPULSE_DIRECT", "CURRENT_AUTHORIZED_LISTING", "owner_listing"] or item["listing_status"] == "CURRENT"


def test_8_historical_search_filter(db_session, client):
    res = client.get("/api/v1/properties/?source_type=historical")
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert item["source_type"] in ["HISTORICAL_MARKET_DATA", "historical_dataset"]
        assert item["contact_available"] is False


def test_9_has_image_filtering(db_session, client):
    res = client.get("/api/v1/properties/?has_real_image=true")
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert item["image_provenance"] in ["OWNER_UPLOADED", "AUTHORIZED_PROVIDER", "LICENSED_EXTERNAL"] or item["has_genuine_image"] is True


def test_10_locality_filtering(client):
    res = client.get("/api/v1/properties/?query=Whitefield")
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert "whitefield" in item["locality"].lower()


def test_11_property_type_filtering(client):
    res = client.get("/api/v1/properties/?property_type=Villa")
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert item["property_type"].lower() == "villa"


def test_12_bhk_filtering(client):
    res = client.get("/api/v1/properties/?bhk=4")
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert item["bhk"] == 4


def test_13_price_filtering(client):
    res = client.get("/api/v1/properties/?max_price=10000000")
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert item["price"] <= 10000000.0


def test_14_area_filtering(client):
    res = client.get("/api/v1/properties/?min_area=1500")
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert item["area_sqft"] >= 1500.0


def test_15_no_fake_image_fallback(db_session):
    p_hist = db_session.query(Property).filter(Property.source_type == "HISTORICAL_MARKET_DATA").first()
    info = ImageProvenanceService.get_property_image_provenance(p_hist)

    assert info["has_genuine_image"] is False
    assert info["provenance_badge"] == "PROPERTY IMAGE UNAVAILABLE"
    assert info["images"] == []


def test_16_no_fake_listing_generation(db_session):
    from app.api.v1.properties import auto_generate_locality_sample_properties
    res = auto_generate_locality_sample_properties("Electronic City", db_session)
    assert res == []


def test_17_authorized_provider_adapter_interface():
    template_provider = AuthorizedProviderTemplate(api_key=None)
    meta = template_provider.get_provider_metadata()

    assert meta["is_authorized"] is True
    assert meta["status"] == "CURRENT AUTHORIZED EXTERNAL INVENTORY NOT YET CONNECTED"
    assert template_provider.search_listings() == []


def test_18_proppulse_direct_provider_adapter(db_session):
    direct_provider = PropPulseDirectProvider(db_session)
    meta = direct_provider.get_provider_metadata()

    assert meta["provider_id"] == "proppulse_direct"
    assert meta["status"] == "ACTIVE"
    listings = direct_provider.search_listings("Indiranagar")
    assert len(listings) >= 1
    assert listings[0]["source_type"] == "PROPPULSE_DIRECT"


def test_19_market_reference_separation(db_session):
    m_refs = db_session.query(MarketReference).all()
    props = db_session.query(Property).all()

    assert len(m_refs) == 1
    assert m_refs[0].provider_name == "99acres Market Observation"
    # Ensure MarketReference table is isolated from main properties table
    for p in props:
        assert p.source_type != "MARKET_REFERENCE"
