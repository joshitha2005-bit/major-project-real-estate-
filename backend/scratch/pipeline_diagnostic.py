import sqlite3
import json
import os

db_path = os.path.abspath('real_estate.db')
print(f"A. Active Database File: {db_path} (Size: {os.path.getsize(db_path)} bytes)")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# B. Active property source distribution
cursor.execute('SELECT source, source_type, COUNT(*) FROM properties GROUP BY source, source_type')
sources = cursor.fetchall()
print("\nB. Active Property Sources in Database:")
for s in sources:
    print(f"   - Source: '{s[0]}' | Source Type: '{s[1]}' | Record Count: {s[2]}")

# Pick 5 actual property IDs from default /properties page (order by created_at desc or id asc)
cursor.execute('SELECT id, title, locality, price, bhk, area_sqft, property_type, latitude, longitude, images, owner_name, owner_phone, source, source_type FROM properties ORDER BY created_at DESC LIMIT 5')
sample_5 = cursor.fetchall()

print("\nC & 4. Sampling 5 Properties from /properties endpoint pipeline:")
print("=" * 120)
for p in sample_5:
    pid, title, locality, price, bhk, area, ptype, lat, lon, imgs, owner, phone, src, stype = p
    imgs_list = json.loads(imgs) if imgs else []
    print(f"Property ID: {pid}")
    print(f"  - Title       : {title}")
    print(f"  - Locality    : {locality}")
    print(f"  - Price       : RS {price:,.2f}")
    print(f"  - Config      : {bhk} BHK | {ptype} | {area} sqft")
    print(f"  - Coordinates : ({lat}, {lon})")
    print(f"  - Source      : {src} ({stype})")
    print(f"  - Raw Images  : {imgs_list}")
    print(f"  - Owner/Phone : {owner} / {phone}")
    print("-" * 120)

# 5. Root cause of bad names like ArsiaEx, Oreldhi, SLiritn, Soiewre, DuenaTa
cursor.execute('SELECT id, title, locality, source FROM properties WHERE title IN ("ArsiaEx", "Oreldhi", "SLiritn", "Soiewre", "DuenaTa", "Coomee", "Theanmp", "Sryalan") OR title LIKE "%Arsia%" LIMIT 10')
bad_names_sample = cursor.fetchall()
print("\n5. Bad Property Name Samples:")
for bn in bad_names_sample:
    print(f"   ID {bn[0]}: Title='{bn[1]}', Locality='{bn[2]}', Source='{bn[3]}'")

# 7. Find Duplicate Records with exact details
cursor.execute('''
    SELECT GROUP_CONCAT(id), title, locality, price, bhk, area_sqft, source, source_url, COUNT(*)
    FROM properties
    GROUP BY LOWER(title), LOWER(locality), price, bhk, area_sqft, source
    HAVING COUNT(*) > 1
''')
exact_duplicates = cursor.fetchall()
print(f"\n7. Duplicate Record Diagnostic Report ({len(exact_duplicates)} duplicate groups found):")
for dup in exact_duplicates:
    ids, title, loc, price, bhk, area, src, url, count = dup
    print(f"   - Group (Count {count}): IDs=[{ids}] | Title='{title}' | Locality='{loc}' | Price=RS {price:,.0f} | {bhk}BHK {area}sqft | Source='{src}' | URL='{url}'")

conn.close()
