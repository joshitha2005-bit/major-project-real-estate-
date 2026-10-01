import sqlite3
import pandas as pd
import re

# Load Master CSV
df_master = pd.read_csv('backend/datasets/Bengaluru_Real_World_Property_Master.csv')
print(f"Master rows: {len(df_master)}")

# Load V21 CSV
df_v21 = pd.read_csv('backend/datasets/Real Estate Data V21.csv')
blr_v21 = df_v21[df_v21['Location'].str.contains('Bangalore|Bengaluru', case=False, na=False)]
print(f"V21 Bangalore rows: {len(blr_v21)}")

# Connect to DB
conn = sqlite3.connect('backend/real_estate.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM properties")
print("DB properties total:", cursor.fetchone()[0])
conn.close()
