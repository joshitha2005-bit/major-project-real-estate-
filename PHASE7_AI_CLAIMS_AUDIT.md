# PHASE 7 — BENGALURU REAL ESTATE AI CLAIMS AUDIT

**Date**: September 12, 2026  
**Status**: AUDITED  
**Repository**: `joshitha2005-bit/cloud-based-real-estate`

---

## AI Claims Audit Matrix

| Feature | Claimed in UI / Docs | Actual Implementation | Evidence / File | Status | Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **XGBoost Price Prediction** | Real-time XGBoost ML Price & Rate Estimation | Genuine trained Scikit-Learn + XGBoost Regressor Pipeline (`price_model.pkl`) using 6 features (`location`, `area_type`, `total_sqft`, `bhk`, `bath`, `balcony`). Linear INR target. | `backend/models/price_model.pkl`, `backend/app/services/price_prediction_service.py` | **A. Genuine & Functional** | Maintain untouchable. Keep 100% consistent with `price_model_meta.json`. |
| **SHAP Feature Explanation** | Dynamic SHAP Feature Attribution | PyTorch/XGBoost `shap.TreeExplainer` fallback and exact model feature importance breakdown (`area_sqft`, `locality`, `bhk`, `bathrooms`, `area_type`). | `backend/app/services/price_prediction_service.py` | **A. Genuine & Functional** | Ensure clear UI label for model feature attributions and exact values. |
| **TF-IDF Description Analysis** | TF-IDF NLP Keyword & Text Quality Analysis | Scikit-Learn `TfidfVectorizer` fitted on property description corpus, extracting n-grams, tf-idf weights, sentiment lexicon, and amenity categorizations. | `backend/app/services/text_ai_service.py` | **A. Genuine & Functional** | Ensure fallback for properties lacking description displays honest text status instead of fake metrics. |
| **ResNet-18 / CNN Image Analysis** | PyTorch ResNet-18 CNN Feature Extraction & Image Quality | PyTorch `resnet18` pre-trained model with forward hook on `avgpool` + OpenCV Laplacian/Brightness metrics. | `backend/app/services/image_ai_service.py` | **B. Partially Functional** | Active for properties with valid images. For properties lacking legitimate images, display *"Image analysis unavailable — no verified property image"* instead of dummy defaults. |
| **GIS Emergency Infrastructure** | GIS Emergency Service Proximity | Live Geoapify queries for Police (`service.police`), Hospitals (`healthcare.hospital`), and Fire Stations (`amenity.fire_station`). | `backend/app/services/safety_service.py` | **A. Genuine & Functional** | Rename UI labels from "Crime Index" / "Flood Index" to **"Emergency Infrastructure Coverage"**. |
| **Crime / Flood / Traffic Index** | Crime Score, Flood Risk, Traffic Score | Heuristic inverse calculation (`100 - emergency_score`), `flood_risk = "Data Not Available"`, static `traffic_score = 50.0`. | `backend/app/services/safety_service.py` | **C. Placeholder / Proxy** | Remove unsupported claims of "Crime Index" or "Flood Risk". Display explicit Geoapify Emergency Infrastructure Distance. |
| **Property Comparison** | Multi-Property Intelligence Comparison | Comprehensive comparison of properties by locality, BHK, area, price, price/sqft, transaction type, property type, coordinate quality, and source provenance. | `frontend/src/pages/PropertyComparisonPage.jsx` | **A. Genuine & Functional** | Ensure complete separation of `HISTORICAL DATA` vs `PROPPULSE DIRECT`. |

---

## Classification Breakdown Summary
- **A. Genuinely Implemented & Functional**: XGBoost Price Prediction, SHAP / Feature Attribution, TF-IDF NLP Text Analysis, Geoapify GIS Emergency Proximity, Multi-Property Comparison.
- **B. Partially Functional**: ResNet-18 CNN Image Analysis (Fully functional for valid images; needs clean fallback for missing images).
- **C. Placeholder / Proxy Claims**: Crime Index / Flood Risk (To be replaced with accurate Emergency Infrastructure Coverage terminology).
