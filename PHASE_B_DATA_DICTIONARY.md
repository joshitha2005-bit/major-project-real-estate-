# PHASE B DATA DICTIONARY & DOMAIN SPECIFICATION

**Document Date**: September 27, 2026  
**Repository**: `joshitha2005-bit/cloud-based-real-estate`  
**Scope**: Master Property Listing Layer & Sourcing Architecture

---

## 1. PROPERTY LISTING DOMAIN (`Property` / `PropertyListing`)

| Attribute Name | Data Type | Allowed Values / Constraint | Description & Purpose |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK Auto-increment | Internal numeric property identifier. |
| `listing_id` | String | `BLR-{id}` format | Universal public listing alias identifier. |
| `source_type` | String | `HISTORICAL_MARKET_DATA`, `CURRENT_AUTHORIZED_LISTING`, `PROPPULSE_DIRECT`, `DEMO_TEST` | Strict data provenance source classification. |
| `source_name` | String | e.g. `Bengaluru_House_Data.csv`, `PropPulse Direct` | Exact dataset or provider origin name. |
| `source_listing_id` | String | Optional string | Provider native listing ID string. |
| `title` | String | Non-empty string | Normalized property title or size + locality string. |
| `property_type` | String | `Apartment`, `Villa`, `Independent House`, `Plot`, `Builder Floor`, `Penthouse` | Primary property category. |
| `bhk` | Integer | $\ge 1$ | Bedrooms configuration count. |
| `area_sqft` | Float | $> 0$ | Total built-up / plot area in square feet. |
| `area_type` | String | `super_built_up`, `carpet`, `plot` | Area measurement methodology. |
| `price_inr` | Float | $> 0$ | Total property price in INR. |
| `price_per_sqft` | Float | `price_inr / area_sqft` | Calculated price per sq.ft rate in INR. |
| `locality` | String | Bengaluru locality string | Locality neighborhood name. |
| `sub_locality` | String | Optional sector/block | Sector, phase, or block name. |
| `zone` | String | East, West, North, South | Bengaluru urban zone classification. |
| `address` | String | Non-empty address string | Full street address or area description. |
| `latitude` | Float | WGS84 coordinate | Latitude coordinate. |
| `longitude` | Float | WGS84 coordinate | Longitude coordinate. |
| `coordinate_quality` | String | `EXACT`, `LOCALITY_APPROXIMATE`, `MISSING` | Spatial coordinate precision level. |
| `listing_status` | String | `CURRENT`, `HISTORICAL`, `REFERENCE`, `DEMO`, `SOLD_INACTIVE`, `UNKNOWN` | Operational listing status badge. |
| `availability_date` | String | `Ready to Move` or date string | Expected possession/move-in timeline. |
| `listed_at` | DateTime | UTC Timestamp | Listing creation timestamp. |
| `image_provenance` | String | `OWNER_UPLOADED`, `AUTHORIZED_PROVIDER`, `LICENSED_EXTERNAL`, `NO_IMAGE`, `DEMO_ONLY` | Visual asset legitimacy badge. |
| `image_count` | Integer | $\ge 0$ | Number of associated photos. |
| `owner_or_agent_type`| String | `Owner`, `Broker`, `Builder` | Seller identity category. |
| `contact_available` | Boolean | `True` / `False` | Contact details disclosure flag. |
| `contact_source` | String | `Owner Provided`, `Historical Dataset - No Contact` | Origin of seller contact details. |
| `verification_status`| String | `Verified`, `Pending`, `Historical / Reference` | Quality verification status. |
| `anomaly_flags` | JSON List | e.g. `["EXTREME_PRICE_PER_SQFT"]` | Data anomaly audit flags. |

---

## 2. PROPERTY IMAGE DOMAIN (`PropertyImage`)

| Attribute Name | Data Type | Constraint / Default | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK Auto-increment | Image record identifier. |
| `property_id` | Integer | FK `properties.id` | Parent property listing reference. |
| `image_path` | String | `/static/uploads/...` | Relative or HTTP image URL path. |
| `image_provenance` | String | `OWNER_UPLOADED`, `AUTHORIZED_PROVIDER`, `NO_IMAGE` | Provenance classification tag. |
| `uploaded_at` | DateTime | UTC Timestamp | Upload timestamp. |
| `is_primary` | Boolean | `True` / `False` | Cover photo flag for gallery display. |
| `image_hash` | String | SHA-256 string | Raw file content hash for duplicate detection. |
| `width` | Integer | $\ge 400$ px | Image width in pixels. |
| `height` | Integer | $\ge 300$ px | Image height in pixels. |
| `verification_status`| String | `Verified`, `Pending` | Image verification status. |
| `image_quality_score`| Float | $0.0 - 100.0$ | Visual sharpness/brightness quality score. |
| `image_validation_status`| String | `Valid`, `Low Resolution`, `Duplicate`, `Corrupted` | Image validation audit status. |

---

## 3. MARKET REFERENCE DOMAIN (`MarketReference`)

| Attribute Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK Auto-increment | Benchmark reference identifier. |
| `provider_name` | String | Non-empty string | Market data provider name. |
| `locality` | String | Non-empty locality | Bengaluru locality name. |
| `property_type` | String | Apartment, Villa, etc. | Property classification. |
| `bhk` | Integer | $\ge 1$ | BHK layout. |
| `area_sqft` | Float | $> 0$ | Area in sq.ft. |
| `price_inr` | Float | $> 0$ | Observed price. |
| `price_per_sqft` | Float | Calculated rate | Observed price per sq.ft. |
| `reference_status` | String | `REFERENCE` | Fixed reference tag (Never shown as "Available now"). |
