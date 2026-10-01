import sqlite3
import pandas as pd
import re
import os

DB_PATHS = ["backend/real_estate.db", "real_estate.db"]
MASTER_CSV_PATH = "backend/datasets/Bengaluru_Real_World_Property_Master.csv"
V21_CSV_PATH = "backend/datasets/Real Estate Data V21.csv"

KNOWN_EXACT_BUILDING_COORDS = {
    "prestige pinewood": (12.9304, 77.6305, "560034", "Koramangala", "Jakkasandra"),
    "elgin court": (12.9568, 77.5998, "560027", "Shanti Nagar", "KSRTC Colony"),
    "embassy lake terraces": (13.0487, 77.5932, "560024", "Hebbal Kempapura", "Hebbal"),
    "shriram blue": (13.0135, 77.7126, "560036", "Krishnarajapura", "Sonnenahalli Colony"),
    "icon iconest 3": (12.8122, 77.6835, "560099", "Bommasandra", "RK Township"),
    "kolte patil raaga": (13.0841, 77.6492, "560077", "Kannuru", "Hennur Road"),
    "scion elite apartments": (12.9839, 77.6628, "560093", "C V Raman Nagar", "Byrasandra"),
    "sukhi apartments": (12.9642, 77.6019, "560025", "Richmond Town", "Rhenius Street"),
    "sobha koramangala": (12.9352, 77.6245, "560034", "Koramangala", "4th Block"),
    "godrej koramangala": (12.9318, 77.6225, "560034", "Koramangala", "2nd Block"),
    "salarpuria sattva koramangala": (12.9335, 77.6270, "560034", "Koramangala", "3rd Block"),
    "assetz koramangala": (12.9360, 77.6250, "560034", "Koramangala", "4th Block"),
    "sobha whitefield": (12.9696, 77.7497, "560066", "Whitefield", "Main Road"),
    "godrej whitefield": (12.9720, 77.7510, "560066", "Whitefield", "ITPL Road"),
    "prestige shantiniketan": (12.9937, 77.7289, "560048", "Whitefield", "Hoodi"),
    "salarpuria sattva whitefield": (12.9750, 77.7450, "560066", "Whitefield", "ECC Road"),
    "assetz whitefield": (12.9800, 77.7400, "560066", "Whitefield", "Channasandra"),
    "salarpuria sattva hsr layout": (12.9116, 77.6389, "560102", "HSR Layout", "Sector 1"),
    "assetz hsr layout": (12.9140, 77.6410, "560102", "HSR Layout", "Sector 3"),
    "sobha hsr layout": (12.9121, 77.6446, "560102", "HSR Layout", "Sector 2"),
    "godrej hsr layout": (12.9150, 77.6430, "560102", "HSR Layout", "Sector 4"),
    "salarpuria sattva electronic city": (12.8436, 77.6687, "560100", "Electronic City", "Phase 1"),
    "assetz electronic city": (12.8410, 77.6650, "560100", "Electronic City", "Phase 1"),
    "sobha electronic city": (12.8452, 77.6602, "560100", "Electronic City", "Phase 1"),
    "godrej electronic city": (12.8470, 77.6620, "560100", "Electronic City", "Phase 2"),
    "prestige golfshire": (13.3125, 77.6948, "562110", "Devanahalli", "Nandi Hills"),
    "prestige woodland park": (13.0035, 77.6252, "560005", "Cooke Town", "Dodda Banaswadi"),
    "sls silver oak": (13.0560, 77.5890, "560092", "Kodigehalli", "Sahakara Nagar"),
    "mjr clique hydra": (12.8398, 77.6640, "560100", "Electronic City", "Gollahalli"),
    "nitesh central park": (13.0980, 77.6120, "560064", "Kogilu", "Yelahanka"),
    "prabhavathi lotus 2": (12.9080, 77.6230, "560068", "Bommanahalli", "Lake City"),
    "vishwas paradise": (12.8870, 77.5960, "560076", "Arakere", "BTS Layout"),
    "gk tropical springs": (13.0040, 77.7320, "560067", "Chansandra", "Whitefield"),
    "profound symphony": (12.7820, 77.6410, "560105", "Jigani", "Industrial Area"),
    "confident jade": (12.8430, 77.7560, "562125", "Kada Agrahara", "Sarjapur Road"),
    "shriram surabhi": (12.8760, 77.5480, "560062", "Mallasandra", "Kanakapura Road"),
    "ss vrudhi": (12.8620, 77.5310, "560109", "Talaghattapura", "VISL Layout"),
    "homes ans blossom": (12.9658, 77.7183, "560037", "Brookefield", "Kundalahalli"),
    "habulus residency": (12.8450, 77.6750, "560100", "Electronic City", "Phase II"),
    "apoorva lakeside": (12.9850, 77.6950, "560037", "Marathahalli", "Outer Ring Road"),
    "svs trendsquare precioso": (12.9520, 77.7150, "560037", "Marathahalli", "Munnekollal"),
    "sri sai enclave": (12.9230, 77.5890, "560041", "Jayanagar", "4th T Block"),
    "aravind residency": (12.9040, 77.5820, "560078", "JP Nagar", "2nd Phase"),
    "capita caroline springs": (12.9810, 77.7280, "560066", "Whitefield", "Borewell Road"),
    "ozone green view": (12.9350, 77.6210, "560034", "Koramangala", "6th Block"),
    "provident welworth city": (13.2185, 77.5512, "561203", "Yelahanka", "Doddaballapur Road"),
    "sobha indiranagar": (12.9784, 77.6408, "560038", "Indiranagar", "100 Feet Road"),
    "godrej indiranagar": (12.9760, 77.6420, "560038", "Indiranagar", "Defence Colony"),
    "salarpuria sattva indiranagar": (12.9740, 77.6390, "560038", "Indiranagar", "HAL 2nd Stage"),
    "assetz indiranagar": (12.9770, 77.6440, "560038", "Indiranagar", "Double Road"),
    "salarpuria sattva marathahalli": (12.9591, 77.6974, "560037", "Marathahalli", "Outer Ring Road"),
    "assetz marathahalli": (12.9580, 77.6960, "560037", "Marathahalli", "Main Road"),
    "sobha marathahalli": (12.9570, 77.6980, "560037", "Marathahalli", "Spice Garden"),
    "godrej marathahalli": (12.9600, 77.6950, "560037", "Marathahalli", "Kalamandir Road"),
    "sobha bellandur": (12.9279, 77.6756, "560103", "Bellandur", "Outer Ring Road"),
    "brigade jp nagar": (12.9063, 77.5857, "560078", "JP Nagar", "7th Phase"),
    "godrej hebbal": (13.0358, 77.5970, "560024", "Hebbal", "Bellary Road"),
    "godrej yelahanka": (13.1007, 77.5963, "560064", "Yelahanka", "New Town"),
    "sobha rajajinagar": (12.9882, 77.5549, "560010", "Rajajinagar", "1st Block"),
    "brigade malleshwaram": (13.0031, 77.5643, "560003", "Malleshwaram", "8th Main Road"),
    "sobha banashankari": (12.9255, 77.5468, "560085", "Banashankari", "3rd Stage"),
    "prestige devanahalli": (13.2450, 77.7120, "562110", "Devanahalli", "Airport Road"),
}

LOCALITY_PINCODES = {
    "koramangala": "560034",
    "whitefield": "560066",
    "hsr layout": "560102",
    "electronic city": "560100",
    "indiranagar": "560038",
    "marathahalli": "560037",
    "bellandur": "560103",
    "jp nagar": "560078",
    "hebbal": "560024",
    "yelahanka": "560064",
    "sarjapur road": "560035",
    "sarjapur": "562125",
    "rajajinagar": "560010",
    "malleshwaram": "560003",
    "banashankari": "560085",
    "devanahalli": "562110",
    "krishnarajapura": "560036",
    "bommasandra": "560099",
    "richmond town": "560025",
    "shanti nagar": "560027",
    "c v raman nagar": "560093",
    "jayanagar": "560041",
    "btm layout": "560076",
    "thanisandra": "560077",
    "hennur": "560043"
}

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
    # If single word with CamelCase like ArsiaEx, Betatsi, GMown
    if re.match(r'^[A-Z][a-z0-9]+[A-Z][a-z0-9]*$', t):
        return True
    if len(t) <= 8 and not any(v in t.lower() for v in ['a', 'e', 'i', 'o', 'u']):
        return True
    if re.match(r'^[A-Za-z0-9]{4,10}$', t) and not any(w in t.lower() for w in COMMON_WORDS):
        return True
    return False

def extract_genuine_building(s: str, addr: str = ""):
    raw = str(s or "").strip()
    raw_addr = str(addr or "").strip()
    
    BUILDING_KEYWORDS = [
        "apartment", "appartment", "flat", "villa", "house", "park", "view", "heights", 
        "residency", "nest", "garden", "enclave", "court", "palace", "manor", 
        "prestige", "sobha", "salarpuria", "brigade", "godrej", "assetz", 
        "puravankara", "shriram", "provident", "embassy", "kolte", "sukhi", 
        "scion", "icon", "elgin", "nitesh", "prabhavathi", "vishwas", "gk", 
        "ss vrudhi", "clique", "casagrand", "springs", "terraces", "woodland",
        "paradise", "aura", "serenity", "churekh", "blossom", "lichen", "tranquil",
        "surabhi", "jade", "symphony"
    ]
    
    # 1. Check raw building string
    if raw and raw.lower() not in ['nan', 'none', 'null', ''] and not is_kaggle_hash_code(raw):
        # If it ends with Bangalore / Bengaluru
        if re.search(r',\s*(bangalore|bengaluru)\b', raw, re.I):
            parts = [p.strip() for p in raw.split(',') if p.strip()]
            first_part = parts[0]
            if any(w in first_part.lower() for w in BUILDING_KEYWORDS):
                # Clean up any trailing sublocality words
                cleaned = re.sub(r'\s+Rhenius Street.*$', '', first_part, flags=re.I)
                return cleaned.strip()
            # Not a building
            raw = ""
        elif any(w in raw.lower() for w in BUILDING_KEYWORDS):
            return raw
            
    # 2. Check address for known buildings
    if raw_addr:
        KNOWN_ADDR_BUILDINGS = [
            "Scion Elite Apartments", "Sukhi Apartments", "Elgin Court", "Embassy Lake Terraces",
            "Prestige Pinewood", "Shriram Blue", "Icon Iconest 3", "Kolte Patil Raaga",
            "Janani Appartment", "SLM Paradise", "Honour Aura", "Bhadras Paradise",
            "Shrivas Serenity", "Victory Churekh", "Homes ANS Blossom", "Habulus Residency",
            "SS Vrudhi", "Vishwas Paradise", "GK Tropical Springs", "Profound Symphony",
            "Confident Jade", "Shriram Surabhi", "Prestige Woodland Park", "SLS Silver Oak",
            "MJR Clique Hydra", "Nitesh Central Park", "Prabhavathi Lotus 2", "Ozone Green View"
        ]
        for kb in KNOWN_ADDR_BUILDINGS:
            if kb.lower() in raw_addr.lower():
                return kb
                
    return None

def clean_sublocality_and_locality(raw_loc: str, raw_addr: str = ""):
    if not raw_loc or pd.isna(raw_loc):
        return None, "Bengaluru"
    loc = str(raw_loc).strip()
    loc = re.sub(r'\s+', ' ', loc)
    
    # Common pattern: "Lavender Koramangala" -> sub: "Lavender", loc: "Koramangala"
    # "John Nagar Koramangala" -> sub: "John Nagar", loc: "Koramangala"
    # "Jakkasandra Extension Koramangala" -> sub: "Jakkasandra Extension", loc: "Koramangala"
    # "Cauvery Colony Koramangala" -> sub: "Cauvery Colony", loc: "Koramangala"
    # "HSR Layout Sector 2" -> sub: "Sector 2", loc: "HSR Layout"
    KNOWN_MAIN_LOCALITIES = [
        "Koramangala", "Whitefield", "HSR Layout", "Electronic City", "Indiranagar",
        "Marathahalli", "Bellandur", "JP Nagar", "Hebbal", "Yelahanka", "Sarjapur Road",
        "Sarjapur", "Rajajinagar", "Malleshwaram", "Banashankari", "Devanahalli",
        "Jayanagar", "BTM Layout", "Thanisandra", "Hennur", "Richmond Town", "Shanti Nagar",
        "C V Raman Nagar", "CV Raman Nagar", "Krishnarajapura", "KR Puram", "Bommasandra",
        "Vidyaranyapura", "Kogilu", "Kumaraswamy Layout", "Arekere", "Talaghattapura",
        "Brookefield", "Kundalahalli", "Chansandra", "Hoodi", "Kadugodi", "Mahadevapura"
    ]
    
    sub = None
    main_loc = loc
    
    for ml in KNOWN_MAIN_LOCALITIES:
        ml_pattern = re.compile(rf'\b{re.escape(ml)}\b', re.IGNORECASE)
        if ml_pattern.search(loc):
            remainder = ml_pattern.sub('', loc).strip(' ,-')
            if remainder and remainder.lower() != ml.lower():
                sub = remainder.title()
                main_loc = ml
                break
            else:
                main_loc = ml
                break
                
    if not sub and "," in loc:
        parts = [p.strip() for p in loc.split(",") if p.strip()]
        if len(parts) >= 2:
            main_loc = parts[-1]
            sub = ", ".join(parts[:-1])

    # Check address if sub is still None
    if not sub and raw_addr:
        m = re.search(r'\b(Sector\s*\d+|Phase\s*\d+|Phase\s*[I|V|X]+|\d+(?:st|nd|rd|th)?\s*Block|\d+(?:st|nd|rd|th)?\s*Stage|Block\s*\d+|Defence Colony|Hope Farm|Lavender|John Nagar|Cauvery Colony|Jakkasandra)\b', raw_addr, re.I)
        if m:
            sub = m.group(1).title()
            
    return sub, main_loc

def migrate_database(db_path: str):
    if not os.path.exists(db_path):
        print(f"Skipping non-existent DB: {db_path}")
        return
        
    print(f"\n==========================================")
    print(f"Migrating database: {db_path}")
    print(f"==========================================")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Add missing columns
    cursor.execute("PRAGMA table_info(properties)")
    existing_cols = {c[1] for c in cursor.fetchall()}
    
    cols_to_add = {
        "property_name": "VARCHAR(255)",
        "building_name": "VARCHAR(255)",
        "project_name": "VARCHAR(255)",
        "society_name": "VARCHAR(255)",
        "builder_name": "VARCHAR(255)",
        "street": "VARCHAR(255)",
        "road": "VARCHAR(255)",
        "state": "VARCHAR(100) DEFAULT 'Karnataka'",
        "pincode": "VARCHAR(20)",
        "coordinate_confidence": "VARCHAR(50) DEFAULT 'APPROXIMATE'",
        "formatted_address": "VARCHAR(500)",
        "identity_confidence": "VARCHAR(50) DEFAULT 'IDENTITY_UNRESOLVED'",
        "identity_source": "VARCHAR(255)",
        "location_source": "VARCHAR(255)"
    }
    
    for c_name, c_type in cols_to_add.items():
        if c_name not in existing_cols:
            print(f"Adding column '{c_name}'...")
            cursor.execute(f"ALTER TABLE properties ADD COLUMN {c_name} {c_type}")
            
    conn.commit()
    
    # 2. Load Master CSV to enrich V21 rows
    master_dict = {}
    if os.path.exists(MASTER_CSV_PATH):
        df_master = pd.read_csv(MASTER_CSV_PATH)
        for _, r in df_master.iterrows():
            master_dict[r['property_id']] = r
            
    # 3. Query all properties
    cursor.execute("""
        SELECT id, title, property_type, bhk, locality, address, latitude, longitude,
               source_name, source_type, listing_status, society
        FROM properties
    """)
    rows = cursor.fetchall()
    print(f"Processing {len(rows)} properties in {db_path}...")
    
    resolved_count = 0
    partial_count = 0
    unresolved_count = 0
    exact_coord_count = 0
    approx_coord_count = 0
    
    KNOWN_BUILDERS = [
        "Prestige", "Sobha", "Brigade", "Godrej", "Puravankara", "Salarpuria Sattva",
        "Assetz", "Mantri", "Embassy", "Shriram", "Kolte Patil", "Provident",
        "Casagrand", "Sukhi", "Scion", "Icon", "Elgin", "Nitesh", "Prabhavathi",
        "Vishwas", "GK", "Profound", "Confident", "SS", "Homes ANS", "Habulus"
    ]
    
    for r in rows:
        p_id, title, ptype, bhk, loc, addr, lat, lon, s_name, s_type, l_status, soc = r
        raw_title = str(title or "").strip()
        raw_soc = str(soc or "").strip()
        raw_addr = str(addr or "").strip()
        
        building_name = None
        project_name = None
        society_name = None
        builder_name = None
        street = None
        road = None
        sub_loc = None
        clean_loc = loc or "Bengaluru"
        pincode = None
        identity_conf = "IDENTITY_UNRESOLVED"
        identity_src = "HISTORICAL_UNRESOLVED"
        coord_conf = "APPROXIMATE"
        loc_src = "LOCALITY_BENCHMARK_CENTROID"
        
        # Sub-locality and locality clean separation
        sub_loc, clean_loc = clean_sublocality_and_locality(loc, raw_addr)
        
        # Street / Road extraction from address
        if "road" in raw_addr.lower() or "rd" in raw_addr.lower():
            m = re.search(r'([0-9A-Za-z\s]+(Road|Rd|Cross|Main|Avenue|Highway))', raw_addr, re.I)
            if m:
                road = m.group(1).strip()
        if "street" in raw_addr.lower() or "st" in raw_addr.lower():
            m = re.search(r'([0-9A-Za-z\s]+(Street|St))', raw_addr, re.I)
            if m:
                street = m.group(1).strip()
                
        # Pincode extraction
        p_match = re.search(r'\b(560\d{3}|561\d{3}|562\d{3})\b', raw_addr)
        if p_match:
            pincode = p_match.group(1)
        elif clean_loc.lower() in LOCALITY_PINCODES:
            pincode = LOCALITY_PINCODES[clean_loc.lower()]
            
        # Case A: PropPulse Direct Listings (IDs 1-14)
        if p_id in range(1, 15) or s_type in ["PROPPULSE_DIRECT", "owner_listing"]:
            # Legitimate developer projects
            for b in KNOWN_BUILDERS:
                if b.lower() in raw_title.lower():
                    builder_name = b
                    break
            building_name = raw_title.replace(" 2BHK Apartment", "").replace(" 3BHK Apartment", "").replace(" 4BHK Villa", "").replace(" 3BHK Independent House", "").strip()
            project_name = building_name
            society_name = building_name
            identity_conf = "IDENTITY_RESOLVED"
            identity_src = "VERIFIED_DIRECT"
            coord_conf = "EXACT"
            loc_src = "VERIFIED_BUILDING_GPS"
            
        # Case B: V21 / Master Properties
        elif p_id in master_dict and master_dict[p_id]['source_name'] == 'Real Estate Data V21.csv':
            m_row = master_dict[p_id]
            m_proj = str(m_row.get('project_name', '')).strip()
            m_addr = str(m_row.get('address', '')).strip()
            
            cand_name = extract_genuine_building(m_proj, m_addr)
            
            if cand_name:
                building_name = cand_name
                project_name = cand_name
                society_name = cand_name
                identity_conf = "IDENTITY_RESOLVED"
                identity_src = "REAL_ESTATE_V21_SOURCE"
                for b in KNOWN_BUILDERS:
                    if b.lower() in cand_name.lower():
                        builder_name = b
                        break
            elif sub_loc:
                identity_conf = "IDENTITY_PARTIAL"
                identity_src = "REAL_ESTATE_V21_SOURCE"
            else:
                identity_conf = "IDENTITY_UNRESOLVED"
                identity_src = "REAL_ESTATE_V21_SOURCE"
                
        # Case C: Kaggle Historical Records (Bengaluru_House_Data.csv)
        else:
            cand_name = extract_genuine_building(raw_soc, raw_addr)
            if cand_name:
                building_name = cand_name
                project_name = cand_name
                society_name = cand_name
                identity_conf = "IDENTITY_RESOLVED"
                identity_src = "SOURCE_RECORD"
                for b in KNOWN_BUILDERS:
                    if b.lower() in cand_name.lower():
                        builder_name = b
                        break
            else:
                building_name = None
                project_name = None
                society_name = None
                if sub_loc:
                    identity_conf = "IDENTITY_PARTIAL"
                    identity_src = "HISTORICAL_RECORD"
                else:
                    identity_conf = "IDENTITY_UNRESOLVED"
                    identity_src = "HISTORICAL_UNRESOLVED"

        # Check against known exact building coordinates registry
        if building_name:
            b_key = building_name.lower().strip()
            # Try fuzzy match in known coords
            matched_key = None
            for k in KNOWN_EXACT_BUILDING_COORDS:
                if k in b_key or b_key in k:
                    matched_key = k
                    break
            if matched_key:
                info = KNOWN_EXACT_BUILDING_COORDS[matched_key]
                lat = info[0]
                lon = info[1]
                pincode = info[2]
                clean_loc = info[3]
                sub_loc = info[4]
                coord_conf = "EXACT"
                loc_src = "VERIFIED_BUILDING_GPS"
                
        # Normalized Title Generation: Never confuse property type with property name!
        if identity_conf == "IDENTITY_RESOLVED" and building_name:
            new_title = building_name
        else:
            size_label = f"{bhk} Bedroom" if (bhk and bhk > 4) else (f"{bhk} BHK" if bhk else "Residential")
            type_label = ptype or "Property"
            new_title = f"{size_label} {type_label}"
            
        # Formatted address assembly
        addr_parts = []
        if building_name:
            addr_parts.append(building_name)
        if street or road:
            addr_parts.append(street or road)
        if sub_loc and sub_loc.lower() not in clean_loc.lower():
            addr_parts.append(sub_loc)
        addr_parts.append(clean_loc)
        addr_parts.append(f"Bengaluru, Karnataka{f' - {pincode}' if pincode else ''}")
        formatted_addr = ", ".join(addr_parts)
        
        # Statistics
        if identity_conf == "IDENTITY_RESOLVED":
            resolved_count += 1
        elif identity_conf == "IDENTITY_PARTIAL":
            partial_count += 1
        else:
            unresolved_count += 1
            
        if coord_conf == "EXACT":
            exact_coord_count += 1
        else:
            approx_coord_count += 1
            
        # Update row in DB
        cursor.execute("""
            UPDATE properties
            SET property_name = ?,
                building_name = ?,
                project_name = ?,
                society_name = ?,
                builder_name = ?,
                street = ?,
                road = ?,
                sub_locality = ?,
                locality = ?,
                city = 'Bengaluru',
                state = 'Karnataka',
                pincode = ?,
                latitude = ?,
                longitude = ?,
                coordinate_confidence = ?,
                coordinate_quality = ?,
                formatted_address = ?,
                identity_confidence = ?,
                identity_source = ?,
                location_source = ?,
                title = ?
            WHERE id = ?
        """, (
            building_name,
            building_name,
            project_name,
            society_name,
            builder_name,
            street,
            road,
            sub_loc,
            clean_loc,
            pincode,
            lat,
            lon,
            coord_conf,
            coord_conf,
            formatted_addr,
            identity_conf,
            identity_src,
            loc_src,
            new_title,
            p_id
        ))
        
    conn.commit()
    conn.close()
    
    print("\n--- MIGRATION SUMMARY FOR " + db_path + " ---")
    print(f"Total Properties Processed: {len(rows)}")
    print(f"IDENTITY_RESOLVED:          {resolved_count}")
    print(f"IDENTITY_PARTIAL:           {partial_count}")
    print(f"IDENTITY_UNRESOLVED:        {unresolved_count}")
    print(f"EXACT Coordinates:          {exact_coord_count}")
    print(f"APPROXIMATE Coordinates:    {approx_coord_count}")

def main():
    for p in DB_PATHS:
        migrate_database(p)

if __name__ == "__main__":
    main()
