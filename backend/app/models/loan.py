from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class BankLoanProduct(Base):
    __tablename__ = "bank_loan_products"

    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String(100), nullable=False, index=True)
    product_name = Column(String(150), nullable=False)
    bank_type = Column(String(50), default="Public Sector")  # Public Sector, Private, Housing Finance
    interest_rate_min = Column(Float, nullable=False)
    interest_rate_max = Column(Float, nullable=False)
    rate_type = Column(String(50), default="Floating (Repo-linked)")
    min_loan = Column(Float, default=300000.0)
    max_loan = Column(Float, default=100000000.0)
    max_tenure_years = Column(Integer, default=30)
    processing_fee_text = Column(String(255), nullable=False)
    eligibility_summary = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=False)
    source_name = Column(String(150), nullable=False)
    publication_date = Column(String(50), default="October 2026")
    last_verified_date = Column(String(50), default="October 2026")
    special_features = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class LoanCalculation(Base):
    __tablename__ = "loan_calculations"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="SET NULL"), nullable=True)
    full_name = Column(String(150), nullable=False)
    mobile_number = Column(String(20), nullable=False)
    age = Column(Integer, nullable=False)
    monthly_income = Column(Float, nullable=False)
    employment_type = Column(String(50), nullable=False)  # Salaried, Self-employed, Business
    existing_monthly_emi = Column(Float, default=0.0)
    property_price = Column(Float, nullable=False)
    down_payment = Column(Float, nullable=False)
    loan_amount = Column(Float, nullable=False)
    tenure_years = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class LoanComparisonReport(Base):
    __tablename__ = "loan_comparison_reports"

    id = Column(Integer, primary_key=True, index=True)
    calculation_id = Column(Integer, ForeignKey("loan_calculations.id", ondelete="CASCADE"), nullable=False)
    report_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
