import sqlite3

conn = sqlite3.connect('backend/real_estate.db')
c = conn.cursor()

c.execute("SELECT id, title, price, area_sqft, images FROM properties WHERE id IN (12127, 12081, 11949)")
rows = c.fetchall()
for r in rows:
    print(f"ID: {r[0]} | Title: {r[1]:<35} | Price: {r[2]} | Area: {r[3]} | Images: {r[4]}")

conn.close()
