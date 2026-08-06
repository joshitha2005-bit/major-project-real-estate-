import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.geoapify_service import GeoapifyService
from app.core.database import SessionLocal, engine, Base
from app.api.v1.location import get_locality_stats
from app.models.property import Property
from app.services.seed_service import SeedService

async def test_6_locations():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    SeedService.seed_properties(db)

    locations = ["Koramangala", "Electronic City", "Whitefield", "HSR Layout", "Chandapura", "JP Nagar"]

    print("=" * 70)
    print("VERIFYING COMPLETE REAL ESTATE AI PLATFORM FOR 6 TARGET LOCATIONS")
    print("=" * 70)

    for loc in locations:
        print(f"\n[LOCATION] TESTING LOCALITY: '{loc}'")
        
        # 1. Geoapify Geocoding API
        geo = await GeoapifyService.search_geocode(loc)
        if not geo:
            print("   [FAILED] Geocoding Failed!")
            continue
            
        print(f"   [OK] Address: {geo['formatted_address']}")
        print(f"   [OK] Lat/Lon: ({geo['latitude']:.4f}, {geo['longitude']:.4f})")
        
        # 2. Live Geoapify Places API
        places = await GeoapifyService.get_nearby_places(geo['latitude'], geo['longitude'], 5000)
        print(f"   [OK] Live Places Found: {len(places)} places")
        
        cats = {}
        for p in places:
            c = p['category']
            cats[c] = cats.get(c, 0) + 1
        for cat, cnt in cats.items():
            print(f"     - {cat}: {cnt}")

        # 3. DB Property Listings
        props = db.query(Property).filter(
            (Property.address.ilike(f"%{loc}%")) |
            (Property.title.ilike(f"%{loc}%"))
        ).all()
        print(f"   [OK] Locality Properties in DB: {len(props)} found")
        for p in props:
            print(f"     * [{p.property_type}] {p.title} - RS {int(p.price):,} (Owner: {p.owner_name}, Phone: {p.owner_phone})")

        # 4. Market Statistics
        stats = get_locality_stats(locality=loc, db=db)
        p_fmt = stats['avg_price_formatted'].replace('₹', 'RS ')
        r_fmt = stats['avg_rental_formatted'].replace('₹', 'RS ')
        print(f"   [OK] Market Stats: {stats['num_apartments']} Apts, {stats['num_villas']} Villas, {stats['num_independent_houses']} Houses, {stats['num_plots']} Plots | Avg Price: {p_fmt}, Rent: {r_fmt}")

    db.close()

if __name__ == "__main__":
    asyncio.run(test_6_locations())
