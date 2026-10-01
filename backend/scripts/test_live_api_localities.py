import urllib.request
import json

for loc in ['Devanahalli', 'Malleshwaram']:
    url = f'http://127.0.0.1:8000/api/v1/properties/?query={loc}&limit=2'
    try:
        req = urllib.request.urlopen(url)
        data = json.loads(req.read().decode())
        print(f'=== {loc.upper()} ===')
        for item in data.get('items', []):
            name = item.get('property_name') or item.get('building_name') or item.get('title')
            loc_name = item.get('locality')
            lat = item.get('latitude')
            lon = item.get('longitude')
            c_conf = (item.get('canonical_location') or {}).get('coordinate_confidence')
            print(f"  ID: {item.get('id')} | {name} | Loc: {loc_name} | Coords: ({lat}, {lon}) | Conf: {c_conf}")
    except Exception as e:
        print(f"Error querying {loc}: {e}")
