import os
import pandas as pd
import glob
import json

datasets_dir = r"c:\major real estate\backend\datasets"
archive_dir = r"c:\major real estate\backend\archive"

files = glob.glob(os.path.join(datasets_dir, "*")) + glob.glob(os.path.join(archive_dir, "*"))

report = {}

for f in files:
    if os.path.isdir(f):
        sub_files = glob.glob(os.path.join(f, "*"))
        files.extend(sub_files)
        continue
    if not (f.endswith('.csv') or f.endswith('.zip') or f.endswith('.xlsx')):
        continue
    
    file_basename = os.path.basename(f)
    print(f"\n--- Inspecting {f} ---")
    size_mb = os.path.getsize(f) / (1024 * 1024)
    print(f"Size: {size_mb:.2f} MB")
    
    if f.endswith('.csv'):
        try:
            df = pd.read_csv(f, low_memory=False)
            total_rows = len(df)
            cols = list(df.columns)
            print(f"Total Rows: {total_rows}")
            print(f"Columns: {cols[:20]}")
            
            # Check for image columns
            img_cols = [c for c in cols if any(k in c.lower() for k in ['image', 'photo', 'picture', 'url', 'thumb', 'gallery'])]
            print(f"Image-related columns: {img_cols}")
            
            # Check for locality / location columns
            loc_cols = [c for c in cols if any(k in c.lower() for k in ['location', 'locality', 'area', 'address', 'city'])]
            print(f"Locality-related columns: {loc_cols}")
            
            # Check BHK / Size / Type / Price
            bhk_cols = [c for c in cols if any(k in c.lower() for k in ['bhk', 'bed', 'room', 'size'])]
            price_cols = [c for c in cols if any(k in c.lower() for k in ['price', 'cost', 'amount', 'val'])]
            coord_cols = [c for c in cols if any(k in c.lower() for k in ['lat', 'lon', 'coord'])]
            owner_cols = [c for c in cols if any(k in c.lower() for k in ['owner', 'agent', 'contact', 'seller', 'posted', 'user', 'name', 'phone'])]
            date_cols = [c for c in cols if any(k in c.lower() for k in ['date', 'time', 'listed', 'posted', 'created', 'updated'])]
            
            print(f"BHK cols: {bhk_cols}")
            print(f"Price cols: {price_cols}")
            print(f"Coord cols: {coord_cols}")
            print(f"Owner cols: {owner_cols}")
            print(f"Date cols: {date_cols}")
            
            # Check sample values
            sample = df.head(3).to_dict(orient='records')
            print("Sample row 0:", json.dumps(sample[0] if sample else {}, default=str))
            
        except Exception as e:
            print(f"Error reading {f}: {e}")
