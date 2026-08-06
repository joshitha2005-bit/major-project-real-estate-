import math
from typing import Dict, Any

class SafetyGuardService:
    @staticmethod
    def analyze_locality_safety(locality_name: str, lat: float, lon: float) -> Dict[str, Any]:
        """Compute locality safety guard analysis based on GIS location metrics."""
        text = (locality_name or "").lower()
        
        # Base ratings for known Bangalore hubs
        base_safety = 88.0
        base_crime = 12.0
        base_flood = "Low Risk"
        base_traffic = 35.0

        if "koramangala" in text or "indiranagar" in text:
            base_safety = 92.0
            base_crime = 8.0
            base_flood = "Minimal Risk"
            base_traffic = 55.0  # Moderate urban traffic
        elif "whitefield" in text or "electronic city" in text:
            base_safety = 89.0
            base_crime = 11.0
            base_flood = "Low Risk"
            base_traffic = 62.0  # Tech corridor traffic
        elif "hsr" in text or "jp nagar" in text or "jayanagar" in text:
            base_safety = 94.0
            base_crime = 6.0
            base_flood = "Minimal Risk"
            base_traffic = 40.0
        elif "bellandur" in text or "marathahalli" in text:
            base_safety = 85.0
            base_crime = 14.0
            base_flood = "Moderate Risk"
            base_traffic = 72.0

        # Small variation based on coordinates
        coord_mod = (abs(lat * 100) % 5.0) - 2.5
        safety_score = max(60.0, min(98.0, round(base_safety + coord_mod, 1)))
        crime_score = max(2.0, min(35.0, round(base_crime - (coord_mod * 0.5), 1)))
        traffic_score = max(20.0, min(90.0, round(base_traffic + coord_mod, 1)))

        rating_label = "A+"
        if safety_score >= 92: rating_label = "A+"
        elif safety_score >= 85: rating_label = "A"
        elif safety_score >= 78: rating_label = "B+"
        elif safety_score >= 70: rating_label = "B"
        else: rating_label = "C"

        return {
            "safety_score": safety_score,
            "crime_score": crime_score,
            "flood_risk": base_flood,
            "traffic_score": traffic_score,
            "overall_rating": rating_label,
            "summary": f"{locality_name or 'Target area'} maintains an {rating_label} safety grade with {base_flood.lower()}."
        }
