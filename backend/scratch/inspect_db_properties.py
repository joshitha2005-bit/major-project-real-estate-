import sqlite3
import json

db_path = 'backend/real_estate.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get property types and image counts
cursor.execute('''
    SELECT property_type, COUNT(*), 
           COUNT(CASE WHEN images IS NOT NULL AND images != '[]' THEN 1 END) 
    FROM properties 
    GROUP BY property_type
''')
print("Property Types Summary:")
for ptype, total, has_img in cursor.fetchall():
    print(f"  Property Type: {ptype:<20} | Total: {total:<5} | Has Images: {has_img:<5}")

# Get count by source_type
cursor.execute('''
    SELECT source_type, COUNT(*),
           COUNT(CASE WHEN images IS NOT NULL AND images != '[]' THEN 1 END)
    FROM properties
    GROUP BY source_type
''')
print("\nSource Types Summary:")
for stype, total, has_img in cursor.fetchall():
    print(f"  Source Type: {stype:<25} | Total: {total:<5} | Has Images: {has_img:<5}")

conn.close()
