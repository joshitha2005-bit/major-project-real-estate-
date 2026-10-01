import sqlite3
import pandas as pd
import numpy as np
import os
import glob
import re

DB_PATH = "backend/real_estate.db"

def run_phase4_audit():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("==========================================================================")
    print("PHASE 4 — AUDIT PART 1: MASTER PROPERTY COVERAGE & DATA QUALITY")
    print("==========================================================================")

    # 1. Total records
    cursor.execute("SELECT COUNT(*) FROM properties")
    total_props = cursor.fetchone()[0]

    # Breakdown by source_type
    cursor.execute("SELECT source_type, COUNT(*) FROM properties GROUP BY source_type")
    source_type_counts = cursor.fetchall()
    print(f"Total Properties: {total_props}")
    print(f"Source Type Breakdown: {source_type_counts}")

    # Breakdown by transaction_type
    cursor.execute("SELECT transaction_type, COUNT(*) FROM properties GROUP BY transaction_type")
    trans_counts = cursor.fetchall()
    print(f"Transaction Type Breakdown: {trans_counts}")

    # Breakdown by zone
    cursor.execute("SELECT zone, COUNT(*) FROM properties GROUP BY zone")
    zone_counts = cursor.fetchall()
    print(f"Zone Breakdown: {zone_counts}")

    # Check missing fields
    fields_to_check = [
        "society", "sub_locality", "furnishing", "floor", "total_floors", 
        "parking", "facing", "property_age", "source_url", "source_listing_id"
    ]
    print("\nField Non-Null Counts & Coverage:")
    for field in fields_to_check:
        cursor.execute(f"SELECT COUNT(*) FROM properties WHERE {field} IS NOT NULL AND {field} != '' AND {field} != 'None'")
        cnt = cursor.fetchone()[0]
        pct = (cnt / total_props) * 100.0
        print(f"  - {field}: {cnt} non-null ({pct:.2f}%)")

    # Duplicate / Near-Duplicate check
    cursor.execute("""
        SELECT title, locality, price, bhk, area_sqft, COUNT(*)
        FROM properties
        GROUP BY lower(title), lower(locality), price, bhk, area_sqft
        HAVING COUNT(*) > 1
    """)
    dup_rows = cursor.fetchall()
    print(f"\nExact Duplicate Groups (title+locality+price+bhk+area): {len(dup_rows)}")

    # Near-duplicates (same location + bhk + area + price)
    cursor.execute("""
        SELECT locality, bhk, area_sqft, price, COUNT(*)
        FROM properties
        GROUP BY lower(locality), bhk, area_sqft, price
        HAVING COUNT(*) > 1
    """)
    near_dup_rows = cursor.fetchall()
    print(f"Near-Duplicate Groups (locality+bhk+area+price): {len(near_dup_rows)}")

    print("\n==========================================================================")
    print("PHASE 4 — AUDIT PART 2: COORDINATE ACCURACY & ENRICHMENT POTENTIAL")
    print("==========================================================================")

    # Coordinate quality breakdown
    cursor.execute("SELECT coordinate_quality, COUNT(*) FROM properties GROUP BY coordinate_quality")
    coord_qual_counts = cursor.fetchall()
    print(f"Coordinate Quality Breakdown: {coord_qual_counts}")

    # Fallback clusters
    cursor.execute("SELECT round(latitude, 4), round(longitude, 4), COUNT(*), GROUP_CONCAT(DISTINCT locality) FROM properties GROUP BY round(latitude, 4), round(longitude, 4) HAVING COUNT(*) > 10 ORDER BY COUNT(*) DESC LIMIT 10")
    clusters = cursor.fetchall()
    print("\nTop Fallback Coordinate Clusters (>10 properties at exact same point):")
    for cl in clusters:
        print(f"  Point ({cl[0]}, {cl[1]}): {cl[2]} properties | Sample Localities: {cl[3][:80]}...")

    # Coordinates outside Bengaluru Bounding Box: [12.7, 77.3, 13.3, 77.8]
    cursor.execute("""
        SELECT id, title, locality, latitude, longitude 
        FROM properties 
        WHERE latitude < 12.7 OR latitude > 13.3 OR longitude < 77.3 OR longitude > 77.8
    """)
    out_of_bounds = cursor.fetchall()
    print(f"\nProperties Outside Bengaluru Bounding Box [12.7-13.3 N, 77.3-77.8 E]: {len(out_of_bounds)}")
    for oob in out_of_bounds[:5]:
        print(f"  ID {oob[0]}: {oob[1]} in {oob[2]} at ({oob[3]}, {oob[4]})")

    # Potential for Exact Geocoding from Society/Address among LOCALITY_APPROXIMATE
    cursor.execute("""
        SELECT COUNT(*) FROM properties 
        WHERE coordinate_quality = 'LOCALITY_APPROXIMATE' 
          AND society IS NOT NULL AND society != '' AND society != 'None'
    """)
    approx_with_society = cursor.fetchone()[0]
    print(f"\nLOCALITY_APPROXIMATE records with explicit Society/Project name: {approx_with_society} (Potential for exact society geocoding)")

    print("\n==========================================================================")
    print("PHASE 4 — AUDIT PART 3: PROPERTY IMAGE & PROVENANCE AUDIT")
    print("==========================================================================")

    cursor.execute("SELECT COUNT(*) FROM property_images")
    total_db_images = cursor.fetchone()[0]
    print(f"Total Property Image Records in property_images table: {total_db_images}")

    cursor.execute("SELECT source_type, COUNT(*) FROM property_images GROUP BY source_type")
    img_source_types = cursor.fetchall()
    print(f"Image Source Type Breakdown: {img_source_types}")

    cursor.execute("SELECT source_name, COUNT(*) FROM property_images GROUP BY source_name")
    img_source_names = cursor.fetchall()
    print(f"Image Source Name Breakdown: {img_source_names}")

    # Unique properties with images
    cursor.execute("SELECT COUNT(DISTINCT property_id) FROM property_images")
    props_with_db_images = cursor.fetchone()[0]
    print(f"Unique Properties with DB Image records: {props_with_db_images}")

    # Check images JSON column in properties table
    cursor.execute("SELECT COUNT(*) FROM properties WHERE images IS NOT NULL AND images != '[]' AND images != ''")
    props_with_json_images = cursor.fetchone()[0]
    print(f"Unique Properties with JSON images column populated: {props_with_json_images}")

    # Properties with NO images (neither in property_images nor images JSON)
    cursor.execute("""
        SELECT COUNT(*) FROM properties 
        WHERE id NOT IN (SELECT DISTINCT property_id FROM property_images)
          AND (images IS NULL OR images = '[]' OR images = '')
    """)
    no_image_count = cursor.fetchone()[0]
    print(f"Properties with NO Image (Null/Empty): {no_image_count}")

    print("\n==========================================================================")
    print("PHASE 4 — AUDIT PART 4: AVAILABLE DATASETS & REPOSITORY FILE DISCOVERY")
    print("==========================================================================")

    csv_files = glob.glob("backend/datasets/*.csv") + glob.glob("*.csv") + glob.glob("backend/*.csv")
    print(f"CSV Datasets Discovered in Workspace: {csv_files}")

    for csv_f in csv_files:
        try:
            df = pd.read_csv(csv_f)
            print(f"\n  File: {csv_f}")
            print(f"    Rows: {len(df)} | Columns: {len(df.columns)}")
            print(f"    Column Names: {df.columns.tolist()[:10]}")
        except Exception as e:
            print(f"    Error reading {csv_f}: {e}")

    conn.close()

if __name__ == "__main__":
    run_phase4_audit()
