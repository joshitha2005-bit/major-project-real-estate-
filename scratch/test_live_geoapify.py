import urllib.request
import json

TEST_LOCATIONS = [
    ("Koramangala", 12.9312, 77.6210),
    ("HSR Layout", 12.9121, 77.6446),
    ("Whitefield", 12.9698, 77.7500),
    ("Electronic City", 12.8399, 77.6770),
    ("Indiranagar", 12.9784, 77.6408)
]

print("=== TESTING LIVE GEOAPIFY LOCATION INTELLIGENCE ===")

for loc_name, lat, lon in TEST_LOCATIONS:
    print(f"\n==========================================")
    print(f"LOCATION: {loc_name} ({lat}, {lon})")
    print(f"==========================================")
    
    url = f"http://127.0.0.1:8000/api/v1/location/nearby-places?lat={lat}&lon={lon}&radius=5000"
    try:
        req = urllib.request.urlopen(url)
        status_code = req.getcode()
        places = json.loads(req.read().decode('utf-8'))
        
        print(f"HTTP Status: {status_code}")
        print(f"Total Unique Places Fetched: {len(places)}")
        
        # Category breakdown
        cat_breakdown = {}
        for p in places:
            cat_breakdown[p["category"]] = cat_breakdown.get(p["category"], 0) + 1
        print(f"Category Breakdown: {cat_breakdown}")
        
        # Nearest item per category
        printed_cats = set()
        print("\nNearest Place per Category:")
        for p in places:
            cat = p["category"]
            if cat not in printed_cats:
                printed_cats.add(cat)
                dist_str = f"{p['distance_meters']/1000:.2f} km" if p['distance_meters'] >= 1000 else f"{int(p['distance_meters'])} m"
                print(f"  [{cat}] {p['name']} -> {dist_str}")
                
    except Exception as e:
        print(f"Error testing {loc_name}: {e}")

print("\n=== TESTING LOCALITY STATS GIS LIFESTYLE SCORE ===")
url_stats = "http://127.0.0.1:8000/api/v1/location/locality-stats?locality=Koramangala&lat=12.9312&lon=77.6210"
try:
    req = urllib.request.urlopen(url_stats)
    stats_data = json.loads(req.read().decode('utf-8'))
    print(f"Locality: {stats_data['locality']}")
    print(f"Calculated GIS Amenities/Lifestyle Score: {stats_data['amenities_score']}")
    print(f"Safety Score: {stats_data['safety_score']}")
except Exception as e:
    print(f"Locality stats error: {e}")
