import urllib.request
import json

print("=== TESTING LIVE BACKEND CNN API ENDPOINT ===")
for prop_id in [1, 2, 3]:
    url = f"http://127.0.0.1:8000/api/v1/ai/analyze-property/{prop_id}"

    req = urllib.request.urlopen(url)
    status_code = req.getcode()
    data = json.loads(req.read().decode('utf-8'))

    image_ai = data["image_ai"]
    price_pred = data["price_prediction"]

    print(f"\n--- PROPERTY #{prop_id}: {data['property']['title']} ---")
    print(f"HTTP Status: {status_code}")
    print(f"Images Analyzed (processed_count): {image_ai['processed_count']}")
    print(f"CNN Model: {image_ai['cnn_model']}")
    print(f"CNN Status: {image_ai['cnn_status']}")
    print(f"CNN Feature Score: {image_ai['cnn_feature_score']}")
    print(f"Brightness Score: {image_ai['brightness_score']}")
    print(f"Sharpness Score: {image_ai['sharpness_score']}")
    print(f"Image Quality Score: {image_ai['image_quality_score']}")
    print(f"Interior Condition Score: {image_ai['interior_condition_score']}")
    print(f"Exterior Condition Score: {image_ai['exterior_condition_score']}")
    print(f"Overall Condition: {image_ai['overall_condition']}")
    print(f"Overall Score: {image_ai['overall_score']}")
    print(f"XGBoost Predicted Selling Price: INR {round(price_pred['predicted_selling_price']):,}")
