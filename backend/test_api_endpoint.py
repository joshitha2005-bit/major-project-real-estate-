import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app

client = TestClient(app)

print("=" * 70)
print("TESTING FASTAPI /api/v1/ai/analyze-property/1 ENDPOINT")
print("=" * 70)

response = client.get("/api/v1/ai/analyze-property/1")
print(f"HTTP Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print("Response Keys:", list(data.keys()))
    price_pred = data.get("price_prediction", {})
    print("Price Prediction Keys:", list(price_pred.keys()))
    print("Predicted Selling Price:", price_pred.get("predicted_selling_price"))
    print("Confidence Score:", price_pred.get("confidence_score"))
    print("SHAP Explanation Keys:", list(price_pred.get("shap_explanation", {}).keys()))
    print("Top Positive Factors Count:", len(price_pred.get("shap_explanation", {}).get("top_positive_factors", [])))
    print("Feature Importance Items:", price_pred.get("shap_explanation", {}).get("feature_importance"))
    print("\n[OK] API ENDPOINT TEST PASSED PERFECTLY!")
else:
    print("API Error Output:", response.text)

print("=" * 70)
