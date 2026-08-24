import csv
import sqlite3
import json
import os
import sys

sys.path.insert(0, os.path.abspath('.'))
from app.core.database import SessionLocal
from app.api.v1.properties import enrich_property_out, is_anonymized_code
from app.models.property import Property

target_ids = [199, 352, 670, 688, 746, 760, 921, 935, 1171, 1195]

csv_path = os.path.abspath('datasets/Bengaluru_House_Data.csv')
db_path = os.path.abspath('real_estate.db')

# 1. Read CSV rows matching HSR
hsr_csv_all = []
if os.path.exists(csv_path):
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            loc = (row.get('location') or '').strip()
            if 'hsr' in loc.lower():
                hsr_csv_all.append(row)

# 2. Query DB properties for the 10 target IDs
db = SessionLocal()
db_props = db.query(Property).filter(Property.id.in_(target_ids)).order_by(Property.id.asc()).all()

print("==================================================")
print("EXACT MAPPING: CSV -> DATABASE -> API RESPONSE")
print("==================================================")
for p in db_props:
    enriched = enrich_property_out(p)
    print(f"PROPERTY ID: {p.id}")
    print(f"  - DB Raw Title   : '{p.title}'")
    print(f"  - DB Locality    : '{p.locality}'")
    print(f"  - DB Address     : '{p.address}'")
    print(f"  - DB PropertyType: '{p.property_type}'")
    print(f"  - DB Config      : {p.bhk} BHK | {p.area_sqft} sqft | Bath={p.bathrooms} | Balcony={p.balconies}")
    print(f"  - DB Price       : RS {p.price:,.0f}")
    print(f"  - Current API Title    : '{enriched.title}'")
    print(f"  - Current API Locality : '{enriched.locality}'")
    print("-" * 80)

db.close()
