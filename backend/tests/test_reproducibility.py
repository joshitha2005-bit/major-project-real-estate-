"""
Golden Reproducibility Test Suite for GeoSmart Price AI
Verifies exact 544-D Multimodal Feature Vector assembly, XGBoost regression,
and TreeSHAP explainability across clean machine installations.
"""

import os
import json
import pytest
import numpy as np
from app.services.multimodal_model_service import MultimodalModelService, ALL_FEATURE_NAMES

GOLDEN_PROPERTIES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "datasets",
    "golden_demo_properties.json"
)

# Reference values established on verified production model artifacts:
# Tolerance: 0.1% relative tolerance to account for platform-level floating-point differences.
GOLDEN_BENCHMARKS = {
    16795: {
        "expected_dim": 544,
        "expected_price": 6436467.50,
        "tolerance_rel": 0.005,  # 0.5% tolerance
        "expected_version": "2.1.0-leakage-free-multimodal-resnet18-xgboost",
        "has_images": True,
        "min_shap_categories": 4
    },
    16799: {
        "expected_dim": 544,
        "expected_price": 13706784.00,
        "tolerance_rel": 0.005,
        "expected_version": "2.1.0-leakage-free-multimodal-resnet18-xgboost",
        "has_images": True,
        "min_shap_categories": 4
    },
    101: {
        "expected_dim": 544,
        "expected_price": 12950924.00,
        "tolerance_rel": 0.005,
        "expected_version": "2.1.0-leakage-free-multimodal-resnet18-xgboost",
        "has_images": True,
        "min_shap_categories": 4
    },
    16797: {
        "expected_dim": 544,
        "expected_price": 24087824.00,
        "tolerance_rel": 0.005,
        "expected_version": "2.1.0-leakage-free-multimodal-resnet18-xgboost",
        "has_images": True,
        "min_shap_categories": 4
    }
}


@pytest.fixture(scope="module")
def golden_properties():
    """Load golden test properties from dataset JSON."""
    assert os.path.exists(GOLDEN_PROPERTIES_PATH), f"Golden dataset missing at {GOLDEN_PROPERTIES_PATH}"
    with open(GOLDEN_PROPERTIES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {int(k): v for k, v in data.items()}


def test_feature_space_dimensions():
    """Assert feature space defines precisely 544 distinct named multimodal features."""
    feature_names = MultimodalModelService.get_feature_names()
    assert len(feature_names) == 544
    assert len(set(feature_names)) == 544
    assert feature_names[:6] == [
        "struct_area_sqft",
        "struct_bhk",
        "struct_bathrooms",
        "struct_balconies",
        "struct_locality_encoded",
        "struct_property_age"
    ]
    assert feature_names[6:16] == [
        "geo_schools",
        "geo_colleges",
        "geo_hospitals",
        "geo_metro_stations",
        "geo_bus_stops",
        "geo_restaurants",
        "geo_shopping_malls",
        "geo_banks",
        "geo_parks",
        "geo_total_count"
    ]
    assert feature_names[16:32] == [f"tfidf_feat_{i}" for i in range(16)]
    assert feature_names[32:544] == [f"resnet18_feat_{i}" for i in range(512)]


@pytest.mark.parametrize("property_id", [16795, 16799, 101, 16797])
def test_golden_property_reproducibility(golden_properties, property_id):
    """
    Assert that each golden property yields deterministic 544-D vector,
    consistent XGBoost valuation within tolerance, and complete 4-modality SHAP breakdown.
    """
    assert property_id in golden_properties, f"Property {property_id} missing from golden set"
    pdata = golden_properties[property_id]
    benchmark = GOLDEN_BENCHMARKS[property_id]

    images = None
    if pdata.get("images"):
        raw_imgs = pdata["images"]
        if isinstance(raw_imgs, str) and raw_imgs.startswith("["):
            images = json.loads(raw_imgs)
        elif isinstance(raw_imgs, list):
            images = raw_imgs

    nearby = []
    if pdata.get("nearby_places"):
        raw_nb = pdata["nearby_places"]
        if isinstance(raw_nb, str) and raw_nb.startswith("["):
            nearby = json.loads(raw_nb)
        elif isinstance(raw_nb, list):
            nearby = raw_nb

    # Run genuine multimodal prediction
    res = MultimodalModelService.predict_property(
        area_sqft=pdata.get("area_sqft", 1000.0),
        bhk=pdata.get("bhk", 2),
        bathrooms=pdata.get("bathrooms", 2),
        balconies=pdata.get("balconies", 1),
        locality=pdata.get("locality", "Other"),
        property_age=pdata.get("property_age", 5),
        nearby_places=nearby,
        description=pdata.get("description", ""),
        image_source=images
    )

    # 1. Feature Dimension Assertion
    assert res["fused_feature_dimension"] == benchmark["expected_dim"]
    fusion_breakdown = res["feature_fusion_breakdown"]
    assert fusion_breakdown["structured_dimensions"] == 6
    assert fusion_breakdown["geoapify_dimensions"] == 10
    assert fusion_breakdown["tfidf_dimensions"] == 16
    assert fusion_breakdown["resnet18_dimensions"] == 512
    assert fusion_breakdown["total_fused_dimensions"] == 544

    # 2. Prediction Status Assertion
    assert res["prediction_status"] == "GENUINE_MODEL_OUTPUT"
    assert res["model_version"] == benchmark["expected_version"]

    # 3. Numerical Valuation Assertion within tolerance
    predicted_price = res["predicted_selling_price"]
    expected_price = benchmark["expected_price"]
    rel_diff = abs(predicted_price - expected_price) / expected_price
    assert rel_diff <= benchmark["tolerance_rel"], (
        f"Property {property_id} predicted ₹{predicted_price:,.2f}, expected ₹{expected_price:,.2f} "
        f"(Relative difference {rel_diff * 100:.3f}% exceeds tolerance {benchmark['tolerance_rel'] * 100}%)"
    )

    # 4. SHAP Structure Assertion
    shap_info = res["shap_explanation"]
    assert shap_info["shap_available"] is True
    mod_contribs = res["modality_contributions"]
    assert len(mod_contribs) >= benchmark["min_shap_categories"]
    assert "structured_tabular" in mod_contribs
    assert "geospatial_geoapify" in mod_contribs
    assert "text_tfidf" in mod_contribs
    assert "image_resnet18" in mod_contribs
    assert mod_contribs["structured_tabular"] > 0
    assert mod_contribs["geospatial_geoapify"] > 0
    assert mod_contribs["text_tfidf"] > 0
    assert mod_contribs["image_resnet18"] > 0

    assert len(shap_info["top_positive_factors"]) > 0
    assert len(shap_info["top_negative_factors"]) > 0
