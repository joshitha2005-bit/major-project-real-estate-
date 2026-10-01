import math
import re
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.models.property import Property

class PropertyDeduplicationService:
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate Haversine distance in meters between two lat/lon coordinates."""
        if lat1 == 0 or lon1 == 0 or lat2 == 0 or lon2 == 0:
            return 999999.0
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    @staticmethod
    def normalize_string(text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return ' '.join(text.split())

    @staticmethod
    def compare_property_pair(p1: Property, p2: Property) -> Tuple[str, float, List[str]]:
        """
        Compare two property objects and return (classification, score, matching_signals).
        Classifications: UNIQUE, POSSIBLE_DUPLICATE, CONFIRMED_DUPLICATE
        """
        if p1.id is not None and p2.id is not None and p1.id == p2.id:
            return "UNIQUE", 0.0, []

        signals = []
        score = 0.0

        # Signal 1: Exact source listing ID match across providers
        if p1.source_listing_id and p2.source_listing_id and p1.source_listing_id == p2.source_listing_id:
            signals.append("exact_source_listing_id_match")
            score += 50.0

        # Signal 2: Locality match
        loc1 = PropertyDeduplicationService.normalize_string(p1.locality or "")
        loc2 = PropertyDeduplicationService.normalize_string(p2.locality or "")
        if loc1 and loc2 and loc1 == loc2:
            signals.append("locality_match")
            score += 15.0

        # Signal 3: Property Type & BHK match
        if p1.property_type and p2.property_type and p1.property_type.lower() == p2.property_type.lower():
            if p1.bhk == p2.bhk:
                signals.append("type_and_bhk_match")
                score += 15.0

        # Signal 4: Area sqft similarity (within 3%)
        if p1.area_sqft > 0 and p2.area_sqft > 0:
            area_diff_pct = abs(p1.area_sqft - p2.area_sqft) / p1.area_sqft
            if area_diff_pct <= 0.03:
                signals.append("area_match_within_3_pct")
                score += 15.0

        # Signal 5: Price similarity (within 5%)
        if p1.price > 0 and p2.price > 0:
            price_diff_pct = abs(p1.price - p2.price) / p1.price
            if price_diff_pct <= 0.05:
                signals.append("price_match_within_5_pct")
                score += 15.0

        # Signal 6: GIS Proximity (< 50 meters)
        dist = PropertyDeduplicationService.haversine_distance(p1.latitude, p1.longitude, p2.latitude, p2.longitude)
        if dist <= 50.0:
            signals.append(f"gis_proximity_{int(dist)}m")
            score += 25.0

        # Signal 7: Address normalized string similarity
        addr1 = PropertyDeduplicationService.normalize_string(p1.address or "")
        addr2 = PropertyDeduplicationService.normalize_string(p2.address or "")
        if addr1 and addr2 and (addr1 == addr2 or addr1 in addr2 or addr2 in addr1):
            signals.append("address_similarity")
            score += 20.0

        # Classification decision rules
        if score >= 85.0 or ("exact_source_listing_id_match" in signals and score >= 65.0):
            classification = "CONFIRMED_DUPLICATE"
        elif score >= 50.0:
            classification = "POSSIBLE_DUPLICATE"
        else:
            classification = "UNIQUE"

        return classification, round(score, 1), signals

    @staticmethod
    def audit_database_duplicates(db: Session, sample_limit: int = 1000) -> Dict[str, Any]:
        """
        Scan database records for potential duplicates across sources.
        """
        props = db.query(Property).order_by(Property.id).limit(sample_limit).all()
        confirmed = []
        possible = []

        # Index properties by locality for efficient pairwise checks
        locality_buckets = {}
        for p in props:
            loc = PropertyDeduplicationService.normalize_string(p.locality or "other")
            locality_buckets.setdefault(loc, []).append(p)

        for loc, bucket in locality_buckets.items():
            if len(bucket) < 2:
                continue
            for i in range(len(bucket)):
                for j in range(i + 1, len(bucket)):
                    p1 = bucket[i]
                    p2 = bucket[j]
                    cls_res, score, signals = PropertyDeduplicationService.compare_property_pair(p1, p2)
                    if cls_res == "CONFIRMED_DUPLICATE":
                        confirmed.append({
                            "property_id_1": p1.id,
                            "property_id_2": p2.id,
                            "title_1": p1.title,
                            "title_2": p2.title,
                            "locality": p1.locality,
                            "score": score,
                            "signals": signals
                        })
                    elif cls_res == "POSSIBLE_DUPLICATE":
                        possible.append({
                            "property_id_1": p1.id,
                            "property_id_2": p2.id,
                            "title_1": p1.title,
                            "title_2": p2.title,
                            "locality": p1.locality,
                            "score": score,
                            "signals": signals
                        })

        return {
            "total_inspected": len(props),
            "confirmed_duplicates_count": len(confirmed),
            "possible_duplicates_count": len(possible),
            "confirmed_duplicates": confirmed[:20],
            "possible_duplicates": possible[:20]
        }
