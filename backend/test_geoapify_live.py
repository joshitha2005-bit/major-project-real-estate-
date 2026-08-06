import urllib.request
import urllib.parse
import json

API_KEY = "7e57c95ce01147f38a78dab8029c635a"

def test_geocode(query):
    url = f"https://api.geoapify.com/v1/geocode/search?text={urllib.parse.quote(query)}&apiKey={API_KEY}&limit=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        features = data.get("features", [])
        if features:
            props = features[0]["properties"]
            coords = features[0]["geometry"]["coordinates"]
            print(f"[GEOCODE SUCCESS] Query: '{query}' -> Address: {props.get('formatted')}, Coords: ({coords[1]}, {coords[0]})")
            return coords[1], coords[0]
    print(f"[GEOCODE FAILED] Query: '{query}'")
    return None, None

def test_places(lat, lon):
    categories = "education.school,healthcare.hospital,public_transport.subway,catering.restaurant,commercial.shopping_mall,leisure.park"
    url = f"https://api.geoapify.com/v2/places?categories={categories}&filter=circle:{lon},{lat},3000&apiKey={API_KEY}&limit=10"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        features = data.get("features", [])
        print(f"[PLACES SUCCESS] Found {len(features)} nearby places around ({lat}, {lon})")
        for f in features[:5]:
            props = f["properties"]
            print(f"  - {props.get('name') or props.get('formatted')} ({props.get('categories')})")

if __name__ == "__main__":
    print("Testing Live Geoapify API Key:", API_KEY)
    lat_k, lon_k = test_geocode("Koramangala, Bengaluru")
    lat_e, lon_e = test_geocode("Electronic City, Bengaluru")
    if lat_k and lon_k:
        test_places(lat_k, lon_k)
