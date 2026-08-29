import sqlite3
import json
import os
import hashlib

def get_image_index(pid, title, num_images):
    # Stable hash of title and pid
    h_str = f"{title}_{pid}"
    h = hashlib.md5(h_str.encode('utf-8')).hexdigest()
    return (int(h, 16) % num_images) + 1

# Databases to update
databases = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "real_estate.db")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "real_estate.db"))
]

for db_path in databases:
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}, skipping.")
        continue

    print(f"\nUpdating database with stable hash image distribution: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, property_type FROM properties")
    properties = cursor.fetchall()
    
    update_count = 0
    for pid, title, ptype in properties:
        ptype_lower = (ptype or "").lower()
        images = []
        if "apartment" in ptype_lower:
            img_idx = get_image_index(pid, title, 5)
            images = [f"/static/images/apartment_{img_idx}.jpg"]
        elif "villa" in ptype_lower:
            img_idx = get_image_index(pid, title, 5)
            images = [f"/static/images/villa_{img_idx}.jpg"]
        elif "house" in ptype_lower or "independent" in ptype_lower:
            img_idx = get_image_index(pid, title, 3)
            images = [f"/static/images/house_{img_idx}.jpg"]
        else:
            img_idx = get_image_index(pid, title, 5)
            images = [f"/static/images/apartment_{img_idx}.jpg"]

        cursor.execute("UPDATE properties SET images = ? WHERE id = ?", (json.dumps(images), pid))
        update_count += 1

    conn.commit()
    conn.close()
    print(f"Updated {update_count} records in {os.path.basename(db_path)}")

print("\nSetup complete!")
