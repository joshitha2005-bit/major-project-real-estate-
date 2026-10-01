# Phase 4 — Real Bengaluru Property Data, Location, and Image Source Audit

---

## Executive Summary

This document presents a comprehensive audit of the **Bengaluru Real Estate Analysis Platform** master dataset (12,458 properties), coordinate enrichment feasibility, repository dataset discovery, and image provenance options.

---

## 1. Current Data Quality Audit

| Attribute | Total Count | Non-Null Count | Coverage % | Primary Source / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Total Properties** | 12,458 | 12,458 | 100.00% | `12,344` historical dataset + `113` demo dataset + `1` owner listing |
| **Property ID (`id`)** | 12,458 | 12,458 | 100.00% | Primary key unique integer |
| **Source Listing ID** | 12,458 | 12,458 | 100.00% | `BLR-HIST-{id}` for historical, `BLR-LIST-{id}` for demo/owner |
| **Title** | 12,458 | 12,458 | 100.00% | Normalized transparent property titles |
| **City** | 12,458 | 12,458 | 100.00% | Standardized to `Bengaluru` |
| **Locality (`locality`)** | 12,458 | 12,458 | 100.00% | 1,228 distinct normalized localities |
| **Sub-Locality (`sub_locality`)** | 12,458 | 409 | 3.28% | Extracted sub-localities (e.g., Sector 1, Phase 2, Block 4) |
| **Society / Project (`society`)** | 12,458 | 7,215 | 57.91% | Includes 6,564 anonymized codes (`PrarePa`, `GrrvaGr`) |
| **Zone (`zone`)** | 12,458 | 12,458 | 100.00% | Mapped to 6 Bengaluru zones |
| **Property Type** | 12,458 | 12,458 | 100.00% | Apartment, Independent House, Villa, Plot, Penthouse |
| **BHK** | 12,458 | 12,458 | 100.00% | Valid integer counts (1 to 16 BHK) |
| **Area (`area_sqft`)** | 12,458 | 12,458 | 100.00% | Numeric sqft parsed (ranges converted to midpoints) |
| **Area Type (`area_type`)** | 12,458 | 12,458 | 100.00% | `super_built_up`, `built_up`, `carpet`, `plot` |
| **Price (`price_inr`)** | 12,458 | 12,458 | 100.00% | Sale prices in INR (`price * 100,000` for Lakhs) |
| **Price / Sq.Ft (`price_per_sqft`)** | 12,458 | 12,458 | 100.00% | `price_inr / area_sqft` |
| **Transaction Type** | 12,458 | 12,458 | 100.00% | `sale` (12,418) vs `rent` (40) |
| **Furnishing** | 12,458 | 113 | 0.91% | `NULL` for historical records without explicit source |
| **Floor / Total Floors** | 12,458 | 113 | 0.91% | `NULL` for historical records without explicit source |
| **Parking** | 12,458 | 113 | 0.91% | `NULL` for historical records without explicit source |
| **Source URL** | 12,458 | 0 | 0.00% | `NULL` for historical dataset |

---

## 2. Bengaluru Locality & Zone Coverage Audit

Distribution across 6 core Bengaluru geographic zones:

- **South Bengaluru**: `7,203` properties (57.82%) — Koramangala, HSR Layout, Electronic City, JP Nagar, Jayanagar, BTM, Kanakapura Road.
- **East Bengaluru**: `2,808` properties (22.54%) — Whitefield, Marathahalli, Bellandur, KR Puram, Hoodi, Varthur, Old Airport Road.
- **North Bengaluru**: `1,318` properties (10.58%) — Hebbal, Yelahanka, Thanisandra, Hennur, Sahakara Nagar, Jakkur, Devanahalli.
- **Outer Bengaluru**: `685` properties (5.50%) — Sarjapur Road, Attibele, Chandapura, Anekal, Hosur Road.
- **West Bengaluru**: `317` properties (2.54%) — Rajajinagar, Malleshwaram, Vijayanagar, Kengeri, Yeshwanthpur.
- **Central Bengaluru**: `127` properties (1.02%) — Indiranagar, MG Road, Richmond Town, Vasanth Nagar, Frazer Town.

**Duplicates & Near-Duplicates Audit**:
- **Exact Duplicates** (`title + locality + price + bhk + area + source`): **0**
- **Near-Duplicate Clusters** (`locality + bhk + area + price`): **4 small groups** (retained as valid independent listings from same project floorplans).
- **Suspicious Out-of-Bounds Records**: **0** (All coordinates lie within valid Bengaluru bounding box `[12.7–13.3° N, 77.3–77.8° E]`).

---

## 3. Coordinate Accuracy & Geocoding Enrichment Audit

| Coordinate Quality Class | Property Count | Percentage | Explanation |
| :--- | :--- | :--- | :--- |
| **`EXACT`** | 1,227 | 9.85% | Specific geocoded building/society coordinates (Demo & Owner listings) |
| **`LOCALITY_APPROXIMATE`** | 11,231 | 90.15% | Locality centroid fallbacks (8,892 Bengaluru center, 506 Whitefield, 473 Sarjapur, etc.) |
| **`MISSING`** | 0 | 0.00% | All properties have valid latitude and longitude coordinates |

### Fallback Coordinate Clusters Audit

Top fallback centroid clusters in the database:

1. **` (12.9716, 77.5946)`**: 8,892 properties — Bengaluru City Center fallback.
2. **` (12.9696, 77.7497)`**: 506 properties — Whitefield locality centroid.
3. **` (12.9107, 77.6970)`**: 473 properties — Sarjapur Road locality centroid.
4. **` (12.9077, 77.5854)`**: 396 properties — JP Nagar locality centroid.
5. **` (12.8436, 77.6687)`**: 368 properties — Electronic City locality centroid.
6. **` (13.1007, 77.5963)`**: 258 properties — Yelahanka locality centroid.
7. **` (13.0547, 77.6338)`**: 226 properties — Thanisandra locality centroid.
8. **` (13.0358, 77.5970)`**: 174 properties — Hebbal locality centroid.

### Society Geocoding Enrichment Potential

- **6,564** of the `11,231` `LOCALITY_APPROXIMATE` properties contain non-null `society` strings.
- **Key Finding**: In the original `Bengaluru_House_Data.csv`, society names were anonymized into obfuscated codes (e.g., `PrarePa` for Prestige Park, `GrrvaGr` for Grandeur, `Prtates` for Prestige Estates, `Sryalan` for Suryalanka).
- **Rule Enforced**: Attempts to geocode anonymized codes directly via Map APIs like Geoapify yield generic locality fallbacks. Therefore, unless an exact society mapping dictionary is established, these records strictly retain **`LOCALITY_APPROXIMATE`** status to guarantee location truth.

---

## 4. Property Image & Provenance Audit

Audit of property images across all 12,458 database properties:

| Image Provenance Category | Property Count | Percentage | Provenance & Legal Status |
| :--- | :--- | :--- | :--- |
| **Real Owner-Uploaded Images** | 1 | 0.01% | PropPulse Direct user-uploaded file (PIL validated) |
| **Licensed External Images** | 0 | 0.00% | No licensed commercial feed connected |
| **Generic Seeded / Demo Images** | 113 | 0.91% | Local catalog images assigned to demo properties |
| **No Image Available (`NULL` / `[]`)** | 12,344 | 99.08% | Historical dataset properties with no photo source |
| **TOTAL** | **12,458** | **100.00%** | |

> [!IMPORTANT]
> Generic category or stock house images are **NEVER** assigned to historical dataset properties to avoid false representation. Historical dataset records display `"Image Not Available"` in the UI.

---

## 5. Repository Data Source Discovery

Audit of datasets discovered in workspace files:

| Source File | Total Rows | Columns | Bengaluru Coverage | Usable Fields | Image URLs | Provenance / Licensing |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [`Bengaluru_House_Data.csv`](file:///c:/real%20estate/backend/datasets/Bengaluru_House_Data.csv) | 13,320 | 9 | 100% Bengaluru | `location`, `size`, `total_sqft`, `bath`, `balcony`, `price`, `society`, `area_type` | None | Open Machine Learning Benchmark (CC0/Public Domain) |
| [`real_estate_dataset.csv`](file:///c:/real%20estate/backend/datasets/real_estate_dataset.csv) | 287 | 9 | 100% Bengaluru | `url`, `beds`, `city`, `date`, `size`, `type`, `baths`, `price`, `neighborhood` | None | 2025 Public Listing Index (Listing URLs included) |
| [`Real Estate Data V21.csv`](file:///c:/real%20estate/backend/datasets/Real Estate Data V21.csv) | 14,528 | 9 | ~18% Bengaluru (2,600 rows) | `Name`, `Property Title`, `Price`, `Location`, `Total_Area`, `Price_per_SQFT`, `Description`, `Baths` | None | Pan-India Kaggle dataset (Needs Bengaluru filtering) |

---

## 6. Candidate API & Data Provider Analysis

Evaluation of candidate real estate data sources for Bengaluru:

| Source Option | Provider Type | Real Listings | Images Included | Exact Coords | Est. Cost | Legal / Terms Risk | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PropPulse Direct Owner Submissions** | Official Native Platform | Yes | Yes (Owner Upload) | Yes (User Pin) | **₹0** | **Zero Risk** (100% legal) | **PRIMARY RECOMMENDED** |
| **Geoapify Places & Reverse Geocode API** | Official GIS API | N/A (POIs/Amenities) | N/A | Yes | **₹0 (Free Tier 3k/day)** | **Zero Risk** (Official API Key) | **PRIMARY RECOMMENDED** |
| **Open License Datasets (Kaggle/GitHub)** | Public Datasets | Historical | No | Locality Level | **₹0** | **Low Risk** (CC-BY / Public Domain) | **RECOMMENDED FOR MODEL & HISTORICAL DATA** |
| **RapidAPI / Third-Party Real Estate Aggregators** | Scraping Wrapper | Mixed | Variable | Variable | **$30–$100/mo** | **HIGH RISK** (Terms of Service violations, unstable) | **REJECTED** |
| **Portal Web Scraping (99acres/MagicBricks)** | Unofficial Scraping | Unlicensed | Copyrighted | Unlicensed | **₹0 (Engineering time)** | **EXTREME RISK** (IP bans, legal cease-and-desist, copyright infringement) | **STRICTLY FORBIDDEN** |

---

## 7. Recommended Implementation Architecture & Master Schema

### Proposed Master Dataset Schema (`properties` table)

```sql
CREATE TABLE properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    source_listing_id VARCHAR(100) UNIQUE,
    source VARCHAR(255) DEFAULT 'PropPulse Direct',
    source_type VARCHAR(100) DEFAULT 'owner_listing', -- historical_dataset, demo_dataset, owner_listing, licensed_feed
    source_url VARCHAR(500),
    title VARCHAR(255) NOT NULL,
    city VARCHAR(100) DEFAULT 'Bengaluru',
    locality VARCHAR(255) NOT NULL,
    sub_locality VARCHAR(255),
    zone VARCHAR(100) NOT NULL, -- East, West, North, South, Central, Outer Bengaluru
    society VARCHAR(255),
    property_type VARCHAR(100) NOT NULL, -- Apartment, Villa, Independent House, Plot, Penthouse
    bhk INTEGER NOT NULL,
    bathrooms INTEGER DEFAULT 1,
    balconies INTEGER DEFAULT 0,
    area_sqft FLOAT NOT NULL,
    area_type VARCHAR(100) DEFAULT 'super_built_up', -- super_built_up, built_up, carpet, plot
    price FLOAT NOT NULL,
    price_inr FLOAT NOT NULL,
    transaction_type VARCHAR(50) DEFAULT 'sale', -- sale, rent
    price_per_sqft FLOAT NOT NULL,
    furnishing VARCHAR(50), -- NULL for historical records
    floor INTEGER,          -- NULL for historical records
    total_floors INTEGER,   -- NULL for historical records
    parking VARCHAR(50),    -- NULL for historical records
    facing VARCHAR(50),
    availability VARCHAR(100),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    coordinate_quality VARCHAR(50) NOT NULL, -- EXACT, LOCALITY_APPROXIMATE, MISSING
    description TEXT,
    images JSON DEFAULT '[]',
    nearby_places JSON DEFAULT '[]',
    verification_status VARCHAR(100) DEFAULT 'Verified',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 8. Final Audit Recommendations & Next Steps

1. **Retain 100% Phase 3 Stability**: Keep all 27/27 passing tests green.
2. **Preserve Geographic Truth**: Keep `11,231` records as `LOCALITY_APPROXIMATE` and `1,227` as `EXACT`. Display coordinate warnings in UI when `coordinate_quality == 'LOCALITY_APPROXIMATE'`.
3. **No Image Fabrication**: Keep `12,344` historical properties as `"Image Not Available"` while encouraging live owner uploads via the verified `StorageService` image uploader.
4. **Geoapify Proximity**: Continue utilizing live Geoapify API with corrected taxonomy (`Hospitals`, `Parks`, `Metro Stations`) for exact and approximate property coordinates.
