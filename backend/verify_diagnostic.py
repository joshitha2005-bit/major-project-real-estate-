import sqlite3
import json

conn = sqlite3.connect('real_estate.db')
cursor = conn.cursor()

# Get 10 different property IDs across different source types to verify
cursor.execute("SELECT id, title, locality, price, bhk, area_sqft, images, source_type, source FROM properties ORDER BY id ASC LIMIT 10")
rows = cursor.fetchall()

print(f"{'ID':<6} | {'Title':<45} | {'Locality':<18} | {'Price':<12} | {'BHK':<4} | {'Area':<8} | {'Image Preview':<50}")
print("-" * 150)
for r in rows:
    pid, title, locality, price, bhk, area, images_json, source_type, source = r
    images = json.loads(images_json) if images_json else []
    # Check fallback logic
    is_historical = source_type == 'historical_dataset' or source == 'Bengaluru_House_Data.csv'
    img_val = "FALLBACK_IMAGE" if (is_historical or not images) else images[0]
    title_short = (title[:42] + "...") if len(title) > 45 else title
    img_val_short = (img_val[:47] + "...") if len(img_val) > 50 else img_val
    print(f"{pid:<6} | {title_short:<45} | {locality:<18} | {price:<12.1f} | {bhk:<4} | {area:<8.1f} | {img_val_short:<50}")

conn.close()
