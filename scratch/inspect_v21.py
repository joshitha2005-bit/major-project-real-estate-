import pandas as pd
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('backend/datasets/Real Estate Data V21.csv')
print(f"Total rows in V21: {len(df)}")
print("Sample rows:")
for i in range(15):
    row = df.iloc[i]
    print(f"Name: {row['Name']} | Title: {row['Property Title']} | Location: {row['Location']}")
