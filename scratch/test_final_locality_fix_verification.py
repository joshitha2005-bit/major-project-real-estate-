import urllib.request
import json

print("=== VERIFYING MODEL INTEGRITY & API RESPONSE AFTER LOCALITY FIX ===")

url = "http://127.0.0.1:8000/api/v1/ai/analyze-property/1"

try:
    req = urllib.request.urlopen(url, timeout=35)
    status_code = req.getcode()
    data = json.loads(req.read().decode('utf-8'))
    
    p = data["property"]
    price_pred = data["price_prediction"]
    shap_exp = price_pred["shap_explanation"]

    print(f"\n1. API HTTP Status: {status_code}")
    print(f"2. Property Title: '{p['title']}'")
    print(f"3. Property Address: '{p['address']}'")
    print(f"4. Predicted Selling Price: INR {round(price_pred['predicted_selling_price']):,}")
    print(f"5. Price per Sqft: INR {price_pred['price_per_sqft']:,}")
    
    print("\n--- SHAP LOCALITY FEATURE ATTRIBUTION ---")
    print(f"Top Positive Factors: {json.dumps(shap_exp['top_positive_factors'], indent=2)}")
    print(f"Top Negative Factors: {json.dumps(shap_exp['top_negative_factors'], indent=2)}")
    
    has_jayanagar = any("jayanagar" in f.get("factor", "").lower() for f in shap_exp.get("top_positive_factors", []) + shap_exp.get("top_negative_factors", []))
    has_koramangala = any("koramangala" in f.get("factor", "").lower() for f in shap_exp.get("top_positive_factors", []) + shap_exp.get("top_negative_factors", []))
    
    print(f"\n6. Contains 1st Block Jayanagar: {has_jayanagar}")
    print(f"7. Contains Koramangala Attribution: {has_koramangala}")
    
except Exception as e:
    print(f"Error testing API: {e}")
