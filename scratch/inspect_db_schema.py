import sqlite3

conn = sqlite3.connect(r"c:\major real estate\real_estate.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:", tables)

for t in tables:
    tname = t[0]
    cursor.execute(f"PRAGMA table_info({tname});")
    cols = cursor.fetchall()
    print(f"\nColumns of table '{tname}':")
    for c in cols:
        print(" ", c[1], c[2])

conn.close()
