import sqlite3
import json

conn = sqlite3.connect(r"c:\major real estate\real_estate.db")
cursor = conn.cursor()

# Check property sources breakdown
cursor.execute("SELECT listing_source, count(*) FROM properties GROUP BY listing_source")
sources = cursor.fetchall()
print("Listing Sources Breakdown:", sources)

# Check images table
cursor.execute("SELECT count(*) FROM property_images")
img_count = cursor.fetchone()[0]
print("Total property_images count:", img_count)

# Check direct listings details
cursor.execute("SELECT id, title, locality, price_inr, area_sqft, listing_source, verification_status, created_at, owner_name, owner_phone FROM properties WHERE listing_source = 'PROPPULSE_DIRECT'")
direct_listings = cursor.fetchall()
print("\nPropPulse Direct Listings (14 records):")
for d in direct_listings:
    print(d)

# Check image records details if any
cursor.execute("SELECT * FROM property_images LIMIT 10")
imgs = cursor.fetchall()
print("\nProperty images sample:", imgs)

conn.close()
