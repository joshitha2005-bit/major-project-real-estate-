import urllib.request
import urllib.parse
import json

API_KEY = "7e57c95ce01147f38a78dab8029c635a"

TARGET_LOCATIONS = [
    "Koramangala, Bengaluru",
    "Electronic City, Bengaluru",
    "Whitefield, Bengaluru",
    "HSR Layout, Bengaluru",
    "Indiranagar, Bengaluru"
]

def geocode_location(query):
    url = f"https://api.geoapify.com/v1/geocode/search?text={urllib.parse.quote(query)}&apiKey={API_KEY}&limit=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        features = data.get("features", [])
        if features:
            props = features[0]["properties"]
            coords = features[0]["geometry"]["coordinates"]
            return {
                "address": props.get("formatted") or props.get("address_line1"),
                "lat": coords[1],
                "lon": coords[0],
                "city": props.get("city") or "Bengaluru"
            }
    return None

def fetch_nearby_places(lat, lon):
    categories = [
        "education.school",
        "education.college",
        "healthcare.hospital",
        "public_transport.subway",
        "public_transport.train",
        "public_transport.bus",
        "catering.restaurant",
        "commercial.shopping_mall",
        "service.financial.bank",
        "leisure.park"
    ]
    cat_str = ",".join(categories)
    url = f"https://api.geoapify.com/v2/places?categories={cat_str}&filter=circle:{lon},{lat},5000&bias=proximity:{lon},{lat}&limit=40&apiKey={API_KEY}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        features = data.get("features", [])
        
        categorized = {
            "Schools": [],
            "Colleges": [],
            "Hospitals": [],
            "Metro Stations": [],
            "Bus Stops": [],
            "Restaurants": [],
            "Shopping Malls": [],
            "Banks": [],
            "Parks": []
        }

        for f in features:
            props = f["properties"]
            name = props.get("name") or props.get("formatted")
            cats = props.get("categories", [])
            
            cat_label = "Other"
            for c in cats:
                if "school" in c: cat_label = "Schools"; break
                elif "college" in c or "university" in c: cat_label = "Colleges"; break
                elif "hospital" in c or "healthcare" in c: cat_label = "Hospitals"; break
                elif "subway" in c or "metro" in c or "train" in c or "station" in c: cat_label = "Metro Stations"; break
                elif "bus" in c: cat_label = "Bus Stops"; break
                elif "restaurant" in c or "catering" in c or "fast_food" in c or "cafe" in c: cat_label = "Restaurants"; break
                elif "shopping_mall" in c or "mall" in c or "commercial" in c: cat_label = "Shopping Malls"; break
                elif "bank" in c or "financial" in c: cat_label = "Banks"; break
                elif "park" in c or "leisure" in c: cat_label = "Parks"; break
            
            if cat_label in categorized:
                categorized[cat_label].append(name)

        return categorized

if __name__ == "__main__":
    print("=" * 60)
    print("LIVE GEOAPIFY VERIFICATION FOR 5 BANGALORE METRO LOCATIONS")
    print("=" * 60)
    
    for loc_name in TARGET_LOCATIONS:
        print(f"\n[LOCATION] {loc_name}")
        geo = geocode_location(loc_name)
        if not geo:
            print("   [FAILED] Geocoding Failed!")
            continue
            
        print(f"   [OK] Address: {geo['address']}")
        print(f"   [OK] Latitude: {geo['lat']}")
        print(f"   [OK] Longitude: {geo['lon']}")
        
        places = fetch_nearby_places(geo['lat'], geo['lon'])
        print(f"   [OK] Nearby Amenities Fetched via Live Geoapify Places API:")
        for cat, items in places.items():
            print(f"     - {cat} ({len(items)} found): {', '.join(items[:3]) if items else 'None'}")
