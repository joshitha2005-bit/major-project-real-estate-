import os
import pandas as pd
import re

def inspect():
    csv_path = r"c:\Users\HP\Downloads\real estate\backend\datasets\real_estate_dataset.csv"
    if not os.path.exists(csv_path):
        print("CSV not found!")
        return
        
    df = pd.read_csv(csv_path)
    print(f"Filename: {os.path.basename(csv_path)}")
    print(f"Total Rows: {len(df)}")
    print(f"Total Columns: {len(df.columns)}")
    print(f"Columns: {list(df.columns)}")
    
    # Bengaluru Filter
    # Let's count records belonging to Bengaluru/Bangalore
    # City column: df['city']
    df['city_clean'] = df['city'].astype(str).str.strip().str.lower()
    bengaluru_mask = df['city_clean'].str.contains('bangalore|bengaluru', na=False)
    total_records = len(df)
    bengaluru_records = len(df[bengaluru_mask])
    non_bengaluru_records = total_records - bengaluru_records
    
    print(f"Total records: {total_records}")
    print(f"Bengaluru records: {bengaluru_records}")
    print(f"Non-Bengaluru records: {non_bengaluru_records}")
    
    df_blr = df[bengaluru_mask].copy()
    
    # Top Bengaluru localities and counts
    # neighborhood is the locality column
    top_localities = df_blr['neighborhood'].value_counts().head(10)
    print("Top Localities:")
    print(top_localities)
    
    # Quality check functions
    # For Bengaluru records:
    # 1. records with property names (url or neighborhood/society or types)
    # The dataset doesn't have an explicit 'property_name' or 'society' column except URL parts
    # Let's check how many have neighborhood, type, etc.
    # 2. records with meaningful property titles (let's assume type is title)
    
    def is_valid(val):
        if pd.isna(val):
            return False
        s = str(val).strip().lower()
        return s not in ["", "nan", "null", "n/a", "-", "unknown", "none"]

    valid_names = df_blr['type'].apply(is_valid).sum() # Let's use type as name/title candidate
    valid_titles = df_blr['type'].apply(is_valid).sum()
    valid_localities = df_blr['neighborhood'].apply(is_valid).sum()
    valid_addresses = df_blr['neighborhood'].apply(is_valid).sum() # No explicit address column in dataset
    valid_prices = df_blr['price'].apply(lambda x: pd.notna(x) and float(x) > 0).sum()
    valid_bhk = df_blr['beds'].apply(lambda x: pd.notna(x) and int(x) > 0).sum()
    
    # Clean size/area
    def clean_area(a):
        if pd.isna(a): return 0
        s = str(a).strip().lower()
        if "-" in s:
            try:
                parts = [float(re.findall(r"[\d\.]+", p)[0]) for p in s.split("-") if p.strip()]
                return sum(parts) / len(parts)
            except:
                return 0
        try:
            return float(re.findall(r"[\d\.]+", s)[0])
        except:
            return 0
            
    valid_areas = df_blr['size'].apply(clean_area).apply(lambda x: x > 0).sum()
    valid_bathrooms = df_blr['baths'].apply(lambda x: pd.notna(x) and int(x) > 0).sum()
    
    # Amenities (not present in columns: url,beds,city,date,size,type,baths,price,neighborhood)
    valid_amenities = 0
    valid_descriptions = 0 # No description column
    valid_images = 0 # No images column
    valid_urls = df_blr['url'].apply(is_valid).sum()
    valid_coordinates = 0 # No lat/lon columns
    
    print("\nQuality Metrics:")
    print(f"Names: {valid_names}")
    print(f"Titles: {valid_titles}")
    print(f"Localities: {valid_localities}")
    print(f"Addresses: {valid_addresses}")
    print(f"Prices: {valid_prices}")
    print(f"BHK: {valid_bhk}")
    print(f"Areas: {valid_areas}")
    print(f"Bathrooms: {valid_bathrooms}")
    print(f"Amenities: {valid_amenities}")
    print(f"Descriptions: {valid_descriptions}")
    print(f"Images: {valid_images}")
    print(f"Urls: {valid_urls}")
    print(f"Coordinates: {valid_coordinates}")
    
    # Duplicate check
    # Combination 1: type + neighborhood + price + size
    df_blr['size_clean'] = df_blr['size'].apply(clean_area)
    dup_comb1 = df_blr.duplicated(subset=['type', 'neighborhood', 'price', 'size_clean'], keep=False)
    dup_comb1_count = dup_comb1.sum()
    
    # Combination 2: type + neighborhood + price
    dup_comb2 = df_blr.duplicated(subset=['type', 'neighborhood', 'price'], keep=False)
    dup_comb2_count = dup_comb2.sum()
    
    exact_duplicates = df_blr.duplicated(keep=False).sum()
    unique_usable = len(df_blr) - df_blr.duplicated().sum()
    
    print(f"\nDuplicates check:")
    print(f"Exact duplicates: {exact_duplicates}")
    print(f"Duplicate Comb 1 (name+loc+price+area): {dup_comb1_count}")
    print(f"Duplicate Comb 2 (title+loc+price): {dup_comb2_count}")
    print(f"Unique usable records: {unique_usable}")
    
    # Card Display Metric:
    # Requires: title/name, BHK, area, price, locality, property type
    # Since we have url, beds (BHK), size (area), price, neighborhood (locality), type (property type)
    # We have all these fields for records that have valid price, area, BHK, locality, type.
    usable_card_mask = (
        df_blr['beds'].apply(lambda x: pd.notna(x) and int(x) > 0) &
        df_blr['size'].apply(clean_area).apply(lambda x: x > 0) &
        df_blr['price'].apply(lambda x: pd.notna(x) and float(x) > 0) &
        df_blr['neighborhood'].apply(is_valid) &
        df_blr['type'].apply(is_valid)
    )
    usable_cards_count = usable_card_mask.sum()
    print(f"\nUsable for property cards: {usable_cards_count}")

if __name__ == "__main__":
    inspect()
