import sqlite3
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(backend_dir)

db_paths = [
    os.path.join(root_dir, "real_estate.db"),
    os.path.join(backend_dir, "real_estate.db")
]

for db_path in db_paths:
    if not os.path.exists(db_path):
        continue
    print(f"Migrating {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. properties table
    cursor.execute("PRAGMA table_info(properties)")
    cols = [c[1] for c in cursor.fetchall()]
    cols_to_add = {
        'source_name': "VARCHAR(255) DEFAULT 'Bengaluru_House_Data.csv'",
        'listing_status': "VARCHAR(50) DEFAULT 'HISTORICAL'",
        'availability_date': "VARCHAR(100)",
        'listed_at': "DATETIME",
        'image_provenance': "VARCHAR(100) DEFAULT 'NO_IMAGE'",
        'image_count': "INTEGER DEFAULT 0",
        'owner_or_agent_type': "VARCHAR(50) DEFAULT 'Owner'",
        'contact_available': "BOOLEAN DEFAULT 0",
        'contact_source': "VARCHAR(255) DEFAULT 'Historical Dataset - No Contact'",
        'data_timestamp': "DATETIME",
        'anomaly_flags': "JSON DEFAULT '[]'"
    }
    for cname, ctype in cols_to_add.items():
        if cname not in cols:
            print(f"  Adding column {cname} to properties in {os.path.basename(db_path)}")
            cursor.execute(f"ALTER TABLE properties ADD COLUMN {cname} {ctype}")

    # 2. property_images table
    cursor.execute("PRAGMA table_info(property_images)")
    img_cols = [c[1] for c in cursor.fetchall()]
    img_cols_to_add = {
        "image_hash": "VARCHAR(255)",
        "width": "INTEGER",
        "height": "INTEGER",
        "image_provenance": "VARCHAR(100) DEFAULT 'OWNER_UPLOADED'",
        "verification_status": "VARCHAR(50) DEFAULT 'Verified'",
        "image_quality_score": "FLOAT",
        "image_validation_status": "VARCHAR(50) DEFAULT 'Valid'"
    }
    for col_name, col_type in img_cols_to_add.items():
        if col_name not in img_cols:
            print(f"  Adding column {col_name} to property_images in {os.path.basename(db_path)}")
            cursor.execute(f"ALTER TABLE property_images ADD COLUMN {col_name} {col_type}")

    conn.commit()
    conn.close()
    print(f"Done migrating {os.path.basename(db_path)}.")
print("All databases checked and migrated.")
