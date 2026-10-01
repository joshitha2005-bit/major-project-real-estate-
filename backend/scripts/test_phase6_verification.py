import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.database import SessionLocal
from app.models.property import Property

client = TestClient(app)

TARGET_LOCALITIES = [
    "HSR Layout",
    "Koramangala",
    "Whitefield",
    "Electronic City",
    "Sarjapur Road",
    "Hebbal",
    "Indiranagar",
    "JP Nagar",
    "Jayanagar",
    "Rajajinagar",
    "Yelahanka",
    "Thanisandra",
    "Marathahalli",
    "Bellandur",
    "KR Puram"
]

def test_15_localities_search():
    """Verify property search returns valid results for all 15 key Bengaluru localities."""
    for loc in TARGET_LOCALITIES:
        res = client.get(f"/api/v1/properties/?search={loc}&limit=5")
        assert res.status_code == 200, f"Failed search for {loc}"
        data = res.json()
        assert "items" in data
        assert len(data["items"]) > 0, f"No properties found for locality {loc}"
        
        # Verify required fields on first item
        item = data["items"][0]
        required_fields = [
            "id", "title", "bhk", "area_sqft", "area_type", "price_inr", "price_per_sqft",
            "transaction_type", "property_type", "locality", "zone", "source_type", "coordinate_quality"
        ]
        for field in required_fields:
            assert field in item, f"Field {field} missing from search result for {loc}"

def test_geoapify_nearby_amenities():
    """Verify Geoapify endpoint works for both 1km (1000m) and 5km (5000m) radii with deduplication and sorting."""
    # Test coordinates for HSR Layout
    lat, lng = 12.9121, 77.6446
    
    # 1 KM test
    res_1k = client.get(f"/api/v1/location/nearby-places?lat={lat}&lon={lng}&radius=1000")
    assert res_1k.status_code == 200
    places_1k = res_1k.json()
    assert len(places_1k) > 0
    # Check max distance <= 1000m
    for p in places_1k:
        assert p["distance_meters"] <= 1000, f"Place distance {p['distance_meters']} exceeds 1000m in 1km test"
        assert all(k in p for k in ["name", "category", "distance_meters", "latitude", "longitude"])
    
    # 5 KM test
    res_5k = client.get(f"/api/v1/location/nearby-places?lat={lat}&lon={lng}&radius=5000")
    assert res_5k.status_code == 200
    places_5k = res_5k.json()
    assert len(places_5k) >= len(places_1k)
    # Check distances are sorted ascending
    distances = [p["distance_meters"] for p in places_5k]
    assert distances == sorted(distances), "Places are not sorted by distance ascending"

def test_exact_vs_approximate_coordinate_quality():
    """Verify database contains both EXACT and LOCALITY_APPROXIMATE properties."""
    db = SessionLocal()
    try:
        exact_prop = db.query(Property).filter(Property.coordinate_quality == "EXACT").first()
        approx_prop = db.query(Property).filter(Property.coordinate_quality == "LOCALITY_APPROXIMATE").first()
        
        assert exact_prop is not None, "No EXACT coordinate property found in DB"
        assert approx_prop is not None, "No LOCALITY_APPROXIMATE coordinate property found in DB"
        
        assert exact_prop.coordinate_quality == "EXACT"
        assert approx_prop.coordinate_quality == "LOCALITY_APPROXIMATE"
    finally:
        db.close()

def test_ai_price_analysis():
    """Verify XGBoost prediction service returns listed price, predicted price, price/sqft, and diff %."""
    from app.services.price_prediction_service import PricePredictionService
    
    db = SessionLocal()
    try:
        prop = db.query(Property).first()
        assert prop is not None
        
        val_data = PricePredictionService.predict_property_valuation(
            address=prop.address,
            lat=prop.latitude,
            lon=prop.longitude,
            area_sqft=prop.area_sqft,
            bhk=prop.bhk,
            bathrooms=prop.bathrooms,
            balconies=prop.balconies,
            parking=prop.parking or "Covered",
            facing=prop.facing or "East",
            property_age=prop.property_age or "New",
            nearby_places=prop.nearby_places or [],
            image_score=80.0,
            text_score=75.0,
            listed_price=prop.price
        )
        
        required_val_fields = [
            "listed_price", "predicted_selling_price", "actual_price_per_sqft",
            "predicted_price_per_sqft", "difference_percentage"
        ]
        for field in required_val_fields:
            assert field in val_data, f"Field {field} missing from valuation response"
        assert val_data["predicted_selling_price"] > 0
    finally:
        db.close()

def test_historical_vs_direct_owner_separation():
    """Verify historical dataset records are tagged HISTORICAL and direct owner listing is tagged PROPPULSE_DIRECT."""
    db = SessionLocal()
    try:
        hist_prop = db.query(Property).filter((Property.source_type == "historical_dataset") | (Property.source_type == "HISTORICAL_DATASET")).first()
        owner_prop = db.query(Property).filter((Property.source_type == "owner_listing") | (Property.source_type == "PROPPULSE_DIRECT") | (Property.source == "PropPulse Direct")).first()
        
        assert hist_prop is not None, "No HISTORICAL_DATASET property found"
        assert owner_prop is not None, "No PROPPULSE_DIRECT property found"
        
        # Verify API serialization
        res_hist = client.get(f"/api/v1/properties/{hist_prop.id}")
        assert res_hist.status_code == 200
        hist_json = res_hist.json()
        assert hist_json["source_type"] in ["HISTORICAL_DATASET", "historical_dataset"]
        assert hist_json["owner_phone"] == "Contact information unavailable"
        
        res_owner = client.get(f"/api/v1/properties/{owner_prop.id}")
        assert res_owner.status_code == 200
        owner_json = res_owner.json()
        assert owner_json["source_type"] in ["PROPPULSE_DIRECT", "owner_listing"]
        assert owner_json["owner_phone"] != "Contact information unavailable"
    finally:
        db.close()

if __name__ == "__main__":
    pytest.main(["-v", __file__])
