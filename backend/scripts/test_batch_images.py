import csv, json, ssl, urllib.request, re, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

with open('backend/datasets/bengaluru_real_property_dataset.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total rows in dataset: {len(rows)}")

# Test fetching multiple images for 5 properties
for r in rows[:5]:
    lid = r['source_listing_id']
    surl = r['source_url']
    if surl and lid:
        try:
            req = urllib.request.Request(surl, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                pattern = rf'https://images\.nobroker\.in/images/{lid}/[^\s\"\'\\]+'
                raw_imgs = list(set(re.findall(pattern, html)))
                # Filter for valid medium/large jpgs
                valid_imgs = [img for img in raw_imgs if ('medium' in img or 'large' in img) and img.endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                print(f"Property {lid} ({r['locality']}): {len(valid_imgs)} images found")
                for img in valid_imgs[:3]:
                    print("   ", img)
        except Exception as e:
            print(f"Property {lid} failed: {e}")
        time.sleep(0.5)
