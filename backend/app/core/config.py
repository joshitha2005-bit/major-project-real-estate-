import os
from typing import List
from pydantic_settings import BaseSettings

# Load python-dotenv if available
try:
    from dotenv import load_dotenv
    # Search root and backend .env
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"))
except ImportError:
    pass

class Settings(BaseSettings):
    PROJECT_NAME: str = "Real Estate Price Prediction & GIS Platform"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("JWT_SECRET", "super-secret-key-real-estate-platform-2026-bangalore")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Mode configuration
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1")
    
    # Database
    _DEFAULT_DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "real_estate.db")
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{_DEFAULT_DB_FILE.replace(chr(92), '/')}")
    
    # Geoapify GIS API Key (Loaded strictly from env variable GEOAPIFY_API_KEY)
    GEOAPIFY_API_KEY: str = os.getenv("GEOAPIFY_API_KEY", "")
    
    # Google Maps API Configuration
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")

    # Gemini Live Voice Assistant
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_LIVE_MODEL: str = os.getenv("GEMINI_LIVE_MODEL", "gemini-2.0-flash-exp")

    # Twilio Programmable Voice & Media Streams
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    VOICE_PUBLIC_BASE_URL: str = os.getenv("VOICE_PUBLIC_BASE_URL", "http://localhost:8000")

    # Razorpay Payment Gateway Configuration
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")
    RAZORPAY_WEBHOOK_SECRET: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
    PROPULSE_PRO_AMOUNT_PAISE: int = 29900  # ₹299.00 = 29900 paise
    PROPULSE_PRO_CURRENCY: str = "INR"

    @property
    def is_razorpay_configured(self) -> bool:
        """Check if real Razorpay credentials are provided."""
        key_id = (self.RAZORPAY_KEY_ID or "").strip()
        key_secret = (self.RAZORPAY_KEY_SECRET or "").strip()
        return bool(
            key_id and key_secret and 
            not key_id.startswith("rzp_test_placeholder") and
            len(key_id) >= 10 and len(key_secret) >= 10
        )

    # Private Admin Configuration (Environment-driven, never hardcoded in client)
    PRIVATE_ADMIN_EMAIL: str = os.getenv("PRIVATE_ADMIN_EMAIL", "admin@geosmart.ai")
    PRIVATE_ADMIN_PHONE: str = os.getenv("PRIVATE_ADMIN_PHONE", "+91 99880 12345")
    PRIVATE_ADMIN_PASSWORD: str = os.getenv("PRIVATE_ADMIN_PASSWORD", "GeoSmartAdmin@2026")
    AUTO_SEND_HIGH_CONFIDENCE_LEADS: bool = os.getenv("AUTO_SEND_HIGH_CONFIDENCE_LEADS", "false").lower() in ("true", "1")
    OWNER_NOTIFICATION_PROVIDER: str = os.getenv("OWNER_NOTIFICATION_PROVIDER", "")  # e.g. "", "EMAIL", "SMS", "WHATSAPP"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
