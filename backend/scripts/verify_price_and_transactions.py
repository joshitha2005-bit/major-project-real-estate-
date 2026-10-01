import sqlite3
import pandas as pd

DB_PATH = "backend/real_estate.db"
CSV_PATH = "backend/datasets/Bengaluru_House_Data.csv"

def audit_and_fix_transactions_and_prices():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("==========================================================================")
    print("AUDITING TRANSACTION TYPES AND PRICE PER SQFT ACROSS ALL 12,458 RECORDS")
    print("==========================================================================")

    cursor.execute("SELECT id, area_sqft, price, price_inr, transaction_type, price_per_sqft, source_type FROM properties")
    rows = cursor.fetchall()

    mismatch_price_sqft = 0
    mismatch_price_inr = 0
    updated_count = 0

    for row in rows:
        p_id, area_sqft, price, price_inr, trans_type, p_sqft, src_type = row
        
        # 1. Verify price_inr
        # In historical dataset, if price < 10000, price was in Lakhs INR (e.g., 39.07 -> 3,907,000 INR)
        expected_price_inr = price
        if src_type == "historical_dataset" and price is not None and price < 10000.0 and (trans_type is None or trans_type == "sale"):
            expected_price_inr = float(price * 100000.0)
            
        # 2. Verify price_per_sqft
        expected_price_per_sqft = None
        if expected_price_inr and area_sqft and area_sqft > 0:
            expected_price_per_sqft = round(expected_price_inr / area_sqft, 2)

        # Transaction type default
        expected_trans_type = trans_type if trans_type in ["sale", "rent"] else "sale"

        # Check if updates needed
        need_update = False
        if abs((price_inr or 0) - expected_price_inr) > 0.01:
            mismatch_price_inr += 1
            need_update = True

        if p_sqft is None or abs((p_sqft or 0) - (expected_price_per_sqft or 0)) > 0.01:
            mismatch_price_sqft += 1
            need_update = True

        if need_update:
            cursor.execute("""
                UPDATE properties SET
                    price_inr = ?,
                    price = ?,
                    price_per_sqft = ?,
                    transaction_type = ?
                WHERE id = ?
            """, (expected_price_inr, expected_price_inr, expected_price_per_sqft, expected_trans_type, p_id))
            updated_count += 1

    conn.commit()

    print(f"Total properties audited: {len(rows)}")
    print(f"Price INR mismatches corrected: {mismatch_price_inr}")
    print(f"Price/sqft mismatches corrected: {mismatch_price_sqft}")
    print(f"Database records updated: {updated_count}")

    # Re-verify all records strictly
    cursor.execute("""
        SELECT COUNT(*) FROM properties 
        WHERE price_per_sqft IS NULL 
           OR abs(price_per_sqft - round(price_inr / area_sqft, 2)) > 0.05
    """)
    invalid_sqft_count = cursor.fetchone()[0]
    print(f"Re-verification: Remaining invalid price_per_sqft records = {invalid_sqft_count}")

    conn.close()

if __name__ == "__main__":
    audit_and_fix_transactions_and_prices()
