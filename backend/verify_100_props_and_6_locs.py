import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.geoapify_service import GeoapifyService
from app.core.database import SessionLocal, engine, Base
from app.api.v1.location import get_locality_stats
from app.models.property import Property
from app.services.seed_service import SeedService

async def test_100_props_and_6_locs():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    SeedService.seed_properties(db)

    total_db_props = db.query(Property).count()
    print("=" * 75)
    print(f"DATABASE VERIFICATION: {total_db_props} TOTAL PROPERTIES SEEDED IN DATABASE")
    print("=" * 75)

    test_localities = ["Koramangala", "Electronic City", "Whitefield", "HSR Layout", "JP Nagar", "Indiranagar"]

    for loc in test_localities:
        print(f"\n[TARGET LOCALITY] {loc.upper()}")
        
        # 1. Geoapify Geocoding API
        geo = await GeoapifyService.search_geocode(loc)
        if not geo:
            print("   [FAILED] Geocoding API error")
            continue
        print(f"   [OK] Address: {geo['formatted_address']}")
        print(f"   [OK] Coordinates: ({geo['latitude']:.4f}, {geo['longitude']:.4f})")

        # 2. Live Geoapify Places API
        places = await GeoapifyService.get_nearby_places(geo['latitude'], geo['longitude'], 5000)
        print(f"   [OK] Live Places Found: {len(places)} places")
        
        cats = {}
        for p in places:
            c = p['category']
            cats[c] = cats.get(c, 0) + 1
        for cat, cnt in cats.items():
            print(f"     - {cat}: {cnt}")

        # 3. Locality Specific Properties in DB
        props = db.query(Property).filter(
            (Property.address.ilike(f"%{loc}%")) |
            (Property.title.ilike(f"%{loc}%"))
        ).all()
        print(f"   [OK] DB Locality Properties ({len(props)} found):")
        for p in props:
            print(f"     * [{p.property_type}] {p.title} - RS {int(p.price):,} (Owner: {p.owner_name}, Phone: {p.owner_phone})")

        # 4. Market Statistics Breakdown
        stats = await get_locality_stats(locality=loc, db=db)
        p_fmt = stats['avg_price_formatted'].replace('₹', 'RS ')
        r_fmt = stats['avg_rental_formatted'].replace('₹', 'RS ')
        print(f"   [OK] Locality Market Stats: {stats['num_apartments']} Apts, {stats['num_villas']} Villas | Safety Score: {stats['safety_score']}/100 | Amenities Score: {stats['amenities_score']}/100 | Avg Price: {p_fmt}, Rent: {r_fmt}")

    db.close()

if __name__ == "__main__":
    asyncio.run(test_100_props_and_6_locs())
