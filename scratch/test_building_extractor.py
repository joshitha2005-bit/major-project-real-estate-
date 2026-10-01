import re

def is_kaggle_hash_code(s: str) -> bool:
    if not s or not isinstance(s, str):
        return True
    t = s.strip()
    if not t or t.lower() in ["none", "null", "nan", ""]:
        return True
    COMMON_WORDS = [
        "apartment", "flat", "villa", "house", "park", "green", "view", 
        "heights", "residency", "nest", "layout", "garden", "enclave", 
        "city", "town", "court", "palace", "manor", "bhk", "bedroom", 
        "floor", "gated", "space", "field", "wood", "sky", "prestige", 
        "sobha", "salarpuria", "brigade", "godrej", "assetz", "puravankara", 
        "shriram", "provident", "embassy", "kolte", "sukhi", "scion", "icon", 
        "elgin", "casagrand", "homes", "habulus", "apoorva", "vrudhi"
    ]
    if any(w in t.lower() for w in COMMON_WORDS):
        return False
    if " " in t or "-" in t or "," in t or "." in t:
        return False
    if re.match(r'^[A-Z][a-z0-9]+[A-Z][a-z0-9]*$', t):
        return True
    if len(t) <= 8 and not any(v in t.lower() for v in ['a', 'e', 'i', 'o', 'u']):
        return True
    if re.match(r'^[A-Za-z0-9]{4,10}$', t) and not any(w in t.lower() for w in COMMON_WORDS):
        return True
    return False

def extract_genuine_building(s: str):
    if not s or not isinstance(s, str):
        return None
    raw = s.strip()
    if raw.lower() in ['nan', 'none', 'null', '']:
        return None
    if is_kaggle_hash_code(raw):
        return None
        
    BUILDING_KEYWORDS = [
        "apartment", "flat", "villa", "house", "park", "view", "heights", 
        "residency", "nest", "garden", "enclave", "court", "palace", "manor", 
        "prestige", "sobha", "salarpuria", "brigade", "godrej", "assetz", 
        "puravankara", "shriram", "provident", "embassy", "kolte", "sukhi", 
        "scion", "icon", "elgin", "nitesh", "prabhavathi", "vishwas", "gk", 
        "ss vrudhi", "clique", "casagrand", "springs", "terraces", "woodland",
        "paradise", "aura", "serenity", "churekh", "blossom", "lichen", "tranquil",
        "surabhi", "jade", "symphony"
    ]
    
    # If ends with Bangalore or Bengaluru, check if building name is in first part
    if re.search(r',\s*(bangalore|bengaluru)\b', raw, re.I):
        # Look for building before comma
        parts = [p.strip() for p in raw.split(',') if p.strip()]
        first_part = parts[0]
        if any(w in first_part.lower() for w in BUILDING_KEYWORDS):
            return first_part.title()
        return None
        
    # Check if raw string itself has building keywords
    if any(w in raw.lower() for w in BUILDING_KEYWORDS):
        return raw
        
    return None

test_cases = [
    "Scion Elite Apartments ,Byrasandra, C V Raman Nagar,Bangalore",
    "Sukhi Apartments Rhenius Street,Richmond Town,Bangalore",
    "Elgin Court",
    "Prestige Pinewood",
    "Embassy Lake Terraces",
    "Icon Iconest 3",
    "Shriram Blue",
    "Kolte Patil Raaga",
    "Phase 2, Bedarahalli,Bangalore",
    "Hoskote, Bangalore",
    "Kyathsandra, Bangalore",
    "Kanka Nagar, Kumaraswamy Layout,Bangalore",
    "Attibele, Bangalore",
    "Betatsi",
    "Prcan P",
    "GMown E",
    "Sobha Koramangala",
    "JANANI Appartment,AMS Layout, Vidyaranyapura,Bangalore",
    "SLM Paradise,East Of NGEF Layout, Kasturi Nagar,Bangalore"
]

print("TEST RESULTS:")
for t in test_cases:
    res = extract_genuine_building(t)
    print(f"'{t}' -> {res}")
