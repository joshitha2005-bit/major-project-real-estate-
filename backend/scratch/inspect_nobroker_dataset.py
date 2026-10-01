import pandas as pd
from app.core.database import SessionLocal
from app.models.property import Property

df_master = pd.read_csv('datasets/bengaluru_master_property_dataset.csv')
df_images = pd.read_csv('datasets/bengaluru_property_images.csv')

print("Master dataset count:", len(df_master))
print("Images dataset count:", len(df_images))

db = SessionLocal()

# Check first 5 rows of master
for idx in range(5):
    row = df_master.iloc[idx]
    blr_id = row['property_id']
    matching_imgs = df_images[df_images['property_id'] == blr_id]
    img_urls = matching_imgs['image_url'].tolist()
    print(f"Master {blr_id}: {row['property_name']} | Images in CSV: {len(img_urls)}")
    for u in img_urls:
        print(f"   {u}")

print("\n--- Matching DB Properties 16795 to 16805 ---")
for pid in range(16795, 16805):
    p = db.query(Property).filter(Property.id == pid).first()
    if p:
        print(f"DB ID {p.id}: {p.title} | Source: {p.source} | Stored imgs: {len(p.images or [])}")
        if p.images:
            for u in p.images:
                print(f"   {u}")
