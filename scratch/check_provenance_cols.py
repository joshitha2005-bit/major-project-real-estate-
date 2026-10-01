import sqlite3

conn = sqlite3.connect(r"c:\major real estate\real_estate.db")
cursor = conn.cursor()

print("=== Properties source_name Breakdown ===")
cursor.execute("SELECT source_name, count(*) FROM properties GROUP BY source_name")
for r in cursor.fetchall():
    print(" ", r)

print("\n=== Properties source Breakdown ===")
cursor.execute("SELECT source, count(*) FROM properties GROUP BY source")
for r in cursor.fetchall():
    print(" ", r)

print("\n=== Properties listing_status Breakdown ===")
cursor.execute("SELECT listing_status, count(*) FROM properties GROUP BY listing_status")
for r in cursor.fetchall():
    print(" ", r)

print("\n=== Properties image_provenance Breakdown ===")
cursor.execute("SELECT image_provenance, count(*) FROM properties GROUP BY image_provenance")
for r in cursor.fetchall():
    print(" ", r)

print("\n=== PropPulse Direct / Owner listings in DB ===")
cursor.execute("SELECT id, title, locality, price_inr, area_sqft, source, source_name, listing_status, verification_status, owner_name, owner_phone FROM properties WHERE source = 'PropPulse Direct' OR source_name = 'PropPulse Direct'")
rows = cursor.fetchall()
print(f"Total count: {len(rows)}")
for r in rows:
    print(" ", r)

conn.close()
