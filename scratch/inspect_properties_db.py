import sqlite3

conn = sqlite3.connect(r"c:\major real estate\real_estate.db")
cursor = conn.cursor()

print("=== Properties Source Type Breakdown ===")
cursor.execute("SELECT source_type, count(*) FROM properties GROUP BY source_type")
for r in cursor.fetchall():
    print(" ", r)

print("\n=== Properties Verification Status Breakdown ===")
cursor.execute("SELECT verification_status, count(*) FROM properties GROUP BY verification_status")
for r in cursor.fetchall():
    print(" ", r)

print("\n=== Property Images Count ===")
cursor.execute("SELECT count(*) FROM property_images")
print("Total property_images rows:", cursor.fetchone()[0])

print("\n=== PropPulse Direct Listings Sample (14 records) ===")
cursor.execute("SELECT id, title, locality, price_inr, area_sqft, source_type, verification_status, created_at, owner_name, owner_phone, seller_name, phone FROM properties WHERE source_type = 'PROPPULSE_DIRECT'")
for d in cursor.fetchall():
    print(d)

print("\n=== Demo Test Listings Sample (100 records) ===")
cursor.execute("SELECT id, title, locality, price_inr, area_sqft, source_type, verification_status FROM properties WHERE source_type = 'DEMO_TEST' LIMIT 5")
for d in cursor.fetchall():
    print(d)

conn.close()
