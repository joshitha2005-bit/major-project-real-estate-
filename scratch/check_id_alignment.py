import sqlite3
import pandas as pd

df_master = pd.read_csv('backend/datasets/Bengaluru_Real_World_Property_Master.csv')
conn = sqlite3.connect('backend/real_estate.db')
cursor = conn.cursor()

# Check a sample of matching IDs
master_ids = set(df_master['property_id'])
cursor.execute("SELECT id, title, locality, price, area_sqft FROM properties LIMIT 10")
db_sample = cursor.fetchall()
print("Sample DB rows and if ID in master:")
for r in db_sample:
    print(f"DB ID {r[0]}: in master? {r[0] in master_ids} | title={r[1]} | loc={r[2]}")

# Check V21 rows
cursor.execute("SELECT id, title, locality, price, area_sqft FROM properties WHERE source_name='Real Estate Data V21.csv' LIMIT 10")
v21_db_sample = cursor.fetchall()
print("\nV21 DB sample rows and if ID in master:")
for r in v21_db_sample:
    in_master = r[0] in master_ids
    proj_in_master = ""
    if in_master:
        m_row = df_master[df_master['property_id'] == r[0]].iloc[0]
        proj_in_master = m_row['project_name']
    print(f"V21 DB ID {r[0]}: in master? {in_master} | master_proj={proj_in_master} | title={r[1]}")

conn.close()
