import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.geoapify_service import GeoapifyService

async def test_locations():
    test_cases = ["Koramangala", "Electronic City", "Whitefield", "HSR Layout"]
    for q in test_cases:
        print(f"\n==========================================")
        print(f"SEARCHING: '{q}'")
        res = await GeoapifyService.search_geocode(q)
        if not res:
            print("FAILED Geocoding")
            continue
        print(f"SUCCESS Geocoding:")
        print(f"  - Address: {res['formatted_address']}")
        print(f"  - Latitude: {res['latitude']}")
        print(f"  - Longitude: {res['longitude']}")
        
        places = await GeoapifyService.get_nearby_places(res['latitude'], res['longitude'], 5000)
        print(f"SUCCESS Places API:")
        print(f"  - Total Nearby Places Found: {len(places)}")
        
        cats = {}
        for p in places:
            c = p['category']
            cats[c] = cats.get(c, 0) + 1
        for cat, cnt in cats.items():
            print(f"    * {cat}: {cnt}")

if __name__ == "__main__":
    asyncio.run(test_locations())
