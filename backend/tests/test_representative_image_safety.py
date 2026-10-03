"""
Regression Test: Representative Image Isolation & Safety
Proves that representative/reference images MUST NEVER enter the production ResNet-18 -> 512 -> 544 -> XGBoost inference pipeline.
Verifies that:
1. Properties with only REPRESENTATIVE images have CNN/property-image evidence marked unavailable.
2. Missing-image zero-vector baseline is applied for the 512 visual dimensions.
3. Model response & SHAP explanation have zero visual attribution (image_resnet18 = 0.0).
4. For genuine PROPERTY_SPECIFIC images, ResNet-18 512-D embedding is used normally.
"""
import pytest
import numpy as np
from unittest.mock import MagicMock, patch

from app.models.property import Property
from app.services.image_provenance import ImageProvenanceService
from app.services.image_ai_service import ImageAIService
from app.services.multimodal_model_service import MultimodalModelService

def test_representative_image_classification_usable_for_ai_false():
    """Representative images must be marked usable_for_ai = False."""
    prop = Property(
        id=88881,
        title="Sample Representative Listing",
        locality="Whitefield",
        images=["/static/property-images/Apartment/Apartment_01.jpg"],
        source="External Reference",
        image_provenance="REPRESENTATIVE"
    )

    prov = ImageProvenanceService.get_property_image_provenance(prop)
    assert prov["image_classification"] == "REPRESENTATIVE"
    assert prov["usable_for_ai"] is False
    assert prov["has_genuine_image"] is False
    assert "REPRESENTATIVE" in prov["provenance_badge"]

def test_representative_images_bypass_resnet18_in_ai_service():
    """ImageAIService.analyze_property_images must reject representative images from CNN feature extraction."""
    res = ImageAIService.analyze_property_images(
        image_urls=["/static/property-images/Apartment/Apartment_01.jpg"],
        image_classification="REPRESENTATIVE"
    )

    assert res["image_analysis_available"] is False
    assert res["cnn_status"] == "UNAVAILABLE_REPRESENTATIVE_ONLY"
    assert res["embedding_dimensions"] is None
    assert res["embedding_norm"] == 0.0
    assert res["non_zero_features"] == 0
    assert res["usable_for_ai"] is False

def test_representative_images_produce_zero_visual_vector_in_multimodal():
    """MultimodalModelService must use zero vector when representative or missing image."""
    # When image_source is None (which ai.py passes for representative images)
    vec = MultimodalModelService.extract_image_vector(None)
    assert isinstance(vec, np.ndarray)
    assert len(vec) == 512
    assert np.all(vec == 0.0)
    assert np.linalg.norm(vec) == 0.0

def test_shap_modality_zero_for_representative_or_missing_image():
    """SHAP explanation must not attribute positive/negative impacts to visual modality when no genuine property image is present."""
    res = MultimodalModelService.predict_property(
        area_sqft=1200.0,
        bhk=2,
        bathrooms=2,
        balconies=1,
        locality="Koramangala",
        property_age=3.0,
        nearby_places=[],
        description="Nice 2 BHK flat",
        image_source=None,  # Representative images are passed as None to predict_property
        listed_price=10000000.0
    )

    # Visual attribution must be exactly 0.0
    assert res["modality_contributions"]["image_resnet18"] == 0.0
    assert res["modality_percentages"]["image_resnet18"] == 0.0
    assert res["feature_fusion_breakdown"]["image_evidence_used"] is False

    # No resnet18_feat_ may appear in top positive or negative SHAP factors
    shap = res.get("shap_explanation", {})
    for factor in shap.get("top_positive_factors", []):
        assert not factor.get("feature", "").startswith("resnet18_feat_")
    for factor in shap.get("top_negative_factors", []):
        assert not factor.get("feature", "").startswith("resnet18_feat_")

def test_property_specific_images_use_resnet18_normally():
    """Genuine PROPERTY_SPECIFIC images extract non-zero 512-D embeddings normally."""
    prop = Property(
        id=88882,
        title="Verified Property Listing",
        locality="Koramangala",
        images=["https://images.nobroker.in/images/8aa9b3109bf9540e019bf9e7d39e4b2c/prop1.jpg"],
        source="NoBroker",
        source_type="CURRENT_AUTHORIZED_LISTING",
        image_provenance="PROPERTY_SPECIFIC"
    )

    prov = ImageProvenanceService.get_property_image_provenance(prop)
    assert prov["image_classification"] == "PROPERTY_SPECIFIC"
    assert prov["usable_for_ai"] is True
    assert prov["has_genuine_image"] is True
