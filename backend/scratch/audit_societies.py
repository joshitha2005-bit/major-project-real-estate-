import sqlite3

conn = sqlite3.connect("backend/real_estate.db")
c = conn.cursor()

c.execute("""
    SELECT society, locality, COUNT(*) 
    FROM properties 
    WHERE coordinate_quality = 'LOCALITY_APPROXIMATE' 
      AND society IS NOT NULL AND society != '' AND society != 'None'
    GROUP BY society, locality
    ORDER BY COUNT(*) DESC
    LIMIT 20
""")
print("Top 20 Societies in LOCALITY_APPROXIMATE properties:")
for r in c.fetchall():
    print(f"  Society: {r[0]:<25} | Locality: {r[1]:<25} | Count: {r[2]}")

# Also check anonymized codes vs genuine society names
c.execute("""
    SELECT society, COUNT(*) 
    FROM properties 
    WHERE society IS NOT NULL AND society != '' 
    GROUP BY society 
    ORDER BY COUNT(*) DESC 
    LIMIT 20
""")
print("\nTop Overall Societies in Database:")
for r in c.fetchall():
    print(f"  Society: {r[0]:<25} | Count: {r[1]}")

conn.close()
