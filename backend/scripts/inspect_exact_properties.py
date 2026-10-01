import sqlite3
import pandas as pd

conn = sqlite3.connect("real_estate.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT id, title, property_name, building_name, project_name, sub_locality, locality,
           formatted_address, latitude, longitude, coordinate_confidence, identity_confidence,
           source, location_source
    FROM properties
    WHERE coordinate_confidence = 'EXACT'
    ORDER BY id ASC
""")
rows = cursor.fetchall()
df = pd.DataFrame([dict(r) for r in rows])
print(f"Total EXACT properties: {len(df)}")
for idx, r in df.iterrows():
    name = r["property_name"] or r["building_name"] or r["title"]
    print(f"ID {r['id']:5d} | {name[:35]:35s} | Loc: {str(r['locality'])[:20]:20s} | Sub: {str(r['sub_locality'])[:15]:15s} | Coords: ({r['latitude']:.5f}, {r['longitude']:.5f}) | LocSrc: {r['location_source']}")

conn.close()
