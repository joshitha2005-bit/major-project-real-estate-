import os
import sys
import re

sys.path.insert(0, os.path.abspath('.'))
from app.core.database import SessionLocal
from app.models.property import Property

def extract_location(p: Property) -> str:
    addr = (p.address or "").strip()
    if addr and addr.lower() not in ["bengaluru", "bangalore"]:
        clean_addr = re.sub(r',\s*(bengaluru|bangalore|karnataka|560\d{3})\b', '', addr, flags=re.I).strip()
        if clean_addr:
            return clean_addr
    return (p.locality or "Bengaluru").title()

def is_anonymized_code(title: str) -> bool:
    if not title:
        return True
    t = title.strip()
    if "" in t or "—" in t or "BHK" in t or "Bedroom" in t:
        return True
    COMMON_WORDS = ["apartment", "flat", "villa", "house", "park", "green", "view", "heights", "residency", "nest", "layout", "garden", "enclave", "city", "town", "court", "palace", "manor", "bhk", "bedroom", "floor", "gated", "space", "field", "wood", "sky"]
    if re.match(r'^[A-Za-z0-9]{4,12}$', t):
        if not any(w in t.lower() for w in COMMON_WORDS):
            return True
    return False

def format_property_title_and_type(p: Property):
    loc_str = extract_location(p)
    raw_title = (p.title or "").strip()
    is_historical = (p.source_type == "historical_dataset" or p.source == "Bengaluru_House_Data.csv")
    
    REAL_BUILDERS = ["prestige", "sobha", "salarpuria", "brigade", "godrej", "assetz", "puravankara", "l&t", "embassy", "shriram", "mantri", "dharani", "signature", "century", "provident"]
    is_real_builder = any(b in raw_title.lower() for b in REAL_BUILDERS)
    
    if is_real_builder:
        title = raw_title
        society_val = raw_title
        ptype = p.property_type
    elif not is_historical and not is_anonymized_code(raw_title):
        title = raw_title
        society_val = raw_title
        ptype = p.property_type
    else:
        if "bedroom" in raw_title.lower() or (p.bhk and p.bhk > 4):
            size_str = f"{p.bhk} Bedroom"
        elif p.bhk and p.bhk > 0:
            size_str = f"{p.bhk} BHK"
        else:
            size_str = ""
            
        if size_str:
            title = f"{size_str} in {loc_str}"
        else:
            title = f"Property in {loc_str}"
            
        society_val = None
        ptype = "Not specified" if is_historical else p.property_type
            
    return title, loc_str, ptype, society_val

db = SessionLocal()
target_ids = [199, 352, 670, 688, 746, 760, 921, 935, 1171, 1195]
props = db.query(Property).filter(Property.id.in_(target_ids)).order_by(Property.id.asc()).all()

print("==================================================")
print("TESTING REFINED TITLE & LOCATION PREVIEW (10 HSR PROPERTIES)")
print("==================================================")
for p in props:
    title, loc, ptype, soc = format_property_title_and_type(p)
    print(f"ID {p.id:4d} | Raw Title: '{p.title:22s}' | Addr: '{p.address}'")
    print(f"         --> New Title: '{title}' | Loc: '{loc}' | Type: '{ptype}'")
    print("-" * 80)

db.close()
