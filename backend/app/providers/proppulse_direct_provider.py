from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.providers.property_provider_base import PropertyProviderBase
from app.models.property import Property

class PropPulseDirectProvider(PropertyProviderBase):
    """
    Direct Listing Provider Adapter handling properties submitted directly
    by owners, brokers, or builders through the PropPulse platform.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def search_listings(self, query: str = "", filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        q = self.db.query(Property).filter(
            (Property.source_type == "PROPPULSE_DIRECT") | (Property.source_type == "owner_listing")
        )
        if query:
            pattern = f"%{query}%"
            q = q.filter(
                (Property.title.ilike(pattern)) |
                (Property.locality.ilike(pattern)) |
                (Property.address.ilike(pattern))
            )
        props = q.all()
        return [self._format_direct_listing(p) for p in props]

    def get_listing(self, listing_id: str) -> Optional[Dict[str, Any]]:
        try:
            pid = int(listing_id.replace("BLR-", ""))
            prop = self.db.query(Property).filter(Property.id == pid).first()
            if prop:
                return self._format_direct_listing(prop)
        except Exception:
            pass
        return None

    def get_images(self, listing_id: str) -> List[Dict[str, Any]]:
        listing = self.get_listing(listing_id)
        if listing:
            return listing.get("property_images", [])
        return []

    def get_location(self, listing_id: str) -> Dict[str, Any]:
        listing = self.get_listing(listing_id)
        if listing:
            return {
                "latitude": listing.get("latitude"),
                "longitude": listing.get("longitude"),
                "address": listing.get("address"),
                "locality": listing.get("locality"),
                "coordinate_quality": listing.get("coordinate_quality", "EXACT")
            }
        return {}

    def get_availability(self, listing_id: str) -> Dict[str, Any]:
        listing = self.get_listing(listing_id)
        if listing:
            return {
                "listing_status": listing.get("listing_status", "CURRENT"),
                "availability": listing.get("availability", "Ready to Move")
            }
        return {}

    def get_provider_metadata(self) -> Dict[str, Any]:
        count = self.db.query(Property).filter(
            (Property.source_type == "PROPPULSE_DIRECT") | (Property.source_type == "owner_listing")
        ).count()
        return {
            "provider_id": "proppulse_direct",
            "provider_name": "PropPulse Direct Listings Engine",
            "source_type": "PROPPULSE_DIRECT",
            "is_authorized": True,
            "status": "ACTIVE",
            "total_listings": count,
            "description": "Native platform engine for verified direct owner & broker property listings."
        }

    def _format_direct_listing(self, p: Property) -> Dict[str, Any]:
        sqft_rate = round(p.price / p.area_sqft, 2) if p.area_sqft > 0 else 0
        return {
            "id": p.id,
            "listing_id": f"BLR-{p.id}",
            "source_type": "PROPPULSE_DIRECT",
            "source_name": "PropPulse Direct",
            "source_listing_id": getattr(p, "source_listing_id", f"BLR-{p.id}"),
            "title": p.title,
            "property_type": p.property_type,
            "bhk": p.bhk,
            "area_sqft": p.area_sqft,
            "area_type": getattr(p, "area_type", "super_built_up"),
            "price_inr": p.price,
            "price_per_sqft": sqft_rate,
            "locality": p.locality,
            "address": p.address,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "coordinate_quality": getattr(p, "coordinate_quality", "EXACT"),
            "listing_status": getattr(p, "listing_status", "CURRENT"),
            "availability": getattr(p, "availability", "Ready to Move"),
            "image_provenance": getattr(p, "image_provenance", "OWNER_UPLOADED" if p.images else "NO_IMAGE"),
            "images": p.images or [],
            "contact_available": True,
            "owner_name": p.owner_name,
            "owner_phone": p.owner_phone
        }
