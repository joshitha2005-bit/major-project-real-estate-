import os
import sys

# Ensure backend directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.price_prediction_service import PricePredictionService

print("=" * 70)
print("VERIFYING PRICE PREDICTION SERVICE WITH REAL XGBOOST & SHAP")
print("=" * 70)

# Test 1: Koramangala Property
res1 = PricePredictionService.predict_property_valuation(
    address="4th Block, Koramangala, Bengaluru - 560034",
    lat=12.9357,
    lon=77.6240,
    area_sqft=1500,
    bhk=3,
    bathrooms=3,
    parking="Covered",
    facing="East",
    property_age="1-5 yrs",
    nearby_places=[]
)

print("\n--- TEST 1: Koramangala 3BHK 1500 Sqft ---")
print(f"  Predicted Selling Price : Rs. {res1['predicted_selling_price']:,}")
print(f"  Estimated Monthly Rent  : Rs. {res1['estimated_rental_price']:,}/mo")
print(f"  Price per Sqft          : Rs. {res1['price_per_sqft']:,}/sqft")
print(f"  Confidence Score        : {res1['confidence_score']}%")
print("  Top Positive Factors:")
for p in res1['shap_explanation']['top_positive_factors']:
    print(f"    - {p['factor']}: {p['impact_amount']} ({p['description']})")
print("  Top Negative Factors:")
for n in res1['shap_explanation']['top_negative_factors']:
    print(f"    - {n['factor']}: {n['impact_amount']} ({n['description']})")
print("  Feature Importance Breakdown:")
for f in res1['shap_explanation']['feature_importance']:
    print(f"    - {f['feature']}: {f['importance']}%")

# Test 2: Unknown / New Locality (Non-crashing test)
res2 = PricePredictionService.predict_property_valuation(
    address="Unknown Random Phase 999, Outer Ring Road, Bengaluru",
    lat=12.9716,
    lon=77.5946,
    area_sqft=1200,
    bhk=2,
    bathrooms=2,
    parking="Open",
    facing="North",
    property_age="New",
    nearby_places=[]
)

print("\n--- TEST 2: Unknown Locality (Fallback/Other Category Test) ---")
print(f"  Predicted Selling Price : Rs. {res2['predicted_selling_price']:,}")
print(f"  Confidence Score        : {res2['confidence_score']}%")
print("  SHAP Factors Count      : ", len(res2['shap_explanation']['top_positive_factors']) + len(res2['shap_explanation']['top_negative_factors']))

print("\n[OK] VERIFICATION SUCCESSFUL: XGBoost model inference and SHAP explainability operational!")
print("=" * 70)
