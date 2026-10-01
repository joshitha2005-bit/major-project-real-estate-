import sqlite3

con = sqlite3.connect('backend/real_estate.db')
cur = con.cursor()

cur.execute("SELECT id, title FROM properties WHERE title LIKE '%\u2014%' LIMIT 10")
rows = cur.fetchall()
print(f"Sample titles with em-dash: {len(rows)}")
for r in rows[:5]:
    fixed = r[1].replace('\u2014', '').replace('\u2013', '').strip()
    print("Original:", repr(r[1][:30]), "-> Fixed:", repr(fixed))

cur.execute("SELECT COUNT(*) FROM properties WHERE title LIKE '%\u2014%'")
cnt = cur.fetchone()[0]
print(f"Total titles with em-dash: {cnt}")

con.close()
