import urllib.request
import urllib.parse
import json

API_KEY = "7e57c95ce01147f38a78dab8029c635a"

def test_query(lat, lon, categories):
    url = f"https://api.geoapify.com/v2/places?categories={categories}&filter=circle:{lon},{lat},5000&bias=proximity:{lon},{lat}&limit=40&apiKey={API_KEY}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            features = data.get("features", [])
            print(f"Status 200: {len(features)} places returned for categories: {categories[:50]}...")
            return features
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    lat, lon = 12.9410352, 77.6241999  # Koramangala
    print("Testing Koramangala (12.941, 77.624)...")
    cats1 = "education,healthcare,public_transport,catering,commercial,service.financial,leisure"
    test_query(lat, lon, cats1)
    
    cats2 = "education.school,education.college,healthcare.hospital,public_transport,catering.restaurant,commercial.shopping_mall,service.financial.bank,leisure.park"
    test_query(lat, lon, cats2)
