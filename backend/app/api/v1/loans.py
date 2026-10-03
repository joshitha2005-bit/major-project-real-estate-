"""
GeoSmart Price AI - Smart Home Loan & Bank Comparison Endpoints
Provides bank listings, EMI calculation, indicative eligibility, multi-bank comparisons,
and PDF report streaming.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
import re
import json

from app.core.database import get_db
from app.models.property import Property
from app.models.loan import BankLoanProduct, LoanCalculation, LoanComparisonReport
from app.services.loan_comparison_service import LoanComparisonService
from app.services.loan_pdf_service import LoanPdfService
from app.models.user import User
from app.dependencies.subscriptions import require_pro_subscription

router = APIRouter()

# ----------------- PYDANTIC SCHEMAS -----------------

class LoanCalculateRequest(BaseModel):
    loan_amount: float = Field(..., gt=0, description="Desired principal loan amount in INR")
    interest_rate: float = Field(..., gt=0, le=25.0, description="Annual interest rate percentage")
    tenure_years: int = Field(..., ge=1, le=30, description="Repayment tenure in years (1-30)")

class LoanCalculateResponse(BaseModel):
    loan_amount: float
    annual_rate: float
    tenure_years: int
    tenure_months: int
    emi: float
    total_interest: float
    total_repayment: float

class LoanCompareRequest(BaseModel):
    property_id: Optional[int] = Field(None, description="Optional property listing ID")
    full_name: str = Field(..., min_length=2, max_length=150, description="Applicant full name")
    mobile_number: str = Field(..., description="Indian 10-digit mobile number")
    age: int = Field(..., ge=18, le=75, description="Applicant age in years (18-75)")
    monthly_income: float = Field(..., gt=0, description="Net/gross monthly income in INR")
    employment_type: str = Field(..., description="Salaried, Self-employed, or Business")
    existing_monthly_emi: float = Field(0.0, ge=0, description="Current existing monthly EMI obligations in INR")
    property_price: float = Field(..., gt=0, description="Property listing or agreed purchase price in INR")
    down_payment: float = Field(..., ge=0, description="Borrower own contribution in INR")
    desired_loan_amount: Optional[float] = Field(None, gt=0, description="Optional override for desired loan amount")
    preferred_tenure_years: int = Field(20, ge=5, le=30, description="Preferred loan tenure in years (5, 10, 15, 20, 25, 30)")

    @field_validator("mobile_number")
    def validate_phone(cls, v):
        cleaned = re.sub(r"[\s\-\+\(\)]", "", v)
        if cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        if not (len(cleaned) == 10 and cleaned.isdigit() and cleaned[0] in "6789"):
            raise ValueError("Mobile number must be a valid 10-digit Indian phone number starting with 6, 7, 8, or 9.")
        return cleaned

    @field_validator("down_payment")
    def validate_down_payment(cls, v, values):
        return v

    @field_validator("employment_type")
    def validate_emp_type(cls, v):
        valid = ["salaried", "self-employed", "business"]
        if v.lower() not in valid:
            raise ValueError(f"Employment type must be one of: Salaried, Self-employed, Business.")
        return v.title()

class BankProductResponse(BaseModel):
    id: int
    bank_name: str
    product_name: str
    bank_type: str
    interest_rate_min: float
    interest_rate_max: float
    rate_type: str
    min_loan: float
    max_loan: float
    max_tenure_years: int
    processing_fee_text: str
    eligibility_summary: str
    source_url: str
    source_name: str
    publication_date: str
    last_verified_date: str
    special_features: List[str]

# ----------------- ROUTE HANDLERS -----------------

@router.get("/banks", response_model=List[BankProductResponse])
def get_verified_bank_loan_products(db: Session = Depends(get_db)):
    """
    Retrieve all verified Indian home loan providers with official rates,
    processing fees, sources, and verification dates.
    """
    banks = db.query(BankLoanProduct).filter(BankLoanProduct.is_active == True).all()
    if not banks:
        from app.services.loan_seed_data import VERIFIED_BANK_PRODUCTS
        for item in VERIFIED_BANK_PRODUCTS:
            db.add(BankLoanProduct(**item))
        db.commit()
        banks = db.query(BankLoanProduct).filter(BankLoanProduct.is_active == True).all()
    result = []
    for b in banks:
        result.append(BankProductResponse(
            id=b.id,
            bank_name=b.bank_name,
            product_name=b.product_name,
            bank_type=b.bank_type,
            interest_rate_min=b.interest_rate_min,
            interest_rate_max=b.interest_rate_max,
            rate_type=b.rate_type,
            min_loan=b.min_loan,
            max_loan=b.max_loan,
            max_tenure_years=b.max_tenure_years,
            processing_fee_text=b.processing_fee_text,
            eligibility_summary=b.eligibility_summary,
            source_url=b.source_url,
            source_name=b.source_name,
            publication_date=b.publication_date,
            last_verified_date=b.last_verified_date,
            special_features=b.special_features or []
        ))
    return result

@router.post("/calculate", response_model=LoanCalculateResponse)
def calculate_single_loan(req: LoanCalculateRequest):
    """
    Calculate monthly EMI, total interest, and total payable amount
    using the standard compound interest EMI formula.
    """
    calc = LoanComparisonService.calculate_emi(
        principal=req.loan_amount,
        annual_rate_pct=req.interest_rate,
        tenure_years=req.tenure_years
    )
    return LoanCalculateResponse(
        loan_amount=req.loan_amount,
        annual_rate=req.interest_rate,
        tenure_years=req.tenure_years,
        tenure_months=calc["tenure_months"],
        emi=calc["emi"],
        total_interest=calc["total_interest"],
        total_repayment=calc["total_repayment"]
    )

@router.post("/compare")
def compare_home_loans(
    req: LoanCompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pro_subscription)
):
    """
    Compare verified Indian lenders for the specified property and borrower profile,
    evaluating indicative eligibility, LTV benchmarks, and personalized insights.
    """
    if req.down_payment >= req.property_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Down payment cannot be greater than or equal to the property price."
        )

    # Determine required loan amount
    auto_loan = req.property_price - req.down_payment
    effective_loan = req.desired_loan_amount if req.desired_loan_amount is not None else auto_loan

    if effective_loan <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Effective loan amount must be greater than zero."
        )

    # Fetch property metadata if property_id supplied
    prop_meta = {
        "property_id": req.property_id,
        "property_price": req.property_price,
        "title": "Selected Property",
        "location": "Bengaluru",
        "bhk": "N/A",
        "total_sqft": "N/A"
    }

    if req.property_id:
        db_prop = db.query(Property).filter(Property.id == req.property_id).first()
        if db_prop:
            prop_meta = {
                "property_id": db_prop.id,
                "property_price": float(db_prop.price),
                "title": db_prop.title,
                "location": getattr(db_prop, "locality", "Bengaluru"),
                "bhk": db_prop.bhk,
                "total_sqft": getattr(db_prop, "area_sqft", "N/A")
            }

    # Run multi-bank comparison
    report_data = LoanComparisonService.compare_all_banks(
        db=db,
        property_price=req.property_price,
        down_payment=req.down_payment,
        loan_amount=effective_loan,
        monthly_income=req.monthly_income,
        age=req.age,
        employment_type=req.employment_type,
        existing_monthly_emi=req.existing_monthly_emi,
        tenure_years=req.preferred_tenure_years,
        property_meta=prop_meta
    )

    # Persist calculation record
    loan_calc = LoanCalculation(
        property_id=req.property_id,
        full_name=req.full_name,
        mobile_number=req.mobile_number,
        age=req.age,
        monthly_income=req.monthly_income,
        employment_type=req.employment_type,
        existing_monthly_emi=req.existing_monthly_emi,
        property_price=req.property_price,
        down_payment=req.down_payment,
        loan_amount=effective_loan,
        tenure_years=req.preferred_tenure_years
    )
    db.add(loan_calc)
    db.commit()
    db.refresh(loan_calc)

    # Persist report record
    report_record = LoanComparisonReport(
        calculation_id=loan_calc.id,
        report_data=report_data
    )
    db.add(report_record)
    db.commit()
    db.refresh(report_record)

    report_data["calculation_id"] = loan_calc.id
    report_data["report_id"] = report_record.id
    return report_data

@router.post("/report")
def generate_loan_report_pdf(
    req: LoanCompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pro_subscription)
):
    """
    Generate and stream a high-fidelity PDF mortgage comparison report
    for the specified property and borrower profile.
    """
    # First obtain the full comparison dataset
    comparison_data = compare_home_loans(req=req, db=db, current_user=current_user)
    
    # Generate PDF bytes
    pdf_bytes = LoanPdfService.generate_loan_report_pdf(comparison_data)

    filename = f"GeoSmart_Home_Loan_Report_Prop_{req.property_id or 'General'}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/pdf"
        }
    )
