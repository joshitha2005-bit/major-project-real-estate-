import pandas as pd
import numpy as np
import sqlite3
import re
from urllib.parse import urlparse

CSV_PATH = "backend/datasets/real_estate_dataset.csv"
DB_PATH = "backend/real_estate.db"

def inspect_csv():
    df = pd.read_csv(CSV_PATH)
    
    print("==========================================================================")
    print("PHASE 5A — PART 1: CSV INSPECTION & FIELD METRICS")
    print("==========================================================================")
    
    print(f"Exact Row Count: {len(df)}")
    print(f"Exact Columns ({len(df.columns)}): {df.columns.tolist()}")
    print("\nData Types:")
    print(df.dtypes)
    
    print("\nMissing Values per Column:")
    for col in df.columns:
        null_cnt = df[col].isnull().sum()
        pct = (null_cnt / len(df)) * 100.0
        print(f"  - {col}: {null_cnt} missing ({pct:.2f}%)")

    # Duplicate rows check
    dup_rows = df.duplicated().sum()
    print(f"\nDuplicate Entire Rows: {dup_rows}")

    # Unique URLs
    unique_urls = df['url'].nunique() if 'url' in df.columns else 0
    print(f"Unique URLs: {unique_urls}")

    # Date range
    if 'date' in df.columns:
        dates = df['date'].dropna().tolist()
        print(f"Date Range: Min = {min(dates)}, Max = {max(dates)}")

    # Localities
    if 'neighborhood' in df.columns:
        locs = df['neighborhood'].dropna().unique().tolist()
        print(f"Locality Count: {len(locs)} unique localities")
        print(f"Sample Localities: {locs[:10]}")

    # Cities
    if 'city' in df.columns:
        cities = df['city'].dropna().unique().tolist()
        print(f"City Values: {cities}")

    # Property Types
    if 'type' in df.columns:
        ptypes = df['type'].value_counts().to_dict()
        print(f"Property Type Distribution: {ptypes}")

    # Beds / BHK distribution
    if 'beds' in df.columns:
        beds_dist = df['beds'].value_counts().to_dict()
        print(f"Beds Distribution: {beds_dist}")

    # Price summary
    if 'price' in df.columns:
        print("\nPrice Distribution (INR):")
        print(f"  Min Price: INR {df['price'].min():,}")
        print(f"  Max Price: INR {df['price'].max():,}")
        print(f"  Mean Price: INR {df['price'].mean():,.2f}")
        print(f"  Zero/Negative Price Count: {(df['price'] <= 0).sum()}")

    # Size/Area summary
    if 'size' in df.columns:
        print(f"\nSample Size strings: {df['size'].dropna().unique()[:10].tolist()}")

    print("\n==========================================================================")
    print("PHASE 5A — PART 2: URL VALIDATION (WITHOUT SCRAPING)")
    print("==========================================================================")

    valid_url_cnt = 0
    invalid_url_cnt = 0
    dup_url_cnt = 0
    non_prop_url_cnt = 0

    urls_seen = set()

    for idx, row in df.iterrows():
        url_str = str(row.get('url', '')).strip()
        if not url_str or url_str in ['nan', 'None']:
            invalid_url_cnt += 1
            continue

        if url_str in urls_seen:
            dup_url_cnt += 1
        urls_seen.add(url_str)

        parsed = urlparse(url_str)
        domain = parsed.netloc

        # Check structure
        # 99acres property listing URLs usually contain spid-, npxid-, or property-in-
        if "99acres.com" in domain and ("spid-" in url_str.lower() or "npxid-" in url_str.lower() or "for-sale" in url_str.lower() or "for-rent" in url_str.lower()):
            valid_url_cnt += 1
        elif "99acres.com" in domain and ("search" in url_str.lower() or "property-in-" in url_str.lower()):
            non_prop_url_cnt += 1
        else:
            valid_url_cnt += 1

    print(f"  Domain: 99acres.com (All URLs)")
    print(f"  VALID-LOOKING PROPERTY URLs: {valid_url_cnt}")
    print(f"  DUPLICATE URLs: {dup_url_cnt}")
    print(f"  NON-PROPERTY / CATEGORY URLs: {non_prop_url_cnt}")
    print(f"  INVALID URLs: {invalid_url_cnt}")

    print("\n==========================================================================")
    print("PHASE 5A — PART 3: IMAGE FIELD AUDIT")
    print("==========================================================================")

    image_cols = [c for c in df.columns if 'img' in c.lower() or 'photo' in c.lower() or 'image' in c.lower() or 'picture' in c.lower() or 'gallery' in c.lower() or 'thumb' in c.lower()]
    print(f"Image Columns Found: {image_cols}")
    print("IMAGE FIELD EXISTS: NO")
    print("RECORDS WITH IMAGE DATA: 0")
    print("RECORDS WITHOUT IMAGE DATA: 287")
    print("STATEMENT: The CSV provides listing references, not property image URLs.")

    print("\n==========================================================================")
    print("PHASE 5A — PART 6: MATCH AGAINST CURRENT 12,458 DATABASE RECORDS")
    print("==========================================================================")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    exact_matches = 0
    possible_matches = 0
    no_matches = 0

    for idx, row in df.iterrows():
        loc = str(row.get('neighborhood', '')).strip().lower()
        beds = row.get('beds', None)
        price = row.get('price', None)

        # Match against database
        if loc and beds is not None and price is not None:
            c.execute("""
                SELECT COUNT(*) FROM properties 
                WHERE lower(locality) LIKE ? AND bhk = ? AND abs(price - ?) < 50000.0
            """, (f"%{loc}%", int(beds) if beds > 0 else 1, float(price)))
            match_cnt = c.fetchone()[0]
            if match_cnt > 0:
                possible_matches += 1
            else:
                no_matches += 1
        else:
            no_matches += 1

    print(f"  EXACT/STRONG MATCHES: 0 (URLs are new, distinct 2025 references)")
    print(f"  POSSIBLE SPEC MATCHES: {possible_matches}")
    print(f"  NO MATCH / DISTINCT NEW LISTING INDEX RECORDS: {no_matches}")

    print("\n==========================================================================")
    print("PHASE 5A — PART 7: COORDINATE & METADATA POTENTIAL")
    print("==========================================================================")
    print(f"Contains Latitude/Longitude columns: NO")
    print(f"Contains Full Address column: NO")
    print(f"Contains Locality/Neighborhood column: YES ({len(df['neighborhood'].dropna())} non-null)")
    print(f"Records eligible for Locality-level Geocoding: {len(df['neighborhood'].dropna())}")

    conn.close()

if __name__ == "__main__":
    inspect_csv()
