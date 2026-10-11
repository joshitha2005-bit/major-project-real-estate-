"""
Cloud-Based Real Estate Analysis - Home Loan & Bank Comparison Service
Production-ready calculation, eligibility evaluation, and multi-bank comparison engine.
"""

from typing import List, Dict, Any, Optional
import math
from sqlalchemy.orm import Session
from app.models.loan import BankLoanProduct, LoanCalculation, LoanComparisonReport
from app.services.loan_seed_data import VERIFIED_BANK_PRODUCTS

class LoanComparisonService:

    @staticmethod
    def calculate_emi(principal: float, annual_rate_pct: float, tenure_years: int) -> Dict[str, Any]:
        """
        Calculate standard Indian home loan EMI:
        EMI = P * r * (1+r)^n / ((1+r)^n - 1)
        where:
        P = principal
        r = monthly interest rate (annual_rate_pct / 12 / 100)
        n = number of monthly installments (tenure_years * 12)
        """
        if principal <= 0 or tenure_years <= 0:
            return {
                "emi": 0.0,
                "total_interest": 0.0,
                "total_repayment": 0.0,
                "tenure_months": tenure_years * 12,
                "monthly_rate": 0.0
            }

        n = tenure_years * 12
        r = (annual_rate_pct / 100.0) / 12.0

        if r == 0:
            emi = principal / n
            total_repayment = principal
            total_interest = 0.0
        else:
            power = math.pow(1.0 + r, n)
            raw_emi = principal * r * power / (power - 1.0)
            emi = float(round(raw_emi))
            total_repayment = float(emi * n)
            total_interest = float(total_repayment - principal)

        return {
            "emi": emi,
            "total_interest": total_interest,
            "total_repayment": total_repayment,
            "tenure_months": n,
            "monthly_rate": r
        }

    @staticmethod
    def get_rbi_max_ltv(property_price: float) -> float:
        """
        RBI Regulatory Loan-to-Value (LTV) limits:
        - Up to ₹30 Lakhs: 90%
        - ₹30 Lakhs to ₹75 Lakhs: 80%
        - Above ₹75 Lakhs: 75%
        """
        if property_price <= 3000000.0:
            return 90.0
        elif property_price <= 7500000.0:
            return 80.0
        else:
            return 75.0

    @classmethod
    def evaluate_indicative_eligibility(
        cls,
        property_price: float,
        loan_amount: float,
        monthly_income: float,
        age: int,
        employment_type: str,
        existing_monthly_emi: float,
        tenure_years: int,
        annual_rate_pct: float
    ) -> Dict[str, Any]:
        """
        Calculate indicative eligibility using standard banking FOIR (Fixed Obligation to Income Ratio)
        and RBI LTV ceilings. Never claims formal bank approval.
        """
        rbi_max_ltv = cls.get_rbi_max_ltv(property_price)
        actual_ltv = (loan_amount / property_price * 100.0) if property_price > 0 else 0.0

        # FOIR standard benchmarks
        foir_ratio = 0.55 if employment_type.lower() in ["self-employed", "business"] else 0.50
        max_allowable_total_emi = monthly_income * foir_ratio
        available_emi_capacity = max(0.0, max_allowable_total_emi - existing_monthly_emi)

        # Inverse EMI calculation to find max allowable principal
        n = tenure_years * 12
        r = (annual_rate_pct / 100.0) / 12.0
        if r > 0 and available_emi_capacity > 0:
            power = math.pow(1.0 + r, n)
            max_loan_by_income = available_emi_capacity * (power - 1.0) / (r * power)
        else:
            max_loan_by_income = available_emi_capacity * n

        max_loan_by_ltv = property_price * (rbi_max_ltv / 100.0)
        indicative_eligible_amount = round(min(max_loan_by_income, max_loan_by_ltv))

        # Check conditions
        is_ltv_compliant = actual_ltv <= (rbi_max_ltv + 0.1)
        is_capacity_sufficient = loan_amount <= indicative_eligible_amount
        is_age_compliant = (age + tenure_years) <= 70

        eligibility_notes = []
        if not is_age_compliant:
            eligibility_notes.append(f"Age at loan maturity ({age + tenure_years} yrs) exceeds standard 70-year ceiling; a shorter tenure or younger co-borrower may be required.")

        if not is_ltv_compliant:
            eligibility_notes.append(f"Requested LTV ({actual_ltv:.1f}%) exceeds RBI benchmark of {rbi_max_ltv}%. Higher down payment recommended.")

        if is_capacity_sufficient and is_ltv_compliant and is_age_compliant:
            status = "Indicative Eligible"
            status_code = "ELIGIBLE"
            eligibility_notes.append(f"Estimated borrowing capacity: up to ₹{indicative_eligible_amount:,.0f} (subject to credit score and underwriting).")
        elif not is_capacity_sufficient:
            status = "Requires Verification / Stretch"
            status_code = "STRETCH"
            eligibility_notes.append(f"Requested loan (₹{loan_amount:,.0f}) exceeds estimated indicative capacity of ₹{indicative_eligible_amount:,.0f}.")
        else:
            status = "Conditional Eligibility"
            status_code = "CONDITIONAL"

        return {
            "status": status,
            "status_code": status_code,
            "indicative_eligible_amount": indicative_eligible_amount,
            "available_monthly_emi_capacity": round(available_emi_capacity),
            "max_allowable_total_emi": round(max_allowable_total_emi),
            "actual_ltv_pct": round(actual_ltv, 2),
            "rbi_max_ltv_pct": rbi_max_ltv,
            "is_ltv_compliant": is_ltv_compliant,
            "is_capacity_sufficient": is_capacity_sufficient,
            "is_age_compliant": is_age_compliant,
            "notes": " ".join(eligibility_notes) if eligibility_notes else "Eligibility requires bank verification."
        }

    @classmethod
    def compare_all_banks(
        cls,
        db: Session,
        property_price: float,
        down_payment: float,
        loan_amount: float,
        monthly_income: float,
        age: int,
        employment_type: str,
        existing_monthly_emi: float,
        tenure_years: int,
        property_meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compare all active verified bank products for the user's specific property loan requirement.
        """
        # Fetch active products from DB
        db_products = db.query(BankLoanProduct).filter(BankLoanProduct.is_active == True).all()
        products_to_evaluate = []
        if db_products:
            for p in db_products:
                products_to_evaluate.append({
                    "id": p.id,
                    "bank_name": p.bank_name,
                    "product_name": p.product_name,
                    "bank_type": p.bank_type,
                    "interest_rate_min": p.interest_rate_min,
                    "interest_rate_max": p.interest_rate_max,
                    "rate_type": p.rate_type,
                    "min_loan": p.min_loan,
                    "max_loan": p.max_loan,
                    "max_tenure_years": p.max_tenure_years,
                    "processing_fee_text": p.processing_fee_text,
                    "eligibility_summary": p.eligibility_summary,
                    "source_url": p.source_url,
                    "source_name": p.source_name,
                    "publication_date": p.publication_date,
                    "last_verified_date": p.last_verified_date,
                    "special_features": p.special_features or []
                })
        else:
            products_to_evaluate = VERIFIED_BANK_PRODUCTS

        comparison_list = []
        for p in products_to_evaluate:
            rate_min = p["interest_rate_min"]
            rate_max = p["interest_rate_max"]

            # Calculate EMI for min and max rate
            emi_calc_min = cls.calculate_emi(loan_amount, rate_min, tenure_years)
            emi_calc_max = cls.calculate_emi(loan_amount, rate_max, tenure_years)

            # Evaluate indicative eligibility for this bank's starting rate
            eligibility = cls.evaluate_indicative_eligibility(
                property_price=property_price,
                loan_amount=loan_amount,
                monthly_income=monthly_income,
                age=age,
                employment_type=employment_type,
                existing_monthly_emi=existing_monthly_emi,
                tenure_years=tenure_years,
                annual_rate_pct=rate_min
            )

            comparison_list.append({
                "id": p.get("id", len(comparison_list) + 1),
                "bank_name": p["bank_name"],
                "product_name": p["product_name"],
                "bank_type": p["bank_type"],
                "interest_rate_min": rate_min,
                "interest_rate_max": rate_max,
                "rate_display": f"{rate_min:.2f}% – {rate_max:.2f}% p.a.",
                "rate_type": p["rate_type"],
                "tenure_years": tenure_years,
                "estimated_monthly_emi_min": emi_calc_min["emi"],
                "estimated_monthly_emi_max": emi_calc_max["emi"],
                "total_interest_min": emi_calc_min["total_interest"],
                "total_interest_max": emi_calc_max["total_interest"],
                "total_repayment_min": emi_calc_min["total_repayment"],
                "total_repayment_max": emi_calc_max["total_repayment"],
                "processing_fee": p["processing_fee_text"],
                "indicative_eligibility": eligibility["status"],
                "indicative_status_code": eligibility["status_code"],
                "eligibility_notes": eligibility["notes"],
                "indicative_eligible_amount": eligibility["indicative_eligible_amount"],
                "special_features": p["special_features"],
                "source_url": p["source_url"],
                "source_name": p["source_name"],
                "publication_date": p["publication_date"],
                "last_verified_date": p["last_verified_date"]
            })

        # Sort by starting EMI ascending
        comparison_list.sort(key=lambda x: x["estimated_monthly_emi_min"])

        # Overall Loan Summary
        baseline_rate = comparison_list[0]["interest_rate_min"] if comparison_list else 7.10
        baseline_emi = cls.calculate_emi(loan_amount, baseline_rate, tenure_years)
        rbi_ltv = cls.get_rbi_max_ltv(property_price)
        actual_ltv = (loan_amount / property_price * 100.0) if property_price > 0 else 0.0

        # Contextual Personalized Observations ("Why these options?")
        observations = []
        observations.append(
            f"Based on your declared monthly income of ₹{monthly_income:,.0f} and existing EMI of ₹{existing_monthly_emi:,.0f}, "
            f"your estimated disposable monthly EMI capacity is ₹{max(0.0, monthly_income * 0.50 - existing_monthly_emi):,.0f} (using 50% FOIR)."
        )
        observations.append(
            f"For this property valued at ₹{property_price:,.0f} with a contribution of ₹{down_payment:,.0f}, "
            f"the requested loan of ₹{loan_amount:,.0f} represents an LTV of {actual_ltv:.1f}% "
            f"(RBI benchmark ceiling is {rbi_ltv}%)."
        )
        observations.append(
            f"At a preferred tenure of {tenure_years} years, starting EMIs range from ₹{comparison_list[0]['estimated_monthly_emi_min']:,} "
            f"to ₹{comparison_list[-1]['estimated_monthly_emi_min']:,} across verified lenders."
        )
        observations.append(
            "Public sector lenders (SBI, Bank of Baroda, Canara Bank, Union Bank) offer the most competitive entry rates (7.10% – 7.20%), "
            "whereas leading private lenders (HDFC Bank, ICICI Bank, Kotak) offer expedited digital processing and doorstep convenience."
        )

        return {
            "property_summary": property_meta or {
                "property_id": None,
                "property_price": property_price,
                "location": "Bengaluru"
            },
            "user_inputs": {
                "monthly_income": monthly_income,
                "age": age,
                "employment_type": employment_type,
                "existing_monthly_emi": existing_monthly_emi,
                "down_payment": down_payment,
                "loan_amount": loan_amount,
                "tenure_years": tenure_years
            },
            "loan_metrics": {
                "property_price": property_price,
                "down_payment": down_payment,
                "loan_amount": loan_amount,
                "tenure_years": tenure_years,
                "actual_ltv_pct": round(actual_ltv, 2),
                "rbi_max_ltv_pct": rbi_ltv,
                "baseline_rate_pct": baseline_rate,
                "estimated_monthly_emi": baseline_emi["emi"],
                "total_interest": baseline_emi["total_interest"],
                "total_repayment": baseline_emi["total_repayment"]
            },
            "banks_evaluated_count": len(comparison_list),
            "bank_comparisons": comparison_list,
            "personalized_observations": observations,
            "disclaimer": (
                "DISCLAIMER: All interest rates, EMI projections, processing fees, and eligibility figures are indicative "
                "and based on verified public disclosures as of October 2026. Actual loan terms, interest rates, and approval decisions "
                "are governed solely by the respective bank/housing finance institution following formal credit assessment."
            )
        }
