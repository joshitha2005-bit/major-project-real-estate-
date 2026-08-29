import sqlite3
import json
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
img_base_dir = os.path.join(backend_dir, "static", "property-images")

# Map available local images by category
category_files = {}
categories = ["apartments", "villas", "houses", "penthouses", "plots"]

for cat in categories:
    cat_path = os.path.join(img_base_dir, cat)
    if os.path.exists(cat_path):
        files = sorted([f for f in os.listdir(cat_path) if f.endswith(".jpg") or f.endswith(".png")])
        # Use web-accessible relative paths (/static/property-images/category/filename)
        category_files[cat] = [f"/static/property-images/{cat}/{f}" for f in files]
    else:
        category_files[cat] = []

print("Loaded local image counts by category:")
for cat, files in category_files.items():
    print(f"  - {cat}: {len(files)} local images")

# Fallback mapping from DB property_type to directory category
def get_category_key(ptype: str, title: str = "") -> str:
    ptype_lower = (ptype or "").lower()
    title_lower = (title or "").lower()
    
    if "villa" in ptype_lower or "villa" in title_lower:
        return "villas"
    elif "penthouse" in ptype_lower or "penthouse" in title_lower:
        return "penthouses"
    elif "house" in ptype_lower or "independent" in ptype_lower or "bedroom" in title_lower:
        return "houses"
    elif "plot" in ptype_lower or "land" in ptype_lower or "layout" in title_lower:
        return "plots"
    else:
        return "apartments"

databases = [
    os.path.join(backend_dir, "real_estate.db"),
    os.path.abspath(os.path.join(backend_dir, "..", "real_estate.db"))
]

for db_path in databases:
    if not os.path.exists(db_path):
        continue

    print(f"\nProcessing database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(properties)")
    cols = [c[1] for c in cursor.fetchall()]
    has_title = "title" in cols

    if has_title:
        cursor.execute("SELECT id, title, property_type FROM properties")
    else:
        cursor.execute("SELECT id, '', property_type FROM properties")
        
    records = cursor.fetchall()
    updated = 0

    for pid, title, ptype in records:
        title_str = title or ""
        cat_key = get_category_key(ptype, title_str)
        pool = category_files.get(cat_key, category_files["apartments"])
        
        if not pool:
            pool = category_files["apartments"]

        # Check for famous builder matching
        images_list = []
        if "prestige" in title_str.lower():
            images_list.append("/static/images/original_prestige.jpg")
        elif "sobha" in title_str.lower():
            images_list.append("/static/images/original_sobha.jpg")
        elif "l&t" in title_str.lower() or "rejuve" in title_str.lower():
            images_list.append("/static/images/original_lnt.jpg")

        # Deterministically select 3-4 images from the category pool using hashing
        base_idx = (pid * 13 + abs(hash(title_str))) % len(pool)
        for offset in range(4):
            img_url = pool[(base_idx + offset * 3) % len(pool)]
            if img_url not in images_list:
                images_list.append(img_url)

        cursor.execute("UPDATE properties SET images = ? WHERE id = ?", (json.dumps(images_list[:4]), pid))
        updated += 1

    conn.commit()
    conn.close()
    print(f"Updated {updated} property records in {os.path.basename(db_path)}")

print("\nDatabase image mapping complete!")
