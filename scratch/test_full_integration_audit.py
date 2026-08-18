import sys, os, asyncio, json, urllib.request

sys.path.insert(0, os.path.abspath('backend'))

print("=== STARTING FULL END-TO-END INTEGRATION AUDIT ===")

test_ids = [1, 2, 3]
audit_results = []

for prop_id in test_ids:
    url = f"http://127.0.0.1:8000/api/v1/ai/analyze-property/{prop_id}"
    try:
        req = urllib.request.urlopen(url, timeout=35)
        status_code = req.getcode()
        data = json.loads(req.read().decode('utf-8'))
        
        prop = data.get("property", {})
        img_ai = data.get("image_ai", {})
        text_ai = data.get("text_ai", {})
        safety = data.get("safety_guard", {})
        price_pred = data.get("price_prediction", {})
        shap_exp = price_pred.get("shap_explanation", {})
        
        result = {
            "property_id": prop_id,
            "title": prop.get("title"),
            "locality": prop.get("address"),
            "http_status": status_code,
            "image_analysis_status": {
                "model": img_ai.get("cnn_model"),
                "status": img_ai.get("cnn_status"),
                "processed_count": img_ai.get("processed_count"),
                "cnn_feature_score": img_ai.get("cnn_feature_score"),
                "overall_score": img_ai.get("overall_score"),
                "overall_condition": img_ai.get("overall_condition")
            },
            "nlp_analysis_status": {
                "quality_score": text_ai.get("text_quality_score"),
                "premium_score": text_ai.get("premium_listing_score"),
                "word_count": text_ai.get("word_count"),
                "sentiment_label": text_ai.get("sentiment_label"),
                "sentiment_score": text_ai.get("sentiment_score"),
                "tone": text_ai.get("tone"),
                "top_tfidf_count": len(text_ai.get("top_tfidf_terms", [])),
                "categorized_amenities_keys": list(text_ai.get("categorized_amenities", {}).keys())
            },
            "geoapify_status": {
                "nearby_places_count": len(prop.get("nearby_places", []))
            },
            "safety_status": {
                "rating": safety.get("overall_rating"),
                "emergency_score": safety.get("emergency_coverage_score"),
                "nearest_police": safety.get("nearest_police_station"),
                "nearest_police_dist": safety.get("nearest_police_station_dist_meters"),
                "nearest_hospital": safety.get("nearest_hospital"),
                "nearest_hospital_dist": safety.get("nearest_hospital_dist_meters")
            },
            "xgboost_prediction": {
                "predicted_price": price_pred.get("predicted_selling_price"),
                "price_per_sqft": price_pred.get("price_per_sqft"),
                "valuation_status": price_pred.get("valuation_status")
            },
            "shap_status": {
                "base_value": shap_exp.get("base_value"),
                "has_force_plot": "force_plot_html" in shap_exp,
                "top_positive": shap_exp.get("top_positive_features", [])[:2],
                "top_negative": shap_exp.get("top_negative_features", [])[:2]
            }
        }
        audit_results.append(result)
    except Exception as e:
        print(f"Audit error for property #{prop_id}: {e}")

print(json.dumps(audit_results, indent=2))
