import csv
import sqlite3
import json
import os
import sys

sys.path.insert(0, os.path.abspath('.'))
from app.core.database import SessionLocal
from app.api.v1.properties import enrich_property_out
from app.models.property import Property

db = SessionLocal()

# Fetch DB properties matching HSR Layout
db_props = db.query(Property).filter(Property.locality.ilike("%hsr%")).order_by(Property.id.asc()).limit(20).all()

print("==================================================")
print("SIDE-BY-SIDE COMPARISON: DB RAW vs API ENRICHED")
print("==================================================")
for p in db_props:
    enriched = enrich_property_out(p)
    print(f"DB ID: {p.id}")
    print(f"  - DB Raw Title : '{p.title}'")
    print(f"  - API Title    : '{enriched.title}'")
    print(f"  - Locality     : '{p.locality}'")
    print(f"  - BHK / Area   : {p.bhk} BHK | {p.area_sqft} sqft | {p.property_type}")
    print(f"  - Price        : RS {p.price:,}")
    print(f"  - Source       : {p.source} ({p.source_type})")
    print(f"  - Images       : DB={p.images} | API={enriched.images}")
    print("-" * 80)

db.close()
