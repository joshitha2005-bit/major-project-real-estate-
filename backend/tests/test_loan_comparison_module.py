
from app.models.user import User
from app.models.subscription import Subscription
from app.core.database import SessionLocal
from app.core.security import get_password_hash, create_access_token
from datetime import datetime, timezone, timedelta

def get_pro_auth_headers():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "test_pro_loan_runner@example.com").first()
        if not user:
            user = User(
                email="test_pro_loan_runner@example.com",
                full_name="Pro Loan Runner",
                hashed_password=get_password_hash("ProRunnerPass123!"),
                role="USER",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
        now = datetime.now(timezone.utc)
        if not sub:
            sub = Subscription(
                user_id=user.id,
                plan="PRO",
                plan_name="PROPULSE_PRO_299",
                subscription_status="ACTIVE",
                status="ACTIVE",
                start_date=now,
                end_date=now + timedelta(days=30)
            )
            db.add(sub)
        else:
            sub.plan = "PRO"
            sub.subscription_status = "ACTIVE"
            sub.status = "ACTIVE"
            sub.end_date = now + timedelta(days=30)
        db.commit()
        token = create_access_token(subject=user.id)
        return {"Authorization": f"Bearer {token}"}
    finally:
        db.close()
"""
Comprehensive Test Suite for Smart Home Loan & Bank Comparison Module
Validates EMI mathematics, bank data provenance, indicative eligibility,
API endpoints, validation constraints, and PDF report generation.
"""

import pytest
import io
from fastapi.testclient import TestClient
from app.main import app
from app.services.loan_comparison_service import LoanComparisonService
from app.services.loan_seed_data import VERIFIED_BANK_PRODUCTS
from app.services.loan_pdf_service import LoanPdfService

client = TestClient(app)

class TestLoanMathematicsAndEligibility:

    def test_01_emi_calculation_exactness(self):
        """
        Verify standard compound interest EMI formula:
        For P = ₹50,00,000, r = 8.5% p.a., n = 20 years (240 months):
        Expected EMI ≈ ₹43,391.
        """
        result = LoanComparisonService.calculate_emi(
            principal=5000000.0,
            annual_rate_pct=8.5,
            tenure_years=20
        )
        assert result["tenure_months"] == 240
        assert abs(result["emi"] - 43391) <= 2  # standard rounding tolerance
        assert result["total_repayment"] == result["emi"] * 240
        assert result["total_interest"] == result["total_repayment"] - 5000000.0

    def test_02_zero_and_negative_inputs_handling(self):
        """Zero or negative loan amount must return zero metrics without dividing by zero."""
        res_zero = LoanComparisonService.calculate_emi(0.0, 8.5, 20)
        assert res_zero["emi"] == 0.0
        assert res_zero["total_interest"] == 0.0

        res_neg = LoanComparisonService.calculate_emi(-100000.0, 8.5, 20)
        assert res_neg["emi"] == 0.0

    def test_03_rbi_ltv_guidelines(self):
        """Verify RBI LTV tiers: <=30L (90%), 30L-75L (80%), >75L (75%)."""
        assert LoanComparisonService.get_rbi_max_ltv(2500000.0) == 90.0
        assert LoanComparisonService.get_rbi_max_ltv(5000000.0) == 80.0
        assert LoanComparisonService.get_rbi_max_ltv(12500000.0) == 75.0

    def test_04_indicative_eligibility_salaried_vs_self_employed(self):
        """Salaried uses 50% FOIR, Self-employed uses 55% FOIR."""
        income = 100000.0
        # Salaried: 50% = 50,000 max EMI
        sal_elig = LoanComparisonService.evaluate_indicative_eligibility(
            property_price=10000000.0,
            loan_amount=5000000.0,
            monthly_income=income,
            age=30,
            employment_type="Salaried",
            existing_monthly_emi=10000.0,
            tenure_years=20,
            annual_rate_pct=7.5
        )
        assert sal_elig["available_monthly_emi_capacity"] == 40000.0  # 50,000 - 10,000

        # Self-employed: 55% = 55,000 max EMI
        se_elig = LoanComparisonService.evaluate_indicative_eligibility(
            property_price=10000000.0,
            loan_amount=5000000.0,
            monthly_income=income,
            age=30,
            employment_type="Self-employed",
            existing_monthly_emi=10000.0,
            tenure_years=20,
            annual_rate_pct=7.5
        )
        assert se_elig["available_monthly_emi_capacity"] == 45000.0  # 55,000 - 10,000

    def test_05_verified_banks_dataset_integrity(self):
        """Verify that 10-15 Indian home-loan providers exist with complete provenance."""
        assert 10 <= len(VERIFIED_BANK_PRODUCTS) <= 15
        for b in VERIFIED_BANK_PRODUCTS:
            assert b["bank_name"], "Missing bank name"
            assert b["product_name"], "Missing product name"
            assert b["interest_rate_min"] > 0, "Invalid interest rate min"
            assert b["interest_rate_max"] >= b["interest_rate_min"], "Invalid interest rate max"
            assert b["source_url"].startswith("http"), "Invalid source URL"
            assert b["source_name"], "Missing source name"
            assert b["last_verified_date"], "Missing verification date"
            assert b["processing_fee_text"], "Missing processing fee"


class TestLoanEndpointsAndValidation:

    def test_06_get_banks_endpoint(self):
        """GET /api/v1/loans/banks returns 200 and verified bank list."""
        resp = client.get("/api/v1/loans/banks")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 10
        first_bank = data[0]
        assert "bank_name" in first_bank
        assert "interest_rate_min" in first_bank
        assert "source_url" in first_bank
        assert "last_verified_date" in first_bank

    def test_07_calculate_endpoint(self):
        """POST /api/v1/loans/calculate returns correct EMI."""
        payload = {
            "loan_amount": 4000000.0,
            "interest_rate": 8.0,
            "tenure_years": 15
        }
        resp = client.post("/api/v1/loans/calculate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["loan_amount"] == 4000000.0
        assert data["tenure_months"] == 180
        assert data["emi"] > 0
        assert data["total_repayment"] > data["loan_amount"]

    def test_08_compare_endpoint_success(self):
        """POST /api/v1/loans/compare evaluates multi-bank comparison."""
        payload = {
            "property_id": 16799,
            "full_name": "Priya Nair",
            "mobile_number": "9812345678",
            "age": 29,
            "monthly_income": 150000.0,
            "employment_type": "Salaried",
            "existing_monthly_emi": 5000.0,
            "property_price": 8000000.0,
            "down_payment": 1600000.0,
            "preferred_tenure_years": 20
        }
        resp = client.post("/api/v1/loans/compare", json=payload, headers=get_pro_auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["banks_evaluated_count"] >= 10
        assert len(data["bank_comparisons"]) >= 10
        assert "loan_metrics" in data
        assert data["loan_metrics"]["loan_amount"] == 6400000.0  # 80L - 16L
        assert len(data["personalized_observations"]) >= 2
        assert "disclaimer" in data

    def test_09_compare_endpoint_validation_errors(self):
        """Validation errors: invalid phone, down payment >= price."""
        # Invalid phone (letters)
        bad_phone_payload = {
            "full_name": "Test User",
            "mobile_number": "not-a-number",
            "age": 30,
            "monthly_income": 100000.0,
            "employment_type": "Salaried",
            "property_price": 5000000.0,
            "down_payment": 1000000.0
        }
        r_phone = client.post("/api/v1/loans/compare", json=bad_phone_payload, headers=get_pro_auth_headers())
        assert r_phone.status_code == 422

        # Down payment >= price
        excess_down_payload = {
            "full_name": "Test User",
            "mobile_number": "9876543210",
            "age": 30,
            "monthly_income": 100000.0,
            "employment_type": "Salaried",
            "property_price": 5000000.0,
            "down_payment": 6000000.0
        }
        r_down = client.post("/api/v1/loans/compare", json=excess_down_payload, headers=get_pro_auth_headers())
        assert r_down.status_code == 400

    def test_10_pdf_report_generation(self):
        """POST /api/v1/loans/report generates valid PDF document."""
        payload = {
            "property_id": 16799,
            "full_name": "Vikram Malhotra",
            "mobile_number": "9898989898",
            "age": 35,
            "monthly_income": 200000.0,
            "employment_type": "Business",
            "existing_monthly_emi": 20000.0,
            "property_price": 15000000.0,
            "down_payment": 3500000.0,
            "preferred_tenure_years": 25
        }
        resp = client.post("/api/v1/loans/report", json=payload, headers=get_pro_auth_headers())
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert resp.content.startswith(b"%PDF"), "Response is not a valid PDF file"
        assert len(resp.content) > 1000
