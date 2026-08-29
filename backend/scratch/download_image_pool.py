import os
import shutil
import urllib.request
import sqlite3
import json
import hashlib

# High-quality direct stock photo URLs (using Pexels image CDN ids)
apartment_urls = [
    "https://images.pexels.com/photos/276724/pexels-photo-276724.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/271816/pexels-photo-271816.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/2102587/pexels-photo-2102587.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/2251247/pexels-photo-2251247.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/534233/pexels-photo-534233.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/101808/pexels-photo-101808.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1643383/pexels-photo-1643383.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/439391/pexels-photo-439391.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1438817/pexels-photo-1438817.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/279719/pexels-photo-279719.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/276514/pexels-photo-276514.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/8031878/pexels-photo-8031878.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/323775/pexels-photo-323775.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/323780/pexels-photo-323780.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1396122/pexels-photo-1396122.jpeg?auto=compress&cs=tinysrgb&w=800"
]

villa_urls = [
    "https://images.pexels.com/photos/258154/pexels-photo-258154.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/208736/pexels-photo-208736.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/2287310/pexels-photo-2287310.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1838640/pexels-photo-1838640.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1396132/pexels-photo-1396132.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1481107/pexels-photo-1481107.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/323772/pexels-photo-323772.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1115804/pexels-photo-1115804.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/2980955/pexels-photo-2980955.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/584399/pexels-photo-584399.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/280222/pexels-photo-280222.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/2102585/pexels-photo-2102585.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1732414/pexels-photo-1732414.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/2251246/pexels-photo-2251246.jpeg?auto=compress&cs=tinysrgb&w=800"
]

house_urls = [
    "https://images.pexels.com/photos/106399/pexels-photo-106399.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1396122/pexels-photo-1396122.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/323780/pexels-photo-323780.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/259588/pexels-photo-259588.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/280222/pexels-photo-280222.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1838640/pexels-photo-1838640.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/164522/pexels-photo-164522.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/164558/pexels-photo-164558.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/2251247/pexels-photo-2251247.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/209276/pexels-photo-209276.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/209315/pexels-photo-209315.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/2251246/pexels-photo-2251246.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/1396132/pexels-photo-1396132.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/2980955/pexels-photo-2980955.jpeg?auto=compress&cs=tinysrgb&w=800",
    "https://images.pexels.com/photos/323772/pexels-photo-323772.jpeg?auto=compress&cs=tinysrgb&w=800"
]

dest_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "images"))
os.makedirs(dest_dir, exist_ok=True)

# User-agent header to prevent HTTP 403 Forbidden from Pexels
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def download_image(url, filepath):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response, open(filepath, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Successfully downloaded: {os.path.basename(filepath)}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

# Download Apartment Images (1 to 15)
apartment_count = 0
for i, url in enumerate(apartment_urls, 1):
    path = os.path.join(dest_dir, f"apartment_{i}.jpg")
    if download_image(url, path):
        apartment_count += 1

# Download Villa Images (1 to 15)
villa_count = 0
for i, url in enumerate(villa_urls, 1):
    path = os.path.join(dest_dir, f"villa_{i}.jpg")
    if download_image(url, path):
        villa_count += 1

# Download House Images (1 to 15)
house_count = 0
for i, url in enumerate(house_urls, 1):
    path = os.path.join(dest_dir, f"house_{i}.jpg")
    if download_image(url, path):
        house_count += 1

print(f"\nSummary of Downloads: {apartment_count} Apartments, {villa_count} Villas, {house_count} Houses")

# Fallback in case of failures (copy existing if any file is missing)
for name, count, fallback_file in [("apartment", apartment_count, "apartment_1.jpg"), 
                                   ("villa", villa_count, "villa_1.jpg"), 
                                   ("house", house_count, "house_1.jpg")]:
    fallback_path = os.path.join(dest_dir, fallback_file)
    if os.path.exists(fallback_path):
        for i in range(count + 1, 16):
            target_path = os.path.join(dest_dir, f"{name}_{i}.jpg")
            shutil.copy2(fallback_path, target_path)
            print(f"Copied fallback {fallback_file} to {target_path}")

# Hashing and Database Updates
def get_image_index(pid, title, num_images):
    h_str = f"{title}_{pid}"
    h = hashlib.md5(h_str.encode('utf-8')).hexdigest()
    return (int(h, 16) % num_images) + 1

databases = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "real_estate.db")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "real_estate.db"))
]

for db_path in databases:
    if not os.path.exists(db_path):
        continue

    print(f"\nUpdating database image pool in: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, property_type FROM properties")
    properties = cursor.fetchall()
    
    update_count = 0
    for pid, title, ptype in properties:
        ptype_lower = (ptype or "").lower()
        images = []
        if "apartment" in ptype_lower:
            img_idx = get_image_index(pid, title, 15)
            images = [f"/static/images/apartment_{img_idx}.jpg"]
        elif "villa" in ptype_lower:
            img_idx = get_image_index(pid, title, 15)
            images = [f"/static/images/villa_{img_idx}.jpg"]
        elif "house" in ptype_lower or "independent" in ptype_lower:
            img_idx = get_image_index(pid, title, 15)
            images = [f"/static/images/house_{img_idx}.jpg"]
        else:
            img_idx = get_image_index(pid, title, 15)
            images = [f"/static/images/apartment_{img_idx}.jpg"]

        cursor.execute("UPDATE properties SET images = ? WHERE id = ?", (json.dumps(images), pid))
        update_count += 1

    conn.commit()
    conn.close()
    print(f"Updated {update_count} records in {os.path.basename(db_path)}")

print("\nSetup complete!")
