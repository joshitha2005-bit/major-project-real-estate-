import sqlite3
import pandas as pd

conn = sqlite3.connect("real_estate.db")
c = conn.cursor()

c.execute("SELECT locality, COUNT(*) as cnt FROM properties GROUP BY locality ORDER BY cnt DESC")
locs = c.fetchall()
print(f"Total unique localities: {len(locs)}")
print("\nTop 50 localities:")
for l in locs[:50]:
    print(f"  {l[0]}: {l[1]}")

conn.close()
