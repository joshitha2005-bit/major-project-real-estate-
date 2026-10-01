import httpx
import re
import json

url = 'https://www.nobroker.in/property/buy/4-bhk-apartment-for-sale-in--hsr-layout-bangalore/8a9faf849a307f49019a30b525f30c89/detail'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
r = httpx.get(url, headers=headers, follow_redirects=True, timeout=15.0)

print("Page status:", r.status_code)
# Search all img tags
img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', r.text)
print(f"Total <img> tags: {len(img_srcs)}")
nobroker_imgs = [s for s in img_srcs if 'images.nobroker.in' in s]
print(f"NoBroker images: {len(nobroker_imgs)}")
for s in set(nobroker_imgs):
    print("  ", s)

# Search for photos in JSON-LD
json_ld_matches = re.findall(r'<script type="application/ld\+json">([^<]+)</script>', r.text)
print(f"Total json-ld scripts: {len(json_ld_matches)}")
for idx, jld in enumerate(json_ld_matches):
    try:
        data = json.loads(jld)
        if isinstance(data, dict):
            photos = data.get('photo') or data.get('image') or []
            print(f"JSON-LD {idx} type={data.get('@type')}, images={photos}")
    except Exception as e:
        print(f"JSON-LD {idx} parse error: {e}")
