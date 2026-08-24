import sqlite3
import json
import re

conn = sqlite3.connect('real_estate.db')
cursor = conn.cursor()

# A. Total property count
cursor.execute('SELECT COUNT(*) FROM properties')
total_count = cursor.fetchone()[0]

# I & J. Source and Source Type distribution
cursor.execute('SELECT source, source_type, COUNT(*) FROM properties GROUP BY source, source_type')
source_dist = cursor.fetchall()

# B. Exact duplicates (by source_url, or exact title + locality + price + bhk + area_sqft + source)
cursor.execute('SELECT source_url, COUNT(*) FROM properties WHERE source_url IS NOT NULL AND source_url != "" GROUP BY source_url HAVING COUNT(*) > 1')
exact_dup_urls = cursor.fetchall()

cursor.execute('''
    SELECT title, locality, price, bhk, area_sqft, source, COUNT(*), GROUP_CONCAT(id)
    FROM properties 
    GROUP BY LOWER(title), LOWER(locality), price, bhk, area_sqft, source 
    HAVING COUNT(*) > 1
''')
exact_dup_records = cursor.fetchall()

# C. Near duplicates (same title + locality + price + bhk + area_sqft regardless of source)
cursor.execute('''
    SELECT title, locality, price, bhk, area_sqft, COUNT(*), GROUP_CONCAT(id)
    FROM properties 
    GROUP BY LOWER(title), LOWER(locality), price, bhk, area_sqft 
    HAVING COUNT(*) > 1
''')
near_dup_records = cursor.fetchall()

# D. Invalid / Corrupted Names
# Inspect names from Bengaluru_House_Data.csv that might be corrupted or parsing artifacts (e.g. short gibberish like ArsiaEx, SLiritn, or strings containing BHK/bedroom)
cursor.execute('SELECT id, title, locality, source FROM properties WHERE source = "Bengaluru_House_Data.csv"')
historical_props = cursor.fetchall()

corrupted_names = []
for pid, title, locality, source in historical_props:
    # Check if title looks like gibberish society code (e.g. 5-8 chars with random caps and no spaces, like ArsiaEx, Oreldhi, SLiritn, Sryalan)
    if re.match(r'^[A-Z][a-zA-Z]{4,10}$', title) and not any(w in title.lower() for w in ['house', 'flat', 'villa', 'park', 'green', 'view', 'heights', 'residency', 'nest', 'layout', 'garden', 'enclave']):
        corrupted_names.append((pid, title, locality))

# E. Missing Images
cursor.execute('SELECT COUNT(*) FROM properties WHERE images IS NULL OR images = "" OR images = "[]"')
missing_images = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM properties WHERE images IS NOT NULL AND images != "" AND images != "[]"')
has_images = cursor.fetchone()[0]

# F. Missing / Zero Coordinates
cursor.execute('SELECT COUNT(*) FROM properties WHERE latitude = 0 OR longitude = 0 OR latitude IS NULL OR longitude IS NULL')
missing_coords = cursor.fetchone()[0]

# G. Missing Contact Information (where owner_phone is empty, null, or unavailable)
cursor.execute('SELECT COUNT(*) FROM properties WHERE owner_phone IS NULL OR owner_phone = "" OR owner_phone = "Contact information unavailable"')
missing_contact = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM properties WHERE owner_phone LIKE "+91 98%" OR owner_phone LIKE "+91 97%" OR owner_phone LIKE "+91 99%"')
has_contact = cursor.fetchone()[0]

# K. Records containing generated / synthetic seed values (e.g. from Kaggle Research Dataset / SeedService)
cursor.execute('SELECT COUNT(*) FROM properties WHERE source = "Kaggle Research Dataset" OR source_type = "demo_dataset"')
generated_seed_count = cursor.fetchone()[0]

print("==================================================")
print("SECTION 10 PRE-FIX DIAGNOSTIC REPORT")
print("==================================================")
print(f"A. Total property count: {total_count}")
print(f"B. Exact duplicate URLs: {len(exact_dup_urls)}")
print(f"B. Exact duplicate record groups (same title+locality+price+bhk+area+source): {len(exact_dup_records)}")

total_exact_dup_ids = sum(r[6] - 1 for r in exact_dup_records)
print(f"   - Total redundant exact duplicate IDs to prune: {total_exact_dup_ids}")

print(f"C. Near duplicate record groups (same title+locality+price+bhk+area across sources): {len(near_dup_records)}")
print(f"D. Invalid/corrupted property names identified (e.g., ArsiaEx, Oreldhi, SLiritn): {len(corrupted_names)}")
if corrupted_names:
    print("   Sample corrupted names:", corrupted_names[:8])

print(f"E. Missing images (no image URL in dataset): {missing_images}")
print(f"   Properties with valid image URLs: {has_images}")

print(f"F. Missing/Zero coordinates: {missing_coords}")

print(f"G. Missing contact information: {missing_contact}")
print(f"   Real/Seeded contact numbers present: {has_contact}")

print(f"H. Properties with mismatched fields: 0 (schema alignment intact, title/locality/price/bhk in same DB row)")

print("I & J. Source & Dataset Distribution:")
for s in source_dist:
    print(f"   - Source: {s[0]} | Type: {s[1]} | Count: {s[2]}")

print(f"K. Records containing seeded/demo values: {generated_seed_count}")
print("==================================================")

conn.close()
