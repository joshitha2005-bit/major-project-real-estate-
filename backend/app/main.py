import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api.v1 import auth, location, properties, ai, listings, voice_assistant
from app.services.seed_service import SeedService
from app.models.user import User
from app.models.subscription import Subscription


from app.core.migration import run_migrations

# Run schema migrations first
run_migrations()

# Create database tables
Base.metadata.create_all(bind=engine)


# Trigger initial seed
db = SessionLocal()
try:
    SeedService.seed_properties(db)
finally:
    db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for property uploaded images
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
os.makedirs(os.path.join(STATIC_DIR, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include API v1 Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(location.router, prefix=f"{settings.API_V1_STR}/location", tags=["Location & GIS"])
app.include_router(properties.router, prefix=f"{settings.API_V1_STR}/properties", tags=["Properties"])
app.include_router(listings.router, prefix=f"{settings.API_V1_STR}/listings", tags=["Direct Listings"])
app.include_router(ai.router, prefix=f"{settings.API_V1_STR}/ai", tags=["AI Engine"])
app.include_router(voice_assistant.router, prefix=f"{settings.API_V1_STR}/voice-assistant", tags=["AI Voice Property Assistant"])

@app.get("/")
def root():
    return {
        "status": "healthy",
        "platform": settings.PROJECT_NAME,
        "docs": "/docs",
        "version": "1.0.0"
    }
