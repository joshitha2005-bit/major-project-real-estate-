import math
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.property import Property, PropertyImage
from app.models.market_reference import MarketReference
from app.services.image_provenance import ImageProvenanceService

ALLOWED_SOURCE_TYPES = {"HISTORICAL_MARKET_DATA", "CURRENT_AUTHORIZED_LISTING", "PROPPULSE_DIRECT", "DEMO_TEST"}
ALLOWED_LISTING_STATUSES = {"CURRENT", "HISTORICAL", "REFERENCE", "DEMO", "SOLD_INACTIVE", "UNKNOWN"}

class ListingService:
    @staticmethod
    def calculate_price_per_sqft(price_inr: float, area_sqft: float) -> float:
        """
        Strict calculation of price per sqft.
        Formula: price_per_sqft = price_inr / area_sqft
        """
        if not area_sqft or area_sqft <= 0 or not price_inr or price_inr <= 0:
            return 0.0
        return round(float(price_inr) / float(area_sqft), 2)

    @staticmethod
    def clean_and_audit_property(prop: Property) -> List[str]:
        """
        Audit property record for anomalies without deleting historical data.
        Returns list of anomaly flags.
        """
        flags = []
        if prop.price is None or prop.price <= 0:
            flags.append("INVALID_PRICE")
        if prop.area_sqft is None or prop.area_sqft <= 0:
            flags.append("INVALID_AREA")

        sqft_rate = ListingService.calculate_price_per_sqft(prop.price or 0, prop.area_sqft or 0)
        if sqft_rate > 0:
            if sqft_rate < 1000.0 or sqft_rate > 100000.0:
                flags.append("EXTREME_PRICE_PER_SQFT")
        else:
            flags.append("INVALID_PRICE_PER_SQFT")

        if not prop.locality or not prop.locality.strip():
            flags.append("MISSING_LOCALITY")

        if not prop.latitude or not prop.longitude or (prop.latitude == 0 and prop.longitude == 0):
            flags.append("MISSING_COORDINATES")

        coord_qual = getattr(prop, "coordinate_quality", None)
        if coord_qual == "LOCALITY_APPROXIMATE":
            flags.append("APPROXIMATE_COORDINATES")

        return flags

    @staticmethod
    def format_listing_out(prop: Property) -> Dict[str, Any]:
        """Format property object into clean Phase B standardized listing representation."""
        price_sqft = ListingService.calculate_price_per_sqft(prop.price, prop.area_sqft)
        anomalies = ListingService.clean_and_audit_property(prop)
        
        # Source type mapping to strict allowed set
        stype = getattr(prop, "source_type", None)
        if stype not in ALLOWED_SOURCE_TYPES:
            if stype == "historical_dataset" or prop.source == "Bengaluru_House_Data.csv":
                stype = "HISTORICAL_MARKET_DATA"
            elif stype in ["owner_listing", "PROPPULSE_DIRECT"]:
                stype = "PROPPULSE_DIRECT"
            else:
                stype = "DEMO_TEST"

        # Status mapping
        lstatus = getattr(prop, "listing_status", None)
        if lstatus not in ALLOWED_LISTING_STATUSES:
            if stype == "PROPPULSE_DIRECT":
                lstatus = "CURRENT"
            elif stype == "HISTORICAL_MARKET_DATA":
                lstatus = "HISTORICAL"
            elif stype == "DEMO_TEST":
                lstatus = "DEMO"
            else:
                lstatus = "UNKNOWN"

        # Coordinate quality mapping
        cqual = getattr(prop, "coordinate_quality", None)
        if not cqual:
            if stype == "HISTORICAL_MARKET_DATA":
                cqual = "LOCALITY_APPROXIMATE"
            elif prop.latitude == 0 and prop.longitude == 0:
                cqual = "MISSING"
            else:
                cqual = "EXACT"

        # Image Sourcing & Provenance
        img_info = ImageProvenanceService.get_property_image_provenance(prop)

        # Contact Availability
        if stype == "PROPPULSE_DIRECT":
            contact_available = True
            contact_source = "Owner Provided"
            phone_val = prop.owner_phone or prop.phone or "+91 98860 12345"
        else:
            contact_available = False
            contact_source = "Historical Dataset - No Contact"
            phone_val = "Contact information unavailable"

        # Formatted currency string
        if prop.price >= 10000000:
            price_formatted = f"₹{prop.price / 10000000:.2f} Cr"
        elif prop.price >= 100000:
            price_formatted = f"₹{prop.price / 100000:.2f} Lakh"
        else:
            price_formatted = f"₹{int(prop.price):,}"

        return {
            "id": prop.id,
            "listing_id": f"BLR-{prop.id}",
            "source_type": stype,
            "source_name": getattr(prop, "source_name", prop.source or "Bengaluru_House_Data.csv"),
            "source_listing_id": getattr(prop, "source_listing_id", f"BLR-{prop.id}"),
            "title": prop.title,
            "property_type": prop.property_type,
            "bhk": prop.bhk,
            "area_sqft": prop.area_sqft,
            "area_type": getattr(prop, "area_type", "super_built_up"),
            "price_inr": prop.price,
            "price_per_sqft": price_sqft,
            "price_formatted": price_formatted,
            "locality": prop.locality,
            "sub_locality": getattr(prop, "sub_locality", None),
            "zone": getattr(prop, "zone", None),
            "address": prop.address,
            "latitude": prop.latitude,
            "longitude": prop.longitude,
            "coordinate_quality": cqual,
            "listing_status": lstatus,
            "availability": getattr(prop, "availability", "Ready to Move"),
            "images": img_info["images"],
            "image_provenance": img_info["image_provenance"],
            "image_provenance_badge": img_info["provenance_badge"],
            "image_disclosure_note": img_info["disclosure_note"],
            "has_genuine_image": img_info["has_genuine_image"],
            "image_count": len(img_info["images"]),
            "owner_or_agent_type": getattr(prop, "seller_type", "Owner"),
            "owner_name": prop.owner_name if contact_available else "Historical Dataset",
            "owner_phone": phone_val if contact_available else "Contact information unavailable",
            "contact_available": contact_available,
            "contact_source": contact_source,
            "source_url": getattr(prop, "source_url", ""),
            "verification_status": prop.verification_status or "Verified",
            "anomaly_flags": anomalies,
            "created_at": prop.created_at
        }

    @staticmethod
    def get_locality_inventory_breakdown(locality_name: str, db: Session) -> Dict[str, Any]:
        """
        Calculate inventory breakdown and market metrics for a locality across all sources.
        """
        loc_clean = locality_name.strip().lower()
        pattern = f"%{loc_clean}%"

        props = db.query(Property).filter(
            (Property.locality.ilike(pattern)) |
            (Property.address.ilike(pattern))
        ).all()

        total_records = len(props)
        current_listings = [p for p in props if getattr(p, "source_type", "") in ["PROPPULSE_DIRECT", "owner_listing", "CURRENT_AUTHORIZED_LISTING"]]
        historical_records = [p for p in props if getattr(p, "source_type", "") in ["HISTORICAL_MARKET_DATA", "historical_dataset", "demo_dataset"]]
        
        m_refs = db.query(MarketReference).filter(MarketReference.locality.ilike(pattern)).count()

        # Property type breakdown
        ptypes = {}
        bhk_dist = {}
        prices = []
        rates = []

        for p in props:
            ptypes[p.property_type] = ptypes.get(p.property_type, 0) + 1
            bhk_dist[str(p.bhk)] = bhk_dist.get(str(p.bhk), 0) + 1
            if p.price and p.price > 0:
                prices.append(p.price)
            sqft_rate = ListingService.calculate_price_per_sqft(p.price, p.area_sqft)
            if sqft_rate > 0:
                rates.append(sqft_rate)

        prices_sorted = sorted(prices)
        rates_sorted = sorted(rates)

        min_price = prices_sorted[0] if prices_sorted else 0.0
        max_price = prices_sorted[-1] if prices_sorted else 0.0
        median_price = prices_sorted[len(prices_sorted) // 2] if prices_sorted else 0.0
        median_sqft_rate = rates_sorted[len(rates_sorted) // 2] if rates_sorted else 0.0

        availability_message = None
        if len(current_listings) == 0:
            availability_message = "No current listings available. Showing historical market data instead."

        return {
            "locality": locality_name.title(),
            "total_records": total_records,
            "current_listings_count": len(current_listings),
            "historical_records_count": len(historical_records),
            "market_references_count": m_refs,
            "availability_message": availability_message,
            "property_types": ptypes,
            "bhk_distribution": bhk_dist,
            "price_range": {
                "min": min_price,
                "max": max_price,
                "median": median_price
            },
            "median_price_per_sqft": median_sqft_rate
        }
