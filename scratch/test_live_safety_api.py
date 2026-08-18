import urllib.request
import json

print("=== TESTING LIVE SAFETY GUARD API ENDPOINTS ===")

for prop_id in [1, 2, 3]:
    url = f"http://127.0.0.1:8000/api/v1/ai/analyze-property/{prop_id}"
    try:
        req = urllib.request.urlopen(url)
        status_code = req.getcode()
        data = json.loads(req.read().decode('utf-8'))
        s = data["safety_guard"]
        p = data["property"]
        
        print(f"\n--- Property #{prop_id}: {p['title']} ({p['address']}) ---")
        print(f"HTTP Status: {status_code}")
        print(f"Emergency Coverage Score: {s['emergency_coverage_score']}")
        print(f"Safety Score: {s['safety_score']}")
        print(f"Crime Score Proxy: {s['crime_score']}")
        print(f"Overall Rating: {s['overall_rating']}")
        print(f"Flood Risk Status: {s['flood_risk']}")
        print(f"Traffic Status: {s['traffic_score']} (Data Not Available)")
        print(f"Nearest Police Station: {s['nearest_police_station']} ({s['nearest_police_station_dist_meters']}m)")
        print(f"Nearest Hospital: {s['nearest_hospital']} ({s['nearest_hospital_dist_meters']}m)")
        print(f"Nearest Fire Station: {s['nearest_fire_station']} ({s['nearest_fire_station_dist_meters']}m)")
        print(f"Summary: {s['summary']}")
        print(f"XGBoost Valuation Check: INR {round(data['price_prediction']['predicted_selling_price']):,}")
    except Exception as e:
        print(f"Error testing property #{prop_id}: {e}")
