
# Phase C — Comprehensive Data Source Inventory & Provenance Report

## Executive Summary
This document provides an exhaustive, empirical audit of all property data sources, datasets, and database structures present within the repository. In strict adherence to system guidelines, zero fake listings, synthetic records, or unauthorized scraped images have been created.

---

## 1. Primary Repository Datasets

### Dataset 1: `Bengaluru_House_Data.csv`
* **File Path**: `backend/datasets/Bengaluru_House_Data.csv`
* **Total Rows**: 13,320
* **Bengaluru Coverage**: 100% (13,320 rows)
* **Historical vs. Current**: Historical Reference Dataset (Kaggle Bengaluru Housing Dataset)
* **Fields Present**: `area_type`, `availability`, `location`, `size`, `society`, `total_sqft`, `bath`, `balcony`, `price`
* **Unique Localities**: ~1,298 unique locations
* **Property Types**: Super built-up Area, Plot Area, Built-up Area, Carpet Area
* **Price Range**: ₹9 Lakhs to ₹3,600 Lakhs (₹0.09 Cr to ₹36.0 Cr)
* **Image URLs / Assets**: 0 embedded images (`PROPERTY IMAGE UNAVAILABLE`)
* **Authorization Status**: Open Benchmark Reference Data. Authorized for offline market reference analytics.

### Dataset 2: `real_estate_dataset.csv`
* **File Path**: `backend/datasets/real_estate_dataset.csv`
* **Total Rows**: 287
* **Bengaluru Rows**: 10 rows (Remaining rows cover Kakinada, Visakhapatnam, Noida, Hyderabad, Chennai, Mumbai, etc.)
* **Historical vs. Current**: External Scrape Data Archive (99acres external listing references)
* **Fields Present**: `url`, `beds`, `city`, `date`, `size`, `type`, `baths`, `price`, `neighborhood`
* **Authorization Status**: `IMAGE_AUTHORIZATION_UNKNOWN`. External listing URLs and image references are unverified. Strictly excluded from production inventory to prevent copyright violations.

### Dataset 3: `Real Estate Data V21.csv`
* **File Path**: `backend/datasets/Real Estate Data V21.csv`
* **Total Rows**: 14,528
* **Bengaluru Rows**: 4,523 rows
* **Fields Present**: `Name`, `Property Title`, `Price`, `Location`, `Total_Area`, `Price_per_SQFT`, `Description`, `Baths`, `Balcony`
* **Authorization Status**: `IMAGE_AUTHORIZATION_UNKNOWN`. Unverified external data archive. Not ingested into active production database.

### Dataset 4: `housing.csv`
* **File Path**: `backend/datasets/housing.csv`
* **Total Rows**: 0 (Empty schema header file)
* **Authorization Status**: N/A

---

## 2. Production Database Inventory (`backend/real_estate.db`)

### Table Statistics
* **Total Properties**: 12,458 records
* **Source Breakdown**:
  * `historical_dataset` / `HISTORICAL_MARKET_DATA`: 12,344 records
  * `demo_dataset`: 113 records
  * `owner_listing` / `PROPPULSE_DIRECT`: 1 record (User direct submission)
* **Verification Status Breakdown**:
  * `Verified`: 12,457 (Historical dataset baseline)
  * `Pending Verification`: 1 (Direct user listing)
* **Listing Status Classification**:
  * `CURRENT AUTHORIZED EXTERNAL INVENTORY`: **NOT YET CONNECTED** (0 records)
  * `PROPPULSE_DIRECT`: 1 record
  * `HISTORICAL_MARKET_DATA`: 12,344 records
  * `DEMO_TEST`: 113 records

---

## 3. Real Property Image Investigation Summary
* **Legitimate Property Images Available**: 0 (All historical reference listings exhibit no legitimate licensed photo assets and display `PROPERTY IMAGE UNAVAILABLE` in accordance with copyright directives).
* **Direct Listing Uploads**: Supported via `/list-property` and `upload_property_images` with file type and size validation.

---

## 4. Current Authorized External Inventory Statement
> **CURRENT AUTHORIZED EXTERNAL INVENTORY NOT YET CONNECTED**  
> **NO LEGITIMATE PROPERTY IMAGES CURRENTLY AVAILABLE FOR HISTORICAL DATASET**
