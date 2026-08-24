import httpx
import math
from typing import List, Dict, Any, Optional
from app.core.config import settings

# Singular label used when Geoapify returns a POI with no name
_SINGULAR_LABEL: Dict[str, str] = {
    "Schools":        "School",
    "Colleges":       "College",
    "Hospitals":      "Hospital",
    "Metro Stations": "Metro Station",
    "Bus Stops":      "Bus Stop",
    "Restaurants":    "Restaurant",
    "Shopping Malls": "Shopping Mall",
    "Banks":          "Bank",
}

GEOAPIFY_GEOCODE_URL = "https://api.geoapify.com/v1/geocode/search"
GEOAPIFY_REVERSE_URL = "https://api.geoapify.com/v1/geocode/reverse"
GEOAPIFY_PLACES_URL = "https://api.geoapify.com/v2/places"

BANGALORE_BENCHMARKS: Dict[str, float] = {
    "koramangala": 12500.0,
    "indiranagar": 14000.0,
    "whitefield": 7800.0,
    "hsr layout": 9500.0,
    "hsr": 9500.0,
    "electronic city": 5600.0,
    "marathahalli": 7200.0,
    "jp nagar": 8800.0,
    "banashankari": 7500.0,
    "jayanagar": 11500.0,
    "bellandur": 8200.0,
    "sarjapur": 6800.0,
    "hebbal": 9200.0,
    "yelahanka": 6100.0,
    "mg road": 16500.0,
    "malleshwaram": 13000.0,
    "rajajinagar": 10500.0,
}

def calculate_price_estimate(location_text: str, lat: float, lon: float) -> tuple[float, str]:
    text_lower = location_text.lower()
    matched_base = None
    
    for key, price in BANGALORE_BENCHMARKS.items():
        if key in text_lower:
            matched_base = price
            break
            
    if not matched_base:
        center_lat, center_lon = 12.9716, 77.5946
        dlat = math.radians(lat - center_lat)
        dlon = math.radians(lon - center_lon)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(center_lat)) * math.cos(math.radians(lat)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance_km = 6371 * c
        matched_base = max(4500.0, 12000.0 - (distance_km * 350.0))
        
    min_price = round(matched_base * 0.9, -2)
    max_price = round(matched_base * 1.15, -2)
    avg_price = round((min_price + max_price) / 2, -2)
    
    price_range_str = f"₹{int(min_price):,} - ₹{int(max_price):,} / sq.ft"
    return avg_price, price_range_str

class GeoapifyService:
    @staticmethod
    async def search_geocode(text: str) -> Optional[Dict[str, Any]]:
        """Geocode address query strictly using live Geoapify API with automatic Bangalore bias."""
        async with httpx.AsyncClient(timeout=12.0) as client:
            params = {
                "text": text,
                "apiKey": settings.GEOAPIFY_API_KEY,
                "limit": 1
            }
            if "india" not in text.lower() and "bangalore" not in text.lower() and "bengaluru" not in text.lower():
                params["bias"] = "proximity:77.5946,12.9716"
                params["filter"] = "countrycode:in"

            try:
                response = await client.get(GEOAPIFY_GEOCODE_URL, params=params)
                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])
                    if features:
                        feature = features[0]
                        props = feature.get("properties", {})
                        geometry = feature.get("geometry", {})
                        coords = geometry.get("coordinates", [77.5946, 12.9716])
                        lon, lat = coords[0], coords[1]
                        
                        formatted = props.get("formatted") or props.get("address_line1") or text
                        city = props.get("city") or props.get("county") or "Bengaluru"
                        state = props.get("state") or "Karnataka"
                        country = props.get("country") or "India"
                        postcode = props.get("postcode")
                        place_id = props.get("place_id")
                        
                        avg_price, price_range = calculate_price_estimate(formatted, lat, lon)

                        return {
                            "query": text,
                            "formatted_address": formatted,
                            "latitude": lat,
                            "longitude": lon,
                            "city": city,
                            "state": state,
                            "country": country,
                            "postcode": postcode,
                            "place_id": place_id,
                            "estimated_price_sqft": avg_price,
                            "price_range": price_range
                        }
            except Exception as e:
                print(f"Geoapify Geocode error: {e}")

        return None

    @staticmethod
    async def reverse_geocode(lat: float, lon: float) -> Dict[str, Any]:
        """Reverse geocode coordinates strictly using live Geoapify API."""
        async with httpx.AsyncClient(timeout=12.0) as client:
            params = {
                "lat": lat,
                "lon": lon,
                "apiKey": settings.GEOAPIFY_API_KEY
            }
            try:
                response = await client.get(GEOAPIFY_REVERSE_URL, params=params)
                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])
                    if features:
                        props = features[0].get("properties", {})
                        formatted = props.get("formatted") or "Current Location"
                        city = props.get("city") or "Bengaluru"
                        state = props.get("state") or "Karnataka"
                        avg_price, price_range = calculate_price_estimate(formatted, lat, lon)
                        return {
                            "query": formatted,
                            "formatted_address": formatted,
                            "latitude": lat,
                            "longitude": lon,
                            "city": city,
                            "state": state,
                            "country": props.get("country", "India"),
                            "postcode": props.get("postcode"),
                            "place_id": props.get("place_id"),
                            "estimated_price_sqft": avg_price,
                            "price_range": price_range
                        }
            except Exception as e:
                print(f"Geoapify Reverse error: {e}")

        avg_price, price_range = calculate_price_estimate("Current Location", lat, lon)
        return {
            "query": "Current Location",
            "formatted_address": f"Location ({lat:.4f}, {lon:.4f}), Bengaluru, Karnataka",
            "latitude": lat,
            "longitude": lon,
            "city": "Bengaluru",
            "state": "Karnataka",
            "country": "India",
            "postcode": "560001",
            "place_id": "current_loc",
            "estimated_price_sqft": avg_price,
            "price_range": price_range
        }

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate Haversine distance in meters between two geographical points."""
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return 6371000.0 * c

    @classmethod
    async def _fetch_category_places(
        cls, 
        client: httpx.AsyncClient, 
        cat_label: str, 
        geo_cats: List[str], 
        lat: float, 
        lon: float, 
        radius_meters: int = 5000, 
        per_category_limit: int = 6
    ) -> List[Dict[str, Any]]:
        """Fetch places for a specific category taxonomy using Geoapify API."""
        cats_query = ",".join(geo_cats)
        params = {
            "categories": cats_query,
            "filter": f"circle:{lon},{lat},{radius_meters}",
            "bias": f"proximity:{lon},{lat}",
            "limit": per_category_limit,
            "apiKey": settings.GEOAPIFY_API_KEY
        }
        try:
            resp = await client.get(GEOAPIFY_PLACES_URL, params=params)
            if resp.status_code == 200:
                data = resp.json()
                features = data.get("features", [])
                places = []
                # Singular form used for honest unnamed-place fallbacks
                singular = _SINGULAR_LABEL.get(cat_label, cat_label)
                for feat in features:
                    props = feat.get("properties", {})
                    geom = feat.get("geometry", {})
                    coords = geom.get("coordinates", [lon, lat])
                    p_lon, p_lat = coords[0], coords[1]

                    # Use proper name only; never use a road/address string as a place name
                    raw_name = props.get("name") or ""
                    name = raw_name.strip() if raw_name.strip() else f"Unnamed {singular}"

                    dist = props.get("distance")
                    if dist is None:
                        dist = cls.haversine_distance(lat, lon, p_lat, p_lon)

                    # Build address from address_line2 first (more specific),
                    # then formatted (full address), then coordinate fallback
                    address = (
                        props.get("address_line2")
                        or props.get("formatted")
                        or f"Near ({p_lat:.4f}, {p_lon:.4f})"
                    )

                    places.append({
                        "name": name,
                        "category": cat_label,
                        "distance_meters": round(float(dist), 1),
                        "latitude": float(p_lat),
                        "longitude": float(p_lon),
                        "address": address
                    })
                return places
        except Exception as e:
            print(f"Geoapify Places error for category '{cat_label}': {e}")
        return []

    @classmethod
    async def get_nearby_places(cls, lat: float, lon: float, radius_meters: int = 5000) -> List[Dict[str, Any]]:
        """Fetch nearby Schools, Hospitals, Metro, Bus Stops, Parks, Restaurants, Malls, Colleges, Banks via targeted Geoapify queries."""
        category_taxonomy_map = {
            "Schools":        ["education.school"],
            "Colleges":       ["education.college", "education.university"],
            "Hospitals":      ["healthcare.hospital", "healthcare.clinic_or_praxis"],
            "Metro Stations": ["building.transportation", "public_transport.subway", "public_transport.train"],
            "Bus Stops":      ["public_transport.bus"],
            "Restaurants":    ["catering.restaurant"],
            "Shopping Malls": ["commercial.shopping_mall"],
            "Banks":          ["service.financial.bank", "service.financial.atm"]
        }

        async with httpx.AsyncClient(timeout=12.0) as client:
            import asyncio
            tasks = [
                cls._fetch_category_places(client, cat_label, geo_cats, lat, lon, radius_meters, per_category_limit=6)
                for cat_label, geo_cats in category_taxonomy_map.items()
            ]
            results_nested = await asyncio.gather(*tasks)

        # Deduplication by (normalized_name, round(lat, 4), round(lon, 4))
        all_places = []
        seen_keys = set()

        for category_places in results_nested:
            for p in category_places:
                norm_name = p["name"].strip().lower()
                key = (norm_name, round(p["latitude"], 4), round(p["longitude"], 4))
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                all_places.append(p)

        # Ascending distance sort: nearest first
        all_places.sort(key=lambda item: item["distance_meters"])

        category_counts = {}
        for p in all_places:
            category_counts[p["category"]] = category_counts.get(p["category"], 0) + 1

        print(f"Geoapify Targeted Places Fetched: {len(all_places)} valid items | Breakdown: {category_counts}")
        return all_places

    @staticmethod
    def calculate_gis_lifestyle_score(places: List[Dict[str, Any]]) -> float:
        """Calculate Location / Lifestyle score based on actual GIS infrastructure proximity."""
        if not places:
            return 65.0

        base_score = 50.0
        cat_min_dists = {}
        for p in places:
            cat = p["category"]
            dist = p["distance_meters"]
            if cat not in cat_min_dists or dist < cat_min_dists[cat]:
                cat_min_dists[cat] = dist

        # Metro accessibility bonus
        metro_dist = cat_min_dists.get("Metro Stations", 99999)
        if metro_dist <= 1500: base_score += 15.0
        elif metro_dist <= 3000: base_score += 10.0
        elif metro_dist <= 5000: base_score += 5.0

        # Healthcare accessibility bonus
        hosp_dist = cat_min_dists.get("Hospitals", 99999)
        if hosp_dist <= 2000: base_score += 12.0
        elif hosp_dist <= 4000: base_score += 7.0

        # Education accessibility bonus
        edu_dist = min(cat_min_dists.get("Schools", 99999), cat_min_dists.get("Colleges", 99999))
        if edu_dist <= 1500: base_score += 10.0
        elif edu_dist <= 3000: base_score += 5.0

        # Parks & Recreation bonus
        park_dist = cat_min_dists.get("Parks", 99999)
        if park_dist <= 1500: base_score += 8.0

        # Shopping & Dining bonus
        shop_dist = min(cat_min_dists.get("Shopping Malls", 99999), cat_min_dists.get("Restaurants", 99999))
        if shop_dist <= 2000: base_score += 5.0

        # Amenities volume bonus
        base_score += min(10.0, len(places) * 0.2)

        return min(98.0, max(35.0, round(base_score, 1)))

