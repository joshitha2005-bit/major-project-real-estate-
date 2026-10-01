import pandas as pd
import os
import json

# Inspect Real Estate Data V21.csv
v21_path = r"c:\major real estate\backend\datasets\Real Estate Data V21.csv"
if os.path.exists(v21_path):
    df_v21 = pd.read_csv(v21_path, low_memory=False)
    print("=== Real Estate Data V21.csv ===")
    print("Total rows:", len(df_v21))
    
    # Filter for Bengaluru / Bangalore
    bengaluru_mask = df_v21['Location'].astype(str).str.contains('Bangalore|Bengaluru', case=False, na=False) | \
                     df_v21['Property Title'].astype(str).str.contains('Bangalore|Bengaluru', case=False, na=False) | \
                     df_v21['Description'].astype(str).str.contains('Bangalore|Bengaluru', case=False, na=False)
    df_bblr_v21 = df_v21[bengaluru_mask]
    print("Bengaluru rows:", len(df_bblr_v21))
    print("Sample Bengaluru Locations:", df_bblr_v21['Location'].unique()[:10])

# Inspect real_estate_dataset.csv
re_path = r"c:\major real estate\backend\datasets\real_estate_dataset.csv"
if os.path.exists(re_path):
    df_re = pd.read_csv(re_path, low_memory=False)
    print("\n=== real_estate_dataset.csv ===")
    print("Total rows:", len(df_re))
    print("Cities:", df_re['city'].value_counts().to_dict())
    print("Unique Neighborhoods:", df_re['neighborhood'].nunique())
    print("Price range:", df_re['price'].min(), "to", df_re['price'].max())
    print("Beds distribution:", df_re['beds'].value_counts().to_dict())
    print("Property types:", df_re['type'].value_counts().to_dict())
    print("Date min/max:", df_re['date'].min(), "to", df_re['date'].max())
    print("URLs with http:", df_re['url'].astype(str).str.startswith('http').sum())
