import pytest
import os
import pandas as pd
from app.core.database import SessionLocal
from app.models.property import Property
from app.api.v1.properties import (
    OFFICIAL_KARNATAKA_DISTRICTS,
    normalize_karnataka_district,
    get_karnataka_districts,
    list_properties,
    get_property_by_id
)

@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()

def test_official_districts_count():
    """Verify that exactly 31 official Karnataka districts are recognized."""
    assert len(OFFICIAL_KARNATAKA_DISTRICTS) == 31
    assert "Bengaluru Urban" in OFFICIAL_KARNATAKA_DISTRICTS
    assert "Mysuru" in OFFICIAL_KARNATAKA_DISTRICTS
    assert "Belagavi" in OFFICIAL_KARNATAKA_DISTRICTS
    assert "Dakshina Kannada" in OFFICIAL_KARNATAKA_DISTRICTS
    assert "Vijayapura" in OFFICIAL_KARNATAKA_DISTRICTS
    assert "Vijayanagara" in OFFICIAL_KARNATAKA_DISTRICTS

def test_district_name_normalization():
    """Test standard normalization and synonyms for Karnataka districts."""
    assert normalize_karnataka_district("mysore") == "Mysuru"
    assert normalize_karnataka_district("Mysuru") == "Mysuru"
    assert normalize_karnataka_district("bangalore") == "Bengaluru Urban"
    assert normalize_karnataka_district("bengaluru") == "Bengaluru Urban"
    assert normalize_karnataka_district("belgaum") == "Belagavi"
    assert normalize_karnataka_district("bellary") == "Ballari"
    assert normalize_karnataka_district("bijapur") == "Vijayapura"
    assert normalize_karnataka_district("gulbarga") == "Kalaburagi"
    assert normalize_karnataka_district("mangalore") == "Dakshina Kannada"
    assert normalize_karnataka_district("shimoga") == "Shivamogga"
    assert normalize_karnataka_district("tumkur") == "Tumakuru"

def test_dataset_file_integrity():
    """Verify Karnataka_Individual_Properties.csv and KARNATAKA_RERA_PROJECTS.csv integrity."""
    base_dir = os.path.join(os.path.dirname(__file__), "..", "datasets")
    ind_csv = os.path.join(base_dir, "Karnataka_Individual_Properties.csv")
    rera_csv = os.path.join(base_dir, "KARNATAKA_RERA_PROJECTS.csv")
    
    assert os.path.exists(ind_csv), f"Dataset file missing at {ind_csv}"
    assert os.path.exists(rera_csv), f"Government project file missing at {rera_csv}"
    
    df_ind = pd.read_csv(ind_csv)
    assert len(df_ind) >= 4500, f"Expected at least 4500 individual properties, got {len(df_ind)}"
    assert df_ind['property_id'].duplicated().sum() == 0, "Duplicate property IDs found in individual dataset!"
    
    df_rera = pd.read_csv(rera_csv)
    assert len(df_rera) == 441, f"Expected 441 RERA government projects, got {len(df_rera)}"
    assert "registration_number" in df_rera.columns
    assert "project_name" in df_rera.columns

def test_database_district_reporting(db_session):
    """Verify database recognizes 31 official districts and reports genuine counts without fabrication."""
    res = get_karnataka_districts(db=db_session)
    assert res['total_districts'] == 31
    assert res['districts_with_properties'] >= 4
    
    # Verify Bengaluru Urban has verified properties
    blr_info = next((d for d in res['districts'] if d['district'] == "Bengaluru Urban"), None)
    assert blr_info is not None
    assert blr_info['verified_properties'] >= 800

def test_zero_cross_district_contamination(db_session):
    """Verify that querying a specific district returns ONLY properties in that district."""
    test_districts = ["Bengaluru Rural", "Ramanagara"]
    for dist in test_districts:
        res = list_properties(district=dist, db=db_session)
        assert res.total >= 10, f"Expected at least 10 properties for {dist}, got {res.total}"
        for item in res.items:
            assert item.district == dist, f"Contamination: found {item.district} when filtering for {dist}"

def test_bengaluru_urban_functionality_preserved(db_session):
    """Verify that existing Bengaluru Urban listings remain intact with verified properties."""
    blr_res = list_properties(district="Bengaluru Urban", db=db_session)
    assert blr_res.total >= 800, f"Expected at least 800 Bengaluru Urban properties, got {blr_res.total}"
    
    # Check that authentic images are preserved for Bengaluru Urban properties
    sample_with_images = [p for p in blr_res.items if p.images and len(p.images) > 0]
    assert len(sample_with_images) > 0, "No Bengaluru properties with images found"

def test_no_synthetic_phone_numbers(db_session):
    """Verify that district records without phone numbers honestly return 'Contact information unavailable'."""
    mysuru_res = list_properties(district="Mysuru", db=db_session)
    for p in mysuru_res.items:
        # If contact is not available, phone should be the honest fallback
        if not p.contact_available:
            assert p.owner_phone == "Contact information unavailable" or p.phone == "Contact information unavailable"

def test_no_fake_fallback_images(db_session):
    """Verify that district records without genuine photos return empty images array."""
    mysuru_res = list_properties(district="Mysuru", db=db_session)
    for p in mysuru_res.items:
        if p.image_status == "NO_IMAGE":
            assert p.images == [] or len(p.images) == 0
            assert p.has_genuine_image is False
