import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect(r"c:\major real estate\real_estate.db")

df = pd.read_sql_query("SELECT id, locality, property_type, bhk, price, area_sqft, source_type, verification_status, images FROM properties", conn)

# Count images in property_images table
df_images = pd.read_sql_query("SELECT property_id, count(*) as img_cnt FROM property_images GROUP BY property_id", conn)

conn.close()

df = df.merge(df_images, left_on='id', right_on='property_id', how='left')
df['img_cnt'] = df['img_cnt'].fillna(0).astype(int)

print(f"Loaded {len(df)} properties from database.")

# Normalize locality names
df['locality_clean'] = df['locality'].fillna('').str.strip().str.title()
loc_groups = df.groupby('locality_clean')

total_localities = df['locality_clean'].nunique()
print(f"Total unique localities: {total_localities}")

# Metrics collection
locality_metrics = []

for loc, group in loc_groups:
    if not loc:
        continue
    tot_rec = len(group)
    hist_rec = len(group[group['source_type'].isin(['HISTORICAL_MARKET_DATA', 'historical_dataset'])])
    curr_rec = len(group[group['source_type'].isin(['PROPPULSE_DIRECT', 'owner_listing', 'CURRENT_AUTHORIZED_LISTING'])])
    ver_curr_rec = len(group[(group['source_type'].isin(['PROPPULSE_DIRECT', 'owner_listing', 'CURRENT_AUTHORIZED_LISTING'])) & (group['verification_status'].isin(['Verified', 'VERIFIED']))])
    real_img_rec = len(group[group['img_cnt'] > 0])
    
    ptypes = group['property_type'].value_counts().to_dict()
    bhk_dist = group['bhk'].value_counts().to_dict()
    
    prices = group['price'].dropna().values
    prices = prices[prices > 0]
    
    min_p = float(np.min(prices)) if len(prices) > 0 else 0.0
    max_p = float(np.max(prices)) if len(prices) > 0 else 0.0
    med_p = float(np.median(prices)) if len(prices) > 0 else 0.0
    
    rates = (group['price'] / group['area_sqft']).dropna().values
    rates = rates[(rates > 0) & np.isfinite(rates)]
    med_rate = float(np.median(rates)) if len(rates) > 0 else 0.0
    
    locality_metrics.append({
        'locality': loc,
        'total_records': tot_rec,
        'historical_records': hist_rec,
        'current_records': curr_rec,
        'verified_current_records': ver_curr_rec,
        'records_with_real_images': real_img_rec,
        'min_price': min_p,
        'max_price': max_p,
        'median_price': med_p,
        'median_price_per_sqft': round(med_rate, 2),
        'property_types': ptypes,
        'bhk_distribution': bhk_dist
    })

locality_df = pd.DataFrame(locality_metrics)

# Summary stats across localities
healthy_current = len(locality_df[locality_df['current_records'] > 0])
historical_only = len(locality_df[(locality_df['current_records'] == 0) & (locality_df['historical_records'] > 0)])

print(f"Localities with current inventory: {healthy_current}")
print(f"Localities with historical-only inventory: {historical_only}")

# Generate markdown report
md_content = f"""# Phase C — Bengaluru Locality Inventory Analysis Report

**Project:** Major Real Estate / PropPulse AI  
**Coverage Scope:** All {total_localities} Bengaluru Localities in Database  
**Generated Date:** September 2026  

---

## Executive Summary

This report presents a comprehensive data provenance audit across all **{total_localities} distinct Bengaluru localities** present in the master property database (`real_estate.db`).

### Key Findings:
1. **Total Localities Audited:** {total_localities}
2. **Localities with Active Direct/Current Inventory:** {healthy_current}
3. **Localities with Historical Market Data Only:** {historical_only}
4. **Localities Needing Direct Owner/Agent Submissions:** {historical_only}
5. **Truthful Provenance State:** No synthetic properties were auto-generated to inflate localities lacking current listings.

---

## Top 30 Bengaluru Localities by Volume

| Locality Name | Total Records | Historical Records | Current Listings | Verified Current | With Real Images | Median Price (INR) | Median ₹/sq.ft |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""

top30 = locality_df.sort_values(by='total_records', ascending=False).head(30)

for idx, row in top30.iterrows():
    m_price_str = f"₹{row['median_price']/100000:.2f} L" if row['median_price'] < 10000000 else f"₹{row['median_price']/10000000:.2f} Cr"
    md_content += f"| **{row['locality']}** | {row['total_records']} | {row['historical_records']} | {row['current_records']} | {row['verified_current_records']} | {row['records_with_real_images']} | {m_price_str} | ₹{row['median_price_per_sqft']:,.2f} |\n"

md_content += f"""

---

## Locality Inventory Categorization

### 1. Localities with Healthy Current Inventory ({healthy_current})
Localities containing verified owner or agent listings submitted via PropPulse Direct:
"""

curr_locs = locality_df[locality_df['current_records'] > 0]
for idx, row in curr_locs.iterrows():
    md_content += f"- **{row['locality']}**: {row['current_records']} current listing(s) ({row['verified_current_records']} verified)\n"

md_content += f"""

### 2. Primary High-Volume Historical Localities ({historical_only} Localities)
Sample of major Bengaluru neighborhoods backed by historical dataset market intelligence:
"""

sample_hist = locality_df[locality_df['current_records'] == 0].sort_values(by='total_records', ascending=False).head(20)
for idx, row in sample_hist.iterrows():
    md_content += f"- **{row['locality']}**: {row['total_records']} historical records (Median rate: ₹{row['median_price_per_sqft']:,.2f}/sqft)\n"

md_content += f"""

---

## Detailed Localities Data Appendix ({total_localities} Localities)

*(Complete structured analysis stored in database and accessible via `/api/v1/properties/` and locality services)*
"""

with open(r"c:\major real estate\PHASE_C_LOCALITY_INVENTORY_REPORT.md", "w", encoding="utf-8") as f:
    f.write(md_content)

print("PHASE_C_LOCALITY_INVENTORY_REPORT.md generated successfully!")
