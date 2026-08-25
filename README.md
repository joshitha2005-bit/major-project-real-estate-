# PropPulse AI - Real Estate Price Prediction & GIS Platform

Production-ready Real Estate Price Intelligence, Property Management, Computer Vision, NLP, Locality Safety Guard, SHAP Explainability, and Spatial GIS Platform built for Bangalore metro areas and Indian urban localities.

![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20React%2019%20%7C%20XGBoost%20%7C%20OpenCV%20%7C%20PostgreSQL-0284c7)

---

## 🔗 Live Demo Links

Click the links below to view the live project:

| Service | Live Link | Status |
| :--- | :--- | :--- |
| **Frontend Web App** | [🔗 Visit Live Demo](https://joshitha2005-bit.github.io/cloud-based-real-estate) | [![Frontend](https://img.shields.io/badge/Frontend-Active-success?style=flat-square)](https://joshitha2005-bit.github.io/cloud-based-real-estate) |
| **Backend API Gateway** | [🔗 View API Docs](https://cloud-based-real-estate-backend.onrender.com/docs) | [![Backend API](https://img.shields.io/badge/API-Active-success?style=flat-square)](https://cloud-based-real-estate-backend.onrender.com/docs) |

> [!NOTE]
> If your live links are different, simply update the URLs in this section of the [README.md](file:///c:/real%20estate/README.md) file.

---

## 🚀 Key Features

- **JWT Authentication & Security**: Complete registration, login, logout, password hashing with `passlib[bcrypt]`, and protected routes.
- **XGBoost Price Prediction Engine**:
  - Predicts **Selling Price**, **Estimated Rental Price** (annual yield), **Price per Sq.ft**, and **Confidence Score (%)**.
  - Incorporates spatial coordinates, area, BHK, bathrooms, parking, facing, building age, nearby amenities counts, CV Image Score, and NLP Text Score.
- **Computer Vision Image AI ("The Eyes")**:
  - OpenCV image analysis calculating Image Quality, Brightness, Sharpness (Laplacian variance), Interior Condition, Exterior Condition, and Overall Property Condition.
- **NLP Text AI ("The Ears")**:
  - Description scoring using TF-IDF & NLTK keyword detection (Gated Community, Lake View, Corner Site, Luxury, Near Metro, Premium, Club House, Swimming Pool, Gym).
- **Locality Safety Guard**:
  - Risk analysis computing Safety Score, Crime Score, Flood Risk, Traffic Congestion, and Locality Grade (A+, A, B+, B, C).
- **SHAP Explainable AI**:
  - Feature attribution identifying Top Positive Price Drivers, Top Negative Adjustments/Penalties, and Feature Importance contribution breakdown.
- **AI Intelligence Dashboard (`/analytics/:id`)**:
  - Interactive dashboard presenting valuation cards, CV gauges, NLP keyword tags, safety meters, SHAP breakdown, location maps, and nearby amenities.
- **PDF Report Generation**:
  - Downloadable PDF report (`GET /api/v1/ai/property-report/{id}/pdf`) rendering valuation summaries, safety ratings, and SHAP explainability.
- **Bangalore Locality GIS Search**: Geocode string queries (Koramangala, Whitefield, Electronic City, HSR Layout, Indiranagar, Marathahalli, JP Nagar, Banashankari) or any custom address into precise coordinates.
- **Categorized Nearby Amenities**: Real-time spatial query & persistence of 9 categories (Schools, Colleges, Hospitals, Metro, Bus Stops, Restaurants, Malls, Banks, Parks).
- **Interactive OpenStreetMap**: Built with React Leaflet 19, custom SVG markers, popups, and current location tracking.

---

## 🛠️ Tech Stack

### Frontend
- **React 18 / 19** + **Vite**
- **Tailwind CSS v3** (Glassmorphic dark theme)
- **React Router DOM v6**
- **Axios** (JWT interceptor & Multipart FormData)
- **React Hook Form**
- **React Leaflet** & **Leaflet**
- **Lucide React** icons

### Backend & AI Engine
- **Python FastAPI**
- **XGBoost** & **Scikit-learn**
- **OpenCV (cv2)** & **Pillow**
- **NLTK** & **TF-IDF**
- **ReportLab** (PDF Report Generation)
- **SQLAlchemy 2.0 ORM** (PostgreSQL / SQLite)
- **Pydantic v2**
- **JWT (jose)** & **Passlib (bcrypt)**
- **FastAPI StaticFiles** middleware
- **Alembic** database migrations

---

## 📄 API Endpoints Reference

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/auth/register` | Register new user account | No |
| `POST` | `/api/v1/auth/login` | Authenticate user & get JWT token | No |
| `GET`  | `/api/v1/auth/profile` | Retrieve user profile & search stats | Yes |
| `GET`  | `/api/v1/ai/analyze-property/{id}` | Run full AI suite (XGBoost, CV, NLP, Safety, SHAP) | No |
| `GET`  | `/api/v1/ai/property-report/{id}/pdf` | Download PDF valuation & GIS report | No |
| `POST` | `/api/v1/properties/upload-images` | Upload multiple property photos | Yes |
| `POST` | `/api/v1/properties/` | Submit property with Geoapify nearby places | Yes |
| `GET`  | `/api/v1/properties/` | List properties with BHK/Type/Price filters | No |
| `GET`  | `/api/v1/properties/{id}` | Get property details by ID | No |
| `DELETE`|`/api/v1/properties/{id}` | Delete property (owner only) | Yes |
| `GET`  | `/api/v1/location/search-location` | Geocode query & estimate price/sqft | Optional |
| `GET`  | `/api/v1/location/nearby-places` | Fetch 9 categories of nearby GIS amenities | No |
| `GET`  | `/api/v1/location/current-location` | Reverse geocode coordinates | No |
| `GET`  | `/api/v1/location/search-history` | Get user search history logs | Yes |
| `POST` | `/api/v1/location/saved-locations` | Save locality bookmark | Yes |
| `GET`  | `/api/v1/location/saved-locations` | Retrieve user saved locations | Yes |

---

## 🏁 Quickstart Guide

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- Interactive API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
- App UI URL: [http://localhost:5173](http://localhost:5173)

---

## 🐳 Docker Deployment

```bash
docker-compose -f docker/docker-compose.yml up --build
```
- App Access: [http://localhost](http://localhost)
- API Access: [http://localhost:8000](http://localhost:8000)
