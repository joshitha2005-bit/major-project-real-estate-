# Cloud-Based Real Estate Analysis

[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?style=flat-square)](#)
[![Backend Tests](https://img.shields.io/badge/Tests-191%20Passed-success?style=flat-square)](#)
[![Frontend](https://img.shields.io/badge/Frontend-Vite%20React%2018-blue?style=flat-square)](#)
[![ML Fusion](https://img.shields.io/badge/Feature%20Fusion-544--D%20Multimodal-orange?style=flat-square)](#)
[![Explainability](https://img.shields.io/badge/XAI-TreeSHAP-purple?style=flat-square)](#)

---

## 1. Project Overview

**Cloud-Based Real Estate Analysis** is an end-to-end, reproducible research and production framework for real estate valuation and geospatial intelligence in the Bengaluru metropolitan area. The platform replaces traditional single-modality property appraisal by synthesizing:
- **Architectural / Tabular Specifications**: BHK, built-up area, bathrooms, balconies, locality micro-market pricing, and building vintage.
- **Geospatial & Civic GIS Density**: Multi-category point-of-interest (POI) radius queries across schools, colleges, hospitals, Namma Metro transit, BMTC bus stations, dining, and commercial centers.
- **Semantic Natural Language (NLP)**: High-dimensional TF-IDF listing text descriptors capturing property amenities, luxury specifications, and builder highlights.
- **Deep Computer Vision (CNN)**: PyTorch ResNet-18 visual feature embeddings extracted directly from authentic, verified property imagery.

### Core Distinctions: Local Demo vs. Production Cloud
| Dimension | Local Demo Mode (`DEMO_MODE=true`) | Production Cloud Environment |
| :--- | :--- | :--- |
| **Database Engine** | Embedded SQLite (`real_estate.db`) | Managed PostgreSQL (e.g. Render / AWS RDS) with SSL |
| **Authentication** | Built-in demo credentials (`admin@cloudrealestate.ai`) | Hardened JWT with rotation, bcrypt salt rounds |
| **Model Pipeline** | Real XGBoost, ResNet-18, TF-IDF, TreeSHAP | Exact same verified 544-D model artifacts |
| **External APIs** | Graceful fallback & truthful UI limitations | Live Geoapify, Twilio Voice, Google Gemini, Razorpay |
| **Payment Gateway** | Truthful unconfigured state notice | Live Razorpay merchant checkout with webhook validation |
| **Telephony / Voice**| Safe local console simulation / mock | Live Twilio media streams + Gemini Live WebSocket |

---

## 2. Architecture

```
+-------------------------------------------------------------------------------------------------+
|                        CLOUD-BASED REAL ESTATE ANALYSIS SYSTEM TOPOLOGY                         |
+-------------------------------------------------------------------------------------------------+
                                                 |
                   +-----------------------------+-----------------------------+
                   |                                                           |
                   v                                                           v
+-------------------------------------+                     +-------------------------------------+
|        Frontend Single-Page App     |                     |        FastAPI Backend Engine       |
|  - React 18 / Vite / Vanilla CSS    |  REST / WebSocket   |  - Python 3.13 / Uvicorn            |
|  - Leaflet GIS Maps / Micro-UI      | ------------------> |  - SQLAlchemy ORM (SQLite / Postgres)|
|  - Interactive SHAP Waterfall/Bars  |                     |  - PyTorch ResNet-18 Visual Core    |
|  - Lead CRM & Subscription Client   |                     |  - XGBoost Multi-Modal Regressor    |
+-------------------------------------+                     +-------------------------------------+
                                                                               |
                                    +------------------------------------------+
                                    v
+-------------------------------------------------------------------------------------------------+
|                                 544-D MULTIMODAL FEATURE FUSION                                 |
+-------------------------------------------------------------------------------------------------+
|  [6]  Structured Spec Vector     : area_sqft, bhk, bathrooms, balconies, locality_enc, age      |
|  [10] Geospatial Geoapify Vector : 9 civic POI category counts (5km radius) + total density count|
|  [16] Textual NLP Vector         : 16-D TF-IDF extracted from property description text         |
|  [512] Deep Visual CNN Vector    : 512-D PyTorch ResNet-18 embedding (mean-pooled over photos) |
+-------------------------------------------------------------------------------------------------+
                                    |
                                    v
+------------------------------------------------------+------------------------------------------+
|            Multimodal XGBoost Regressor              |           TreeSHAP Explainability        |
|  Artifact: `backend/models/multimodal_xgboost.joblib`|  Attribution for each of the 544 features|
|  Model Version: `2.1.0-leakage-free-multimodal...`   |  Grouped by Modality & Price Impact (INR)|
+------------------------------------------------------+------------------------------------------+
```

---

## 3. Requirements

### Host Environment Requirements
- **Operating System**: Windows 10/11, Ubuntu 20.04+, or macOS 12+
- **Python**: Version `3.10` to `3.13` (Verified on `Python 3.13.7`)
- **Node.js**: Version `18.x` to `22.x` (Verified on `Node v22.20.0`)
- **Package Managers**: `pip >= 24.0`, `npm >= 9.0`
- **Memory**: Minimum 4 GB RAM (8 GB recommended for ResNet-18 PyTorch operations)
- **Disk Space**: ~2 GB free disk space

---

## 4. Installation

### Option A: 1-Click Windows Setup (Recommended for Windows)
Double-click `START_DEMO.bat` or run from cmd/PowerShell:
```bat
START_DEMO.bat
```
This batch script will automatically check prerequisites, set up `.env`, install dependencies, initialize the demo database, launch backend and frontend servers, and open the application in your browser.

### Option B: Manual Clean Machine Installation

#### 1. Clone or Extract the Repository
```bash
git clone https://github.com/joshitha2005-bit/major-project-real-estate-.git
cd major-project-real-estate-
```

#### 2. Backend Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install pinned backend dependencies
pip install -r backend/requirements.txt
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

---

## 5. Environment Configuration

Copy the sanitized `.env.example` templates to `.env`:

```bash
# Root environment
copy .env.example .env

# Backend environment
copy backend\.env.example backend\.env
```

### Configuration Parameters
```ini
# Core Configuration
DEMO_MODE=true
PROJECT_NAME="Real Estate Price Prediction & GIS Platform"
API_V1_STR="/api/v1"

# Database (Default embedded SQLite for local demo)
DATABASE_URL="sqlite:///./real_estate.db"

# Security (Safe default secret for local demonstration)
JWT_SECRET="local-demo-jwt-secret-key-cloud-real-estate-2026"
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# External APIs (Optional: Platform falls back gracefully when empty)
GEOAPIFY_API_KEY=""
GOOGLE_MAPS_API_KEY=""
GEMINI_API_KEY=""
TWILIO_ACCOUNT_SID=""
TWILIO_AUTH_TOKEN=""
TWILIO_PHONE_NUMBER=""
RAZORPAY_KEY_ID=""
RAZORPAY_KEY_SECRET=""
RAZORPAY_WEBHOOK_SECRET=""

# Admin Credentials for Demo Portal
PRIVATE_ADMIN_EMAIL="admin@cloudrealestate.ai"
PRIVATE_ADMIN_PASSWORD="Admin@2026"
PRIVATE_ADMIN_PHONE="+91 99880 12345"
```

---

## 6. Demo Mode (`DEMO_MODE=true`)

When `DEMO_MODE` is active:
1. **Real ML Execution**: The actual 544-D fusion pipeline, ResNet-18 CNN, TF-IDF vectorizer, XGBoost regressor, and TreeSHAP explainer run genuinely on every request. Predictions are **never** fabricated or hardcoded.
2. **Safe Payments**: If Razorpay credentials are not provided, the payment gateway truthfully reports `PAYMENT_GATEWAY_NOT_CONFIGURED` without claiming fake transactions.
3. **Safe Telephony**: If Twilio credentials are not provided, outbound calls are not made, and an informational limitation is presented truthfully.
4. **Data Protection**: Owner phone numbers and contact details are automatically masked for standard users.
5. **Geospatial Fallback**: If `GEOAPIFY_API_KEY` is not provided, the platform uses verified micro-market Bangalore POI density benchmarks.

---

## 7. Database Initialization

Run the automated database initialization script:
```bash
python backend/init_demo_db.py
```

### What this accomplishes:
1. Creates all database tables via SQLAlchemy ORM metadata (`users`, `properties`, `bank_loan_products`, `ai_leads`, `site_visits`, etc.).
2. Creates the default administrator account (`admin@cloudrealestate.ai` / `Admin@2026`).
3. Seeds the 4 verified golden test properties (IDs: `16795`, `16799`, `101`, `16797`).
4. Seeds 12 verified Indian bank home loan products (SBI, HDFC, ICICI, etc.).

---

## 8. Starting Backend

From the repository root (with virtual environment activated):
```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI Schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 9. Starting Frontend

In a separate terminal:
```bash
cd frontend
npm run dev
```
- **Frontend Application**: [http://localhost:5173](http://localhost:5173)

---

## 10. Docker Startup

The project includes multi-stage container definitions:
- `Dockerfile.backend`: Python 3.11-slim with OpenCV/PyTorch dependencies.
- `Dockerfile.frontend`: Multi-stage Node 20 build served via Nginx.
- `docker-compose.yml`: Single-command container orchestration.

```bash
# Build and run containers
docker-compose up --build

# Run in background
docker-compose up -d
```
Access the application at `http://localhost`.

---

## 11. AI Pipeline & Verification

### Multimodal Modality Composition
| Modality | Features | Extraction Engine | Dimension |
| :--- | :--- | :--- | :--- |
| **Tabular** | Area, BHK, Baths, Balconies, Locality, Age | Standardized numeric transforms | 6 |
| **Geospatial** | Schools, Hospitals, Metro, Malls, Banks, etc. | Geoapify radius POI aggregator | 10 |
| **Textual** | Listing keywords, luxury amenities | Scikit-learn TF-IDF Vectorizer | 16 |
| **Visual** | Architectural & interior imagery | PyTorch Pretrained ResNet-18 | 512 |
| **Total** | **Unified Feature Vector** | **Concatenation & Imputation** | **544** |

### Running the Golden Reproducibility Test
```bash
pytest backend/tests/test_reproducibility.py -v
```

### Golden Properties Benchmark Values
| Property ID | Configuration | Predicted Price (INR) | Fused Dim | SHAP Modalities |
| :--- | :--- | :--- | :--- | :--- |
| **16795** | 2 BHK Flat, Koramangala (1028 sqft) | ₹64,36,467.50 | 544 | 4 / 4 Active |
| **16799** | 3 BHK Flat, Koramangala (1600 sqft) | ₹1,37,06,784.00 | 544 | 4 / 4 Active |
| **101** | 3 BHK Apartment, Koramangala (1500 sqft) | ₹1,29,50,924.00 | 544 | 4 / 4 Active |
| **16797** | 4 BHK House, Koramangala (2200 sqft) | ₹2,40,87,824.00 | 544 | 4 / 4 Active |

---

## 12. Troubleshooting

### 1. `ModuleNotFoundError: No module named 'app'`
Make sure you run scripts from the `backend/` directory or run python with `PYTHONPATH=.`.

### 2. PyTorch Torchvision Warnings
On clean Windows systems, PyTorch might emit CPU optimization hints; these do not affect prediction output or numerical reproducibility.

### 3. Port Conflicts
- Backend defaults to port `8000`. If busy, specify: `uvicorn app.main:app --port 8080`
- Frontend defaults to port `5173`. Vite will automatically suggest `5174` if busy.

---

## 13. Production Deployment

### Production Cloud Infrastructure (Render / AWS)
1. Set `DATABASE_URL` to your production PostgreSQL connection string with SSL (`sslmode=require`).
2. Run database migrations: `alembic upgrade head`.
3. Set `JWT_SECRET` to a cryptographically secure 256-bit string.
4. Set `DEMO_MODE=false`.
5. Supply merchant credentials for live Razorpay and Twilio.

---

## 14. External API Configuration

When enabling live cloud services, populate the respective fields in `.env`:
- **Geoapify API**: Obtain a key at [geoapify.com](https://www.geoapify.com/) and set `GEOAPIFY_API_KEY`.
- **Google Gemini**: Obtain a key from Google AI Studio and set `GEMINI_API_KEY`.
- **Twilio**: Obtain Account SID, Auth Token, and a verified Twilio phone number and set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`.
- **Razorpay**: Generate API Keys from the Razorpay Dashboard (Test or Live) and set `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`.

---

## 15. Security Notes

1. **No Credentials in Version Control**: `.env` is strictly git-ignored. Only `.env.example` with safe placeholder values is committed.
2. **Contact Privacy**: Private property owner contact details (`phone`, `email`) are masked for non-admin viewers to prevent unsolicited contact and data harvesting.
3. **HMAC Signature Verification**: All Razorpay payment captures are mathematically verified on the backend via HMAC-SHA256 before granting `PRO` subscription status.
4. **Role-Based Access Control**: Sensitive admin and CRM endpoints (`/api/v1/admin/*`) enforce strict role validation via JWT claims.

---
*Cloud-Based Real Estate Analysis — Built for transparent, multimodal, and reproducible real estate intelligence.*
