import sqlite3
import json

conn = sqlite3.connect('real_estate.db')
cursor = conn.cursor()

# A. Total property count
cursor.execute('SELECT COUNT(*) FROM properties')
total_count = cursor.fetchone()[0]

# I & J. Source distribution and source_type
cursor.execute('SELECT source, source_type, COUNT(*) FROM properties GROUP BY source, source_type')
sources = cursor.fetchall()

# B & C. Duplicates
cursor.execute('SELECT source_url, COUNT(*) FROM properties WHERE source_url IS NOT NULL AND source_url != "" GROUP BY source_url HAVING COUNT(*) > 1')
dup_urls = cursor.fetchall()

cursor.execute('SELECT title, locality, price, bhk, area_sqft, source, COUNT(*) FROM properties GROUP BY title, locality, price, bhk, area_sqft, source HAVING COUNT(*) > 1')
dup_exact_fields = cursor.fetchall()

cursor.execute('SELECT title, locality, price, bhk, area_sqft, COUNT(*) FROM properties GROUP BY title, locality, price, bhk, area_sqft HAVING COUNT(*) > 1')
dup_near_fields = cursor.fetchall()

# D. Suspicious / corrupted names
cursor.execute('SELECT id, title, source, locality FROM properties WHERE title LIKE "%Arsia%" OR title LIKE "%Oreldhi%" OR title LIKE "%SLiritn%" OR title LIKE "%—%" OR title LIKE "%BHK%" LIMIT 20')
suspicious_titles = cursor.fetchall()

# E. Images analysis
cursor.execute('SELECT id, title, images, source_type, source FROM properties WHERE images IS NOT NULL AND images != "[]" LIMIT 10')
sample_images_with_urls = cursor.fetchall()

cursor.execute('SELECT COUNT(*) FROM properties WHERE images IS NULL OR images = "[]"')
missing_images_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM properties WHERE images IS NOT NULL AND images != "[]"')
has_images_count = cursor.fetchone()[0]

# G. Contact info (phone & owner)
cursor.execute('SELECT owner_phone, COUNT(*) FROM properties GROUP BY owner_phone')
phone_dist = cursor.fetchall()

cursor.execute('SELECT owner_name, COUNT(*) FROM properties GROUP BY owner_name LIMIT 15')
owner_dist = cursor.fetchall()

# F. Coordinates
cursor.execute('SELECT COUNT(*) FROM properties WHERE latitude = 0 AND longitude = 0')
zero_coords = cursor.fetchone()[0]

print("=== DIAGNOSTIC REPORT ===")
print(f"A. Total Property Count: {total_count}")
print(f"I & J. Sources Distribution: {sources}")
print(f"B. Duplicate URLs Count: {len(dup_urls)}")
print(f"B & C. Duplicate Exact (Title+Loc+Price+BHK+Area+Source): {len(dup_exact_fields)}")
print(f"C. Near Duplicates (Title+Loc+Price+BHK+Area across sources): {len(dup_near_fields)}")
print(f"D. Suspicious/Corrupted Titles Count (sample): {len(suspicious_titles)}")
for st in suspicious_titles[:10]:
    print("   -", st)
print(f"E. Images: Has Images={has_images_count}, Missing Images={missing_images_count}")
print("   Sample images:", sample_images_with_urls[:3])
print(f"F. Zero Coordinates: {zero_coords}")
print(f"G. Phone Distribution: {phone_dist}")
print(f"G. Owner Name Samples: {owner_dist[:5]}")

conn.close()
