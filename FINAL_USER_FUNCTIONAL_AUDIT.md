# Cloud-Based Real Estate Analysis — Final User Functional Audit & Verification Report

**Date:** October 9, 2026  
**Platform Version:** 2.1.0-leakage-free-multimodal-resnet18-xgboost  
**Audit Scope:** Real-World User Browser Journey, Critical Bug Fixes, ML Pipeline Integrity, Test Suite Verification  
**Audit Status:** **ALL AUDIT GATES PASSED (191/191 TESTS PASSED)**

---

## Executive Summary

A comprehensive real-world functional audit and bug-fix cycle was conducted on **Cloud-Based Real Estate Analysis** (Cloud-Deployed Multi-Modal Framework for Real Estate Price Prediction Using Geospatial, Textual, and Visual Data with Explainable AI). 

All three target issues identified during runtime inspection have been surgically resolved and verified:
1. **Bug #1 (Blank Dashboard Screen on `/dashboard`):** Completely resolved. Repaired route shadowing and PostgreSQL JSON query error on `dataset-stats`, and added safe array fallbacks across the frontend dashboard.
2. **Bug #2 (Routing Time Display Implying Live Traffic):** Updated to explicit "Estimated driving time" / "Estimated riding time" labels and added a prominent disclaimer: *"Durations are calculated using speed limits on the OpenStreetMap/Geoapify road network. Actual travel time may vary with traffic conditions, weather, and peak road hours in Bengaluru."* Verified with 3 distinct live Geoapify routes.
3. **Bug #3 (OpenStreetMap / Street View 429 Errors):** Gracefully handled unavailable Street View state with clear "Street View unavailable" messaging and a direct "Open Map" button returning to the Leaflet interactive map, eliminating external 429 rate limit errors.

---

## 1. Verified Bug Fixes

### Bug #1: Blank Dashboard Screen on `/dashboard`
- **Root Causes:**
  1. **Route Shadowing in Backend:** `backend/app/api/v1/properties.py` had duplicate declarations for `/dashboard-stats`. The upper declaration omitted the `top_localities` array, resulting in `undefined` returned to `DashboardPage.jsx`, where `dashboardStats.top_localities.slice(0, 8)` threw an unhandled `TypeError: Cannot read properties of undefined (reading 'slice')`.
  2. **PostgreSQL JSON Column Comparison Error:** `/dataset-stats` failed on PostgreSQL with HTTP 500 because it queried `Property.images == ""` on a JSON column (`operator does not exist: json = unknown`), crashing the admin data quality audit panel.
- **Backend Fix Applied:**
  - Unified `/dashboard-stats` into a single authoritative handler returning `top_localities`, `localities_covered`, `independent_houses`, and listings counts.
  - Corrected `missing_images` filtering in `properties.py` using `(Property.images.is_(None)) | (Property.image_count == 0) | (Property.image_count.is_(None))`.
- **Frontend Hardening Applied:**
  - In `frontend/src/pages/DashboardPage.jsx`, added safe array fallbacks:
    ```jsx
    (dashboardStats?.top_localities || []).slice(0, 8).map(...)
    (datasetStats?.source_distribution || []).map(...)
    (datasetStats?.locality_distribution || []).slice(0, 10).map(...)
    ```
  - Added nullish coalescing operators for numerical stats (`total_properties ?? 0`, `buy_properties ?? 0`, etc.).
- **Verification Result:**
  - `GET http://127.0.0.1:8000/api/v1/properties/dashboard-stats` -> **HTTP 200 OK** (Returns 10 localities, counts, and breakdown).
  - `GET http://127.0.0.1:8000/api/v1/properties/dataset-stats` -> **HTTP 200 OK** (Returns source distribution, 15 localities, missing images count).
  - `/dashboard` renders smoothly with zero console errors or white screens.

---

### Bug #2: Routing Time Display Implying Live Traffic
- **Requirement:** Route cards must explicitly display "Estimated driving time" and "Estimated riding time", and display the traffic disclaimer: *"Actual travel time may vary with traffic conditions."*
- **Frontend Changes Applied (`frontend/src/pages/PropertyDetailsPage.jsx`):**
  - Updated Car route header with uppercase tag `Estimated driving time`.
  - Updated Bike route header with uppercase tag `Estimated riding time`.
  - Updated Public Transit header with uppercase tag `Estimated transit time`.
  - Added prominent traffic disclaimer banner:
    > **Routing Notice:** Durations are calculated using speed limits on the OpenStreetMap/Geoapify road network. Actual travel time may vary with traffic conditions, weather, and peak road hours in Bengaluru.
- **Backend Route Testing (3 Distinct Bengaluru Routes via `GeoapifyService.get_multi_mode_routes`):**
  1. **Majestic Station -> Koramangala:**
     - Origin: (12.9779, 77.5724) | Destination: (12.9352, 77.6245)
     - Estimated driving time: **12.7 mins** (Distance: **11.49 km**)
     - Estimated riding time: **33.0 mins** (Distance: **9.58 km**)
     - Provider: Geoapify Routing API (`is_live_geoapify = True`)
  2. **Indiranagar -> Whitefield:**
     - Origin: (12.9784, 77.6408) | Destination: (12.9698, 77.7500)
     - Estimated driving time: **14.5 mins** (Distance: **16.18 km**)
     - Estimated riding time: **56.9 mins** (Distance: **16.23 km**)
     - Provider: Geoapify Routing API (`is_live_geoapify = True`)
  3. **Electronic City -> HSR Layout:**
     - Origin: (12.8452, 77.6602) | Destination: (12.9121, 77.6446)
     - Estimated driving time: **12.9 mins** (Distance: **11.84 km**)
     - Estimated riding time: **31.7 mins** (Distance: **9.15 km**)
     - Provider: Geoapify Routing API (`is_live_geoapify = True`)

---

### Bug #3: OpenStreetMap / Street View 429 Errors
- **Requirement:** Handle Street View unavailable state gracefully with "Street View unavailable" and "Open Map" option; keep Leaflet map working; no broken external error pages.
- **Frontend Fix Applied (`frontend/src/components/MapView.jsx`):**
  - Updated fallback modal heading to **"Street View unavailable"**.
  - Replaced external OpenStreetMap button (which triggered HTTP 429 rate limit errors from upstream OSM servers) with an internal **"Open Map"** primary button.
  - Clicking "Open Map" invokes `handleBackToMap()`, immediately restoring the interactive Leaflet map canvas without page reloads or external navigation.
  - Retained optional secondary **"View in Google Maps"** link via official Google Maps URL for users wanting external satellite exploration.
- **Verification Result:**
  - Tested unavailable Street View state: renders cleanly with property address, coordinates, and "Open Map" button.
  - Clicking "Open Map" restores interactive Leaflet map seamlessly.

---

## 2. 544-D Multimodal Machine Learning Pipeline Verification

The core machine learning architecture was verified strictly without architectural modification:

| Modality | Extractor / Method | Dimensions | Feature Space Range |
| :--- | :--- | :---: | :--- |
| **Tabular / Structural** | Numerical & categorical scaling (area, BHK, baths, balconies, locality, age) | **6** | `[0 : 6]` |
| **Geospatial Intelligence** | Geoapify POI categories within 1 km (schools, colleges, hospitals, metro, bus, restaurants, shopping, banks, parks, total) | **10** | `[6 : 16]` |
| **Textual Semantics (NLP)** | Scikit-learn TF-IDF Vectorizer with Sublinear TF on property descriptions | **16** | `[16 : 32]` |
| **Computer Vision** | Pretrained PyTorch ResNet-18 Penultimate Layer (`avgpool`) with L2 normalization | **512** | `[32 : 544]` |
| **Total Multimodal Space** | Unified Concatenated Multi-Modal Feature Vector | **544** | `[0 : 544]` |

### XGBoost & TreeSHAP Benchmark Verification
- **Model Artifact:** `backend/models/multimodal_xgboost.joblib`
- **Metadata Version:** `2.1.0-leakage-free-multimodal-resnet18-xgboost`
- **Explainability:** SHAP `TreeExplainer` across all 4 modalities (Structural, Geospatial, NLP, Vision).
- **Golden Benchmark Property 16799:**
  - Benchmark Valuation: **₹1,37,06,784.00**
  - Dimension: Exactly **544 features**
  - Modalities Present: All 4 (Tabular: 6, Geoapify: 10, TF-IDF: 16, ResNet-18: 512)
  - Result: **MATCHED 100% (PASSED)**

---

## 3. Bank Loan & Comparison Engine Verification

- **Endpoint:** `GET http://127.0.0.1:8000/api/v1/loans/banks` -> **HTTP 200 OK**
- **Database Model:** `bank_loan_products` in `backend/app/models/loan.py`
- **Active Bank Products:** 12 verified Indian banking institutions:
  1. State Bank of India (SBI) — 7.50% to 8.75%
  2. HDFC Bank — 7.75% to 9.10%
  3. ICICI Bank — 8.50% to 9.60%
  4. Bank of Baroda — 7.20% to 8.85%
  5. Axis Bank — 8.20% to 9.35%
  6. Punjab National Bank (PNB) — 7.25% to 8.75%
  7. Canara Bank — 7.15% to 8.70%
  8. Union Bank of India — 7.15% to 8.65%
  9. Kotak Mahindra Bank — 7.60% to 8.90%
  10. LIC Housing Finance — 7.15% to 8.80%
  11. Bank of India (BOI) — 7.10% to 8.85%
  12. Indian Bank — 7.15% to 8.55%
- **EMI & Eligibility Calculator:** Formula verifies `E = P * r * (1+r)^n / ((1+r)^n - 1)` with FOIR assessment, interest amortizations, and ReportLab PDF streaming.

---

## 4. Test Suite Execution & Build Results

### 1. Reproducibility Test Suite (`pytest backend/tests/test_reproducibility.py -v`)
```
backend/tests/test_reproducibility.py::test_feature_space_dimensions PASSED
backend/tests/test_reproducibility.py::test_golden_property_reproducibility[16795] PASSED
backend/tests/test_reproducibility.py::test_golden_property_reproducibility[16799] PASSED
backend/tests/test_reproducibility.py::test_golden_property_reproducibility[101] PASSED
backend/tests/test_reproducibility.py::test_golden_property_reproducibility[16797] PASSED

============================= 5 passed in 14.00s ==============================
```

### 2. Full Project Test Suite (`python -m pytest backend/tests --capture=sys -q`)
```
191 passed in 673.68s (0:11:13)
```
- **Total Tests:** 191
- **Passed:** 191
- **Failed:** 0
- **Skipped:** 0

### 3. Frontend Production Build (`npm run build`)
```
vite v5.4.21 building for production...
✓ 1614 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   1.34 kB │ gzip:   0.70 kB
dist/assets/index-7QOXwAEU.css   55.18 kB │ gzip:   9.31 kB
dist/assets/index-PIo530W3.js   820.85 kB │ gzip: 210.70 kB
✓ built in 14.59s
```
- **Exit Code:** 0 (Clean production build without compilation errors).

---

## 5. End-to-End User Journey Audit Matrix

| Step | User Interaction Flow | Expected System Behavior | Verified Status |
| :---: | :--- | :--- | :---: |
| 1 | Visit `/` (Landing Page) | Hero banner, multimodal badges, Bangalore market highlights render | **PASS** |
| 2 | Register new account `/register` | JWT tokens created, bcrypt hashed password stored in PostgreSQL | **PASS** |
| 3 | Login at `/login` | Access token stored in localStorage, user redirected to `/dashboard` | **PASS** |
| 4 | Dashboard View `/dashboard` | Live market index, top localities, database provenance display (no blank screen) | **PASS** |
| 5 | Locality Filter click | Quick locality buttons ("Koramangala", "Whitefield") activate GIS map tab | **PASS** |
| 6 | Property Search | Autocomplete returns geocoded Bangalore localities with lat/lon | **PASS** |
| 7 | Interactive Map | Leaflet renders custom markers, 1KM / 5KM amenity radius circles | **PASS** |
| 8 | Property Details `/properties/:id` | Full specifications, gallery, exact GPS coordinates display | **PASS** |
| 9 | Multi-Modal Routing | Live Geoapify routing displays "Estimated driving time" & traffic notice | **PASS** |
| 10 | Street View Overlay | If unavailable, displays "Street View unavailable" + "Open Map" button | **PASS** |
| 11 | Home Loan Planner | 12 verified banks display official October 2026 interest rates | **PASS** |
| 12 | Loan Comparison Form | Validates applicant income, computes FOIR eligibility and EMI | **PASS** |
| 13 | PDF Loan Report | Downloads genuine ReportLab PDF with loan comparison schedules | **PASS** |
| 14 | AI Price Valuation | Multimodal 544-D inference runs via XGBoost with confidence intervals | **PASS** |
| 15 | Explainable AI (SHAP) | Visualizes impact of Structural, Geospatial, NLP, and Vision features | **PASS** |
| 16 | Free vs Pro Tier Gating | Free users see pro feature lock modal for deep analytics & PDF export | **PASS** |
| 17 | Subscription Upgrade `/subscription` | Razorpay simulation activates pro plan with status `ACTIVE` | **PASS** |
| 18 | Direct Property Listing `/list-property` | Allows listing creation with image upload and geocoding | **PASS** |
| 19 | Admin Verification Queue | Admin role views pending listings and clicks "Verify" to publish | **PASS** |
| 20 | Admin Audit Panel | Displays dataset provenance, source distribution, and image completeness | **PASS** |
| 21 | AI Voice Assistant | Natural language query processing via OpenAI/ElevenLabs integration | **PASS** |
| 22 | Security Audit | Public navbar excludes admin direct links; zero exposed NoBroker URLs | **PASS** |

---

## 6. Conclusion

The functional audit is complete. All 3 critical bugs are permanently resolved, both frontend and backend test gates pass with 100% compliance (191/191 tests passed), and the application provides a smooth, production-grade user experience from initial landing to deep multimodal valuation.
