import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from bs4 import BeautifulSoup
import json, re

path = r'C:\Users\HP\.gemini\antigravity-ide\brain\bb1a7cda-5d58-4934-abd2-91f6e1beb51d\.system_generated\steps\1570\content.md'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
articles = soup.find_all('article')
print(f"Total articles in Koramangala page: {len(articles)}")

def parse_article(a, default_locality="Koramangala"):
    inner_div = a.find('div', itemscope=True)
    listing_id = inner_div.get('id', '') if inner_div else ''
    if not listing_id:
        listing_id = a.get('id', '')
        
    h2 = a.find('h2')
    title = h2.get_text(strip=True) if h2 else ''
    a_link = h2.find('a') if h2 else None
    rel_url = a_link.get('href', '') if a_link else ''
    source_url = f"https://www.nobroker.in{rel_url}" if rel_url.startswith('/') else rel_url
    
    # Meta elements
    metas = {}
    for m in a.find_all('meta'):
        prop = m.get('itemprop') or m.get('property') or m.get('name')
        val = m.get('content')
        if prop:
            metas[prop] = val
        elif val and 'Bengaluru' in val or 'Karnataka' in val:
            metas['address'] = val
            
    lat = float(metas.get('latitude')) if metas.get('latitude') else None
    lon = float(metas.get('longitude')) if metas.get('longitude') else None
    raw_address = metas.get('address') or metas.get('null') or ''
    
    # Image
    img_name = metas.get('image', '')
    if img_name and listing_id:
        img_url = f"https://images.nobroker.in/images/{listing_id}/{img_name}"
    else:
        img_url = None
        
    # Strings in article
    strings = [s.strip() for s in a.stripped_strings if s.strip()]
    
    # Extract price
    price_inr = None
    # Check numeric price in strings (e.g. '9900000', '23000000')
    for s in strings:
        if s.isdigit() and len(s) >= 6:
            price_inr = float(s)
            break
            
    # Extract price per sqft
    source_price_sqft = None
    for s in strings:
        m = re.search(r'₹\s*([\d,]+)\s*(?:per\s*sq\.?ft|/\s*sq\.?ft)', s, re.I)
        if m:
            source_price_sqft = float(m.group(1).replace(',', ''))
            break
            
    # Extract area
    area_sqft = None
    area_type = "Builtup"
    for idx, s in enumerate(strings):
        m = re.search(r'([\d,]+)\s*sqft', s, re.I)
        if m:
            area_sqft = float(m.group(1).replace(',', ''))
            if idx + 1 < len(strings) and strings[idx+1] in ['Builtup', 'Carpet', 'Super Builtup']:
                area_type = strings[idx+1]
            break
            
    # BHK
    bhk = 2
    bhk_match = re.search(r'(\d+)\+?\s*BHK', title, re.I)
    if bhk_match:
        bhk = int(bhk_match.group(1))
        
    # Facing
    facing = None
    for f in ['North', 'East', 'South', 'West', 'North-East', 'North-West', 'South-East', 'South-West']:
        if f in strings:
            facing = f
            break
            
    # Bathrooms
    bathrooms = bhk
    for idx, s in enumerate(strings):
        if s == 'Apartment Type' and idx + 1 < len(strings):
            cand = strings[idx + 1]
            if cand.isdigit():
                bathrooms = int(cand)
                break
                
    # Building / Project Name extraction
    # Titles often look like:
    # "2 BHK Flat In Bilden Swaraganga  For Sale  In Jakkasandra"
    # "3 BHK Apartment In Ngv Apartment For Sale In Koramangala"
    # "3 BHK Flat In Raheja Vivarea For Sale In Koramangala"
    # "4+ BHK House For Sale In Ejipura"
    project_name = None
    p_match = re.search(r'(?:Flat|Apartment|House|Villa)\s+In\s+(.*?)\s+For\s+Sale', title, re.I)
    if p_match:
        cand = p_match.group(1).strip()
        # If cand is generic like "Koramangala" or "Bangalore", it's not a building name
        if cand.lower() not in [default_locality.lower(), 'bangalore', 'bengaluru', 'ejipura', 'hsr layout']:
            project_name = cand
            
    # Property Type
    prop_type = "Apartment"
    if "House" in title or "Independent House" in raw_address:
        prop_type = "Independent House"
    elif "Villa" in title:
        prop_type = "Villa"
        
    # Calculate price per sqft
    calc_price_sqft = round(price_inr / area_sqft, 2) if (price_inr and area_sqft and area_sqft > 0) else None
    
    # Pincode
    pin_m = re.search(r'\b(560\d{3})\b', raw_address)
    pincode = pin_m.group(1) if pin_m else "560034"
    
    return {
        "listing_id": listing_id,
        "title": title,
        "building_name": project_name,
        "property_type": prop_type,
        "bhk": bhk,
        "bathrooms": bathrooms,
        "area_sqft": area_sqft,
        "area_type": area_type,
        "price_inr": price_inr,
        "source_price_sqft": source_price_sqft,
        "calc_price_sqft": calc_price_sqft,
        "facing": facing,
        "address": raw_address,
        "pincode": pincode,
        "latitude": lat,
        "longitude": lon,
        "source_url": source_url,
        "image_url": img_url
    }

for i in range(5):
    res = parse_article(articles[i])
    print(f"Record {i}:")
    print(json.dumps(res, indent=2))
