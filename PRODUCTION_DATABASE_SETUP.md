# Production Database Setup Guide — Render PostgreSQL

This guide documents the production database configuration, schema migrations, and environment variable requirements for deploying the **GeoSmart Price AI / PropPulse** FastAPI backend to Render.

---

## 1. Render PostgreSQL Database Creation

1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. Click the **"New +"** button in the top navigation bar and select **"PostgreSQL"**.
3. Fill in the database details:
   - **Name**: `geosmart-proppulse-db`
   - **Database**: `real_estate_db` (or accept default)
   - **User**: (auto-generated or custom)
   - **Region**: Select the same region as your backend Web Service (e.g., *Oregon (US West)* or *Frankfurt (EU)*) to minimize latency.
   - **PostgreSQL Version**: `16` (or latest stable)
   - **Instance Type**: `Free` or `Starter`
4. Click **"Create Database"**.
5. Once provisioned, locate the **"Connections"** section:
   - If your FastAPI backend is deployed on Render: Copy the **Internal Database URL** (e.g., `postgres://user:password@dpg-...-a:5432/real_estate_db`).
   - If connecting from external tools or local testing: Copy the **External Database URL**.

---

## 2. DATABASE_URL Configuration

1. In your Render Dashboard, navigate to your backend **Web Service** (`cloud-based-real-estate-backend`).
2. Go to the **"Environment"** tab.
3. Add or update the following environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: *(Paste the Render PostgreSQL connection string copied above)*

> [!NOTE]
> **Automatic Dialect Normalization:**
> Render provides PostgreSQL URLs prefixed with `postgres://`. SQLAlchemy 2.0+ requires `postgresql://` or `postgresql+psycopg2://`. The application (`app/core/database.py` and `alembic/env.py`) automatically detects and normalizes `postgres://` to `postgresql://` at runtime, requiring no manual URL edits.

---

## 3. Database Schema Migrations & Startup

The backend supports two seamless initialization pathways:

### Option A: Automatic Table Creation on Startup (Zero Manual Steps)
FastAPI's startup sequence in `app/main.py` automatically invokes:
```python
Base.metadata.create_all(bind=engine)
```
When pointed to a fresh Render PostgreSQL instance, all 16 application tables and indexes are automatically created upon initial boot.

### Option B: Alembic Database Migration
You can apply versioned migrations using Alembic:
```bash
# In the backend directory:
alembic upgrade head
```
To set this to run automatically on every Render deployment, update your Render **Build Command**:
```bash
pip install -r requirements.txt && alembic upgrade head
```

---

## 4. Verification Commands

### Check Alembic Migration Status
```bash
cd backend
alembic current
alembic heads
```
Expected output:
```
a8e7309dd217 (head)
```

### Verify Live Database Connectivity via API
1. Check the interactive API documentation:
   `https://<your-render-backend-url>/docs`
2. Test the property catalog endpoint:
   `GET /api/v1/properties`
3. Test authentication:
   `POST /api/v1/auth/login`

---

## 5. Local Development vs. Production Database Behavior

| Parameter | Local Development (SQLite) | Production (Render PostgreSQL) |
| :--- | :--- | :--- |
| **DATABASE_URL** | `sqlite:///./real_estate.db` (default fallback) | `postgres://...` or `postgresql://...` (via env) |
| **Driver** | Built-in Python `sqlite3` | `psycopg2-binary>=2.9.9` |
| **Connection Pooling** | Single-connection (`check_same_thread: False`) | Pooled (`pool_size=10`, `max_overflow=20`, `pool_recycle=1800`, `pool_pre_ping=True`) |
| **Persistence** | Local file on disk | Managed cloud database with automatic failover |
| **Safety** | Isolated testing without affecting production | Scalable multi-worker concurrent transactions |

---

## 6. Supported Application Tables

All existing application models are fully supported in PostgreSQL:
1. `users` — User profiles, roles (`USER`, `ADMIN`), hashed passwords.
2. `properties` — Real estate catalog, spatial coordinates, multimodal specifications.
3. `property_images` — Image metadata, provenance badges, quality scores, SHA-256 hashes.
4. `subscriptions` — PropPulse Pro subscriptions, Razorpay order/payment IDs, validity dates.
5. `bank_loan_products` — 6-bank comparative interest rates, eligibility rules, processing fees.
6. `loan_calculations` — Buyer loan calculations and EMI parameters.
7. `loan_comparison_reports` — Stored comparative mortgage reports.
8. `voice_callback_requests` — Twilio voice telephony sessions, call SIDs, inquiry logs.
9. `property_inquiries` — Buyer property inquiry logs.
10. `private_owner_contacts` — Sensitive owner/agent contact data with strict privacy masking.
11. `ai_leads` — Extracted AI leads with timeline, budget, and CRM status workflows.
12. `site_visits` — Scheduled property visits with appointment codes and statuses.
13. `admin_audit_logs` — Immutable audit logs of administrative actions.
14. `search_history` — User locality searches and queries.
15. `saved_locations` — User locality bookmarks.
16. `market_references` — Historical market valuation reference data.

---

## 7. Render Web Service Deployment Configuration

- **Language**: `Python`
- **Root Directory**: `backend`
- **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
