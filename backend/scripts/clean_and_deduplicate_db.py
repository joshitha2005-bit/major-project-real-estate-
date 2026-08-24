import sqlite3
import json
import os

db_path = os.path.abspath('real_estate.db')
print(f"Connecting to database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Count before
cursor.execute('SELECT COUNT(*) FROM properties')
count_before = cursor.fetchone()[0]

# 2. Identify and remove exact duplicates (title + locality + price + bhk + area_sqft + source)
cursor.execute('''
    SELECT LOWER(title), LOWER(locality), price, bhk, area_sqft, source, GROUP_CONCAT(id)
    FROM properties
    GROUP BY LOWER(title), LOWER(locality), price, bhk, area_sqft, source
    HAVING COUNT(*) > 1
''')
dup_groups = cursor.fetchall()

removed_ids = []
for group in dup_groups:
    ids = [int(i) for i in group[6].split(',')]
    ids.sort()
    keep_id = ids[0]
    delete_ids = ids[1:]
    removed_ids.extend(delete_ids)

if removed_ids:
    placeholders = ','.join('?' for _ in removed_ids)
    cursor.execute(f'DELETE FROM properties WHERE id IN ({placeholders})', removed_ids)

# 3. Clear synthetic seeded image pools for non-user uploaded properties
cursor.execute('SELECT id, images FROM properties WHERE source != "owner_listing"')
rows = cursor.fetchall()
cleared_images_count = 0
for pid, imgs_str in rows:
    if imgs_str and imgs_str != "[]":
        try:
            imgs = json.loads(imgs_str)
            # If images contain unsplash seed links, clear to empty list
            if any("unsplash.com" in img for img in imgs):
                cursor.execute('UPDATE properties SET images = "[]" WHERE id = ?', (pid,))
                cleared_images_count += 1
        except Exception:
            cursor.execute('UPDATE properties SET images = "[]" WHERE id = ?', (pid,))
            cleared_images_count += 1

# 4. Clear synthetic seeded phone numbers
SEED_PHONES = ["+91 98860 12345", "+91 98450 67890", "+91 99001 88345", "+91 98110 99887", "+91 98801 33456", "+91 97400 22341", "+91 98440 66789", "+91 98866 55432", "+91 98451 77654", "+91 98800 33210"]
cleared_phones_count = 0

cursor.execute('SELECT id, owner_phone, phone FROM properties WHERE source_type != "owner_listing"')
phone_rows = cursor.fetchall()
for pid, ophone, phone in phone_rows:
    if ophone in SEED_PHONES or phone in SEED_PHONES or not ophone or ophone.strip() == "":
        cursor.execute('UPDATE properties SET owner_phone = "Contact information unavailable", phone = "Contact information unavailable" WHERE id = ?', (pid,))
        cleared_phones_count += 1

conn.commit()

# 5. Count after
cursor.execute('SELECT COUNT(*) FROM properties')
count_after = cursor.fetchone()[0]

print("==================================================")
print("DATABASE CLEANUP & DEDUPLICATION SUMMARY")
print("==================================================")
print(f"Total Property Count Before : {count_before}")
print(f"Exact Duplicate Groups Found: {len(dup_groups)}")
print(f"Total Duplicate Rows Removed: {len(removed_ids)}")
print(f"Total Property Count After  : {count_after}")
print(f"Synthetic Images Cleared    : {cleared_images_count}")
print(f"Synthetic Phones Cleared    : {cleared_phones_count}")
print("==================================================")

conn.close()
