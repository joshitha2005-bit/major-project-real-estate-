import sqlite3
import os
import json
import pandas as pd
import joblib
from app.services.price_prediction_service import PricePredictionService

def main():
    print("=" * 80)
    print("BENGALURU REAL ESTATE XGBOOST MODEL - 5 PROPERTY PREDICTION EVALUATION")
    print("=" * 80)

    db_path = os.path.join(os.path.dirname(__file__), "real_estate.db")
    if not os.path.exists(db_path):
        db_path = "real_estate.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT id, title, address, locality, bhk, area_sqft, bathrooms, balconies, price
    FROM properties
    WHERE area_sqft > 0 AND price > 0
    LIMIT 5
    """

    cursor.execute(query)
    properties = cursor.fetchall()

    results = []

    for prop in properties:
        prop_id, title, address, locality, bhk, area_sqft, bathrooms, balconies, listed_price = prop

        prediction = PricePredictionService.predict_property_valuation(
            address=address,
            lat=12.9716,
            lon=77.5946,
            area_sqft=area_sqft,
            bhk=bhk,
            bathrooms=bathrooms,
            balconies=balconies or 1,
            listed_price=listed_price
        )

        pred_price = prediction["predicted_selling_price"]
        actual_price_per_sqft = round(listed_price / area_sqft, 2)
        pred_price_per_sqft = prediction["predicted_price_per_sqft"]
        
        # Verify formula: pred_price_per_sqft == pred_price / area_sqft
        expected_sqft_rate = round(pred_price / area_sqft, 2)
        formula_correct = abs(pred_price_per_sqft - expected_sqft_rate) < 0.1

        abs_error = abs(pred_price - listed_price)
        pct_error = (abs_error / listed_price) * 100.0

        res_item = {
            "property_id": prop_id,
            "locality": locality or prediction["data_quality"]["locality_matched"],
            "bhk": bhk,
            "area_sqft": area_sqft,
            "listed_price": listed_price,
            "predicted_price": pred_price,
            "actual_price_per_sqft": actual_price_per_sqft,
            "predicted_price_per_sqft": pred_price_per_sqft,
            "absolute_error": abs_error,
            "percentage_error": pct_error,
            "formula_verified": formula_correct
        }
        results.append(res_item)

        print(f"\nProperty ID              : #{prop_id} - {title}")
        print(f"Locality                 : {res_item['locality']}")
        print(f"BHK & Area               : {bhk} BHK | {area_sqft} sq.ft")
        print(f"Listed Price             : Rs. {listed_price:,.2f} (Rs. {listed_price/100000:.2f} Lakhs)")
        print(f"Predicted Price (XGBoost): Rs. {pred_price:,.2f} (Rs. {pred_price/100000:.2f} Lakhs)")
        print(f"Actual Price / Sq.ft     : Rs. {actual_price_per_sqft:,.2f} / sq.ft")
        print(f"Predicted Price / Sq.ft  : Rs. {pred_price_per_sqft:,.2f} / sq.ft (Verified: {formula_correct})")
        print(f"Absolute Error           : Rs. {abs_error:,.2f} (Rs. {abs_error/100000:.2f} Lakhs)")
        print(f"Percentage Error         : {pct_error:.2f}%")
        print("-" * 80)

    print("\nSUMMARY:")
    avg_pct_error = sum(r["percentage_error"] for r in results) / len(results)
    print(f"Average Percentage Error across 5 properties: {avg_pct_error:.2f}%")
    all_formulas_valid = all(r["formula_verified"] for r in results)
    print(f"Formula Verification (predicted_price_per_sqft == predicted_price / area): {all_formulas_valid}")
    print("=" * 80)

if __name__ == "__main__":
    main()
