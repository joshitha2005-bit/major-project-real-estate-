import csv
import sqlite3
import json
import os
import re

csv_path = os.path.abspath('datasets/Bengaluru_House_Data.csv')
db_path = os.path.abspath('real_estate.db')
bak_path = os.path.abspath('real_estate.db.bak')

print("==================================================")
print("STEP 1: INSPECTING ORIGINAL CSV")
print("==================================================")
hsr_csv_rows = []
if os.path.exists(csv_path):
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            loc = (row.get('location') or '').strip()
            if 'hsr' in loc.lower():
                hsr_csv_rows.append(row)

print(f"Total matching CSV rows for 'HSR': {len(hsr_csv_rows)}")

# Sample 10 CSV rows
print("\nSample 10 Original CSV Records:")
for idx, r in enumerate(hsr_csv_rows[:10]):
    print(f"  {idx+1}. Location='{r.get('location')}' | Society='{r.get('society')}' | Size='{r.get('size')}' | Sqft='{r.get('total_sqft')}' | Bath='{r.get('bath')}' | Price='{r.get('price')}'")

print("\n==================================================")
print("STEP 2: INSPECTING CURRENT DATABASE")
print("==================================================")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT id, title, locality, property_type, bhk, area_sqft, price, images, source, source_type FROM properties WHERE LOWER(locality) LIKE "%hsr%"')
db_hsr_props = cursor.fetchall()
print(f"Total Database properties matching 'HSR': {len(db_hsr_props)}")

print("\nSample 10 Current DB Records:")
for p in db_hsr_props[:10]:
    pid, title, loc, ptype, bhk, area, price, imgs, src, stype = p
    print(f"  ID {pid}: Title='{title}' | Locality='{loc}' | {bhk}BHK {ptype} {area}sqft | Price=RS {price} | Source='{src}'")

conn.close()

print("\n==================================================")
print("STEP 2B: CHECKING BACKUP DATABASE BEFORE CLEANUP")
print("==================================================")
if os.path.exists(bak_path):
    conn_bak = sqlite3.connect(bak_path)
    cursor_bak = conn_bak.cursor()
    cursor_bak.execute('SELECT COUNT(*) FROM properties WHERE LOWER(locality) LIKE "%hsr%"')
    bak_count = cursor_bak.fetchone()[0]
    print(f"Total Backup DB properties matching 'HSR': {bak_count}")
    
    cursor_bak.execute('SELECT id, title, locality, price, bhk, area_sqft FROM properties WHERE LOWER(locality) LIKE "%hsr%" LIMIT 5')
    bak_samples = cursor_bak.fetchall()
    print("Sample 5 Backup DB Records:")
    for b in bak_samples:
        print(f"  ID {b[0]}: Title='{b[1]}' | Locality='{b[2]}' | Price={b[3]} | {b[4]}BHK {b[5]}sqft")
    conn_bak.close()

