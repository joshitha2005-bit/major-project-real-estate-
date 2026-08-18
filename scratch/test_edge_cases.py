import sys, os
sys.path.insert(0, os.path.abspath('backend'))

from app.services.image_ai_service import ImageAIService
from app.services.text_ai_service import TextAIService
from app.services.safety_service import SafetyGuardService
from app.services.price_prediction_service import PricePredictionService

print("=== TESTING EDGE CASES AND ROBUSTNESS ===")

# Edge Case 1: Empty images list
img_res = ImageAIService.analyze_property_images([], os.path.abspath("backend"))
print("Empty Images Test:", img_res.get("overall_score"), img_res.get("overall_condition"))

# Edge Case 2: Empty text description
text_res = TextAIService.analyze_description("")
print("Empty Text Test:", text_res.get("text_quality_score"), text_res.get("sentiment_label"))

# Edge Case 3: Unknown locality & coordinates
import asyncio
safety_res = asyncio.run(SafetyGuardService.analyze_locality_safety("Unknown Zone XYZ", 12.0, 77.0))
print("Unknown Locality Safety Test:", safety_res.get("safety_score"), safety_res.get("overall_rating"))

# Edge Case 4: XGBoost prediction with empty nearby places
xgb_res = PricePredictionService.predict_property_valuation(
    address="Unknown Locality",
    lat=12.93,
    lon=77.62,
    area_sqft=1000.0,
    bhk=2,
    bathrooms=2,
    parking=1,
    facing="East",
    property_age=3,
    nearby_places=[],
    image_score=80.0,
    text_score=75.0
)
print("XGBoost Prediction Test:", xgb_res.get("predicted_selling_price"), "SHAP Positive Factors:", len(xgb_res["shap_explanation"]["top_positive_factors"]))
