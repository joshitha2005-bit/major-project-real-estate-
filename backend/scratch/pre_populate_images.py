import sqlite3
import json
import os
import sys

# Add backend directory to sys.path so we can import services
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)

from app.services.image_retrieval_service import ImageRetrievalService

databases = [
    os.path.join(backend_dir, "real_estate.db"),
    os.path.abspath(os.path.join(backend_dir, "..", "real_estate.db"))
]

for db_path in databases:
    if not os.path.exists(db_path):
        continue

    print(f"\nPre-populating real images for database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Introspect columns dynamically
    cursor.execute("PRAGMA table_info(properties)")
    cols = [col[1] for col in cursor.fetchall()]
    has_locality = "locality" in cols
    
    if has_locality:
        cursor.execute("SELECT id, title, locality, property_type, images FROM properties")
    else:
        # Use address as locality fallback
        cursor.execute("SELECT id, title, address, property_type, images FROM properties")
        
    properties = cursor.fetchall()
    
    update_count = 0
    # Limit to 120 properties per database to avoid rate limits
    limit = 120
    for pid, title, loc_or_addr, ptype, imgs_json in properties:
        try:
            imgs = json.loads(imgs_json) if imgs_json else []
        except Exception:
            imgs = []
            
        if not imgs or len(imgs) == 0:
            locality_val = loc_or_addr
            if not has_locality and loc_or_addr:
                # Extract locality name from address (last parts before pin)
                parts = [p.strip() for p in loc_or_addr.split(",")]
                if len(parts) >= 2:
                    locality_val = parts[-2]
                    
            print(f"Retrieving unique image for ID {pid}: {title} in {locality_val}...")
            img_url = ImageRetrievalService.get_unique_property_image(
                prop_id=pid,
                title=title,
                locality=locality_val or "Bengaluru",
                property_type=ptype
            )
            if img_url:
                cursor.execute("UPDATE properties SET images = ? WHERE id = ?", (json.dumps([img_url]), pid))
                update_count += 1
                if update_count >= limit:
                    break

    conn.commit()
    conn.close()
    print(f"Pre-populated {update_count} properties in {os.path.basename(db_path)}")

print("\nPre-population complete!")
