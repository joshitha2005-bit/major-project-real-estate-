import sys, os, urllib.request, json

print("==================================================")
print("     REAL ESTATE AI PLATFORM INTEGRATION AUDIT    ")
print("==================================================")

url = "http://127.0.0.1:8000/api/v1/ai/analyze-property/1"

req = urllib.request.urlopen(url, timeout=35)
status_code = req.getcode()
data = json.loads(req.read().decode('utf-8'))

print(f"\n1. HTTP Status Code: {status_code}")
print(f"2. Root Response Keys: {list(data.keys())}")

prop = data.get("property", {})
img_ai = data.get("image_ai", {})
text_ai = data.get("text_ai", {})
safety = data.get("safety_guard", {})
price_pred = data.get("price_prediction", {})
shap_exp = price_pred.get("shap_explanation", {})

print("\n--- PROPERTY DATA MAPPING ---")
print(f"ID: {prop.get('id')} | Title: '{prop.get('title')}'")
print(f"Address: '{prop.get('address')}' | Coordinates: ({prop.get('latitude')}, {prop.get('longitude')})")
print(f"BHK: {prop.get('bhk')} | Sqft: {prop.get('area_sqft')} | Price: INR {prop.get('price'):,}")

print("\n--- IMAGE AI / PYTORCH CNN MODULE ---")
print(f"Model: {img_ai.get('cnn_model')} | Status: {img_ai.get('cnn_status')}")
print(f"Processed Count: {img_ai.get('processed_count')} images")
print(f"CNN Feature Score: {img_ai.get('cnn_feature_score')} / 100")
print(f"OpenCV Brightness: {img_ai.get('brightness_score')} | Sharpness: {img_ai.get('sharpness_score')}")
print(f"Overall Score: {img_ai.get('overall_score')} | Condition: {img_ai.get('overall_condition')}")

print("\n--- NLP / TF-IDF MODULE ---")
print(f"Word Count: {text_ai.get('word_count')} words | Readability: '{text_ai.get('readability')}'")
print(f"Sentiment: {text_ai.get('sentiment_label')} ({text_ai.get('sentiment_score')}) | Tone: {text_ai.get('tone')}")
print(f"Text Quality Score: {text_ai.get('text_quality_score')} | Premium Score: {text_ai.get('premium_listing_score')}")
print(f"Top TF-IDF Terms: {text_ai.get('top_tfidf_terms')[:3]}")
print(f"Categorized Amenities: {text_ai.get('categorized_amenities')}")

print("\n--- GEOAPIFY LOCATION INTELLIGENCE ---")
print(f"Nearby Places Count in Property: {len(prop.get('nearby_places', []))}")

print("\n--- EMERGENCY SAFETY GUARD MODULE ---")
print(f"Safety Score: {safety.get('safety_score')} | Crime Proxy: {safety.get('crime_score')} | Rating: {safety.get('overall_rating')}")
print(f"Nearest Police Station: {safety.get('nearest_police_station')} ({safety.get('nearest_police_station_dist_meters')}m)")
print(f"Nearest Hospital: {safety.get('nearest_hospital')} ({safety.get('nearest_hospital_dist_meters')}m)")
print(f"Nearest Fire Station: {safety.get('nearest_fire_station')} ({safety.get('nearest_fire_station_dist_meters')}m)")
print(f"Emergency Coverage Score: {safety.get('emergency_coverage_score')}")
print(f"Flood Risk Status: '{safety.get('flood_risk')}' | Traffic Status: {safety.get('traffic_score')}")

print("\n--- XGBOOST VALUATION PIPELINE ---")
print(f"Predicted Selling Price: INR {round(price_pred.get('predicted_selling_price', 0)):,}")
print(f"Estimated Rental Value: INR {round(price_pred.get('estimated_rental_price', 0)):,}/month")
print(f"Price per Sqft: INR {price_pred.get('price_per_sqft'):,}")
print(f"Model Confidence Score: {price_pred.get('confidence_score')}%")

print("\n--- DYNAMIC SHAP EXPLAINABILITY ---")
print(f"Top Positive Valuation Drivers: {shap_exp.get('top_positive_factors')}")
print(f"Top Negative Valuation Drivers: {shap_exp.get('top_negative_factors')}")
print(f"Feature Importance Breakdown: {shap_exp.get('feature_importance')}")
