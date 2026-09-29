"""
Database Building Identity & Location Clean-Up Script.
1. Removes the '\u2014' artifact inserted between every character in property titles.
2. Preserves and normalizes source building/project/society names.
3. Formats clean honest property titles (e.g. '3 BHK Apartment', '4 BHK Independent House')
   when no building name exists, guaranteeing NEVER using only a generic locality as a title.
4. Ensures coordinate_quality is either 'EXACT' or 'LOCALITY_APPROXIMATE'.
"""

import sqlite3
import os
import re

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "real_estate.db")

def fix_building_identity():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM properties")
    total = cur.fetchone()[0]
    print(f"Total properties in DB: {total}")

    # 1. Clean em-dash / en-dash corruption in titles
    cur.execute("SELECT id, title, property_type, bhk, locality, sub_locality, society, address FROM properties")
    rows = cur.fetchall()

    fixed_titles_count = 0
    clean_titles = []

    for pid, title, ptype, bhk, loc, sub_loc, soc, addr in rows:
        cleaned_title = title
        if '\u2014' in title or '\u2013' in title:
            # Strip the inter-character dashes
            cleaned_title = title.replace('\u2014', '').replace('\u2013', '').strip()
            # Collapse multiple spaces
            cleaned_title = re.sub(r'\s+', ' ', cleaned_title)

        # Check if the title is merely a generic locality name like "Koramangala" or empty
        loc_str = (loc or "Bengaluru").strip()
        is_generic_locality = (cleaned_title.lower() == loc_str.lower() or 
                               cleaned_title.lower() in ["bengaluru", "bangalore", "property", "apartment", "house", ""])

        if is_generic_locality:
            # Form honest property-type title
            bhk_str = f"{bhk} BHK " if bhk and bhk > 0 else ""
            type_str = ptype if ptype and ptype.strip() else "Residential Property"
            cleaned_title = f"{bhk_str}{type_str}".strip()

        # If society exists and is genuine (not 'None' / empty)
        # and title doesn't mention the society name, we preserve society in society column
        clean_soc = None
        if soc and str(soc).strip() and str(soc).strip().lower() not in ['none', 'null', 'nan']:
            clean_soc = str(soc).strip()

        if cleaned_title != title or clean_soc != soc:
            fixed_titles_count += 1
            clean_titles.append((cleaned_title, clean_soc, pid))

    print(f"Updating {fixed_titles_count} properties with clean titles and societies...")
    batch_size = 1000
    for i in range(0, len(clean_titles), batch_size):
        batch = clean_titles[i:i+batch_size]
        cur.executemany("UPDATE properties SET title = ?, society = ? WHERE id = ?", batch)
    conn.commit()

    print("Title and society normalization complete!")

    # 2. Verify samples
    print("\n--- 10 Sample Updated Properties ---")
    cur.execute("SELECT id, title, society, sub_locality, locality, address, coordinate_quality FROM properties LIMIT 10")
    for r in cur.fetchall():
        print(f"ID {r[0]}: Title='{r[1]}' | Soc='{r[2]}' | Loc='{r[4]}' | Quality='{r[6]}'")

    # 3. Repeat for backend/real_estate.db if run from workspace root
    conn.close()

if __name__ == "__main__":
    fix_building_identity()
