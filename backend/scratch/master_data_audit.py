import sqlite3
import pandas as pd
import json

def run_master_audit():
    conn = sqlite3.connect('backend/real_estate.db')
    cursor = conn.cursor()

    # 1. Record counts
    cursor.execute("SELECT count(*) FROM properties")
    total_properties = cursor.fetchone()[0]

    # Data sources count
    cursor.execute("SELECT source, count(*) FROM properties GROUP BY source")
    sources_breakdown = dict(cursor.fetchall())

    cursor.execute("SELECT source_type, count(*) FROM properties GROUP BY source_type")
    source_types_breakdown = dict(cursor.fetchall())

    # 2. Duplicate records audit (title, locality, bhk, area_sqft, price)
    cursor.execute("""
    SELECT title, locality, bhk, area_sqft, price, count(*) 
    FROM properties 
    GROUP BY title, locality, bhk, area_sqft, price 
    HAVING count(*) > 1
    """)
    duplicate_groups = cursor.fetchall()
    total_duplicate_rows = sum(row[5] - 1 for row in duplicate_groups)

    # 3. Locality coverage & normalization
    cursor.execute("SELECT count(DISTINCT locality) FROM properties")
    unique_localities = cursor.fetchone()[0]

    cursor.execute("SELECT locality, count(*) FROM properties GROUP BY locality ORDER BY count(*) DESC LIMIT 20")
    top_localities = cursor.fetchall()

    # 4. Coordinate quality
    # Plausible Bengaluru geographic range: Lat 12.75 to 13.25, Lon 77.35 to 77.85
    cursor.execute("""
    SELECT 
        count(CASE WHEN latitude = 0 AND longitude = 0 THEN 1 END) as zero_coords,
        count(CASE WHEN latitude BETWEEN 12.75 AND 13.25 AND longitude BETWEEN 77.35 AND 77.85 THEN 1 END) as valid_bengaluru_coords,
        count(CASE WHEN (latitude != 0 OR longitude != 0) AND NOT (latitude BETWEEN 12.75 AND 13.25 AND longitude BETWEEN 77.35 AND 77.85) THEN 1 END) as out_of_bounds_coords
    FROM properties
    """)
    coord_stats = cursor.fetchone()

    # Identical coordinates check
    cursor.execute("""
    SELECT latitude, longitude, count(*) 
    FROM properties 
    GROUP BY latitude, longitude 
    HAVING count(*) > 5
    ORDER BY count(*) DESC LIMIT 5
    """)
    identical_coords = cursor.fetchall()

    # 5. Area coverage & quality
    cursor.execute("""
    SELECT 
        count(CASE WHEN area_sqft <= 0 OR area_sqft IS NULL THEN 1 END) as invalid_area,
        count(CASE WHEN area_sqft > 0 AND area_sqft < 200 THEN 1 END) as tiny_area,
        count(CASE WHEN area_sqft > 20000 THEN 1 END) as huge_area,
        count(CASE WHEN area_sqft / bhk < 200 THEN 1 END) as unrealistic_ratio
    FROM properties
    """)
    area_stats = cursor.fetchone()

    # 6. Price coverage & quality
    cursor.execute("""
    SELECT 
        count(CASE WHEN price <= 0 OR price IS NULL THEN 1 END) as invalid_price,
        count(CASE WHEN price > 0 AND price < 500000 THEN 1 END) as low_price,
        count(CASE WHEN price > 500000000 THEN 1 END) as ultra_high_price,
        count(CASE WHEN listing_type = 'Rent' THEN 1 END) as rent_count,
        count(CASE WHEN listing_type = 'Buy' OR listing_type IS NULL THEN 1 END) as buy_count
    FROM properties
    """)
    price_stats = cursor.fetchone()

    # 7. Image coverage
    cursor.execute("SELECT count(*) FROM properties WHERE images IS NOT NULL AND images != '' AND images != '[]'")
    properties_with_images_json = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM property_images")
    property_images_table_rows = cursor.fetchone()[0]

    print("=" * 85)
    print("MASTER DATA AUDIT REPORT — BENGALURU REAL ESTATE")
    print("=" * 85)
    print(f"1. Total Properties in Database           : {total_properties}")
    print(f"   - Breakdown by Source                  : {sources_breakdown}")
    print(f"   - Breakdown by Source Type             : {source_types_breakdown}")
    print(f"2. Duplicate Record Groups                : {len(duplicate_groups)} groups ({total_duplicate_rows} redundant rows)")
    print(f"3. Unique Localities                      : {unique_localities}")
    print(f"4. Coordinate Quality Breakdown           :")
    print(f"   - Zero/Missing Coordinates (0.0, 0.0)  : {coord_stats[0]}")
    print(f"   - Valid Bengaluru Range Coordinates    : {coord_stats[1]}")
    print(f"   - Out of Bounds Coordinates            : {coord_stats[2]}")
    print(f"   - Identical Cluster Coordinates        : {identical_coords[:3]}")
    print(f"5. Area/Sqft Quality Breakdown            :")
    print(f"   - Invalid/Zero Area                    : {area_stats[0]}")
    print(f"   - Tiny Area (<200 sqft)                : {area_stats[1]}")
    print(f"   - Huge Area (>20,000 sqft)             : {area_stats[2]}")
    print(f"   - Unrealistic BHK/Sqft Ratio (<200/BHK): {area_stats[3]}")
    print(f"6. Price Quality Breakdown                :")
    print(f"   - Invalid/Zero Price                   : {price_stats[0]}")
    print(f"   - Rent Listings                        : {price_stats[3]}")
    print(f"   - Buy/Sale Listings                    : {price_stats[4]}")
    print(f"7. Image Coverage Breakdown               :")
    print(f"   - Properties with JSON image array     : {properties_with_images_json}")
    print(f"   - Table 'property_images' row count    : {property_images_table_rows}")
    print("=" * 85)

if __name__ == '__main__':
    run_master_audit()
