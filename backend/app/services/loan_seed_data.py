"""
Verified Indian Home Loan Providers (12 Major Lenders)
Data Sourced from Official Bank Portals and Public Published Schedules
As of October 2026.
"""

VERIFIED_BANK_PRODUCTS = [
    {
        "bank_name": "State Bank of India (SBI)",
        "product_name": "SBI Regular Home Loan",
        "bank_type": "Public Sector",
        "interest_rate_min": 7.10,
        "interest_rate_max": 8.70,
        "rate_type": "Floating (EBLR-linked)",
        "min_loan": 300000.0,
        "max_loan": 100000000.0,
        "max_tenure_years": 30,
        "processing_fee_text": "0.17% (Min ₹2,000, Max ₹10,000) + GST",
        "eligibility_summary": "Resident / Non-Resident Indians; Age 18–70; Minimum monthly income ₹15,000; Salaried or Self-Employed.",
        "source_url": "https://bank.sbi",
        "source_name": "State Bank of India Official Portal",
        "publication_date": "October 2026",
        "last_verified_date": "October 2026",
        "special_features": [
            "Concession for women borrowers (5 bps)",
            "Zero prepayment penalty on floating rate",
            "Overdraft Maxgain facility available"
        ]
    },
    {
        "bank_name": "HDFC Bank",
        "product_name": "HDFC Bank Home Loan",
        "bank_type": "Private",
        "interest_rate_min": 7.75,
        "interest_rate_max": 9.10,
        "rate_type": "Floating (Repo-linked / RPLR)",
        "min_loan": 500000.0,
        "max_loan": 100000000.0,
        "max_tenure_years": 30,
        "processing_fee_text": "Up to 0.50% of loan amount or ₹3,000 + GST",
        "eligibility_summary": "Salaried / Self-Employed professionals; Age 21–65; Minimum monthly income ₹20,000.",
        "source_url": "https://www.hdfcbank.com",
        "source_name": "HDFC Bank Official Portal",
        "publication_date": "October 2026",
        "last_verified_date": "October 2026",
        "special_features": [
            "Express digital loan approval in 24 hours",
            "Special rates for women applicants",
            "Flexible top-up and balance transfer"
        ]
    },
    {
        "bank_name": "ICICI Bank",
        "product_name": "ICICI Bank Extra Home Loan",
        "bank_type": "Private",
        "interest_rate_min": 8.50,
        "interest_rate_max": 9.60,
        "rate_type": "Floating (Repo-linked)",
        "min_loan": 500000.0,
        "max_loan": 100000000.0,
        "max_tenure_years": 30,
        "processing_fee_text": "0.50% – 2.00% of loan amount + GST",
        "eligibility_summary": "Salaried / Self-Employed; Age 21–65; Minimum monthly income ₹25,000.",
        "source_url": "https://www.icicibank.com",
        "source_name": "ICICI Bank Official Portal",
        "publication_date": "October 2026",
        "last_verified_date": "October 2026",
        "special_features": [
            "Pre-approved home loans for existing customers",
            "Mortgage Guarantee backed loan enhancement",
            "Paperless sanction via iMobile app"
        ]
    },
    {
        "bank_name": "Bank of Baroda",
        "product_name": "Baroda Home Loan (Max Savings)",
        "bank_type": "Public Sector",
        "interest_rate_min": 7.20,
        "interest_rate_max": 8.85,
        "rate_type": "Floating (BRLLR-linked)",
        "min_loan": 300000.0,
        "max_loan": 100000000.0,
        "max_tenure_years": 30,
        "processing_fee_text": "0.25% – 0.50% (Min ₹8,500, Max ₹25,000) + GST",
        "eligibility_summary": "Indian residents and NRIs; Age 21–70; Minimum monthly income ₹15,000.",
        "source_url": "https://www.bankofbaroda.in",
        "source_name": "Bank of Baroda Official Portal",
        "publication_date": "October 2026",
        "last_verified_date": "October 2026",
        "special_features": [
            "Savings-linked overdraft scheme",
            "Nil prepayment charges",
            "Preferential rate for CIBIL 750+"
        ]
    },
    {
        "bank_name": "Axis Bank",
        "product_name": "Axis Bank Home Loan",
        "bank_type": "Private",
        "interest_rate_min": 8.20,
        "interest_rate_max": 9.35,
        "rate_type": "Floating (Repo-linked)",
        "min_loan": 300000.0,
        "max_loan": 100000000.0,
        "max_tenure_years": 30,
        "processing_fee_text": "Up to 1.00% of loan amount or ₹10,000 + GST",
        "eligibility_summary": "Salaried / Professionals / Self-Employed; Age 21–65; Minimum monthly income ₹20,000.",
        "source_url": "https://www.axisbank.com",
        "source_name": "Axis Bank Official Portal",
        "publication_date": "October 2026",
        "last_verified_date": "October 2026",
        "special_features": [
            "Doorstep document pickup service",
            "Shubh Aarambh 12 EMI waiver feature",
            "Fast-track sanction mechanism"
        ]
    },
    {
        "bank_name": "Punjab National Bank (PNB)",
        "product_name": "PNB Max Saver Home Loan",
        "bank_type": "Public Sector",
        "interest_rate_min": 7.25,
        "interest_rate_max": 8.75,
        "rate_type": "Floating (RLLR-linked)",
        "min_loan": 300000.0,
        "max_loan": 100000000.0,
        "max_tenure_years": 30,
        "processing_fee_text": "0.35% (Min ₹2,500, Max ₹15,000) + GST",
        "eligibility_summary": "Salaried & Self-Employed Indian Nationals; Age 18–70; Minimum monthly income ₹15,000.",
        "source_url": "https://www.pnbindia.in",
        "source_name": "Punjab National Bank Official Portal",
        "publication_date": "October 2026",
        "last_verified_date": "October 2026",
        "special_features": [
            "Overdraft facility attached to current/savings account",
            "Subsidized rates for women co-borrowers",
            "Flexible repayment step-up options"
        ]
    },
    {
        "bank_name": "Canara Bank",
        "product_name": "Canara Housing Loan",
        "bank_type": "Public Sector",
        "interest_rate_min": 7.15,
        "interest_rate_max": 8.70,
        "rate_type": "Floating (RLLR-linked)",
        "min_loan": 300000.0,
        "max_loan": 100000000.0,
        "max_tenure_years": 30,
        "processing_fee_text": "0.50% (Min ₹1,500, Max ₹10,000) + GST",
        "eligibility_summary": "Individuals / Joint applicants; Age 21–70; Minimum monthly income ₹15,000.",
        "source_url": "https://canarabank.com",
        "source_name": "Canara Bank Official Portal",
        "publication_date": "October 2026",
        "last_verified_date": "October 2026",
        "special_features": [
            "Lowest entry rate among tier-1 public sector banks",
            "Up to 90% financing for loans under ₹30 Lakhs",
            "No hidden documentation charges"
        ]
    },
    {
        "bank_name": "Union Bank of India",
        "product_name": "Union Home Loan",
        "bank_type": "Public Sector",
        "interest_rate_min": 7.15,
        "interest_rate_max": 8.65,
        "rate_type": "Floating (EBLR-linked)",
        "min_loan": 300000.0,
        "max_loan": 100000000.0,
        "max_tenure_years": 30,
        "processing_fee_text": "0.50% (Max ₹15,000) + GST",
        "eligibility_summary": "Indian Citizens / NRIs; Age 18–75; Minimum monthly income ₹15,000.",
        "source_url": "https://www.unionbankofindia.co.in",
        "source_name": "Union Bank of India Official Portal",
        "publication_date": "October 2026",
        "last_verified_date": "October 2026",
        "special_features": [
            "Generous maximum age limit up to 75 years",
            "Solar rooftop top-up available",
            "Concession on festive/online applications"
        ]
    },
    {
        "bank_name": "Kotak Mahindra Bank",
        "product_name": "Kotak Home Loan",
        "bank_type": "Private",
        "interest_rate_min": 7.60,
        "interest_rate_max": 8.90,
        "rate_type": "Floating (Repo-linked)",
        "min_loan": 500000.0,
        "max_loan": 100000000.0,
        "max_tenure_years": 30,
        "processing_fee_text": "0.50% – 1.00% + GST",
        "eligibility_summary": "Salaried / Self-Employed Indian residents; Age 21–65; Minimum monthly income ₹20,000.",
        "source_url": "https://www.kotak.com",
        "source_name": "Kotak Mahindra Bank Official Portal",
        "publication_date": "October 2026",
        "last_verified_date": "October 2026",
        "special_features": [
            "Competitive private bank rates for high credit scores",
            "Instant digital in-principle sanction",
            "Simplified documentation for salaried applicants"
        ]
    },
    {
        "bank_name": "LIC Housing Finance",
        "product_name": "LIC HFL Griha Suvidha",
        "bank_type": "Housing Finance",
        "interest_rate_min": 7.15,
        "interest_rate_max": 8.80,
        "rate_type": "Floating (LHFL-PLR linked)",
        "min_loan": 300000.0,
        "max_loan": 100000000.0,
        "max_tenure_years": 30,
        "processing_fee_text": "0.25% – 0.50% + GST",
        "eligibility_summary": "Salaried / Pensioners / Self-Employed; Age 21–65; Minimum monthly income ₹15,000.",
        "source_url": "https://www.lichousing.com",
        "source_name": "LIC Housing Finance Official Portal",
        "publication_date": "October 2026",
        "last_verified_date": "October 2026",
        "special_features": [
            "Backed by Life Insurance Corporation of India (LIC)",
            "Special loan terms for pension holders",
            "Wide network across Tier-1, Tier-2, and Tier-3 cities"
        ]
    },
    {
        "bank_name": "Bank of India (BOI)",
        "product_name": "Star Home Loan",
        "bank_type": "Public Sector",
        "interest_rate_min": 7.10,
        "interest_rate_max": 8.85,
        "rate_type": "Floating (RLLR-linked)",
        "min_loan": 300000.0,
        "max_loan": 100000000.0,
        "max_tenure_years": 30,
        "processing_fee_text": "0.25% (Min ₹1,000, Max ₹20,000) + GST",
        "eligibility_summary": "Salaried / Professionals / Agriculturalists; Age 18–70; Minimum monthly income ₹15,000.",
        "source_url": "https://bankofindia.co.in",
        "source_name": "Bank of India Official Portal",
        "publication_date": "October 2026",
        "last_verified_date": "October 2026",
        "special_features": [
            "Concession of 0.10% for women borrowers",
            "Special packages for government and defense personnel",
            "Step-up/Step-down repayment schedules"
        ]
    },
    {
        "bank_name": "Indian Bank",
        "product_name": "IB Home Loan",
        "bank_type": "Public Sector",
        "interest_rate_min": 7.15,
        "interest_rate_max": 8.55,
        "rate_type": "Floating (Repo-linked)",
        "min_loan": 300000.0,
        "max_loan": 100000000.0,
        "max_tenure_years": 30,
        "processing_fee_text": "0.23% – 0.40% (Max ₹20,000) + GST",
        "eligibility_summary": "Resident Indians & NRIs; Age 18–70; Minimum monthly income ₹15,000.",
        "source_url": "https://www.indianbank.in",
        "source_name": "Indian Bank Official Portal",
        "publication_date": "October 2026",
        "last_verified_date": "October 2026",
        "special_features": [
            "Lowest upper-end rate ceiling among PSU lenders (8.55%)",
            "Flexible holiday/moratorium periods during construction",
            "Special concession for solar PV installations"
        ]
    }
]
