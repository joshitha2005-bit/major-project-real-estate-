import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.geoapify_service import GeoapifyService
from app.core.config import settings

TARGET_LOCATIONS = [
    {"name": "Koramangala", "lat": 12.9357, "lon": 77.6240},
    {"name": "HSR Layout", "lat": 12.9116, "lon": 77.6389},
    {"name": "Whitefield", "lat": 12.9696, "lon": 77.7497},
    {"name": "Electronic City", "lat": 12.8436, "lon": 77.6687},
    {"name": "Indiranagar", "lat": 12.9733, "lon": 77.6405}
]

async def verify_geoapify_places():
    print("=" * 80)
    print("VERIFYING LIVE GEOAPIFY PLACES API FOR TARGET BANGALORE LOCALITIES")
    print("=" * 80)
    
    categories = "education,healthcare,public_transport,catering,commercial,service.financial,leisure"

    for loc in TARGET_LOCATIONS:
        print(f"\n[TARGET LOCALITY] {loc['name'].upper()}")
        req_url = f"https://api.geoapify.com/v2/places?categories={categories}&filter=circle:{loc['lon']},{loc['lat']},5000&bias=proximity:{loc['lon']},{loc['lat']}&limit=50&apiKey={settings.GEOAPIFY_API_KEY[:6]}..."
        print(f"   [GEOAPIFY REQUEST URL] {req_url}")

        places = await GeoapifyService.get_nearby_places(loc["lat"], loc["lon"], 5000)
        
        assert len(places) > 0, f"FAILED: Geoapify Places returned 0 places for {loc['name']}!"

        cat_breakdown = {}
        for p in places:
            c = p['category']
            cat_breakdown[c] = cat_breakdown.get(c, 0) + 1

        print(f"   [TOTAL PLACES RETURNED] {len(places)} places")
        print("   [CATEGORY BREAKDOWN]:")
        for cat_name, cnt in sorted(cat_breakdown.items()):
            print(f"     - {cat_name:<20}: {cnt} places")

        print("   [SAMPLE PLACES DETAILS]:")
        for sample in places[:3]:
            dist_str = f"{sample['distance_meters']/1000:.2f} km" if sample['distance_meters'] > 1000 else f"{sample['distance_meters']} m"
            print(f"     * [{sample['category']}] {sample['name']}")
            print(f"       Distance: {dist_str} | Address: {sample['address']}")
            print(f"       Coordinates: ({sample['latitude']:.4f}, {sample['longitude']:.4f})")

    print("\n" + "=" * 80)
    print("ALL 5 LOCALITIES DISPLAY REAL LIVE GEOAPIFY NEARBY AMENITIES SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(verify_geoapify_places())
