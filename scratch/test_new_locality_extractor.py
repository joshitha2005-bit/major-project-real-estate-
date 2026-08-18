import sys, os, re
sys.path.insert(0, os.path.abspath('backend'))

from app.services.price_prediction_service import _KNOWN_LOCATIONS, _load_model

_load_model()

GENERIC_TOKENS = {
    "block", "phase", "sector", "stage", "road", "main", "street", 
    "layout", "extension", "cross", "near", "opp", "opposite", 
    "behind", "next", "bengaluru", "bangalore", "karnataka", "india"
}

def extract_locality_enhanced(address: str) -> str:
    """Extract and clean primary locality from address string with strict priority matching."""
    if not address or not isinstance(address, str):
        return "Other"

    # Normalize full address
    addr_clean = re.sub(r'[^\w\s]', ' ', address.lower())
    addr_clean = ' '.join(addr_clean.split())
    addr_nospace = addr_clean.replace(" ", "")

    if not _KNOWN_LOCATIONS:
        return "Other"

    sorted_known = sorted(list(_KNOWN_LOCATIONS), key=lambda loc: len(loc), reverse=True)

    # 1. Step 1: Check for exact word/phrase or spaceless phrase match in full address
    for loc in sorted_known:
        loc_norm = ' '.join(re.sub(r'[^\w\s]', ' ', loc.lower()).split())
        if not loc_norm or loc_norm in GENERIC_TOKENS:
            continue
        
        # Word boundary pattern search
        pattern = r'\b' + re.escape(loc_norm) + r'\b'
        if re.search(pattern, addr_clean):
            return loc

        # Spaceless pattern match for variants like "Indiranagar" vs "Indira Nagar"
        loc_nospace = loc_norm.replace(" ", "")
        if len(loc_nospace) >= 5 and loc_nospace in addr_nospace:
            return loc

    # 2. Step 2: Split address by commas and check non-generic tokens
    parts = [p.strip() for p in address.split(',') if p.strip()]
    for p in parts:
        clean_part = re.sub(r'[^\w\s]', ' ', p.lower())
        clean_words = [w for w in clean_part.split() if not w.isdigit() and w not in GENERIC_TOKENS]
        cleaned_token = ' '.join(clean_words)

        if len(cleaned_token) > 2:
            # Check for exact match in known locations
            for loc in sorted_known:
                loc_norm = ' '.join(re.sub(r'[^\w\s]', ' ', loc.lower()).split())
                if cleaned_token == loc_norm or cleaned_token.replace(" ", "") == loc_norm.replace(" ", ""):
                    return loc

            # Substring match ONLY if cleaned_token is NOT a generic token and >= 4 chars
            if len(cleaned_token) >= 4:
                for loc in sorted_known:
                    loc_norm = ' '.join(re.sub(r'[^\w\s]', ' ', loc.lower()).split())
                    if cleaned_token in loc_norm or loc_norm in cleaned_token:
                        return loc

    return "Other"

test_addresses = [
    "Block 1, Main Road, Koramangala, Bengaluru",
    "Block 2, Main Road, HSR Layout, Bengaluru",
    "Phase 1, Electronic City, Bengaluru",
    "Koramangala 4th Block, Bengaluru",
    "Whitefield Main Road, Bengaluru",
    "Indiranagar 100 Feet Road, Bengaluru",
    "Unknown locality that does not exist in training data"
]

print("=== TESTING ENHANCED LOCALITY EXTRACTION LOGIC ===")
for addr in test_addresses:
    res = extract_locality_enhanced(addr)
    print(f"Address: '{addr}'\n  ==> Extracted: '{res}'\n")
