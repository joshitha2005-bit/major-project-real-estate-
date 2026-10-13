"""
Cloud-Based Real Estate Analysis - Demo Database Initialization Script
Reproducible, credential-free initialization for clean machines.
Creates all database tables, seeds verified bank loan products,
sets up demo credentials, and ensures golden properties exist.
"""

import os
import sys
import json

# Force UTF-8 stream output if supported
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure backend root is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.database import Base, engine, SessionLocal
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.user import User
from app.models.subscription import Subscription
from app.models.property import Property
from app.models.loan import BankLoanProduct
from app.services.loan_seed_data import VERIFIED_BANK_PRODUCTS
from datetime import datetime, timezone, timedelta


def init_database():
    print("=" * 65)
    print("CLOUD-BASED REAL ESTATE ANALYSIS -- REPRODUCIBLE DEMO DB INIT")
    print("=" * 65)
    clean_db_target = settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL
    print(f"Target Database URL: {clean_db_target}")
    print(f"Demo Mode: {settings.DEMO_MODE}")
    
    # 1. Create all schema tables
    print("\n[Step 1/4] Creating database tables from SQLAlchemy metadata...")
    Base.metadata.create_all(bind=engine)
    print("  [OK] Schema tables verified and ready.")

    db = SessionLocal()
    try:
        # 2. Seed Demo / Admin Accounts
        print("\n[Step 2/4] Verifying default user accounts...")
        admin_email = settings.PRIVATE_ADMIN_EMAIL
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            admin_user = db.query(User).filter(User.role == "ADMIN").first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash(settings.PRIVATE_ADMIN_PASSWORD),
                full_name="Platform Admin",
                role="ADMIN",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"  [OK] Created demo admin account: {admin_email}")
        else:
            admin_user.email = admin_email
            admin_user.hashed_password = get_password_hash(settings.PRIVATE_ADMIN_PASSWORD)
            admin_user.role = "ADMIN"
            admin_user.is_active = True
            db.commit()
            print(f"  [OK] Admin account verified & synchronized: {admin_email}")

        demo_email = "demo@cloudrealestate.ai"
        demo_user = db.query(User).filter(User.email == demo_email).first()
        if not demo_user:
            demo_user = db.query(User).filter(User.email == "demo@geosmart.ai").first()
        if not demo_user:
            demo_user = User(
                email=demo_email,
                hashed_password=get_password_hash("DemoUser@2026"),
                full_name="Demo User",
                role="USER",
                is_active=True
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            print(f"  [OK] Created demo standard user account: {demo_email}")
        else:
            demo_user.email = demo_email
            demo_user.hashed_password = get_password_hash("DemoUser@2026")
            demo_user.role = "USER"
            demo_user.is_active = True
            db.commit()
            print(f"  [OK] Demo user account verified & synchronized: {demo_email}")

        # Ensure active PRO subscription for demo user
        sub = db.query(Subscription).filter(Subscription.user_id == demo_user.id).first()
        if not sub:
            sub = Subscription(
                user_id=demo_user.id,
                plan="PRO",
                plan_name="PROPULSE_PRO_299",
                subscription_status="ACTIVE",
                status="ACTIVE",
                plan_amount=299.0,
                currency="INR",
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc) + timedelta(days=365),
                payment_reference="DEMO_SEED_PRO"
            )
            db.add(sub)
            db.commit()
            print(f"  [OK] Created active PRO subscription for demo user: {demo_email}")
        else:
            sub.plan = "PRO"
            sub.plan_name = "PROPULSE_PRO_299"
            sub.subscription_status = "ACTIVE"
            sub.status = "ACTIVE"
            sub.end_date = datetime.now(timezone.utc) + timedelta(days=365)
            db.commit()
            print(f"  [OK] Verified active PRO subscription for demo user: {demo_email}")

        # 3. Seed Golden Properties
        print("\n[Step 3/4] Verifying golden demo properties...")
        golden_file = os.path.join(BASE_DIR, "datasets", "golden_demo_properties.json")
        golden_count = 0
        if os.path.exists(golden_file):
            with open(golden_file, "r", encoding="utf-8") as f:
                golden_props = json.load(f)

            for pid_str, pdata in golden_props.items():
                pid = int(pid_str)
                existing = db.query(Property).filter(Property.id == pid).first()
                if not existing:
                    prop_fields = {k: v for k, v in pdata.items() if hasattr(Property, k)}
                    prop_fields["user_id"] = admin_user.id
                    
                    if "images" in prop_fields and isinstance(prop_fields["images"], str) and prop_fields["images"].startswith("["):
                        prop_fields["images"] = json.loads(prop_fields["images"])
                    if "nearby_places" in prop_fields and isinstance(prop_fields["nearby_places"], str) and prop_fields["nearby_places"].startswith("["):
                        prop_fields["nearby_places"] = json.loads(prop_fields["nearby_places"])
                    if "amenities" in prop_fields and isinstance(prop_fields["amenities"], str) and prop_fields["amenities"].startswith("["):
                        prop_fields["amenities"] = json.loads(prop_fields["amenities"])
                        
                    p = Property(**prop_fields)
                    db.add(p)
                    golden_count += 1
            db.commit()
            print(f"  [OK] Verified/Inserted golden demo properties (Count newly inserted: {golden_count}).")
        else:
            print(f"  [INFO] Golden properties file not found at {golden_file}")

        # 4. Seed Verified Bank Loan Products
        print("\n[Step 4/4] Verifying bank loan products...")
        loan_count = 0
        existing_loans = db.query(BankLoanProduct).count()
        if existing_loans == 0:
            for item in VERIFIED_BANK_PRODUCTS:
                loan_prod = BankLoanProduct(
                    bank_name=item["bank_name"],
                    product_name=item["product_name"],
                    bank_type=item["bank_type"],
                    interest_rate_min=item["interest_rate_min"],
                    interest_rate_max=item["interest_rate_max"],
                    rate_type=item["rate_type"],
                    min_loan=item["min_loan"],
                    max_loan=item["max_loan"],
                    max_tenure_years=item["max_tenure_years"],
                    processing_fee_text=item["processing_fee_text"],
                    eligibility_summary=item["eligibility_summary"],
                    source_url=item["source_url"],
                    source_name=item["source_name"],
                    publication_date=item["publication_date"],
                    last_verified_date=item["last_verified_date"],
                    special_features=item["special_features"]
                )
                db.add(loan_prod)
                loan_count += 1
            db.commit()
            print(f"  [OK] Seeded {loan_count} verified bank loan products.")
        else:
            print(f"  [OK] {existing_loans} bank loan products already present.")

        total_properties = db.query(Property).count()
        total_users = db.query(User).count()
        total_loans = db.query(BankLoanProduct).count()

        print("\n" + "=" * 65)
        print("DATABASE INITIALIZATION SUMMARY:")
        print(f"  Total Registered Users: {total_users}")
        print(f"  Total Properties Available: {total_properties}")
        print(f"  Bank Loan Products: {total_loans}")
        print("  Status: DEMO DATABASE INITIALIZED SUCCESSFULLY (PASS)")
        print("=" * 65)

    finally:
        db.close()


if __name__ == "__main__":
    init_database()
