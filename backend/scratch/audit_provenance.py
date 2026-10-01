import sqlite3
import json

def audit():
    conn = sqlite3.connect('backend/real_estate.db')
    cursor = conn.cursor()

    # 1. Total properties
    cursor.execute("SELECT count(*) FROM properties")
    total_properties = cursor.fetchone()[0]

    # 2. Total image records in property_images table
    cursor.execute("SELECT count(*) FROM property_images")
    total_db_image_records = cursor.fetchone()[0]

    # 3. Source type counts in property_images table
    cursor.execute("SELECT source_type, count(*) FROM property_images GROUP BY source_type")
    source_type_counts = dict(cursor.fetchall())

    # 4. Source name counts in property_images table
    cursor.execute("SELECT source_name, count(*) FROM property_images GROUP BY source_name")
    source_name_counts = dict(cursor.fetchall())

    # 5. User uploads vs seeded
    cursor.execute("SELECT count(*) FROM property_images WHERE source_type = 'owner_upload'")
    owner_upload_count = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM property_images WHERE source_type = 'licensed_external'")
    licensed_external_count = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM property_images WHERE source_type NOT IN ('owner_upload', 'licensed_external')")
    other_source_count = cursor.fetchone()[0]

    # Unique properties in property_images table
    cursor.execute("SELECT count(DISTINCT property_id) FROM property_images")
    unique_props_in_pi_table = cursor.fetchone()[0]

    # 6. Properties with images in properties.images JSON column vs property_images table
    cursor.execute("SELECT id, title, locality, images, source_type, source FROM properties WHERE images IS NOT NULL AND images != '' AND images != '[]'")
    props_with_json_images = cursor.fetchall()
    json_image_props_count = len(props_with_json_images)

    # Breakdown of images in JSON column
    seeded_json_count = 0
    props_with_multiple_images = 0
    sample_json_paths = set()

    for p in props_with_json_images:
        try:
            img_list = json.loads(p[3])
            if isinstance(img_list, list) and len(img_list) > 0:
                seeded_json_count += 1
                if len(img_list) > 1:
                    props_with_multiple_images += 1
                for path in img_list[:3]:
                    sample_json_paths.add(path)
        except Exception:
            pass

    # Total properties with images across both table and JSON
    cursor.execute("""
    SELECT count(DISTINCT p.id)
    FROM properties p
    LEFT JOIN property_images pi ON p.id = pi.property_id
    WHERE (p.images IS NOT NULL AND p.images != '' AND p.images != '[]') OR pi.id IS NOT NULL
    """)
    unique_props_with_any_images = cursor.fetchone()[0]

    # Breakdown by property source_type in properties table
    cursor.execute("SELECT source_type, count(*) FROM properties GROUP BY source_type")
    prop_source_type_breakdown = dict(cursor.fetchall())

    cursor.execute("SELECT source, count(*) FROM properties GROUP BY source")
    prop_source_breakdown = dict(cursor.fetchall())

    # Fetch 10 sample property records
    cursor.execute("""
    SELECT p.id, p.title, p.locality, p.images, p.source_type, p.source, pi.source_type, pi.source_name, pi.image_path
    FROM properties p
    LEFT JOIN property_images pi ON p.id = pi.property_id
    LIMIT 10
    """)
    samples = cursor.fetchall()

    print("=" * 85)
    print("PHASE 2.1 — IMAGE DATA PROVENANCE AUDIT REPORT")
    print("=" * 85)
    print(f"1. Total Properties in Database                        : {total_properties}")
    print(f"2. Total Image Records in property_images Table         : {total_db_image_records}")
    print(f"3. Count of Image Records by source_type (property_images table): {source_type_counts}")
    print(f"4. Count of Image Records by source_name (property_images table): {source_name_counts}")
    print(f"5. Count of owner_upload (property_images table)       : {owner_upload_count}")
    print(f"6. Count of licensed_external (property_images table)   : {licensed_external_count}")
    print(f"7. Count of Other source_types (property_images table)  : {other_source_count}")
    print(f"8. Unique Properties with Records in property_images Table: {unique_props_in_pi_table}")
    print(f"9. Properties with Seeding in properties.images JSON Column: {json_image_props_count}")
    print(f"10. Total Unique Properties with Any Image Assignment  : {unique_props_with_any_images}")
    print(f"11. Properties with Multiple Images Assigned            : {props_with_multiple_images}")
    print(f"12. Number of Properties Automatically Seeded           : {json_image_props_count}")
    print(f"13. Number of Images Actually Uploaded by Users         : {owner_upload_count}")
    print(f"14. Number of External URLs Legitimately Added          : {licensed_external_count}")
    print("-" * 85)
    print("PROPERTY SOURCE BREAKDOWN IN DATABASE:")
    print(f"  - By source_type: {prop_source_type_breakdown}")
    print(f"  - By source     : {prop_source_breakdown}")
    print("-" * 85)
    print("SAMPLE IMAGE PATHS IN JSON COLUMN:")
    for path in list(sample_json_paths)[:8]:
        print(f"  - {path}")
    print("-" * 85)
    print("10 SAMPLE PROPERTY RECORDS:")
    for s in samples:
        pid, title, loc, img_json, p_stype, p_src, pi_stype, pi_sname, pi_path = s
        parsed_img = json.loads(img_json) if img_json else []
        img_val = pi_path if pi_path else (parsed_img[0] if parsed_img else 'None')
        stype_val = pi_stype if pi_stype else 'seeded_demo_catalog'
        sname_val = pi_sname if pi_sname else 'Pre-seeded Demo Catalog'
        print(f"ID #{pid:5d} | Title: {title[:35]:35s} | Locality: {str(loc)[:15]:15s} | SourceType: {stype_val:22s} | SourceName: {sname_val:22s} | Path: {img_val}")
    print("=" * 85)

if __name__ == '__main__':
    audit()
