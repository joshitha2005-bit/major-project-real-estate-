import httpx
import math
from typing import List, Dict, Any, Optional
from app.core.config import settings

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
    async def get_nearby_places(lat: float, lon: float, radius_meters: int = 5000) -> List[Dict[str, Any]]:
        """Fetch nearby Schools, Hospitals, Metro, Restaurants, Malls, Banks, Parks, Colleges, Bus Stops via live Geoapify Places API."""
        categories = "education,healthcare,public_transport,catering,commercial,service.financial,leisure"
        
        async with httpx.AsyncClient(timeout=12.0) as client:
            params = {
                "categories": categories,
                "filter": f"circle:{lon},{lat},{radius_meters}",
                "bias": f"proximity:{lon},{lat}",
                "limit": 50,
                "apiKey": settings.GEOAPIFY_API_KEY
            }
            url = f"{GEOAPIFY_PLACES_URL}?categories={categories}&filter=circle:{lon},{lat},{radius_meters}&bias=proximity:{lon},{lat}&limit=50&apiKey={settings.GEOAPIFY_API_KEY[:6]}..."
            try:
                response = await client.get(GEOAPIFY_PLACES_URL, params=params)
                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])
                    results = []
                    category_counts = {}

                    for item in features:
                        props = item.get("properties", {})
                        geom = item.get("geometry", {})
                        c_coords = geom.get("coordinates", [lon, lat])
                        
                        name = props.get("name") or props.get("street") or props.get("formatted") or "Point of Interest"
                        cats = props.get("categories", [])
                        cats_str = " ".join(cats).lower()
                        
                        # Categorization
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
                        
                        category_counts[cat_label] = category_counts.get(cat_label, 0) + 1

                        dist = props.get("distance")
                        if dist is None:
                            dlat = math.radians(c_coords[1] - lat)
                            dlon = math.radians(c_coords[0] - lon)
                            a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(c_coords[1])) * math.sin(dlon / 2)**2
                            dist = 6371000 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

                        results.append({
                            "name": name,
                            "category": cat_label,
                            "distance_meters": round(dist, 1),
                            "latitude": c_coords[1],
                            "longitude": c_coords[0],
                            "address": props.get("address_line2") or props.get("formatted") or f"Near ({c_coords[1]:.4f}, {c_coords[0]:.4f})"
                        })

                    print(f"Geoapify Places Request URL: {url}")
                    print(f"Total Places Fetched: {len(results)} | Breakdown: {category_counts}")

                    if results:
                        return results
            except Exception as e:
                print(f"Geoapify Places error: {e}")

        return []
