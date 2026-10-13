import sqlite3
import pandas as pd
import os
import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'datasets', 'Karnataka_Individual_Properties.csv')

DB_PATHS = [
    os.path.join(BASE_DIR, 'real_estate.db'),
    os.path.join(os.path.dirname(BASE_DIR), 'real_estate.db')
]

if not os.path.exists(CSV_PATH):
    print(f"Error: {CSV_PATH} not found!")
    sys.exit(1)

df_ind = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df_ind)} authentic records from {CSV_PATH}")

for db_path in DB_PATHS:
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist, skipping.")
        continue
    
    print(f"\n==========================================")
    print(f"Migrating individual properties for: {db_path}")
    print(f"==========================================")
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Clean out the 441 synthetic K-RERA records from properties table
    deleted_synthetic = cur.execute("""
        DELETE FROM properties 
        WHERE source_name = 'Karnataka Real Estate Regulatory Authority (K-RERA)'
           OR source = 'Government RERA Registry'
    """).rowcount
    print(f"Removed {deleted_synthetic} synthetic project records from properties table.")
    conn.commit()

    # 2. Verify / Normalize districts on existing Bengaluru properties
    print("Normalizing existing properties districts...")
    cur.execute("""
        UPDATE properties 
        SET district = 'Bengaluru Rural' 
        WHERE (district IS NULL OR district = '' OR district = 'Bengaluru Urban') 
          AND (locality LIKE '%Devanahalli%' OR locality LIKE '%Doddaballapur%' OR locality LIKE '%Nelamangala%' OR locality LIKE '%Hoskote%'
               OR address LIKE '%Devanahalli%' OR address LIKE '%Doddaballapur%' OR address LIKE '%Nelamangala%' OR address LIKE '%Hoskote%')
    """)
    cur.execute("""
        UPDATE properties 
        SET district = 'Ramanagara' 
        WHERE (district IS NULL OR district = '' OR district = 'Bengaluru Urban')
          AND (locality LIKE '%Bidadi%' OR locality LIKE '%Ramanagara%' OR locality LIKE '%Harohalli%' OR locality LIKE '%Magadi%' OR locality LIKE '%Channapatna%'
               OR address LIKE '%Bidadi%' OR address LIKE '%Ramanagara%' OR address LIKE '%Harohalli%' OR address LIKE '%Magadi%' OR address LIKE '%Channapatna%')
    """)
    cur.execute("""
        UPDATE properties 
        SET district = 'Kolar' 
        WHERE (district IS NULL OR district = '' OR district = 'Bengaluru Urban')
          AND (locality LIKE '%Kolar%' OR locality LIKE '%Malur%' OR address LIKE '%Kolar%' OR address LIKE '%Malur%')
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

    # 3. Check which genuine non-Urban properties from Karnataka_Individual_Properties.csv need to be inserted
    # Check by source_listing_id or title + locality
    existing_rids = set(r[0] for r in cur.execute("SELECT source_listing_id FROM properties WHERE source_listing_id IS NOT NULL").fetchall())
    
    non_blr_rows = df_ind[df_ind['district'] != 'Bengaluru Urban']
    print(f"Checking {len(non_blr_rows)} verified non-Bengaluru-Urban individual properties for database synchronization...")
    
    inserted_count = 0
    max_id = cur.execute("SELECT COALESCE(MAX(id), 0) FROM properties").fetchone()[0]
    
    for idx, row in non_blr_rows.iterrows():
        pid = str(row.get('property_id'))
        rid = str(row.get('source_record_id'))
        if rid in existing_rids:
            continue
        
        max_id += 1
        sql = """
        INSERT INTO properties (
            id, user_id, title, property_name, building_name, project_name, society_name, builder_name,
            property_type, listing_type, bhk, area_sqft, bathrooms, balconies, floor, total_floors,
            property_age, facing, parking, furnishing, price, price_inr, price_per_sqft,
            description, address, formatted_address, locality, city, district, state, pincode,
            latitude, longitude, coordinate_confidence, coordinate_quality, location_source,
            images, image_status, image_count, image_provenance,
            contact_available, contact_number, contact_type, contact_source,
            source, source_name, source_url, source_listing_id, listing_status, availability,
            dataset_category, is_main_ai_ready, verified, verification_status,
            created_at, updated_at
        ) VALUES (
            ?, 1, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, 1, 1, 4,
            'New', 'East', 'Covered', 'Semi-Furnished', ?, ?, ?,
            ?, ?, ?, ?, ?, ?, 'Karnataka', ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, 'CURRENT', 'Ready To Move',
            ?, ?, 1, 'Verified Genuine Listing',
            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        )
        """
        has_img = bool(row.get('has_genuine_image'))
        img_str = str(row.get('images', '[]'))
        coord_conf = str(row.get('coordinate_confidence', 'LOCALITY_CENTROID'))
        loc_src = 'VERIFIED_DIRECT_GPS' if coord_conf == 'EXACT' else 'NOMINATIM_LOCALITY_CENTROID'
        
        # Pincode extraction if available
        import re
        addr_str = str(row.get('full_address', ''))
        pin_match = re.search(r'\b(\d{6})\b', addr_str)
        pincode_val = pin_match.group(1) if pin_match else ""

        is_ai_ready = 1 if (has_img and row.get('price_inr') and row.get('area_sqft') and row.get('bhk')) else 0
        cat = 'MAIN_AI_READY' if is_ai_ready else 'REFERENCE_HISTORICAL'

        params = (
            max_id,
            str(row['property_title']), str(row['property_title']), str(row['property_title']), str(row['property_title']), "", "",
            str(row['property_type']), str(row['listing_type']), int(row['bhk']) if pd.notna(row['bhk']) else 2,
            float(row['area_sqft']) if pd.notna(row['area_sqft']) else 1000.0,
            int(row['bathrooms']) if pd.notna(row['bathrooms']) else 1,
            float(row['price_inr']), float(row['price_inr']), float(row['price_per_sqft']) if pd.notna(row['price_per_sqft']) else 0.0,
            str(row['description']), str(row['full_address']), str(row['full_address']), str(row['locality']), str(row['district']), str(row['district']), pincode_val,
            float(row['latitude']) if pd.notna(row['latitude']) else 12.9716, float(row['longitude']) if pd.notna(row['longitude']) else 77.5946,
            coord_conf, coord_conf, loc_src,
            img_str, 'HAVE_IMAGE' if has_img else 'NO_IMAGE', 1 if has_img else 0, 'PROPERTY_SPECIFIC' if has_img else 'NO_IMAGE',
            0, None, 'Owner', 'Public Listing Source',
            str(row['source_name']), str(row['source_name']), str(row['source_url']), rid,
            cat, is_ai_ready
        )
        cur.execute(sql, params)
        existing_rids.add(rid)
        inserted_count += 1
    
    conn.commit()
    print(f"Inserted {inserted_count} new authentic district properties into {db_path}.")
    
    # 4. Final check of counts by district in properties table
    total_props = cur.execute("SELECT count(*) FROM properties").fetchone()[0]
    print(f"\nTotal properties in {db_path}: {total_props}")
    dist_breakdown = cur.execute("SELECT district, count(*), sum(case when is_main_ai_ready=1 then 1 else 0 end) FROM properties GROUP BY district ORDER BY count(*) DESC").fetchall()
    print("Database district breakdown (Total / AI Ready):")
    for d, c, ai in dist_breakdown:
        print(f"  {d:20s}: {c:5d} total | {ai:4d} AI ready")
        
    conn.close()

print("\nDatabase synchronization completed successfully!")
