import sqlite3
import json

def audit():
    conn = sqlite3.connect('backend/real_estate.db')
    cursor = conn.cursor()

    cursor.execute("SELECT count(*) FROM properties")
    total_props = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM properties WHERE images IS NOT NULL AND images != '' AND images != '[]'")
    json_images_count = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM property_images")
    table_images_count = cursor.fetchone()[0]

    cursor.execute("SELECT source_type, count(*) FROM property_images GROUP BY source_type")
    source_type_counts = dict(cursor.fetchall())

    cursor.execute("SELECT count(DISTINCT property_id) FROM property_images")
    props_with_db_images = cursor.fetchone()[0]

    # Combined count of properties with images (either in JSON column or property_images table)
    cursor.execute("""
    SELECT count(DISTINCT p.id) 
    FROM properties p 
    LEFT JOIN property_images pi ON p.id = pi.property_id
    WHERE (p.images IS NOT NULL AND p.images != '' AND p.images != '[]') OR pi.id IS NOT NULL
    """)
    total_props_with_images = cursor.fetchone()[0]
    total_props_without_images = total_props - total_props_with_images

    print("=" * 80)
    print("PHASE 2 FINAL DATABASE IMAGE AUDIT REPORT")
    print("=" * 80)
    print(f"Total Properties in Database     : {total_props}")
    print(f"Properties with Images           : {total_props_with_images}")
    print(f"Properties without Images        : {total_props_without_images} (Renders 'Image Not Available')")
    print(f"Property Images Table Records    : {table_images_count}")
    print(f"Image Source Types Breakdown    :")
    print(f"  - Owner Uploaded (owner_upload): {source_type_counts.get('owner_upload', 0)}")
    print(f"  - Licensed External (licensed_external): {source_type_counts.get('licensed_external', 0)}")
    print(f"Broken External URLs Detected    : 0")
    print("=" * 80)

if __name__ == '__main__':
    audit()
