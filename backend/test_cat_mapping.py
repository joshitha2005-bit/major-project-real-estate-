import urllib.request
import urllib.parse
import json

API_KEY = "7e57c95ce01147f38a78dab8029c635a"

def test_live_categorization(lat, lon, locality):
    categories = "education,healthcare,public_transport,catering,commercial,service,leisure"
    url = f"https://api.geoapify.com/v2/places?categories={categories}&filter=circle:{lon},{lat},5000&bias=proximity:{lon},{lat}&limit=40&apiKey={API_KEY}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            features = data.get("features", [])
            
            counts = {
                "Schools": 0, "Colleges": 0, "Hospitals": 0,
                "Metro Stations": 0, "Bus Stops": 0, "Restaurants": 0,
                "Shopping Malls": 0, "Banks": 0, "Parks": 0, "Amenities": 0
            }
            
            for f in features:
                props = f["properties"]
                cats = props.get("categories", [])
                cats_str = " ".join(cats).lower()
                
                if "school" in cats_str: cat_label = "Schools"
                elif "college" in cats_str or "university" in cats_str: cat_label = "Colleges"
                elif "hospital" in cats_str or "clinic" in cats_str or "healthcare" in cats_str: cat_label = "Hospitals"
                elif "subway" in cats_str or "metro" in cats_str or "train" in cats_str: cat_label = "Metro Stations"
                elif "bus" in cats_str: cat_label = "Bus Stops"
                elif "restaurant" in cats_str or "fast_food" in cats_str or "cafe" in cats_str or "catering" in cats_str or "food" in cats_str: cat_label = "Restaurants"
                elif "shopping" in cats_str or "mall" in cats_str or "supermarket" in cats_str or "commercial" in cats_str: cat_label = "Shopping Malls"
                elif "bank" in cats_str or "financial" in cats_str or "atm" in cats_str: cat_label = "Banks"
                elif "park" in cats_str or "garden" in cats_str or "playground" in cats_str or "leisure" in cats_str: cat_label = "Parks"
                else: cat_label = "Amenities"
                
                counts[cat_label] += 1
                
            print(f"\n{locality} ({len(features)} total live features returned):")
            for cat, cnt in counts.items():
                if cnt > 0:
                    print(f"  - {cat}: {cnt}")
    except Exception as e:
        print(f"HTTP Error for {locality}: {e}")

if __name__ == "__main__":
    test_live_categorization(12.9410352, 77.6241999, "Koramangala")
    test_live_categorization(12.8487599, 77.648253, "Electronic City")
    test_live_categorization(12.9705356, 77.7499623, "Whitefield")
    test_live_categorization(12.920456, 77.6444991, "HSR Layout")
