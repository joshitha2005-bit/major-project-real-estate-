import shutil
import sqlite3
import json
import os

# Define newly generated images with their actual filenames
new_images = [
    # Apartments
    ("apartment_2", r"C:\Users\HP\.gemini\antigravity-ide\brain\92ed42e9-a9fe-4749-a526-18c17c3bd398\apartment_2_1787996404452.jpg"),
    ("apartment_3", r"C:\Users\HP\.gemini\antigravity-ide\brain\92ed42e9-a9fe-4749-a526-18c17c3bd398\apartment_3_1787996427151.jpg"),
    ("apartment_4", r"C:\Users\HP\.gemini\antigravity-ide\brain\92ed42e9-a9fe-4749-a526-18c17c3bd398\apartment_4_1787996453543.jpg"),
    ("apartment_5", r"C:\Users\HP\.gemini\antigravity-ide\brain\92ed42e9-a9fe-4749-a526-18c17c3bd398\apartment_5_1787996477327.jpg"),
    # Villas
    ("villa_2", r"C:\Users\HP\.gemini\antigravity-ide\brain\92ed42e9-a9fe-4749-a526-18c17c3bd398\villa_2_1787996504041.jpg"),
    ("villa_3", r"C:\Users\HP\.gemini\antigravity-ide\brain\92ed42e9-a9fe-4749-a526-18c17c3bd398\villa_3_1787996555900.jpg"),
    ("villa_4", r"C:\Users\HP\.gemini\antigravity-ide\brain\92ed42e9-a9fe-4749-a526-18c17c3bd398\villa_4_1787996586751.jpg"),
    ("villa_5", r"C:\Users\HP\.gemini\antigravity-ide\brain\92ed42e9-a9fe-4749-a526-18c17c3bd398\villa_5_1787996617163.jpg"),
    # Houses
    ("house_2", r"C:\Users\HP\.gemini\antigravity-ide\brain\92ed42e9-a9fe-4749-a526-18c17c3bd398\house_2_1787996650808.jpg"),
    ("house_3", r"C:\Users\HP\.gemini\antigravity-ide\brain\92ed42e9-a9fe-4749-a526-18c17c3bd398\house_3_1787996676996.jpg")
]

dest_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "images"))
os.makedirs(dest_dir, exist_ok=True)

# Copy newly generated images to the destination folder
for name, src_path in new_images:
    if os.path.exists(src_path):
        dest_path = os.path.join(dest_dir, f"{name}.jpg")
        shutil.copy2(src_path, dest_path)
        print(f"Copied {name} to {dest_path}")
    else:
        print(f"Warning: Source image {src_path} not found.")

# Databases to update
databases = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "real_estate.db")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "real_estate.db"))
]

for db_path in databases:
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}, skipping.")
        continue

    print(f"\nUpdating database with image pool: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query all properties to update them with modulo logic
    cursor.execute("SELECT id, property_type FROM properties")
    properties = cursor.fetchall()
    
    update_count = 0
    for pid, ptype in properties:
        ptype_lower = (ptype or "").lower()
        images = []
        if "apartment" in ptype_lower:
            img_idx = (pid % 5) + 1
            images = [f"/static/images/apartment_{img_idx}.jpg"]
        elif "villa" in ptype_lower:
            img_idx = (pid % 5) + 1
            images = [f"/static/images/villa_{img_idx}.jpg"]
        elif "house" in ptype_lower or "independent" in ptype_lower:
            img_idx = (pid % 3) + 1
            images = [f"/static/images/house_{img_idx}.jpg"]
        else:
            # Fallback to apartment modulo if unspecified
            img_idx = (pid % 5) + 1
            images = [f"/static/images/apartment_{img_idx}.jpg"]

        cursor.execute("UPDATE properties SET images = ? WHERE id = ?", (json.dumps(images), pid))
        update_count += 1

    conn.commit()
    conn.close()
    print(f"Updated {update_count} records in {os.path.basename(db_path)}")

print("\nSetup complete!")
