import shutil
import sqlite3
import json
import os

# Define source image paths from the artifact directory
src_apartment = r"C:\Users\HP\.gemini\antigravity-ide\brain\92ed42e9-a9fe-4749-a526-18c17c3bd398\apartment_1_1787995192976.jpg"
src_villa = r"C:\Users\HP\.gemini\antigravity-ide\brain\92ed42e9-a9fe-4749-a526-18c17c3bd398\villa_1_1787995208702.jpg"
src_house = r"C:\Users\HP\.gemini\antigravity-ide\brain\92ed42e9-a9fe-4749-a526-18c17c3bd398\house_1_1787995227389.jpg"

# Define destination directory
dest_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "images"))
os.makedirs(dest_dir, exist_ok=True)
print(f"Created static images directory: {dest_dir}")

# Define destination paths
dest_apartment = os.path.join(dest_dir, "apartment_1.jpg")
dest_villa = os.path.join(dest_dir, "villa_1.jpg")
dest_house = os.path.join(dest_dir, "house_1.jpg")

# Copy the images
shutil.copy2(src_apartment, dest_apartment)
shutil.copy2(src_villa, dest_villa)
shutil.copy2(src_house, dest_house)
print("Copied all images to backend/static/images/")

# Databases to update
databases = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "real_estate.db")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "real_estate.db"))
]

for db_path in databases:
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}, skipping.")
        continue
        
    print(f"Updating database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Update Apartments
    apt_img = json.dumps(["/static/images/apartment_1.jpg"])
    cursor.execute("UPDATE properties SET images = ? WHERE LOWER(property_type) = 'apartment'", (apt_img,))
    apt_count = cursor.rowcount
    
    # 2. Update Villas
    villa_img = json.dumps(["/static/images/villa_1.jpg"])
    cursor.execute("UPDATE properties SET images = ? WHERE LOWER(property_type) = 'villa'", (villa_img,))
    villa_count = cursor.rowcount
    
    # 3. Update Independent Houses / Buildings
    house_img = json.dumps(["/static/images/house_1.jpg"])
    cursor.execute("UPDATE properties SET images = ? WHERE LOWER(property_type) = 'independent house'", (house_img,))
    house_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    print(f"  Updated: {apt_count} Apartments, {villa_count} Villas, {house_count} Independent Houses.")

print("Database update complete!")
