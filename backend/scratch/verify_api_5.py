import sys, os
sys.path.insert(0, os.path.abspath('.'))

from app.core.database import SessionLocal
from app.api.v1.properties import enrich_property_out
from app.models.property import Property

db = SessionLocal()
sample_ids = [12497, 12496, 12495, 12494, 12493]

print("VERIFYING 5 SAMPLE PROPERTY IDS END-TO-END VIA API SERIALIZER:")
print("=" * 120)
for pid in sample_ids:
    p = db.query(Property).filter(Property.id == pid).first()
    enriched = enrich_property_out(p)
    p_fmt = (enriched.price_formatted or "").replace("₹", "RS ")
    print(f"API Property ID: {enriched.id}")
    print(f"  - Title       : {enriched.title}")
    print(f"  - Locality    : {enriched.locality}")
    print(f"  - Price       : RS {enriched.price} ({p_fmt})")
    print(f"  - Config      : {enriched.bhk} BHK | {enriched.property_type} | {enriched.area_sqft} sqft")
    print(f"  - Coordinates : ({enriched.latitude}, {enriched.longitude}) -> Status: {enriched.coordinate_status}")
    print(f"  - Source      : {enriched.source} ({enriched.source_type})")
    print(f"  - Images List : {enriched.images}")
    print(f"  - Phone       : {enriched.phone}")
    print("-" * 120)

db.close()
