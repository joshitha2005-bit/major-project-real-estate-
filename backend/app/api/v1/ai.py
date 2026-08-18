import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.property import Property
from app.services.image_ai_service import ImageAIService
from app.services.text_ai_service import TextAIService
from app.services.safety_service import SafetyGuardService
from app.services.price_prediction_service import PricePredictionService
from app.services.pdf_report_service import PDFReportService
from app.api.v1.properties import enrich_property_out
from app.models.user import User
from app.api.deps import verify_pro_access


router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

@router.get("/analyze-property/{id}", response_model=Dict[str, Any])
async def analyze_property_full_ai(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_pro_access)
):

    """Run complete AI suite (CV, NLP, Safety Guard, XGBoost Price Prediction, SHAP Explainability) on a property."""
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    enriched = enrich_property_out(prop).model_dump()

    # 1. Computer Vision Image Analysis
    cv_results = ImageAIService.analyze_property_images(prop.images or [], BASE_DIR)

    # 2. NLP Text Analysis
    nlp_results = TextAIService.analyze_description(prop.description or "")

    # 3. Locality Safety Guard Analysis
    safety_results = await SafetyGuardService.analyze_locality_safety(prop.address, prop.latitude, prop.longitude)


    # 4. XGBoost Price Prediction & SHAP Explainability
    prediction_results = PricePredictionService.predict_property_valuation(
        address=prop.address,
        lat=prop.latitude,
        lon=prop.longitude,
        area_sqft=prop.area_sqft,
        bhk=prop.bhk,
        bathrooms=prop.bathrooms,
        parking=prop.parking,
        facing=prop.facing,
        property_age=prop.property_age,
        nearby_places=prop.nearby_places or [],
        image_score=cv_results.get("overall_score", 80.0),
        text_score=nlp_results.get("text_quality_score", 75.0)
    )

    return {
        "property": enriched,
        "image_ai": cv_results,
        "text_ai": nlp_results,
        "safety_guard": safety_results,
        "price_prediction": prediction_results
    }

@router.get("/property-report/{id}/pdf")
async def generate_pdf_report(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_pro_access)
):
    """Generate and stream downloadable PDF report for a property."""
    prop = db.query(Property).filter(Property.id == id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    enriched = enrich_property_out(prop).model_dump()
    analytics = await analyze_property_full_ai(id, db, current_user=current_user)


    pdf_bytes = PDFReportService.generate_property_pdf_report(enriched, analytics)
    
    filename = f"PropPulse_Report_{prop.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

