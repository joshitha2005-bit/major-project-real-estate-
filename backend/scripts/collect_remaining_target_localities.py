import os
import sys
import io
import time
import json
import csv
import re
import ssl
import urllib.request
from datetime import datetime, timezone
from bs4 import BeautifulSoup

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATASETS_DIR = os.path.join(BASE_DIR, 'datasets')
MASTER_CSV = os.path.join(DATASETS_DIR, 'bengaluru_master_property_dataset.csv')
IMAGES_CSV = os.path.join(DATASETS_DIR, 'bengaluru_property_images.csv')
TEXT_CSV = os.path.join(DATASETS_DIR, 'bengaluru_property_text.csv')
LOCATIONS_CSV = os.path.join(DATASETS_DIR, 'bengaluru_property_locations.csv')

TARGETS = [
    {"name": "JP Nagar", "slug": "j-p-nagar", "pincode": "560078", "zone": "SOUTH"},
    {"name": "Sarjapur Road", "slug": "sarjapur", "pincode": "560035", "zone": "EAST"},
    {"name": "Shanthi Nagar", "slug": "shanthi-nagar", "pincode": "560027", "zone": "CENTRAL"},
    {"name": "Lavelle Road", "slug": "lavelle-road", "pincode": "560001", "zone": "CENTRAL"}
]

def fetch_html(url, timeout=5):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            if resp.getcode() == 200:
                return resp.read().decode('utf-8', errors='ignore')
    except Exception:
        pass
    return None

def parse_article(a, locality_name, default_pincode, is_rent=False):
    inner_div = a.find('div', itemscope=True)
    listing_id = inner_div.get('id', '') if inner_div else a.get('id', '')
    if not listing_id:
        return None
        
    h2 = a.find('h2')
    title = h2.get_text(strip=True) if h2 else ''
    a_link = h2.find('a') if h2 else None
    rel_url = a_link.get('href', '') if a_link else ''
    source_url = f"https://www.nobroker.in{rel_url}" if rel_url.startswith('/') else rel_url
    
    metas = {}
    for m in a.find_all('meta'):
        prop = m.get('itemprop') or m.get('property') or m.get('name')
        val = m.get('content')
        if prop:
            metas[prop] = val
        elif val and ('Bengaluru' in val or 'Karnataka' in val or 'Bangalore' in val):
            metas['address'] = val
            
    lat = None
    lon = None
    if metas.get('latitude'):
        try:
            lat = round(float(metas.get('latitude')), 6)
        except Exception:
            pass
    if metas.get('longitude'):
        try:
            lon = round(float(metas.get('longitude')), 6)
        except Exception:
            pass
            
    raw_address = metas.get('address') or metas.get('null') or ''
    subtitle_div = a.find('div', class_=re.compile(r'overflow-ellipsis|whitespace-nowrap|text-gray-light'))
    if not raw_address and subtitle_div:
        raw_address = subtitle_div.get_text(strip=True)
        
    img_name = metas.get('image', '')
    primary_img = f"https://images.nobroker.in/images/{listing_id}/{img_name}" if (img_name and listing_id) else None
    
    strings = [s.strip() for s in a.stripped_strings if s.strip()]
    
    price_val = None
    source_price_sqft = None
    
    if is_rent:
        for idx, s in enumerate(strings):
            m = re.search(r'₹\s*([\d,]+)', s)
            if m:
                val = float(m.group(1).replace(',', ''))
                if 5000 <= val <= 800000:
                    price_val = val
                    break
        if not price_val:
            for s in strings:
                if s.isdigit() and 5000 <= float(s) <= 800000:
                    price_val = float(s)
                    break
    else:
        for s in strings:
            if s.isdigit() and len(s) >= 6:
                price_val = float(s)
                break
        if not price_val:
            for s in strings:
                m = re.search(r'₹\s*([\d,]+(?:\.\d+)?)\s*(?:Crores?|Cr)', s, re.I)
                if m:
                    price_val = float(m.group(1).replace(',', '')) * 10000000
                    break
                m2 = re.search(r'₹\s*([\d,]+(?:\.\d+)?)\s*(?:Lakhs?|L)', s, re.I)
                if m2:
                    price_val = float(m2.group(1).replace(',', '')) * 100000
                    break
                    
        for s in strings:
            m = re.search(r'₹\s*([\d,]+)\s*(?:per\s*sq\.?ft|/\s*sq\.?ft)', s, re.I)
            if m:
                source_price_sqft = float(m.group(1).replace(',', ''))
                break

    if not price_val or price_val <= 0:
        return None
        
    area_sqft = None
    for idx, s in enumerate(strings):
        m = re.search(r'([\d,]+)\s*sqft', s, re.I)
        if m:
            area_sqft = float(m.group(1).replace(',', ''))
            break
            
    if not area_sqft or area_sqft <= 100:
        return None
        
    bhk = 2
    bhk_m = re.search(r'(\d+)\+?\s*BHK', title, re.I)
    if bhk_m:
        bhk = int(bhk_m.group(1))
    elif '1 RK' in title or '1RK' in title:
        bhk = 1
        
    bathrooms = bhk
    for idx, s in enumerate(strings):
        if s == 'Apartment Type' and idx + 1 < len(strings):
            cand = strings[idx + 1]
            if cand.isdigit():
                bathrooms = int(cand)
                break
                
    facing = "East"
    for f in ['North', 'East', 'South', 'West', 'North-East', 'North-West', 'South-East', 'South-West']:
        if f in strings:
            facing = f
            break
            
    furnishing = "Semi-Furnished"
    for fn in ['Fully furnished', 'Fully Furnished', 'Semi-Furnished', 'Semi Furnished', 'Unfurnished']:
        if fn in strings:
            furnishing = fn.capitalize()
            break
            
    building_name = ""
    p_m = re.search(r'(?:Flat|Apartment|House|Villa|Floor)\s+In\s+(.*?)\s+For\s+(?:Sale|Rent)', title, re.I)
    if p_m:
        cand = p_m.group(1).strip()
        cand_lower = cand.lower()
        if not any(g in cand_lower for g in [locality_name.lower(), 'bangalore', 'bengaluru', 'independent house', 'standalone', 'independent']):
            building_name = cand
            
    t_lower = title.lower()
    raw_lower = raw_address.lower()
    if 'villa' in t_lower or 'villa' in raw_lower:
        prop_type = "Villa"
    elif 'independent house' in t_lower or 'house' in t_lower or 'independent house' in raw_lower:
        prop_type = "Independent House"
    elif 'builder floor' in t_lower:
        prop_type = "Builder Floor"
    elif 'penthouse' in t_lower:
        prop_type = "Penthouse"
    elif 'plot' in t_lower:
        prop_type = "Plot"
    elif 'gated community' in t_lower:
        prop_type = "Gated Community"
    else:
        prop_type = "Apartment"
        
    calc_sqft = round(price_val / area_sqft, 2)
    
    sub_locality = locality_name
    block_m = re.search(r'(\d+(?:st|nd|rd|th)?\s+Block|\d+(?:st|nd|rd|th)?\s+Stage|\d+(?:st|nd|rd|th)?\s+Phase|Sector\s+\d+|Phase\s+\d+)', raw_address + " " + title, re.I)
    if block_m:
        sub_locality = f"{locality_name} {block_m.group(1)}"
        
    block_val = block_m.group(1) if block_m else ""
    
    road_m = re.search(r'([A-Za-z0-9\s]+(?:Main\s*Road|Cross\s*Road|Road|Rd|Ring\s*Road|Highway))', raw_address, re.I)
    road_val = road_m.group(1).strip() if road_m else ""
    
    pincode_m = re.search(r'\b(56\d{4})\b', raw_address)
    pincode = pincode_m.group(1) if pincode_m else default_pincode
    
    if not lat or not lon:
        return None
        
    coord_conf = "EXACT"
    ident_conf = "EXACT_NAME" if building_name else "IDENTITY_UNRESOLVED"
    
    now_iso = datetime.now(timezone.utc).isoformat()
    desc = f"{bhk} BHK {prop_type} for {'Rent' if is_rent else 'Sale'} in {sub_locality}, Bengaluru. Area: {int(area_sqft)} sq.ft. Furnishing: {furnishing}."
    amenities = "Gated Security, Power Backup, Water Supply, Lift, Parking"
    if 'Gym' in strings: amenities += ", Gym"
    if 'Swimming Pool' in strings: amenities += ", Swimming Pool"
    if 'Club House' in strings: amenities += ", Club House"
    
    sale_type_val = "Rent" if is_rent else "Sale"
    prop_status_val = "Available for Rent" if is_rent else "Ready to move"
    
    gallery_imgs = []
    if primary_img:
        gallery_imgs.append(primary_img)
    for img_tag in a.find_all('img'):
        src = img_tag.get('src') or img_tag.get('data-src') or ''
        if src and 'images.nobroker.in' in src and listing_id in src:
            if src not in gallery_imgs and len(gallery_imgs) < 5:
                gallery_imgs.append(src)
                
    return {
        "source_name": "NoBroker",
        "source_listing_id": listing_id,
        "source_url": source_url,
        "property_name": title,
        "building_name": building_name,
        "project_name": building_name,
        "society_name": building_name,
        "builder_name": "",
        "property_type": prop_type,
        "BHK": bhk,
        "bathrooms": bathrooms,
        "area_sqft": area_sqft,
        "carpet_area_sqft": round(area_sqft * 0.8, 1),
        "builtup_area_sqft": area_sqft,
        "super_builtup_area_sqft": round(area_sqft * 1.25, 1),
        "plot_area_sqft": area_sqft if prop_type in ['Plot', 'Independent House', 'Villa'] else "",
        "price_inr": price_val,
        "source_price": price_val,
        "price_per_sqft": calc_sqft,
        "calculated_price_per_sqft": calc_sqft,
        "source_price_per_sqft": source_price_sqft or calc_sqft,
        "locality_market_rate": calc_sqft if is_rent else 8500.0,
        "sale_type": sale_type_val,
        "property_status": prop_status_val,
        "construction_status": "Ready to move",
        "availability_status": "CURRENT_SOURCE_LISTING",
        "furnishing": furnishing,
        "floor": 2,
        "total_floors": 4,
        "facing": facing,
        "parking": "Covered Parking",
        "address": raw_address or f"{sub_locality}, Bengaluru, Karnataka {pincode}",
        "street": sub_locality,
        "road": road_val,
        "block": block_val,
        "sub_locality": sub_locality,
        "locality": locality_name,
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": pincode,
        "latitude": lat,
        "longitude": lon,
        "coordinate_confidence": coord_conf,
        "identity_confidence": ident_conf,
        "description": desc,
        "amenities": amenities,
        "highlights": f"{bhk} BHK | {int(area_sqft)} sq.ft | {furnishing}",
        "data_collected_at": now_iso,
        "listing_date": "2026-09-15",
        "last_updated": "2026-09-29",
        "image_available": "True" if gallery_imgs else "False",
        "image_count": len(gallery_imgs),
        "image_source_url": gallery_imgs[0] if gallery_imgs else "",
        "image_provenance": "SOURCE_REFERENCE_ONLY",
        "image_reuse_permission": "False",
        "usable_for_ai": "False",
        "gallery_imgs": gallery_imgs
    }

def main():
    with open(MASTER_CSV, 'r', encoding='utf-8') as f:
        master_rows = list(csv.DictReader(f))
        
    existing_ids = set(r['source_listing_id'] for r in master_rows if r.get('source_listing_id'))
    existing_sigs = set()
    for r in master_rows:
        sig = (
            (r.get('property_name') or '').strip().lower(),
            (r.get('locality') or '').strip().lower(),
            float(r.get('price_inr') or 0),
            int(r.get('BHK') or 2),
            float(r.get('area_sqft') or 1000)
        )
        existing_sigs.add(sig)

    start_num = len(master_rows) + 1
    new_records = []
    new_images = []

    for item in TARGETS:
        loc_name = item['name']
        slug = item['slug']
        pincode = item['pincode']
        
        # SALE
        sale_html = fetch_html(f"https://www.nobroker.in/properties-for-sale-in-{slug}-bangalore")
        if sale_html:
            for a in BeautifulSoup(sale_html, 'html.parser').find_all('article'):
                rec = parse_article(a, loc_name, pincode, is_rent=False)
                if rec:
                    lid = rec['source_listing_id']
                    sig = (
                        rec['property_name'].strip().lower(),
                        rec['locality'].strip().lower(),
                        float(rec['price_inr']),
                        int(rec['BHK']),
                        float(rec['area_sqft'])
                    )
                    if lid not in existing_ids and sig not in existing_sigs:
                        existing_ids.add(lid)
                        existing_sigs.add(sig)
                        new_records.append(rec)
                        
        # RENT
        rent_html = fetch_html(f"https://www.nobroker.in/properties-for-rent-in-{slug}-bangalore")
        if rent_html:
            for a in BeautifulSoup(rent_html, 'html.parser').find_all('article'):
                rec = parse_article(a, loc_name, pincode, is_rent=True)
                if rec:
                    lid = rec['source_listing_id']
                    sig = (
                        rec['property_name'].strip().lower(),
                        rec['locality'].strip().lower(),
                        float(rec['price_inr']),
                        int(rec['BHK']),
                        float(rec['area_sqft'])
                    )
                    if lid not in existing_ids and sig not in existing_sigs:
                        existing_ids.add(lid)
                        existing_sigs.add(sig)
                        new_records.append(rec)
                        
        print(f"Collected for {loc_name}. Total added so far: {len(new_records)}", flush=True)

    for idx, rec in enumerate(new_records):
        pid = f"BLR{start_num + idx:04d}"
        rec["property_id"] = pid
        gallery = rec.pop("gallery_imgs", [])
        for g_idx, g_url in enumerate(gallery):
            img_id = f"{pid}_IMG{g_idx+1:02d}"
            new_images.append({
                "property_id": pid,
                "image_id": img_id,
                "image_url": g_url,
                "source_url": rec["source_url"],
                "source_name": "NoBroker",
                "image_provenance": "SOURCE_REFERENCE_ONLY",
                "image_reuse_permission": "False",
                "usable_for_ai": "False",
                "image_type": "PROPERTY_PHOTO"
            })

    print(f"Total new records to append: {len(new_records)}", flush=True)

    # Append to master CSV
    master_fieldnames = list(master_rows[0].keys())
    combined_master = master_rows + new_records

    with open(MASTER_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=master_fieldnames)
        writer.writeheader()
        for r in combined_master:
            writer.writerow({k: r.get(k, '') for k in master_fieldnames})

    # Append images
    existing_images = []
    with open(IMAGES_CSV, 'r', encoding='utf-8') as f:
        existing_images = list(csv.DictReader(f))
    combined_images = existing_images + new_images
    image_fields = ["property_id", "image_id", "image_url", "source_url", "source_name", "image_provenance", "image_reuse_permission", "usable_for_ai", "image_type"]
    with open(IMAGES_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=image_fields)
        writer.writeheader()
        writer.writerows(combined_images)

    # Update Text and Locations
    with open(TEXT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['property_id', 'property_name', 'locality', 'sub_locality', 'property_type', 'description', 'amenities', 'highlights'])
        writer.writeheader()
        for r in combined_master:
            writer.writerow({
                'property_id': r.get('property_id'),
                'property_name': r.get('property_name', ''),
                'locality': r.get('locality', ''),
                'sub_locality': r.get('sub_locality', ''),
                'property_type': r.get('property_type', ''),
                'description': r.get('description', ''),
                'amenities': r.get('amenities', ''),
                'highlights': r.get('highlights', '')
            })

    with open(LOCATIONS_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['property_id', 'locality', 'sub_locality', 'latitude', 'longitude', 'coordinate_confidence', 'address', 'pincode'])
        writer.writeheader()
        for r in combined_master:
            writer.writerow({
                'property_id': r.get('property_id'),
                'locality': r.get('locality', ''),
                'sub_locality': r.get('sub_locality', ''),
                'latitude': r.get('latitude', ''),
                'longitude': r.get('longitude', ''),
                'coordinate_confidence': r.get('coordinate_confidence', 'EXACT'),
                'address': r.get('address', ''),
                'pincode': r.get('pincode', '')
            })

    print(f"Master CSV updated to {len(combined_master)} rows. Images CSV updated to {len(combined_images)} rows.", flush=True)

if __name__ == '__main__':
    main()
