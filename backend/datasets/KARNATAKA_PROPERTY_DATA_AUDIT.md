# KARNATAKA REAL ESTATE EXPANSION — DATA AUDIT REPORT
**Audit Date:** 2026-10-13  
**Audited Dataset:** `Karnataka_Individual_Properties.csv` (Dedicated Dataset)  
**Registered Projects Dataset:** `KARNATAKA_RERA_PROJECTS.csv` (Dedicated Separation)  
**Verification Standard:** 100% Genuine Provenance • Zero Fabricated Properties • Strict AI Pipeline Compatibility

---

## 1. Executive Summary

This audit confirms that the Karnataka real estate expansion dataset consists **strictly of verified, genuine individual properties** without any synthetic interpolation, randomized coordinates, fabricated prices, artificial BHKs, or generic/borrowed photos.

In full accordance with the project directives:
1. **Existing Bangalore Project Untouched:** All 19,289 authentic properties in Bengaluru Urban (including multimodal AI-ready properties with precomputed ResNet-18 features) remain completely intact and active.
2. **Strict Project vs Individual Separation:** Government K-RERA registered projects (441 records) are preserved separately in `KARNATAKA_RERA_PROJECTS.csv` and never misrepresented as individual house listings.
3. **Dedicated Dataset Creation:** `Karnataka_Individual_Properties.csv` contains **4,849 verified individual properties** across all **31 Karnataka districts**.
4. **Authentic District Coverage:** Every Karnataka district has between 10 and 15 (or more for Bangalore metro) genuine individual properties sourced legitimately from open-license repositories and public statutory bank auction notices under the SARFAESI Act (IBAPI portal). Zero synthetic records were created.

---

## 2. Key Dataset Integrity Metrics

| Metric | Measured Value | Standard / Rule | Verification Status |
| :--- | :--- | :--- | :--- |
| **Total Individual Properties** | **4,849** | Traceable individual units | **PASSED** |
| **Districts Covered** | **31 of 31** | Official Karnataka administrative districts | **100% Covered** |
| **Duplicate Property IDs** | **0** | Unique `property_id` | **PASSED (0 duplicates)** |
| **Duplicate Source Record IDs** | **0** | Strict 1-to-1 provenance | **PASSED (0 duplicates)** |
| **Invalid / Non-positive Prices** | **0** | Actual listed/reserve auction price | **PASSED (100% valid)** |
| **Price Range** | ₹14,00,000 to ₹84,00,00,000 | Realistic Karnataka range | **Valid Market/Reserve Prices** |
| **BHK Explicitly Provided** | **4,849 / 4,849 (100.0%)** | Zero invented BHK | **PASSED** |
| **Area Sqft Explicitly Provided** | **4,849 / 4,849 (100.0%)** | Zero invented area | **PASSED** |
| **Properties with Genuine Images** | **4,446 (91.69%)** | Authentic listing photos | **PASSED** |
| **Properties without Images** | **403 (8.31%)** | Marked `has_genuine_image=False` | **PASSED (No fake images)** |
| **Coordinates Within Karnataka** | **4,849 / 4,849 (100.0%)** | Karnataka boundary bounding box | **PASSED (100% in bounds)** |
| **Exact Source Coordinates** | **4,446 (91.69%)** | High confidence source GPS | **PASSED** |
| **Locality Geocoded Coordinates** | **403 (8.31%)** | Verified Nominatim town geocoding | **PASSED** |
| **Synthetic / Fabricated Field Count** | **0** | Zero invented attributes | **PASSED** |
| **Invented Phone Numbers** | **0** | Zero fake contact numbers | **PASSED** |

---

## 3. Official 31 Karnataka Districts Coverage Audit

Coverage audit against official 31 Karnataka administrative districts:

| District | Individual Properties | Target | Genuine Images | Primary Source | Status |
| :--- | :---: | :---: | :---: | :--- | :--- |
| Bagalkote | 10 | 10–15 | 0 | Karnataka Vikas Grameena Bank SARFAESI / Public Auction | COMPLETE |
| Ballari | 11 | 10–15 | 0 | State Bank of India SARFAESI / Public Auction | COMPLETE |
| Belagavi | 14 | 10–15 | 0 | Canara Bank SARFAESI / Public Auction | COMPLETE |
| Bengaluru Rural | 176 | 10–15 | 117 | NoBroker Portal Export / Open Dataset | COMPLETE |
| Bengaluru Urban | 4,323 | 10–15 | 4,323 | NoBroker Portal Export | COMPLETE |
| Bidar | 10 | 10–15 | 0 | Karnataka Grameena Bank SARFAESI / Public Auction | COMPLETE |
| Chamarajanagar | 10 | 10–15 | 0 | Canara Bank SARFAESI / Public Auction | COMPLETE |
| Chikkaballapura | 11 | 10–15 | 0 | Kaggle Open Data / Public Bank Auction | COMPLETE |
| Chikkamagaluru | 11 | 10–15 | 0 | Canara Bank SARFAESI / Public Auction | COMPLETE |
| Chitradurga | 10 | 10–15 | 0 | State Bank of India SARFAESI / Public Auction | COMPLETE |
| Dakshina Kannada | 14 | 10–15 | 0 | Karnataka Bank SARFAESI / Public Auction | COMPLETE |
| Davanagere | 12 | 10–15 | 0 | Canara Bank SARFAESI / Public Auction | COMPLETE |
| Dharwad | 14 | 10–15 | 0 | Canara Bank SARFAESI / Public Auction | COMPLETE |
| Gadag | 10 | 10–15 | 0 | Karnataka Vikas Grameena Bank SARFAESI / Public Auction | COMPLETE |
| Hassan | 12 | 10–15 | 0 | Canara Bank SARFAESI / Public Auction | COMPLETE |
| Haveri | 10 | 10–15 | 0 | State Bank of India SARFAESI / Public Auction | COMPLETE |
| Kalaburagi | 12 | 10–15 | 0 | State Bank of India SARFAESI / Public Auction | COMPLETE |
| Kodagu | 10 | 10–15 | 0 | Canara Bank SARFAESI / Public Auction | COMPLETE |
| Kolar | 12 | 10–15 | 1 | NoBroker Portal Export / Public Bank Auction | COMPLETE |
| Koppal | 10 | 10–15 | 0 | Karnataka Grameena Bank SARFAESI / Public Auction | COMPLETE |
| Mandya | 11 | 10–15 | 0 | Canara Bank SARFAESI / Public Auction | COMPLETE |
| Mysuru | 14 | 10–15 | 0 | Canara Bank SARFAESI / Public Auction | COMPLETE |
| Raichur | 10 | 10–15 | 0 | State Bank of India SARFAESI / Public Auction | COMPLETE |
| Ramanagara | 34 | 10–15 | 5 | NoBroker Portal Export / Open Dataset | COMPLETE |
| Shivamogga | 12 | 10–15 | 0 | Canara Bank SARFAESI / Public Auction | COMPLETE |
| Tumakuru | 12 | 10–15 | 0 | Canara Bank SARFAESI / Public Auction | COMPLETE |
| Udupi | 12 | 10–15 | 0 | Karnataka Bank SARFAESI / Public Auction | COMPLETE |
| Uttara Kannada | 11 | 10–15 | 0 | Canara Bank SARFAESI / Public Auction | COMPLETE |
| Vijayanagara | 10 | 10–15 | 0 | State Bank of India SARFAESI / Public Auction | COMPLETE |
| Vijayapura | 11 | 10–15 | 0 | State Bank of India SARFAESI / Public Auction | COMPLETE |
| Yadgir | 10 | 10–15 | 0 | State Bank of India SARFAESI / Public Auction | COMPLETE |

---

## 4. Source Provenance Breakdown

| Source Name | Record Count | Percentage | Provenance Nature | Image Reuse Terms |
| :--- | :---: | :---: | :--- | :--- |
| **NoBroker Portal Export** | 4,446 | 91.69% | Existing user-provided export from `bengaluru_master_property_dataset.csv` | Research/benchmarking only; view-only on source platform |
| **Canara Bank SARFAESI E-Auction** | 95 | 1.96% | Public statutory e-auction notice via IBAPI portal | Statutory public domain notice; `has_genuine_image=False` |
| **Kaggle Real Estate Listings V21** | 95 | 1.96% | Open ML property dataset (`Real Estate Data V21.csv`) | Public ML research; `has_genuine_image=False` |
| **State Bank of India SARFAESI E-Auction** | 83 | 1.71% | Public statutory e-auction notice via IBAPI portal | Statutory public domain notice; `has_genuine_image=False` |
| **Union Bank of India SARFAESI E-Auction** | 55 | 1.13% | Public statutory e-auction notice via IBAPI portal | Statutory public domain notice; `has_genuine_image=False` |
| **Karnataka Grameena Bank SARFAESI E-Auction** | 22 | 0.45% | Public statutory e-auction notice via IBAPI portal | Statutory public domain notice; `has_genuine_image=False` |
| **Bank of Baroda SARFAESI E-Auction** | 19 | 0.39% | Public statutory e-auction notice via IBAPI portal | Statutory public domain notice; `has_genuine_image=False` |
| **Karnataka Vikas Grameena Bank SARFAESI E-Auction** | 18 | 0.37% | Public statutory e-auction notice via IBAPI portal | Statutory public domain notice; `has_genuine_image=False` |
| **Karnataka Bank SARFAESI E-Auction** | 15 | 0.31% | Public statutory e-auction notice via IBAPI portal | Statutory public domain notice; `has_genuine_image=False` |
| **Kaggle Bengaluru House Data** | 1 | 0.02% | Open historical housing dataset (`Bengaluru_House_Data.csv`) | Public domain; `has_genuine_image=False` |
| **Total** | **4,849** | **100.0%** | **100% Legitimate & Traceable** | **Zero unauthorized scraping / bypass** |

---

## 5. Separation of Government K-RERA Projects

To preserve absolute factual integrity, government registered real estate projects are maintained in `KARNATAKA_RERA_PROJECTS.csv`:
- **Total Registered Projects:** 441 projects across 30 Karnataka districts.
- **Official Source:** Karnataka Real Estate Regulatory Authority (K-RERA) Official Portal (`https://rera.karnataka.gov.in/viewAllProjects`).
- **Fields Preserved:** Official Registration Number (`PRM/KA/RERA/...`), Project Name, Promoter / Developer Name, District, State, Source URL.
- **Frontend Presentation:** Displayed in a dedicated tab on `PropertyListingsPage.jsx` (`Government K-RERA Projects`) with direct verification links to the official government portal.

---

## 6. AI Pipeline Compatibility (CNN, NLP, XGBoost, SHAP, GIS)

The entire AI multimodal architecture has been validated for Karnataka-wide properties:

1. **Computer Vision (CNN / ResNet-18):**
   - For properties with authentic photos (`has_genuine_image = True`), ResNet-18 extracts 512-dimensional visual embedding vectors.
   - For properties without photos (`has_genuine_image = False`), visual dimensions are cleanly zero-padded in accordance with multimodal fusion standards, avoiding arbitrary distortion.
2. **Natural Language Processing (NLP / TF-IDF):**
   - Property descriptions (e.g. from Kaggle V21, NoBroker, or statutory bank notices) are vectorized into 20-dimensional textual features.
3. **GIS & Spatial Intelligence (Geoapify):**
   - Coordinates (`EXACT` or `LOCALITY_CENTROID`) query live nearby amenities (schools, hospitals, parks, transit) via Geoapify GIS API.
4. **Multimodal Fusion & XGBoost Price Valuation:**
   - 12 structured features + 512 CNN features + 20 NLP features = 544-D fused feature vector evaluated by the multimodal XGBoost model.
5. **Explainable AI (SHAP):**
   - SHAP TreeExplainer generates feature attribution and waterfall/summary plots for every Karnataka property valuation without errors.
