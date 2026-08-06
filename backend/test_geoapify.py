import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.geoapify_service import GeoapifyService

async def main():
    print(f"Loaded GEOAPIFY_API_KEY: {settings.GEOAPIFY_API_KEY[:8]}...")
    
    # 1. Geocode Koramangala
    k_res = await GeoapifyService.search_geocode("Koramangala")
    print(f"\n1. Koramangala Geocoding Success:")
    print(f"   Address: {k_res['formatted_address']}")
    print(f"   Coordinates: ({k_res['latitude']}, {k_res['longitude']})")
    
    # 2. Geocode Electronic City
    e_res = await GeoapifyService.search_geocode("Electronic City")
    print(f"\n2. Electronic City Geocoding Success:")
    print(f"   Address: {e_res['formatted_address']}")
    print(f"   Coordinates: ({e_res['latitude']}, {e_res['longitude']})")
    
    # 3. Places API around Koramangala
    places = await GeoapifyService.get_nearby_places(k_res['latitude'], k_res['longitude'], 3000)
    print(f"\n3. Live Geoapify Places API Success:")
    print(f"   Total nearby amenities returned: {len(places)}")
    for p in places[:5]:
        print(f"   - [{p['category']}] {p['name']} ({p['distance_meters']}m away)")

if __name__ == "__main__":
    asyncio.run(main())
