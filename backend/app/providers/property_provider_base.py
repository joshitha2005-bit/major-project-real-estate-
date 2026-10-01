from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class PropertyProviderBase(ABC):
    """
    Abstract Base Class for all property data providers in PropPulse AI.
    All authorized listing feeds, direct listing engines, and market reference
    adapters must implement this strict interface.
    """

    @abstractmethod
    def search_listings(self, query: str = "", filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search and filter property listings from provider."""
        pass

    @abstractmethod
    def get_listing(self, listing_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve single property listing details by listing_id."""
        pass

    @abstractmethod
    def get_images(self, listing_id: str) -> List[Dict[str, Any]]:
        """Retrieve image records and metadata for given listing_id."""
        pass

    @abstractmethod
    def get_location(self, listing_id: str) -> Dict[str, Any]:
        """Retrieve location, address, locality, and coordinate metadata."""
        pass

    @abstractmethod
    def get_availability(self, listing_id: str) -> Dict[str, Any]:
        """Retrieve listing availability date and status."""
        pass

    @abstractmethod
    def get_provider_metadata(self) -> Dict[str, Any]:
        """Retrieve provider authorization status, licensing details, and capabilities."""
        pass
