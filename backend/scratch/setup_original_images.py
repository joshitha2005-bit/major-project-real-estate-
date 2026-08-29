import os
import urllib.request
import sqlite3
import json
import ssl

# Original project image CDN URLs from MagicBricks and NoBroker (with correct MB dimension suffix)
original_images = {
    "prestige": "https://img.staticmb.com/mbimages/project/Photo_h300_w450/2021/05/11/Project-Photo-93-Prestige-Lakeside-Habitat-Bangalore-5019468_345_1366_300_450.jpg",
    "sobha": "https://img.staticmb.com/mbimages/project/2023/01/31/Project-Photo-32-Sobha-Dream-Acres-Bangalore-5082765_345_1366.jpg",
    "brigade": "https://img.staticmb.com/mbimages/project/Photo_h300_w450/2021/08/17/Project-Photo-14-Brigade-Cornerstone-Utopia-Bangalore-5182181_345_1366_300_450.jpg",
    "godrej": "https://img.staticmb.com/mbimages/project/Photo_h300_w450/2022/10/26/Project-Photo-4-Godrej-Lakeside-Orchard-Bangalore-5353139_345_1366_300_450.jpg",
    "lnt": "https://assets.nobroker.in/media/building/ff80818168f01e810168f06f77eb200d/images/ff80818168f01e810168f06f77eb200d_project_image_qthSvpFvLd1682692840731_53722_iris_medium.jpg",
    "salarpuria": "https://img.staticmb.com/mbimages/project/Photo_h300_w450/2020/09/28/Project-Photo-1-Salarpuria-Sattva-Cadenza-Bangalore-5079633_345_1366_300_450.jpg",
    "puravankara": "https://img.staticmb.com/mbimages/project/Photo_h300_w450/2021/04/30/Project-Photo-8-Purva-Atmosphere-Bangalore-5118742_345_1366_300_450.jpg",
    "adarsh": "https://img.staticmb.com/mbimages/project/Photo_h300_w450/2022/03/17/Project-Photo-17-Adarsh-Park-Heights-Bangalore-5339247_345_1366_300_450.jpg",
    "valmark": "https://img.staticmb.com/mbimages/project/Photo_h300_w450/2021/11/24/Project-Photo-10-Valmark-Orchard-Square-Bangalore-5126830_345_1366_300_450.jpg",
    "assetz": "https://img.staticmb.com/mbimages/project/Photo_h300_w450/2021/06/18/Project-Photo-2-Assetz-Marq-3.0-Bangalore-5211603_345_1366_300_450.jpg"
}

dest_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "images"))
os.makedirs(dest_dir, exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
ssl_ctx = ssl._create_unverified_context()

# Download original images
print("Downloading original property images...")
downloaded = {}
for builder, url in original_images.items():
    filepath = os.path.join(dest_dir, f"original_{builder}.jpg")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as response, open(filepath, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Downloaded original photo for {builder.upper()} -> original_{builder}.jpg")
        downloaded[builder] = f"/static/images/original_{builder}.jpg"
    except Exception as e:
        print(f"Failed to download {builder} from {url}: {e}")

# Databases to update
databases = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "real_estate.db")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "real_estate.db"))
]

for db_path in databases:
    if not os.path.exists(db_path):
        continue

    print(f"\nUpdating database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(properties)")
    cols = [col[1] for col in cursor.fetchall()]
    
    has_source_type = "source_type" in cols
    has_source = "source" in cols
    
    if has_source_type and has_source:
        cursor.execute("SELECT id, title, source_type, source FROM properties")
    elif has_source:
        cursor.execute("SELECT id, title, source, source FROM properties")
    else:
        cursor.execute("SELECT id, title, id, id FROM properties")
        
    properties = cursor.fetchall()
    
    update_count = 0
    cleared_count = 0
    for pid, title, s_type, s_name in properties:
        title_lower = (title or "").lower()
        is_historical = (s_type == 'historical_dataset' or s_name == 'Bengaluru_House_Data.csv') if (has_source_type or has_source) else True
        
        assigned_img = None
        for builder, local_path in downloaded.items():
            if builder in title_lower or (builder == "lnt" and "l&t" in title_lower):
                assigned_img = local_path
                break
        
        if assigned_img:
            cursor.execute("UPDATE properties SET images = ? WHERE id = ?", (json.dumps([assigned_img]), pid))
            update_count += 1
        elif is_historical:
            cursor.execute("UPDATE properties SET images = ? WHERE id = ?", (json.dumps([]), pid))
            cleared_count += 1

    conn.commit()
    conn.close()
    print(f"Updated {update_count} project-matched properties. Cleared {cleared_count} anonymous properties.")

print("\nDatabase update complete!")
