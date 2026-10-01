from typing import Dict, Any, List, Optional
from app.providers.property_provider_base import PropertyProviderBase

class ProviderRegistry:
    """
    Central Provider Registry managing listing provider adapters.
    Ensures seamless plug-and-play connection of authorized API feeds, MLS connectors,
    and direct submission providers.
    """
    _providers: Dict[str, PropertyProviderBase] = {}

    @classmethod
    def register_provider(cls, name: str, provider: PropertyProviderBase):
        """Register a provider instance with unique provider name."""
        cls._providers[name.lower()] = provider

    @classmethod
    def get_provider(cls, name: str) -> Optional[PropertyProviderBase]:
        """Retrieve registered provider instance."""
        return cls._providers.get(name.lower())

    @classmethod
    def list_providers(cls) -> List[Dict[str, Any]]:
        """List metadata for all currently registered providers."""
        return [
            provider.get_provider_metadata()
            for provider in cls._providers.values()
        ]

    @classmethod
    def search_all_authorized(cls, query: str = "", filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Aggregate search results across all registered active authorized listing providers."""
        results = []
        for name, provider in cls._providers.items():
            meta = provider.get_provider_metadata()
            if meta.get("is_authorized") and meta.get("status") == "ACTIVE":
                try:
                    res = provider.search_listings(query=query, filters=filters)
                    results.extend(res)
                except Exception as e:
                    print(f"Provider '{name}' search execution error: {e}")
        return results
