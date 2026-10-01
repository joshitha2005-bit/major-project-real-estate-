import sqlite3

conn = sqlite3.connect("real_estate.db")
c = conn.cursor()

for pid in [12716, 15748, 12816, 12907, 14713, 210, 85]:
    row = c.execute("SELECT id, title, property_name, building_name, project_name, locality, sub_locality, latitude, longitude, coordinate_confidence FROM properties WHERE id = ?", (pid,)).fetchone()
    print(row)

conn.close()
