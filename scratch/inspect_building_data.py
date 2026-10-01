import sqlite3
import json

con = sqlite3.connect('backend/real_estate.db')
cur = con.cursor()

cur.execute("""
    SELECT 
        COUNT(*), 
        COUNT(CASE WHEN society IS NOT NULL AND society != '' THEN 1 END),
        COUNT(CASE WHEN sub_locality IS NOT NULL AND sub_locality != '' THEN 1 END),
        COUNT(CASE WHEN coordinate_quality = 'EXACT' THEN 1 END),
        COUNT(CASE WHEN coordinate_quality = 'LOCALITY_APPROXIMATE' THEN 1 END)
    FROM properties
""")
stats = cur.fetchone()
print(f"Total: {stats[0]}, With Society: {stats[1]}, With Sub-locality: {stats[2]}, EXACT coords: {stats[3]}, APPROX coords: {stats[4]}")

print("\n--- Samples with Society ---")
cur.execute("""
    SELECT id, title, society, sub_locality, locality, address, coordinate_quality, latitude, longitude 
    FROM properties 
    WHERE society IS NOT NULL AND society != '' AND society != 'None'
    LIMIT 5
""")
for r in cur.fetchall():
    print(r)

print("\n--- Samples from other sources / general ---")
cur.execute("""
    SELECT id, title, society, sub_locality, locality, address, coordinate_quality, latitude, longitude, source_name
    FROM properties 
    LIMIT 5
""")
for r in cur.fetchall():
    print(r)

print("\n--- Check distinct source names ---")
cur.execute("SELECT source_name, count(*) FROM properties GROUP BY source_name")
for r in cur.fetchall():
    print(r)

con.close()
