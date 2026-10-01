import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.database import SessionLocal
from app.models.property import Property
from app.services.image_ai_service import ImageAIService
from app.services.text_ai_service import TextAIService
from app.services.safety_service import SafetyGuardService
from app.services.pdf_report_service import PDFReportService

client = TestClient(app)

TARGET_LOCALITIES = [
    "HSR Layout", "Koramangala", "Whitefield", "Electronic City", "Sarjapur Road",
    "Hebbal", "Indiranagar", "JP Nagar", "Jayanagar", "Rajajinagar",
    "Yelahanka", "Thanisandra", "Marathahalli", "Bellandur", "KR Puram"
]

def test_phase8_search_all_localities():
    """Verify search across all 15 key Bengaluru localities returns valid records with accurate metrics."""
    for loc in TARGET_LOCALITIES:
        res = client.get(f"/api/v1/properties/?search={loc}&limit=5")
        assert res.status_code == 200, f"Search failed for {loc}"
        data = res.json()
        assert "items" in data
        assert len(data["items"]) > 0, f"No properties returned for locality {loc}"
        
        item = data["items"][0]
        assert item["price"] > 0
        assert item["area_sqft"] > 0
        assert item["price_per_sqft"] == round(item["price"] / item["area_sqft"], 2)
        assert item["source_type"] in ["historical_dataset", "HISTORICAL_DATASET", "demo_dataset", "DEMO_DATASET", "owner_listing", "PROPPULSE_DIRECT"]

def test_phase8_pdf_generation():
    """Verify PDF report generation outputs valid non-empty PDF bytes for property."""
    db = SessionLocal()
    try:
        prop = db.query(Property).first()
        assert prop is not None
        
        # Test PDF Report Service directly
        prop_dict = {
            "id": prop.id,
            "title": prop.title,
            "property_type": prop.property_type,
            "bhk": prop.bhk,
            "area_sqft": prop.area_sqft,
            "price": prop.price,
            "price_per_sqft": round(prop.price / prop.area_sqft, 2),
            "address": prop.address,
            "locality": prop.locality,
            "latitude": prop.latitude,
            "longitude": prop.longitude,
            "source_type": prop.source_type,
            "coordinate_quality": prop.coordinate_quality or "LOCALITY_APPROXIMATE"
        }
        
        analytics_dict = {
            "price_prediction": {
                "predicted_selling_price": prop.price,
                "predicted_price_per_sqft": round(prop.price / prop.area_sqft, 2),
                "model_metrics": {
                    "r2": 0.7843,
                    "mae_lakhs": 23.27,
                    "mape_percent": 25.18
                }
            },
            "safety_guard": {
                "emergency_coverage_score": 85.0,
                "nearest_police_station": "HSR Layout Police Station",
                "nearest_hospital": "Narayana Multispeciality Hospital"
            }
        }
        
        pdf_bytes = PDFReportService.generate_property_pdf_report(prop_dict, analytics_dict)
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 1000, "Generated PDF is unexpectedly small"
        assert pdf_bytes.startswith(b"%PDF"), "Generated output is not a valid PDF file"
    finally:
        db.close()

def test_phase8_emergency_infrastructure():
    """Verify Emergency Infrastructure Coverage calculation and safety service response format."""
    db = SessionLocal()
    try:
        prop = db.query(Property).first()
        assert prop is not None
        
        import asyncio
        safety_res = asyncio.run(SafetyGuardService.analyze_locality_safety("HSR Layout", prop.latitude, prop.longitude))
        
        assert "emergency_coverage_score" in safety_res
        assert 0 <= safety_res["emergency_coverage_score"] <= 100
        assert "nearest_police_station" in safety_res
        assert "nearest_hospital" in safety_res
        assert "nearest_fire_station" in safety_res
    finally:
        db.close()

def test_phase8_missing_image_handling():
    """Verify ImageAIService handles empty image list by returning explicit unavailable status."""
    res = ImageAIService.analyze_property_images([])
    assert res["image_analysis_available"] is False
    assert res["overall_condition"] == "Image analysis unavailable — no verified property image"
    assert res["processed_count"] == 0

def test_phase8_missing_description_nlp_handling():
    """Verify TextAIService handles empty description by returning basic fallback without crashing."""
    res = TextAIService.analyze_description("")
    assert res["word_count"] == 0
    assert res["readability"] == "Basic"
    assert res["top_tfidf_terms"] == []

if __name__ == "__main__":
    pytest.main(["-v", __file__])
