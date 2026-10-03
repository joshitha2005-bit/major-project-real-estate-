# GeoSmart Price AI / PropPulse Real Estate Platform

Production-ready Multimodal Real Estate Valuation, Bangalore Property Catalog, Spatial GIS Intelligence, TreeSHAP Explainability, AI Voice Property Assistant, Private CRM & Admin Dashboard, and PropPulse Pro Subscription System.

![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?style=flat-square)
![Tests](https://img.shields.io/badge/Backend%20Tests-186%20Passed-success?style=flat-square)
![Frontend](https://img.shields.io/badge/Frontend-Vite%20React%2018-blue?style=flat-square)
![ML Pipeline](https://img.shields.io/badge/Multimodal%20Vector-544--D%20XGBoost-orange?style=flat-square)
![Subscriptions](https://img.shields.io/badge/PropPulse%20Pro-%E2%82%B9299%2Fmonth-indigo?style=flat-square)

---

## 📌 Repository & Deployment Status

- **GitHub Repository**: [https://github.com/joshitha2005-bit/major-project-real-estate-.git](https://github.com/joshitha2005-bit/major-project-real-estate-.git)
- **Frontend Live Demo**: NOT DEPLOYED (GitHub Pages workflow configured; awaiting production backend link)
- **Backend API**: NOT DEPLOYED (Render configuration prepared; requires live Render web service launch & environment secret provisioning)
- **Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs) (Local) / `/docs` on deployed backend

---

## 🏗️ System Architecture & 544-D Multimodal Pipeline

GeoSmart Price AI integrates tabular property specifications, spatial geographic context, natural language description features, and deep computer vision representations into a unified **544-dimensional multimodal vector** feeding an **XGBoost regressor** with **TreeSHAP explainability**:

```
+-----------------------------------------------------------------------------------+
|                           544-D MULTIMODAL FEATURE FUSION                         |
+-----------------------------------------------------------------------------------+
|  [6] Structured Specs  : BHK, Total Area, Bathrooms, Balconies, Price/SqFt, Age   |
|  [10] Geoapify GIS     : Schools, Banks, Bus Stops, Pharmacies, Restaurants,      |
|                          Malls, Colleges, Police Stations, Transit, Hospitals      |
|  [16] TF-IDF NLP       : High-value luxury descriptors & locality keywords       |
|  [512] ResNet-18 Embed : Deep visual features from verified property photography  |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |  Multimodal XGBoost Regressor     |
                     |  -> Valuation & Rental Estimation |
                     +-----------------------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |  TreeSHAP Explainability Engine   |
                     |  -> Attribution breakdown by D    |
                     +-----------------------------------+
```

### Dataset & Provenance
- **Main AI-Ready Properties**: 863 verified Bangalore records with coordinates and spatial POI.
- **Genuine Property Images**: 11,665 photos with cryptographic SHA-256 fingerprinting and strict anti-leak provenance. Representative stock photos are strictly quarantined from entering the CNN inference vector.

---

## 🌟 Key Platform Modules

### 1. Bangalore Property Catalog & Search
- Full text, BHK, locality, price range, and amenity filtering across Bangalore localities (Whitefield, Koramangala, Indiranagar, HSR Layout, Electronic City, Bellandur, etc.).
- Genuine photo galleries with provenance badges (`VERIFIED_ORIGINAL` vs `REPRESENTATIVE`).
- Interactive Leaflet OpenStreetMap with POI heatmaps and distance circles.

### 2. PropPulse Pro Subscription & Razorpay Integration
- **Tiers**:
  - **FREE (₹0)**: Public property catalog, search, details, genuine photos, basic map, standard EMI calculator.
  - **PRO (₹299/month - 29900 paise)**: 544-D AI multimodal valuation, TreeSHAP price driver breakdown, ResNet-18 visual feature analysis, advanced Geoapify GIS metrics, multi-bank loan comparison, premium loan & valuation PDFs, AI Voice Property Assistant.
- **Security & User Isolation**:
  - Razorpay order creation and HMAC-SHA256 signature verification executed strictly on the server (`app/services/subscription_service.py`).
  - Payments are tied directly to authenticated JWT `user_id`. No cross-user activation or client-side tampering possible.
  - Webhooks verified with `X-Razorpay-Signature` against `RAZORPAY_WEBHOOK_SECRET`.
  - Non-Pro access to protected endpoints returns `HTTP 403` with code `PRO_REQUIRED`.

### 3. Home Loan Comparison & Premium PDF Reports
- Multi-bank loan comparison engine (SBI, HDFC, ICICI, Axis, Bank of Baroda, Kotak).
- Dynamic EMI calculator, processing fees, loan tenure comparison, and eligibility estimators.
- Pro users can generate and download comprehensive, publication-grade Mortgage PDF comparison reports.

### 4. AI Voice Property Assistant (Twilio + Google Gemini)
- Integrated voice assistant connecting buyers with property-context AI via real telephony (Twilio Programmable Voice).
- Multi-turn conversation powered by Google Gemini with strict property grounding (never invents false details).
- Automatically captures visitor preferences, extracts validated AI leads, schedules site visits, and registers owner callback requests.

### 5. Private Admin Dashboard & CRM
- Dedicated private administrative portal (`/admin/dashboard`) requiring `ADMIN` role.
- Comprehensive lead management with status workflows (`NEW`, `CONTACTED`, `SITE_VISIT_REQUESTED`, `CLOSED`, `SPAM`).
- Sensitive owner contact masking: unauthenticated users and regular buyers never see private phone numbers or personal contact data.
- Complete immutable audit logging and real-time subscription roster visibility.

---

## 🔌 API Endpoints Summary

### Subscriptions & Access Control (`/api/v1/subscriptions`)
- `GET /config`: Public gateway status and Razorpay key ID (no secrets exposed).
- `GET /me`: Authenticated user's active subscription profile and expiry.
- `POST /create-order`: Server-authenticated order generation for ₹299 (29900 paise).
- `POST /verify-payment`: Cryptographic HMAC payment signature verification and PRO role activation.
- `POST /webhook`: Razorpay asynchronous lifecycle event webhook.
- `POST /cancel`: User-initiated subscription cancellation.

### AI & GIS Engine (`/api/v1/ai`)
- `POST /predict-price-multimodal`: 544-D multimodal valuation (Pro required).
- `GET /explain-shap/{id}`: TreeSHAP feature attributions (Pro required).
- `GET /property-report/{id}/pdf`: Downloadable AI valuation PDF report (Pro required).

### Private Admin (`/api/v1/admin`)
- `POST /login`: Administrative credential authentication.
- `GET /stats`: Real-time KPI summary counts.
- `GET /leads`: Lead pipeline management.
- `GET /subscriptions`: Subscription roster and active PRO accounts.
- `GET /audit-logs`: Administrative action audit trails.

### Loans & Telephony (`/api/v1/loans`, `/api/v1/voice-assistant`)
- `POST /loans/compare`: Multi-bank comparison (Pro required).
- `POST /loans/report/pdf`: Mortgage analysis PDF (Pro required).
- `POST /voice-assistant/call-request`: Outbound Twilio AI telephone call dispatch (Pro required).

---

## 💻 Local Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm 9+

### 1. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at [http://localhost:8000/docs](http://localhost:8000/docs).

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Web application will be live at [http://localhost:5173](http://localhost:5173).

### 3. Running Test Suites
```bash
# Backend (Full regression suite)
pytest tests -q

# Frontend (Production build validation)
cd frontend
npm run build
```

---

## 🔒 Security & Environment Variables

Create a `backend/.env` file with the following keys (do **not** commit this file):

```ini
# Application
PROJECT_NAME="Real Estate Price Prediction & GIS Platform"
API_V1_STR="/api/v1"
DATABASE_URL="sqlite:///./real_estate.db"

# Security
JWT_SECRET="your-strong-random-jwt-secret"
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Geoapify GIS
GEOAPIFY_API_KEY="your-geoapify-key"

# AI Voice & Telephony
GEMINI_API_KEY="your-google-ai-studio-gemini-key"
GEMINI_LIVE_MODEL="gemini-2.0-flash-exp"
TWILIO_ACCOUNT_SID="your-twilio-sid"
TWILIO_AUTH_TOKEN="your-twilio-auth-token"
TWILIO_PHONE_NUMBER="your-twilio-phone"
VOICE_PUBLIC_BASE_URL="https://your-public-webhook-tunnel"

# Razorpay Subscriptions (PropPulse Pro)
RAZORPAY_KEY_ID="rzp_test_or_live_key"
RAZORPAY_KEY_SECRET="your_razorpay_secret"
RAZORPAY_WEBHOOK_SECRET="your_webhook_secret"

# Private Admin Credentials
PRIVATE_ADMIN_EMAIL="admin@geosmart.ai"
PRIVATE_ADMIN_PHONE="+91 99880 12345"
PRIVATE_ADMIN_PASSWORD="YourSecureAdminPassword"
```

---

## ☁️ Deployment Instructions

### Backend (Render / Cloud Container)
1. Link your GitHub repository `https://github.com/joshitha2005-bit/major-project-real-estate-.git` to Render as a Web Service.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set Environment Variables in Render Dashboard (refer to `.env.example`).

### Frontend (GitHub Pages / Vercel / Netlify)
1. The included `.github/workflows/deploy.yml` automatically triggers on push to `main` and deploys the Vite bundle to GitHub Pages.
2. Set repository secret `VITE_API_URL` to point to the live Render backend URL.
