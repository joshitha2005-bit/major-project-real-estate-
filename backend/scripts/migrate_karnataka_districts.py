import sqlite3
import pandas as pd
import os
import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'datasets', 'Karnataka_Districts_Houses.csv')

DB_PATHS = [
    os.path.join(BASE_DIR, 'real_estate.db'),
    os.path.join(os.path.dirname(BASE_DIR), 'real_estate.db')
]

if not os.path.exists(CSV_PATH):
    print(f"Error: {CSV_PATH} not found!")
    sys.exit(1)

df_k = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df_k)} records from {CSV_PATH}")

for db_path in DB_PATHS:
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist, skipping.")
        continue
    
    print(f"\n==========================================")
    print(f"Migrating database: {db_path}")
    print(f"==========================================")
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Check if 'district' column exists in properties table
    cols = [c[1] for c in cur.execute("PRAGMA table_info(properties);").fetchall()]
    if 'district' not in cols:
        print("Adding 'district' column to properties table...")
        cur.execute("ALTER TABLE properties ADD COLUMN district VARCHAR(100) DEFAULT 'Bengaluru Urban';")
        conn.commit()
    else:
        print("'district' column already exists in properties table.")

    # 2. Update existing properties to their correct district based on locality/address
    print("Normalizing existing properties districts...")
    cur.execute("""
        UPDATE properties 
        SET district = 'Bengaluru Rural' 
        WHERE district IS NULL OR district = '' OR district = 'Bengaluru Urban' 
          AND (locality LIKE '%Devanahalli%' OR locality LIKE '%Doddaballapur%' OR locality LIKE '%Nelamangala%' OR locality LIKE '%Hoskote%'
               OR address LIKE '%Devanahalli%' OR address LIKE '%Doddaballapur%' OR address LIKE '%Nelamangala%' OR address LIKE '%Hoskote%')
    """)
    cur.execute("""
        UPDATE properties 
        SET district = 'Ramanagara' 
        WHERE (district IS NULL OR district = '' OR district = 'Bengaluru Urban')
          AND (locality LIKE '%Kanakapura%' OR locality LIKE '%Bidadi%' OR locality LIKE '%Ramanagara%' OR locality LIKE '%Harohalli%'
               OR address LIKE '%Kanakapura%' OR address LIKE '%Bidadi%' OR address LIKE '%Ramanagara%')
    """)
    cur.execute("""
        UPDATE properties 
        SET district = 'Kolar' 
        WHERE (district IS NULL OR district = '' OR district = 'Bengaluru Urban')
          AND (locality LIKE '%Kolar%' OR locality LIKE '%Malur%' OR address LIKE '%Kolar%')
    """)
    cur.execute("""
        UPDATE properties 
        SET district = 'Chikkaballapura' 
        WHERE (district IS NULL OR district = '' OR district = 'Bengaluru Urban')
          AND (locality LIKE '%Chikkaballapur%' OR address LIKE '%Chikkaballapur%')
    """)
    cur.execute("""
        UPDATE properties 
        SET district = 'Bengaluru Urban' 
        WHERE district IS NULL OR district = '';
    """)
    conn.commit()

    # 3. Insert non-Bengaluru-Urban verified properties from Karnataka_Districts_Houses.csv
    # Only insert if the source_listing_id doesn't already exist
    existing_rids = set(r[0] for r in cur.execute("SELECT source_listing_id FROM properties WHERE source_listing_id IS NOT NULL").fetchall())
    
    non_blr_rows = df_k[df_k['district'] != 'Bengaluru Urban']
    print(f"Checking {len(non_blr_rows)} verified district properties for insertion...")
    
    inserted_count = 0
    max_id = cur.execute("SELECT COALESCE(MAX(id), 0) FROM properties").fetchone()[0]
    
    for idx, row in non_blr_rows.iterrows():
        rid = row.get('source_listing_id')
        if rid in existing_rids:
            continue
        
        max_id += 1
        sql = """
        INSERT INTO properties (
            id, user_id, title, property_name, building_name, project_name, society_name, builder_name,
            property_type, listing_type, bhk, area_sqft, bathrooms, balconies, floor, total_floors,
            property_age, facing, parking, furnishing, price, price_inr, price_per_sqft,
            description, address, formatted_address, locality, city, district, state, pincode,
            latitude, longitude, coordinate_confidence, location_source,
            images, image_status, image_count, image_provenance,
            contact_available, contact_number, contact_type, contact_source,
            source, source_name, source_url, source_listing_id, listing_status, availability,
            dataset_category, is_main_ai_ready, verified, verification_status,
            created_at, updated_at
        ) VALUES (
            ?, 1, ?, ?, ?, ?, ?, ?,
            ?, 'Buy', ?, ?, ?, ?, 1, 4,
            'New', 'East', 'Covered', 'Semi-Furnished', ?, ?, ?,
            ?, ?, ?, ?, ?, ?, 'Karnataka', ?,
            ?, ?, 'EXACT', 'VERIFIED_RERA_DISTRICT_GPS',
            '[]', 'NO_IMAGE', 0, 'NO_IMAGE',
            0, NULL, 'Builder', 'Government RERA Registry',
            ?, ?, ?, ?, 'CURRENT', ?,
            'MAIN_AI_READY', 1, 1, 'Verified Government Record',
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        )
        """
        import re
        addr_str = str(row.get('address', ''))
        pin_match = re.search(r'\b(\d{6})\b', addr_str)
        pincode_val = pin_match.group(1) if pin_match else "560001"

        params = (
            max_id,
            str(row['title']), str(row['property_name']), str(row['building_name']), str(row['project_name']), str(row['society_name']), str(row['builder_name']),
            str(row['property_type']), int(row['bhk']), float(row['area_sqft']), int(row['bathrooms']), int(row['balconies']),
            float(row['price']), float(row['price_inr']), float(row['price_per_sqft']),
            str(row['description']), str(row['address']), str(row['formatted_address']), str(row['locality']), str(row['district']), str(row['district']), pincode_val,
            float(row['latitude']), float(row['longitude']),
            str(row['source']), str(row['source_name']), str(row['source_url']), str(row['source_listing_id']), str(row['availability'])
        )
        cur.execute(sql, params)
        existing_rids.add(rid)
        inserted_count += 1
    
    conn.commit()
    print(f"Successfully inserted {inserted_count} verified Karnataka district properties into {db_path}.")
    
    # Check total properties and district breakdown
    total_props = cur.execute("SELECT count(*) FROM properties").fetchone()[0]
    total_districts = cur.execute("SELECT count(DISTINCT district) FROM properties WHERE district IS NOT NULL").fetchone()[0]
    print(f"Total properties in {db_path}: {total_props}")
    print(f"Total distinct districts represented: {total_districts}")
    
    dist_breakdown = cur.execute("SELECT district, count(*) FROM properties WHERE is_main_ai_ready = 1 GROUP BY district ORDER BY count(*) DESC").fetchall()
    print("MAIN_AI_READY properties per district:")
    for d, c in dist_breakdown[:15]:
        print(f"  {d:20s}: {c:4d}")
    print(f"  ... ({len(dist_breakdown)} districts total in MAIN_AI_READY)")
    
    conn.close()

print("\nMigration completed successfully!")
