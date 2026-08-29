import sqlite3

conn = sqlite3.connect('backend/real_estate.db')
c = conn.cursor()

c.execute('SELECT id, title, property_type, images FROM properties WHERE locality = ? LIMIT 10', ('Electronic City',))
rows = c.fetchall()
for r in rows:
    print(f"ID: {r[0]} | Title: {r[1]:<45} | Type: {r[2]} | Images: {r[3]}")

conn.close()
