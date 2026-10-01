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
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./real_estate.db")
    
    # Geoapify GIS API Key (Loaded strictly from env variable GEOAPIFY_API_KEY)
    GEOAPIFY_API_KEY: str = os.getenv("GEOAPIFY_API_KEY", "7e57c95ce01147f38a78dab8029c635a")
    
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
