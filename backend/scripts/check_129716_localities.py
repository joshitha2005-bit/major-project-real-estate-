import sqlite3
from collections import Counter

conn = sqlite3.connect("real_estate.db")
c = conn.cursor()

c.execute("SELECT locality, COUNT(*) FROM properties WHERE round(latitude, 4) = 12.9716 AND round(longitude, 4) = 77.5946 GROUP BY locality ORDER BY COUNT(*) DESC")
rows = c.fetchall()

print(f"Total distinct localities mapped to (12.9716, 77.5946): {len(rows)}")
print("\nTop 30 localities mapped to (12.9716, 77.5946):")
for r in rows[:30]:
    print(f"  {r[0]}: {r[1]} properties")

conn.close()
