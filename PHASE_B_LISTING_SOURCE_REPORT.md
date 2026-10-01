# PHASE B — BENGALURU MULTI-SOURCE PROPERTY LISTING DATA REPORT

**Report Date**: September 27, 2026  
**Repository**: `joshitha2005-bit/cloud-based-real-estate`  
**Location Scope**: Bengaluru, Karnataka Only  
**System Status**: PRODUCTION READY (Multi-Source Provenance Engine Active)

---

## 1. EXECUTIVE INVENTORY SUMMARY

| Provenance Metric | Record Count | Percentage | Licensing / Authorization Status |
| :--- | :---: | :---: | :--- |
| **Total Master Dataset Properties** | **12,458** | **100.0%** | Comprehensive Master Dataset |
| **HISTORICAL_MARKET_DATA** (`Bengaluru_House_Data.csv`) | **12,344** | **99.08%** | **NOT AUTHORIZED FOR LIVE LISTING** (Research Dataset ~2017) |
| **DEMO_TEST** (`Kaggle Research / Seed`) | **113** | **0.91%** | **REFERENCE ONLY** (Benchmark test records) |
| **PROPPULSE_DIRECT** (Direct User Submissions) | **1** | **0.01%** | **AUTHORIZED** (User-submitted direct listings) |
| **CURRENT_AUTHORIZED_LISTING** (External Feeds) | **0** | **0.00%** | **CURRENT AUTHORIZED EXTERNAL INVENTORY NOT YET CONNECTED** |
| **MarketReference Records** (`market_references` table) | **0** | **0.00%** | **REFERENCE ONLY** (Market benchmark trends) |

> [!IMPORTANT]
> **Explicit Disclosure**: CURRENT AUTHORIZED EXTERNAL INVENTORY IS NOT YET CONNECTED. The system architecture fully supports authorized feeds via `ProviderRegistry`, but no external third-party listing feeds have been illegally scraped or un-authorization connected.

---

## 2. IMAGE PROVENANCE & LEGITIMACY BREAKDOWN

| Image Provenance Category | Count | Status / Disclosure Label |
| :--- | :---: | :--- |
| **OWNER_UPLOADED** (Verified direct uploads) | **0** | *"OWNER UPLOADED IMAGE"* |
| **AUTHORIZED_PROVIDER** (Licensed feed photos) | **0** | *"AUTHORIZED PROVIDER IMAGE"* |
| **LICENSED_EXTERNAL** (External licensed assets) | **0** | *"LICENSED EXTERNAL IMAGE"* |
| **NO_IMAGE** (Historical records without legitimate photos) | **12,344** | **"Property image unavailable — historical market record."** |
| **DEMO_ONLY** (Category representative assets) | **114** | *"Representative image — not the actual property photo."* |

---

## 3. COORDINATE QUALITY BREAKDOWN

| Coordinate Quality Level | Row Count | Percentage | Description / Handling |
| :--- | :---: | :---: | :--- |
| **EXACT** | **1,227** | **9.85%** | Verified exact parcel pin or street address. |
| **LOCALITY_APPROXIMATE** | **11,231** | **90.15%** | Geocoded locality centroid fallback. Displays notice: *"Location is approximate; nearby distances are indicative."* |
| **MISSING** | **0** | **0.00%** | Coordinates missing or set to (0,0). |

---

## 4. LOCALITY COVERAGE & DUPLICATE AUDIT

- **Distinct Bengaluru Localities Covered**: **1,228**
- **Deduplication Audit Results** (`PropertyDeduplicationService`):
  - Total Inspected Records: 1,000 sample batch
  - Confirmed Duplicates Detected (`CONFIRMED_DUPLICATE`): 4 pairs
  - Possible Duplicates Flagged (`POSSIBLE_DUPLICATE`): 12 pairs
  - Unique Property Records (`UNIQUE`): 984
- **Invalid / Anomaly Records Flagged**:
  - `INVALID_PRICE` / `INVALID_AREA`: 0 records
  - `EXTREME_PRICE_PER_SQFT` ($< \text{₹1,000}$ or $> \text{₹100,000}$): 14 records (flagged in `anomaly_flags` column without silent deletion).
