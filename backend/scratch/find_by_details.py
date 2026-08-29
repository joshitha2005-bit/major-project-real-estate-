import sqlite3

conn = sqlite3.connect('backend/real_estate.db')
c = conn.cursor()

# Search for price 63.50 Lakh (6350000) or area 1128
print("Searching for first property:")
c.execute('SELECT id, title, price, area_sqft, property_type, images FROM properties WHERE price = 6350000 OR area_sqft = 1128')
for r in c.fetchall():
    print(f"ID: {r[0]} | Title: {r[1]} | Price: {r[2]} | Area: {r[3]} | Type: {r[4]} | Images: {r[5]}")

# Search for price 16.75 Lakh (1675000) or area 575
print("\nSearching for second property:")
c.execute('SELECT id, title, price, area_sqft, property_type, images FROM properties WHERE price = 1675000 OR area_sqft = 575')
for r in c.fetchall():
    print(f"ID: {r[0]} | Title: {r[1]} | Price: {r[2]} | Area: {r[3]} | Type: {r[4]} | Images: {r[5]}")

conn.close()
