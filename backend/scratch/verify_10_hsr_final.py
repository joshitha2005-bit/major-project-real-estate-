import os
import sys

sys.path.insert(0, os.path.abspath('.'))
from app.core.database import SessionLocal
from app.api.v1.properties import enrich_property_out
from app.models.property import Property

target_ids = [199, 352, 670, 688, 746, 760, 921, 935, 1171, 1195]
db = SessionLocal()
props = db.query(Property).filter(Property.id.in_(target_ids)).order_by(Property.id.asc()).all()

print("==================================================")
print("FINAL ACCEPTANCE TEST: 10 TARGET HSR PROPERTIES")
print("==================================================")
for p in props:
    enriched = enrich_property_out(p)
    p_fmt = (enriched.price_formatted or "").replace("₹", "RS ")
    print(f"ID {enriched.id:4d} | Title: '{enriched.title}' | Locality: '{enriched.locality}' | Price: {p_fmt} | Config: {enriched.bhk} BHK ({enriched.area_sqft} sqft)")

db.close()
