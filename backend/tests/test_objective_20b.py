import os
import pytest
import numpy as np
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.property import Property, PropertyImage
from app.services.image_provenance import ImageProvenanceService
from app.services.image_ai_service import ImageAIService
from app.services.contact_verification_service import ContactVerificationService, VERIFIED_BUILDER_OFFICES
from app.api.v1.properties import enrich_property_out


@pytest.fixture(scope="module")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="module")
def sample_authorized_image_path(tmp_path_factory):
    """Create a temporary real image file to test ResNet-18 and OpenCV metrics."""
    fn = tmp_path_factory.mktemp("data") / "test_authorized.jpg"
    img = Image.new("RGB", (640, 480), color=(120, 160, 200))
    # Draw some patterns to ensure non-zero sharpness/Laplacian variance
    import cv2
    np_img = np.array(img)
    cv2.circle(np_img, (320, 240), 80, (255, 255, 255), -1)
    cv2.rectangle(np_img, (50, 50), (200, 200), (40, 40, 40), 3)
    pil_out = Image.fromarray(np_img)
    pil_out.save(str(fn), "JPEG")
    return str(fn)


# ==============================================================================
# SCENARIO 1: Property with Authorized Image (Owner / Verified Provider)
# ==============================================================================
def test_scenario_1_authorized_property_image(sample_authorized_image_path):
    prop = Property(
        id=9001,
        title="Luxury 3BHK Penthouse",
        source_type="PROPPULSE_DIRECT",
        source_name="PropPulse Direct",
        images=[sample_authorized_image_path],
        image_provenance="OWNER_UPLOADED",
        listing_status="CURRENT"
    )
    
    # 1. Provenance Classification
    prov = ImageProvenanceService.get_property_image_provenance(prop)
    assert prov["image_classification"] == "AUTHORIZED_PROPERTY_IMAGE"
    assert prov["usable_for_ai"] is True
    assert prov["has_genuine_image"] is True
    assert "AUTHORIZED PROPERTY IMAGE" in prov["provenance_badge"]

    # 2. ResNet-18 Computer Vision Feature Extraction
    cv_res = ImageAIService.analyze_property_images(
        image_urls=prov["images"],
        image_classification=prov["image_classification"]
    )
    assert cv_res["image_analysis_available"] is True
    assert cv_res["image_status"] == "IMAGE ANALYSIS COMPLETE"
    assert cv_res["cnn_model"] == "ResNet-18 (Pretrained ImageNet)"
    assert cv_res["embedding_dimensions"] == 512
    assert cv_res["image_quality_score"] > 0
    assert "sharpness" in cv_res["visual_features"]
    assert "brightness" in cv_res["visual_features"]
    assert "contrast" in cv_res["visual_features"]
    assert "resolution" in cv_res["visual_features"]
    assert "color_tone" in cv_res["visual_features"]
    assert "embedding_l2_norm" in cv_res["visual_features"]


# ==============================================================================
# SCENARIO 2: Property with Source-Reference Image (Portal Listing)
# ==============================================================================
def test_scenario_2_source_reference_image():
    prop = Property(
        id=9002,
        title="2 BHK Flat in Whitefield",
        source_type="CURRENT_AUTHORIZED_LISTING",
        source_name="NoBroker",
        source_url="https://www.nobroker.in/property/buy/2bhk-flat-for-sale-in-whitefield-bangalore",
        images=["https://images.nobroker.in/images/8a9f9082/prop_1.jpg"]
    )

    # 1. Provenance Classification
    prov = ImageProvenanceService.get_property_image_provenance(prop)
    assert prov["image_classification"] == "SOURCE_LISTING_IMAGE"
    assert prov["usable_for_ai"] is False
    assert prov["has_genuine_image"] is True
    assert "SOURCE LISTING IMAGE" in prov["provenance_badge"]

    # 2. CNN Gate Enforcement (No unauthorized CNN execution)
    cv_res = ImageAIService.analyze_property_images(
        image_urls=prov["images"],
        image_classification=prov["image_classification"]
    )
    assert cv_res["image_analysis_available"] is False
    assert cv_res["cnn_status"] == "Image available for reference; AI analysis unavailable because image-use permission is not established."
    assert cv_res["embedding_dimensions"] is None
    assert cv_res["image_quality_score"] is None


# ==============================================================================
# SCENARIO 3: Property with No Image
# ==============================================================================
def test_scenario_3_no_image():
    prop = Property(
        id=9003,
        title="Plot in Devanahalli",
        source_type="HISTORICAL_MARKET_DATA",
        source_name="Bengaluru_House_Data.csv",
        images=[]
    )

    # 1. Provenance Classification
    prov = ImageProvenanceService.get_property_image_provenance(prop)
    assert prov["image_classification"] == "NO_IMAGE"
    assert prov["usable_for_ai"] is False
    assert prov["has_genuine_image"] is False
    assert prov["provenance_badge"] == "PROPERTY IMAGE NOT AVAILABLE"

    # 2. AI Service Handling
    cv_res = ImageAIService.analyze_property_images(
        image_urls=prov["images"],
        image_classification=prov["image_classification"]
    )
    assert cv_res["image_analysis_available"] is False
    assert cv_res["image_status"] == "PROPERTY IMAGE NOT AVAILABLE"
    assert cv_res["embedding_dimensions"] is None


# ==============================================================================
# SCENARIO 4: Legitimate Published Builder/Corporate Office Contact (Rule C)
# ==============================================================================
def test_scenario_4_builder_office_contact():
    prop = Property(
        id=9004,
        title="Sobha Dream Acres 2 BHK",
        project_name="Sobha Dream Acres",
        builder_name="Sobha Limited",
        locality="Panathur",
        source="NoBroker",
        source_type="CURRENT_AUTHORIZED_LISTING"
    )

    contact = ContactVerificationService.resolve_property_contact(prop)
    assert contact["contact_type"] == "Builder"
    assert contact["contact_number"] == "+91 80 4646 4500"
    assert contact["contact_display_permission"] is True
    assert "Sobha Limited" in contact["contact_source"]
    assert "https://www.sobha.com" in contact["contact_source_url"]


# ==============================================================================
# SCENARIO 5: Masked Portal Contact (NoBroker / Housing - Rule B)
# ==============================================================================
def test_scenario_5_masked_portal_contact():
    prop = Property(
        id=9005,
        title="3 BHK Flat in HSR Layout",
        source="NoBroker",
        source_name="NoBroker",
        source_type="CURRENT_AUTHORIZED_LISTING",
        source_url="https://www.nobroker.in/property/buy/detail/blr12345",
        phone=None,
        owner_phone=None
    )

    contact = ContactVerificationService.resolve_property_contact(prop)
    # Contact must NOT be displayed or fabricated
    assert contact["contact_display_permission"] is False
    assert contact["contact_number"] is None
    assert contact["display_message"] == "Contact available through source listing"
    assert contact["source_platform"] == "NoBroker"
    assert contact["source_listing_url"] == "https://www.nobroker.in/property/buy/detail/blr12345"


# ==============================================================================
# SCENARIO 6: Historical Record with No Contact (Rule D)
# ==============================================================================
def test_scenario_6_historical_dataset_no_contact():
    prop = Property(
        id=9006,
        title="Electronic City Phase 1 Plot",
        source="Bengaluru_House_Data.csv",
        source_type="HISTORICAL_MARKET_DATA",
        locality="Electronic City"
    )

    contact = ContactVerificationService.resolve_property_contact(prop)
    assert contact["contact_display_permission"] is False
    assert contact["contact_number"] is None
    assert contact["source_platform"] == "Historical Dataset"
    assert "historical" in contact["display_message"].lower()


# ==============================================================================
# SCENARIO 7: Disambiguation - Two Properties with Similar Names in Different Locations
# ==============================================================================
def test_scenario_7_contact_locality_disambiguation():
    # Property A: Sobha Silicon Oasis in Hosa Road
    prop_a = Property(
        id=9007,
        title="Sobha Silicon Oasis Apartment",
        project_name="Sobha Silicon Oasis",
        builder_name="Sobha Limited",
        locality="Hosa Road"
    )

    # Property B: Unrelated private project with "Oasis" in name located in Hebbal
    prop_b = Property(
        id=9008,
        title="Green Oasis Residency",
        project_name="Green Oasis",
        builder_name="Local Private Developer",
        locality="Hebbal",
        source="NoBroker",
        source_url="https://www.nobroker.in/property/buy/detail/hebbal99"
    )

    contact_a = ContactVerificationService.resolve_property_contact(prop_a)
    contact_b = ContactVerificationService.resolve_property_contact(prop_b)

    # Prop A correctly matches Sobha office
    assert contact_a["contact_type"] == "Builder"
    assert contact_a["contact_number"] == "+91 80 4646 4500"
    assert contact_a["contact_display_permission"] is True

    # Prop B MUST NOT match Sobha office or invent numbers
    assert contact_b["contact_display_permission"] is False
    assert contact_b["contact_number"] is None
    assert contact_b["source_platform"] == "NoBroker"
    assert contact_a["contact_number"] != contact_b["contact_number"]
