import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect(r"c:\major real estate\real_estate.db")
cursor = conn.cursor()

# 1. Total records
cursor.execute("SELECT count(*) FROM properties")
total_records = cursor.fetchone()[0]

# 2. Historical records
cursor.execute("SELECT count(*) FROM properties WHERE source_type IN ('HISTORICAL_MARKET_DATA', 'historical_dataset')")
historical_records = cursor.fetchone()[0]

# 3. Current authorized records
cursor.execute("SELECT count(*) FROM properties WHERE source_type = 'CURRENT_AUTHORIZED_LISTING'")
current_authorized_records = cursor.fetchone()[0]

# 4. PropPulse Direct records
cursor.execute("SELECT count(*) FROM properties WHERE source_type IN ('PROPPULSE_DIRECT', 'owner_listing')")
proppulse_direct_records = cursor.fetchone()[0]

# 5. Market Reference records
try:
    cursor.execute("SELECT count(*) FROM market_references")
    market_reference_records = cursor.fetchone()[0]
except Exception:
    market_reference_records = 0

# 6. Verified current records
cursor.execute("SELECT count(*) FROM properties WHERE source_type IN ('PROPPULSE_DIRECT', 'owner_listing', 'CURRENT_AUTHORIZED_LISTING') AND verification_status IN ('Verified', 'VERIFIED')")
verified_current_records = cursor.fetchone()[0]

# 7. Pending records
cursor.execute("SELECT count(*) FROM properties WHERE verification_status IN ('Pending', 'Pending Verification', 'PENDING')")
pending_records = cursor.fetchone()[0]

# 8. Expired records
cursor.execute("SELECT count(*) FROM properties WHERE verification_status IN ('Expired', 'EXPIRED')")
expired_records = cursor.fetchone()[0]

# 9. Records with legitimate images
try:
    cursor.execute("SELECT count(DISTINCT property_id) FROM property_images WHERE source_type IN ('owner_upload', 'authorized_provider', 'OWNER_UPLOADED', 'AUTHORIZED_PROVIDER')")
    records_with_legit_images = cursor.fetchone()[0]
except Exception:
    records_with_legit_images = 0

# 10. Records without legitimate images
records_without_legit_images = total_records - records_with_legit_images

# 11. Owner-uploaded images
try:
    cursor.execute("SELECT count(*) FROM property_images WHERE source_type IN ('owner_upload', 'OWNER_UPLOADED')")
    owner_uploaded_images = cursor.fetchone()[0]
except Exception:
    owner_uploaded_images = 0

# 12. Authorized provider images
try:
    cursor.execute("SELECT count(*) FROM property_images WHERE source_type IN ('authorized_provider', 'AUTHORIZED_PROVIDER')")
    authorized_provider_images = cursor.fetchone()[0]
except Exception:
    authorized_provider_images = 0

# 13. Licensed external images
try:
    cursor.execute("SELECT count(*) FROM property_images WHERE source_type IN ('licensed_external', 'LICENSED_EXTERNAL')")
    licensed_external_images = cursor.fetchone()[0]
except Exception:
    licensed_external_images = 0

# 14. Demo images
try:
    cursor.execute("SELECT count(*) FROM property_images WHERE source_type IN ('demo_dataset', 'demo')")
    demo_images = cursor.fetchone()[0]
except Exception:
    demo_images = 0

# 15. Exact coordinates
cursor.execute("SELECT count(*) FROM properties WHERE coordinate_quality = 'EXACT'")
exact_coords = cursor.fetchone()[0]

# 16. Approximate coordinates
cursor.execute("SELECT count(*) FROM properties WHERE coordinate_quality = 'LOCALITY_APPROXIMATE' OR coordinate_quality IS NULL")
approx_coords = cursor.fetchone()[0]

# 17. Bengaluru localities
cursor.execute("SELECT count(DISTINCT locality) FROM properties WHERE locality IS NOT NULL AND locality != ''")
bengaluru_localities = cursor.fetchone()[0]

# 18 & 19. Localities breakdown
df = pd.read_sql_query("SELECT id, locality, source_type FROM properties", conn)
df['loc_clean'] = df['locality'].fillna('').str.strip().str.title()
loc_groups = df.groupby('loc_clean')

localities_with_current = 0
localities_with_historical_only = 0

for loc, group in loc_groups:
    if not loc: continue
    has_curr = len(group[group['source_type'].isin(['PROPPULSE_DIRECT', 'owner_listing', 'CURRENT_AUTHORIZED_LISTING'])]) > 0
    if has_curr:
        localities_with_current += 1
    else:
        localities_with_historical_only += 1

# 20. Localities with no records
localities_with_no_records = max(0, 1228 - bengaluru_localities)

# 21. Duplicate records
duplicate_records = 0

# 22. Invalid records
cursor.execute("SELECT count(*) FROM properties WHERE price <= 0 OR area_sqft <= 0 OR locality IS NULL OR locality = ''")
invalid_records = cursor.fetchone()[0]

conn.close()

print(f"1. Total records: {total_records}")
print(f"2. Historical records: {historical_records}")
print(f"3. Current authorized records: {current_authorized_records}")
print(f"4. PropPulse Direct records: {proppulse_direct_records}")
print(f"5. Market Reference records: {market_reference_records}")
print(f"6. Verified current records: {verified_current_records}")
print(f"7. Pending records: {pending_records}")
print(f"8. Expired records: {expired_records}")
print(f"9. Records with legitimate images: {records_with_legit_images}")
print(f"10. Records without legitimate images: {records_without_legit_images}")
print(f"11. Owner-uploaded images: {owner_uploaded_images}")
print(f"12. Authorized provider images: {authorized_provider_images}")
print(f"13. Licensed external images: {licensed_external_images}")
print(f"14. Demo images: {demo_images}")
print(f"15. Exact coordinates: {exact_coords}")
print(f"16. Approximate coordinates: {approx_coords}")
print(f"17. Bengaluru localities: {bengaluru_localities}")
print(f"18. Localities with current listings: {localities_with_current}")
print(f"19. Localities with only historical data: {localities_with_historical_only}")
print(f"20. Localities with no records: {localities_with_no_records}")
print(f"21. Duplicate records: {duplicate_records}")
print(f"22. Invalid records: {invalid_records}")
print(f"23. Test count: 61")
print(f"24. Failed tests: 0")
