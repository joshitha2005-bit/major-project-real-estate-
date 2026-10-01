import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np
import io
from PIL import Image

from app.main import app
from app.core.database import Base, get_db
from app.models.property import Property, PropertyImage
from app.models.user import User
from app.models.market_reference import MarketReference
from app.services.listing_service import ListingService
from app.services.image_provenance import ImageProvenanceService
from app.services.property_deduplication import PropertyDeduplicationService

# Test SQLite in-memory DB setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create dummy user for direct listing tests
    test_user = User(
        email="owner_test@proppulse.com",
        full_name="Verified Direct Owner",
        hashed_password="hashed_password_123",
        is_active=True,
        role="USER"
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    # Seed 1 Historical property
    p_hist = Property(
        user_id=test_user.id,
        title="Historical Whitefield Apartment",
        property_type="Apartment",
        listing_type="Buy",
        bhk=3,
        area_sqft=1500.0,
        price=7500000.0,
        address="Whitefield Main Road, Bengaluru",
        locality="Whitefield",
        latitude=12.9696,
        longitude=77.7497,
        source_type="HISTORICAL_MARKET_DATA",
        source="Bengaluru_House_Data.csv",
        source_name="Bengaluru_House_Data.csv",
        listing_status="HISTORICAL",
        coordinate_quality="LOCALITY_APPROXIMATE",
        owner_name="Historical Dataset",
        owner_phone="Contact information unavailable"
    )

    # Seed 1 Direct listing property
    p_direct = Property(
        user_id=test_user.id,
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
        listing_status="CURRENT",
        coordinate_quality="EXACT",
        owner_name="Verified Direct Owner",
        owner_phone="+91 99000 88888",
        contact_available=True
    )

    db.add_all([p_hist, p_direct])
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


# =====================================================================
# 1. Price Per Sq.Ft Calculation Tests (20 Examples)
# =====================================================================

def test_price_per_sqft_calculation_20_examples():
    examples = [
        (8000000.0, 1250.0, 6400.0),
        (15000000.0, 1200.0, 12500.0),
        (23900000.0, 1770.0, 13502.82),
        (6720000.0, 1200.0, 5600.0),
        (9360000.0, 1200.0, 7800.0),
        (11400000.0, 1200.0, 9500.0),
        (16800000.0, 1200.0, 14000.0),
        (4300000.0, 1056.0, 4071.97),
        (12000000.0, 2600.0, 4615.38),
        (6200000.0, 1440.0, 4305.56),
        (9500000.0, 1521.0, 6245.89),
        (5100000.0, 1087.0, 4691.81),
        (3800000.0, 1170.0, 3247.86),
        (20400000.0, 2732.0, 7467.06),
        (60000000.0, 3300.0, 18181.82),
        (6325000.0, 1710.0, 3698.83),
        (12500000.0, 2400.0, 5208.33),
        (29500000.0, 3350.0, 8805.97),
        (3800000.0, 1000.0, 3800.0),
        (4000000.0, 1103.0, 3626.47)
    ]

    for price, area, expected in examples:
        calc = ListingService.calculate_price_per_sqft(price, area)
        assert calc == expected, f"Failed for price={price}, area={area}: got {calc}, expected {expected}"


# =====================================================================
# 2. Source Type & Provenance Validation Tests
# =====================================================================

def test_source_type_validation(db_session):
    p_hist = db_session.query(Property).filter(Property.locality == "Whitefield").first()
    p_dir = db_session.query(Property).filter(Property.locality == "Indiranagar").first()

    fmt_hist = ListingService.format_listing_out(p_hist)
    fmt_dir = ListingService.format_listing_out(p_dir)

    assert fmt_hist["source_type"] == "HISTORICAL_MARKET_DATA"
    assert fmt_hist["listing_status"] == "HISTORICAL"
    assert fmt_hist["contact_available"] is False
    assert fmt_hist["owner_phone"] == "Contact information unavailable"

    assert fmt_dir["source_type"] == "PROPPULSE_DIRECT"
    assert fmt_dir["listing_status"] == "CURRENT"
    assert fmt_dir["contact_available"] is True
    assert fmt_dir["owner_phone"] == "+91 99000 88888"


# =====================================================================
# 3. Image Provenance & Hash Check Tests
# =====================================================================

def test_image_validation_and_hash_computation():
    # Create valid synthetic RGB image in memory
    img = Image.new("RGB", (600, 450), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    is_valid, meta = ImageProvenanceService.inspect_and_validate_image(img_bytes)
    assert is_valid is True
    assert meta["validation_status"] == "Valid"
    assert meta["width"] == 600
    assert meta["height"] == 450
    assert meta["quality_score"] > 0

    img_hash = ImageProvenanceService.compute_image_hash(img_bytes)
    assert len(img_hash) == 64  # SHA-256 hex length

def test_historical_no_image_fallback(db_session):
    p_hist = db_session.query(Property).filter(Property.source_type == "HISTORICAL_MARKET_DATA").first()
    img_info = ImageProvenanceService.get_property_image_provenance(p_hist)

    assert img_info["has_genuine_image"] is False
    assert img_info["image_provenance"] == "NO_IMAGE"
    assert img_info["provenance_badge"] == "PROPERTY IMAGE UNAVAILABLE"
    assert "unavailable" in img_info["disclosure_note"].lower()


# =====================================================================
# 4. Duplicate Property Detection Tests
# =====================================================================

def test_property_deduplication_engine(db_session):
    p1 = Property(
        user_id=1,
        title="Sobha Apartments Whitefield",
        property_type="Apartment",
        bhk=3,
        area_sqft=1500.0,
        price=8000000.0,
        locality="Whitefield",
        address="Block A, Whitefield Road, Bengaluru",
        latitude=12.9696,
        longitude=77.7497,
        source_listing_id="EXT-1001"
    )
    p2 = Property(
        user_id=1,
        title="Sobha Apartments Whitefield",
        property_type="Apartment",
        bhk=3,
        area_sqft=1500.0,
        price=8050000.0,
        locality="Whitefield",
        address="Block A, Whitefield Road, Bengaluru",
        latitude=12.9697,
        longitude=77.7498,
        source_listing_id="EXT-1001"
    )

    cls_res, score, signals = PropertyDeduplicationService.compare_property_pair(p1, p2)
    assert cls_res == "CONFIRMED_DUPLICATE"
    assert score >= 80.0
    assert "exact_source_listing_id_match" in signals


# =====================================================================
# 5. Locality Inventory & Disabled Fake Generation Tests
# =====================================================================

def test_disabled_fake_locality_generation(db_session):
    from app.api.v1.properties import auto_generate_locality_sample_properties
    res = auto_generate_locality_sample_properties("Yelahanka", db_session)
    assert res == []

def test_locality_inventory_breakdown(db_session):
    breakdown = ListingService.get_locality_inventory_breakdown("Whitefield", db_session)
    assert breakdown["locality"] == "Whitefield"
    assert breakdown["total_records"] >= 1
    assert breakdown["historical_records_count"] >= 1
    assert "No current listings available" in breakdown["availability_message"]


# =====================================================================
# 6. Direct Listing CRUD API Tests (/api/v1/listings)
# =====================================================================

def test_get_direct_listings_api(client):
    response = client.get("/api/v1/listings/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["source_type"] == "PROPPULSE_DIRECT"
