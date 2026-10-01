import sqlite3

conn = sqlite3.connect("real_estate.db")
c = conn.cursor()

print("--- DEVANAHALLI PROPERTIES ---")
devs = c.execute("SELECT id, title, property_name, locality, sub_locality, latitude, longitude, coordinate_confidence FROM properties WHERE locality LIKE '%Devanahalli%' LIMIT 10").fetchall()
for d in devs:
    print(d)

print("\n--- MALLESHWARAM PROPERTIES ---")
mals = c.execute("SELECT id, title, property_name, locality, sub_locality, latitude, longitude, coordinate_confidence FROM properties WHERE locality LIKE '%Malleshwaram%' OR sub_locality LIKE '%Malleshwaram%' LIMIT 10").fetchall()
for m in mals:
    print(m)

conn.close()
