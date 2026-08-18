import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import urllib.request
import json
from app.services.text_ai_service import TextAIService

print("--- TESTING LIVE API PROPERTIES ---")
for prop_id in [1, 2, 3]:
    try:
        url = f"http://127.0.0.1:8000/api/v1/ai/analyze-property/{prop_id}"
        req = urllib.request.urlopen(url)
        data = json.loads(req.read().decode('utf-8'))
        t = data["text_ai"]
        print(f"\nProperty #{prop_id}: {data['property']['title']}")
        print(f"  Quality Score: {t['text_quality_score']} | Premium Score: {t['premium_listing_score']}")
        print(f"  Sentiment: {t['sentiment_label']} ({t['sentiment_score']}) | Tone: {t['tone']}")
        print(f"  Top TF-IDF Terms: {t['top_tfidf_terms'][:4]}")
        print(f"  Amenities Categories Detected: {[k for k, v in t['categorized_amenities'].items() if len(v) > 0]}")
        print(f"  XGBoost Predicted Selling Price: ₹{round(data['price_prediction']['predicted_selling_price']):,}")
    except Exception as e:
        print(f"Property {prop_id} error: {e}")

print("\n--- TESTING MINIMAL & EMPTY DESCRIPTIONS DIRECTLY ---")
short_test = TextAIService.analyze_description("Basic 1BHK room.")
print("Short Description Output:\n", json.dumps(short_test, indent=2))

empty_test = TextAIService.analyze_description("")
print("\nEmpty Description Output:\n", json.dumps(empty_test, indent=2))
