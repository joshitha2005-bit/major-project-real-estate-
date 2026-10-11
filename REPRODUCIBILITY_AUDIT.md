# CLOUD-BASED REAL ESTATE ANALYSIS — REPRODUCIBILITY AUDIT REPORT

**Audit Date**: October 2026  
**Platform**: Windows 11 / PowerShell / Multi-Platform Container Ready  
**Repository**: `joshitha2005-bit/major-project-real-estate-`  
**Evaluation Scope**: Clean-Machine Reproducibility, 544-D Multimodal Inference, Zero Secret Exposure, Standalone Demo Mode  

---

## 1. Executive Summary & Verification Matrix

| Component | Status | Verification Summary |
| :--- | :--- | :--- |
| **PYTHON_VERSION** | **Python 3.13.7** | Compatible with Python 3.10 – 3.13 |
| **NODE_VERSION** | **v22.20.0 (npm 11.6.2)** | Compatible with Node 18.x – 22.x |
| **BACKEND_DEPENDENCIES** | **PASS** | Pinned in `backend/requirements.txt` & root `requirements.txt`. Full pytest suite: 191 passed / 0 failed. |
| **FRONTEND_DEPENDENCIES** | **PASS** | Locked in `package.json` & `package-lock.json`. Production build: `npm run build` passed in 15.69s with 0 errors. |
| **MODEL_ARTIFACTS** | **PASS** | 6 artifacts audited with cryptographic SHA-256 checksums documented in `REPRODUCIBILITY_MANIFEST.json`. |
| **DATABASE_SETUP** | **PASS** | Standalone, credential-free initialization via `backend/init_demo_db.py`. Supports both SQLite and PostgreSQL. |
| **DEMO_MODE** | **PASS** | `DEMO_MODE=true` environment flag. Real 544-D pipeline, real XGBoost, real SHAP. Zero fake predictions. |
| **DOCKER** | **PASS** | `Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.yml`, and `nginx.conf` present and verified. |
| **GOLDEN_TEST** | **PASS** | `tests/test_reproducibility.py` passed 5/5 test benchmarks on properties 16795, 16799, 101, and 16797. |
| **CLEAN_STARTUP** | **PASS** | 1-Click launcher `START_DEMO.bat` and documented step-by-step workflow in `README.md`. |
| **SAME_OUTPUT** | **PASS** | Deterministic outputs across multiple evaluation cycles within documented 0.5% tolerance. |

---

## 2. Environment & Pinned Dependencies

### Backend Runtime
- **Python**: `3.13.7` (64-bit)
- **Virtual Environment**: `.venv`
- **Core Pinned Libraries**:
  - `torch==2.6.0+cpu`, `torchvision==0.21.0+cpu` (ResNet-18 CNN feature extractor)
  - `xgboost==3.1.2` (Multimodal Gradient Boosted Regressor)
  - `shap==0.50.0` (TreeExplainer game-theoretic attribution)
  - `scikit-learn==1.7.2` (TF-IDF vectorizer and tabular preprocessing)
  - `fastapi==0.110.1`, `uvicorn==0.29.0` (Asynchronous REST API engine)
  - `sqlalchemy==2.0.44`, `psycopg2-binary==2.9.10` (Database abstraction layer)
  - `pydantic==2.11.9`, `pydantic-settings==2.11.0` (Configuration validation)
  - `httpx==0.27.0` (Geoapify geospatial API client)
  - `reportlab==4.4.10` (Mortgage & Valuation PDF generation engine)

### Frontend Runtime
- **Node.js**: `v22.20.0`
- **npm**: `11.6.2`
- **Core Libraries**:
  - `react==18.3.1`, `react-dom==18.3.1`
  - `vite==5.4.19`
  - `leaflet==1.9.4`, `react-leaflet==4.2.1`
  - `lucide-react==0.344.0`

---

## 3. Model Artifact Checksum Audit (`REPRODUCIBILITY_MANIFEST.json`)

All 6 production ML model and cache artifacts were inspected, size-verified, and cryptographically fingerprinted using SHA-256:

| Artifact Name | Size (Bytes) | SHA-256 Checksum | Modality / Role |
| :--- | :--- | :--- | :--- |
| `multimodal_xgboost.joblib` | 1,460,332 | `9ea63a03c39aa030cff32a5df6cb2aaad3f7a3efd2024ad6e088ba767efc464c` | Core 544-D XGBoost Regressor |
| `multimodal_model_meta.json` | 3,114 | `1ae7f47e30d707f154378f44ff521360183b0f5b1397ee4587eebe5a43b71ca5` | Model metadata, R²=0.6305, Locality Map |
| `price_model.pkl` | 610,610 | `6fb7307040bf5e227a6599ccbce151beea9d20c32585f3baee1527ef3e3d64fe` | Baseline Tabular XGBoost Pipeline |
| `price_model_meta.json` | 682 | `e61ba90c6f50b86a8ff35df68c6a2ba2709aa7536d10c0bfdff30b6f1207e4d8` | Baseline model feature metadata |
| `tfidf_vectorizer.pkl` | 7,605 | `271607ef3cff9d71b835cf86b16d1ba56b3e8e191fe9ae92942b03657b98cf91` | 16-D NLP Scikit-learn TF-IDF Vectorizer |
| `geo_training_cache.json` | 7,858,367 | `bc507cba1572911b33346f0cff972236e792c89ea4101e1494873111f1ae599e` | Geoapify 5km POI density cache |

---

## 4. Golden Reproducibility Benchmark Results

Executed via `pytest tests/test_reproducibility.py -v`:

```
tests/test_reproducibility.py::test_feature_space_dimensions PASSED
tests/test_reproducibility.py::test_golden_property_reproducibility[16795] PASSED
tests/test_reproducibility.py::test_golden_property_reproducibility[16799] PASSED
tests/test_reproducibility.py::test_golden_property_reproducibility[101] PASSED
tests/test_reproducibility.py::test_golden_property_reproducibility[16797] PASSED

============================= 5 passed in 14.32s ==============================
```

### Detailed Golden Properties Verification:

#### 1. Property ID 16795 (2 BHK Flat In Bilden Swaraganga, Koramangala)
- **Built-up Area**: 1,028 sq.ft. | **BHK**: 2 | **Bathrooms**: 2 | **Balconies**: 1
- **Visual Evidence**: 7 verified original property photos
- **Feature Vector Shape**: `(1, 544)` (6 Struct + 10 Geo + 16 NLP + 512 CNN)
- **Model Version**: `2.1.0-leakage-free-multimodal-resnet18-xgboost`
- **Valuation (INR)**: ₹64,36,467.50 (~₹6,261/sq.ft.)
- **SHAP Breakdown**:
  - `structured_tabular`: 11,581,870.56
  - `image_resnet18`: 4,463,290.25
  - `geospatial_geoapify`: 346,389.82
  - `text_tfidf`: 281,263.01
- **Determinism Check**: Exact match across repeated inferences (0.00% drift).

#### 2. Property ID 16799 (3 BHK Apartment In Ngv Apartment, Koramangala)
- **Built-up Area**: 1,600 sq.ft. | **BHK**: 3 | **Bathrooms**: 3 | **Balconies**: 2
- **Visual Evidence**: 35 verified original property photos
- **Feature Vector Shape**: `(1, 544)`
- **Model Version**: `2.1.0-leakage-free-multimodal-resnet18-xgboost`
- **Valuation (INR)**: ₹1,37,06,784.00 (~₹8,566/sq.ft.)
- **SHAP Breakdown**:
  - `structured_tabular`: 7,326,549.85
  - `image_resnet18`: 5,578,028.79
  - `text_tfidf`: 542,261.23
  - `geospatial_geoapify`: 205,219.53
- **Determinism Check**: Exact match across repeated inferences (0.00% drift).

#### 3. Property ID 101 (PropPulse Direct Test Apartment, Koramangala)
- **Built-up Area**: 1,500 sq.ft. | **BHK**: 3 | **Bathrooms**: 2 | **Balconies**: 1
- **Feature Vector Shape**: `(1, 544)`
- **Model Version**: `2.1.0-leakage-free-multimodal-resnet18-xgboost`
- **Valuation (INR)**: ₹1,29,50,924.00 (~₹8,633/sq.ft.)
- **SHAP Breakdown**:
  - `structured_tabular`: 6,821,955.78
  - `image_resnet18`: 6,086,756.71
  - `geospatial_geoapify`: 448,871.56
  - `text_tfidf`: 340,455.96
- **Determinism Check**: Exact match across repeated inferences (0.00% drift).

#### 4. Property ID 16797 (4 BHK House In Hsr Layout, Koramangala)
- **Built-up Area**: 2,200 sq.ft. | **BHK**: 4 | **Bathrooms**: 4 | **Balconies**: 2
- **Feature Vector Shape**: `(1, 544)`
- **Model Version**: `2.1.0-leakage-free-multimodal-resnet18-xgboost`
- **Valuation (INR)**: ₹2,40,87,824.00 (~₹10,949/sq.ft.)
- **SHAP Breakdown**:
  - `structured_tabular`: 13,570,888.11
  - `image_resnet18`: 8,275,121.97
  - `geospatial_geoapify`: 741,374.25
  - `text_tfidf`: 330,746.96
- **Determinism Check**: Exact match across repeated inferences (0.00% drift).

---

## 5. Security & Zero-Secret Audit

1. **No Live Credentials in Package**:
   - `GeoSmart-Price-AI-Demo.zip` contains 4,078 files (263.83 MB).
   - Zero `.env` files with credentials are packaged. Only safe `.env.example` placeholder files are included.
   - Any sensitive or ephemeral files (`render.env`, credentials, logs, test artifacts) were completely purged.
2. **Safe Payment Handling**:
   - In `DEMO_MODE=true` without live Razorpay credentials, the server raises `503 PAYMENT_GATEWAY_NOT_CONFIGURED` with a truthful message. Fake payments are never recorded.
3. **Safe Telephony Handling**:
   - In `DEMO_MODE=true` without Twilio credentials, outbound telephony calls are not placed.
4. **Data Isolation**:
   - Private owner contact details (phone, email) are masked by default (`mask_lead_for_user`), ensuring complete buyer-seller privacy.

---

## 6. Documented Unavoidable Differences

1. **Floating-Point Tolerances Across CPU Architectures**:
   - Standard PyTorch convolution operations (`torch.nn.functional.conv2d`) and XGBoost tree accumulations can exhibit minute floating-point variances (order of $10^{-5}$ to $10^{-4}$) depending on underlying CPU instruction sets (AVX-512 vs AVX2 vs ARM NEON).
   - **Mitigation**: A relative tolerance bound of $\pm 0.5\%$ is codified and enforced in `tests/test_reproducibility.py`.
2. **Missing Image Graceful Degradation**:
   - When a property lacks verified original imagery, the CNN extraction pipeline deterministically substitutes a 512-dimensional zero vector (`image_vector_l2_norm = 0.0`), allowing XGBoost to compute an unbiased valuation relying on tabular, spatial, and textual dimensions without crashing.
3. **External Service Graceful Degradation**:
   - In offline/demo environments without paid Geoapify API credits, the system defaults to pre-calculated Bengaluru micro-market POI density benchmarks, guaranteeing zero downtime.

---

## 7. Audit Verdict

```
===============================================================
FINAL REPRODUCIBILITY AUDIT: COMPLETE & VERIFIED
===============================================================
TOTAL BACKEND TESTS: 191 PASSED / 0 FAILED / 0 SKIPPED
REPRODUCIBILITY BENCHMARKS: 5 PASSED / 0 FAILED
DISTRIBUTABLE PACKAGE: GeoSmart-Price-AI-Demo.zip (263.83 MB)
STATUS: READY FOR REPRODUCIBLE DEMO EVALUATION
===============================================================
```
