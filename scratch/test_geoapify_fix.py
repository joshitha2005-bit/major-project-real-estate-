import asyncio
import httpx
import math
from typing import List, Dict, Any

GEOAPIFY_API_KEY = "7e57c95ce01147f38a78dab8029c635a"
GEOAPIFY_PLACES_URL = "https://api.geoapify.com/v2/places"

TARGET_CATEGORY_MAP = {
    "Schools": ["education.school"],
    "Colleges": ["education.college", "education.university"],
    "Hospitals": ["healthcare.hospital", "healthcare.clinic"],
    "Metro Stations": ["building.transportation", "public_transport.subway", "public_transport.train"],
    "Bus Stops": ["public_transport.bus"],
    "Parks": ["leisure.park", "leisure.playground"],
    "Restaurants": ["catering.restaurant"],
    "Shopping Malls": ["commercial.shopping_mall", "commercial.supermarket"],
    "Banks": ["service.financial.bank", "service.financial.atm"]
}

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 6371000.0 * c

async def fetch_category_places(client: httpx.AsyncClient, cat_label: str, geo_cats: List[str], lat: float, lon: float, radius: int = 5000) -> List[Dict[str, Any]]:
    cats_query = ",".join(geo_cats)
    params = {
        "categories": cats_query,
        "filter": f"circle:{lon},{lat},{radius}",
        "bias": f"proximity:{lon},{lat}",
        "limit": 6,
        "apiKey": GEOAPIFY_API_KEY
    }
    try:
        resp = await client.get(GEOAPIFY_PLACES_URL, params=params, timeout=10.0)
        if resp.status_code == 200:
            data = resp.json()
            features = data.get("features", [])
            places = []
            for feat in features:
                props = feat.get("properties", {})
                geom = feat.get("geometry", {})
                coords = geom.get("coordinates", [lon, lat])
                p_lon, p_lat = coords[0], coords[1]
                name = props.get("name") or props.get("formatted") or "Point of Interest"
                
                dist = props.get("distance")
                if dist is None:
                    dist = haversine_distance(lat, lon, p_lat, p_lon)
                    
                places.append({
                    "name": name,
                    "category": cat_label,
                    "distance_meters": round(dist, 1),
                    "latitude": p_lat,
                    "longitude": p_lon,
                    "address": props.get("address_line2") or props.get("formatted") or f"Near ({p_lat:.4f}, {p_lon:.4f})"
                })
            return places
    except Exception as e:
        print(f"Error fetching {cat_label}: {e}")
    return []

async def get_nearby_places_enhanced(lat: float, lon: float, radius_meters: int = 5000) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=12.0) as client:
        tasks = [
            fetch_category_places(client, cat_label, geo_cats, lat, lon, radius_meters)
            for cat_label, geo_cats in TARGET_CATEGORY_MAP.items()
        ]
        results_nested = await asyncio.gather(*tasks)

    # Flatten & Deduplicate
    all_places = []
    seen = set()
    dedup_count = 0

    for category_places in results_nested:
        for p in category_places:
            norm_name = p["name"].strip().lower()
            key = (norm_name, round(p["latitude"], 4), round(p["longitude"], 4))
            if key in seen:
                dedup_count += 1
                continue
            seen.add(key)
            all_places.append(p)

    # Sort ascending by distance
    all_places.sort(key=lambda x: x["distance_meters"])
    print(f"Deduplicated count: {dedup_count} duplicates removed. Total valid places: {len(all_places)}")
    return all_places

async def main():
    print("=== TESTING ENHANCED GEOAPIFY NEARBY PLACES (Koramangala: 12.9312, 77.621) ===")
    places = await get_nearby_places_enhanced(12.9312, 77.621, 5000)
    
    counts = {}
    for p in places:
        counts[p["category"]] = counts.get(p["category"], 0) + 1
    print("\nCategory breakdown:", counts)

    print("\nNearest item per category:")
    printed_cats = set()
    for p in places:
        if p["category"] not in printed_cats:
            printed_cats.add(p["category"])
            dist_str = f"{p['distance_meters']/1000:.2f} km" if p['distance_meters'] >= 1000 else f"{int(p['distance_meters'])} m"
            print(f"  {p['category']}: '{p['name']}' at {dist_str}")

asyncio.run(main())
