import asyncio
import httpx
import math
from typing import Dict, Any, Optional

GEOAPIFY_API_KEY = "7e57c95ce01147f38a78dab8029c635a"
GEOAPIFY_PLACES_URL = "https://api.geoapify.com/v2/places"

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 6371000.0 * c

async def fetch_nearest_poi(client: httpx.AsyncClient, category: str, lat: float, lon: float, radius: int = 5000) -> Optional[Dict[str, Any]]:
    params = {
        "categories": category,
        "filter": f"circle:{lon},{lat},{radius}",
        "bias": f"proximity:{lon},{lat}",
        "limit": 1,
        "apiKey": GEOAPIFY_API_KEY
    }
    try:
        resp = await client.get(GEOAPIFY_PLACES_URL, params=params, timeout=8.0)
        if resp.status_code == 200:
            data = resp.json()
            features = data.get("features", [])
            if features:
                props = features[0].get("properties", {})
                geom = features[0].get("geometry", {})
                coords = geom.get("coordinates", [lon, lat])
                p_lon, p_lat = coords[0], coords[1]
                name = props.get("name") or props.get("formatted") or "Emergency Facility"
                dist = props.get("distance")
                if dist is None:
                    dist = haversine_distance(lat, lon, p_lat, p_lon)
                return {
                    "name": name,
                    "distance_meters": round(float(dist), 1),
                    "latitude": float(p_lat),
                    "longitude": float(p_lon)
                }
    except Exception as e:
        print(f"Error querying category '{category}': {e}")
    return None

async def analyze_locality_safety(locality_name: str, lat: float, lon: float) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        police_poi, hospital_poi, fire_poi = await asyncio.gather(
            fetch_nearest_poi(client, "service.police", lat, lon),
            fetch_nearest_poi(client, "healthcare.hospital", lat, lon),
            fetch_nearest_poi(client, "amenity.fire_station", lat, lon)
        )

    # 1. Calculate Emergency Coverage Score
    # Police Station Contribution (Max 40 pts)
    police_dist = police_poi["distance_meters"] if police_poi else None
    if police_dist is not None:
        if police_dist <= 1000: police_pts = 40.0
        elif police_dist <= 2000: police_pts = 30.0
        elif police_dist <= 3500: police_pts = 20.0
        elif police_dist <= 5000: police_pts = 10.0
        else: police_pts = 5.0
    else:
        police_pts = 0.0

    # Hospital Contribution (Max 35 pts)
    hosp_dist = hospital_poi["distance_meters"] if hospital_poi else None
    if hosp_dist is not None:
        if hosp_dist <= 1000: hosp_pts = 35.0
        elif hosp_dist <= 2000: hosp_pts = 25.0
        elif hosp_dist <= 3500: hosp_pts = 15.0
        elif hosp_dist <= 5000: hosp_pts = 8.0
        else: hosp_pts = 4.0
    else:
        hosp_pts = 0.0

    # Fire Station Contribution (Max 25 pts)
    fire_dist = fire_poi["distance_meters"] if fire_poi else None
    if fire_dist is not None:
        if fire_dist <= 1500: fire_pts = 25.0
        elif fire_dist <= 3000: fire_pts = 18.0
        elif fire_dist <= 5000: fire_pts = 10.0
        else: fire_pts = 5.0
    else:
        fire_pts = 0.0

    emergency_coverage_score = round(min(100.0, max(0.0, police_pts + hosp_pts + fire_pts)), 1)
    safety_score = emergency_coverage_score
    crime_score = round(100.0 - safety_score, 1)

    # Overall Rating Grade
    if safety_score >= 90.0: overall_rating = "A+"
    elif safety_score >= 80.0: overall_rating = "A"
    elif safety_score >= 70.0: overall_rating = "B+"
    elif safety_score >= 60.0: overall_rating = "B"
    else: overall_rating = "C"

    # Summary Generation
    parts = []
    if police_poi:
        p_dist_str = f"{police_dist/1000:.2f}km" if police_dist >= 1000 else f"{int(police_dist)}m"
        parts.append(f"Police ({police_poi['name']} at {p_dist_str})")
    if hospital_poi:
        h_dist_str = f"{hosp_dist/1000:.2f}km" if hosp_dist >= 1000 else f"{int(hosp_dist)}m"
        parts.append(f"Hospital ({hospital_poi['name']} at {h_dist_str})")

    if parts:
        summary_text = f"Emergency infrastructure score: {emergency_coverage_score}/100. Nearby services: {', '.join(parts)}."
    else:
        summary_text = f"Emergency infrastructure score: {emergency_coverage_score}/100. Limited immediate GIS emergency facilities detected."

    return {
        "safety_score": safety_score,
        "crime_score": crime_score,
        "flood_risk": "Data Not Available",
        "traffic_score": 50.0,
        "overall_rating": overall_rating,
        "summary": summary_text,
        "nearest_police_station": police_poi["name"] if police_poi else None,
        "nearest_police_station_dist_meters": police_dist,
        "nearest_hospital": hospital_poi["name"] if hospital_poi else None,
        "nearest_hospital_dist_meters": hosp_dist,
        "nearest_fire_station": fire_poi["name"] if fire_poi else None,
        "nearest_fire_station_dist_meters": fire_dist,
        "emergency_coverage_score": emergency_coverage_score
    }

async def main():
    print("=== TESTING REAL GIS SAFETY GUARD ACROSS 5 LOCATIONS ===")
    test_locs = [
        ("Koramangala", 12.9312, 77.6210),
        ("Indiranagar", 12.9784, 77.6408),
        ("Whitefield", 12.9698, 77.7500),
        ("HSR Layout", 12.9121, 77.6446),
        ("Electronic City", 12.8399, 77.6770)
    ]
    for loc, lat, lon in test_locs:
        print(f"\n--- {loc} ({lat}, {lon}) ---")
        res = await analyze_locality_safety(loc, lat, lon)
        print(res)

asyncio.run(main())
