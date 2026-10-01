import pandas as pd

df = pd.read_csv('backend/datasets/Bengaluru_Real_World_Property_Master.csv')
v21 = df[df['source_name'] == 'Real Estate Data V21.csv']
print(f'Total V21 rows in Master: {len(v21)}')
print('V21 project_name not null:', v21['project_name'].notna().sum())
print('Sample 20 V21 in Master:')
for idx, r in v21[['property_id', 'project_name', 'locality', 'sub_locality', 'address']].head(25).iterrows():
    p_name = r['project_name']
    loc = r['locality']
    sub = r['sub_locality']
    print(f"ID {r['property_id']}: proj='{p_name}' | loc='{loc}' | sub='{sub}'")
