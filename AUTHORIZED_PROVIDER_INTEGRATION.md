# AUTHORIZED PROVIDER INTEGRATION ARCHITECTURE GUIDE

**Document Date**: September 27, 2026  
**Module Path**: `backend/app/providers/`  
**System**: PropPulse AI Real Estate Intelligence Engine

---

## 1. ARCHITECTURAL OVERVIEW

PropPulse AI uses a strict **Provider Adapter Architecture** designed to allow authorized third-party MLS feeds, builder APIs, or licensed listing providers to be connected seamlessly without altering the core database models, AI engines, or frontend interfaces.

```
                  ┌─────────────────────────────────────┐
                  │          ProviderRegistry           │
                  │   (backend/app/providers/registry)  │
                  └──────────────────┬──────────────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           │                         │                         │
┌──────────▼──────────┐   ┌──────────▼──────────┐   ┌──────────▼──────────┐
│ PropPulseDirect     │   │ AuthorizedProvider  │   │  Future Builder API │
│ Provider Adapter    │   │ Template Adapter    │   │  Provider Adapter   │
└─────────────────────┘   └─────────────────────┘   └─────────────────────┘
```

---

## 2. PROVIDER ADAPTER INTERFACE

All listing providers must inherit from `PropertyProviderBase` (`backend/app/providers/property_provider_base.py`) and implement the following standard methods:

```python
from app.providers.property_provider_base import PropertyProviderBase

class MyAuthorizedProvider(PropertyProviderBase):
    def search_listings(self, query: str = "", filters: dict = None) -> list:
        ...

    def get_listing(self, listing_id: str) -> dict:
        ...

    def get_images(self, listing_id: str) -> list:
        ...

    def get_location(self, listing_id: str) -> dict:
        ...

    def get_availability(self, listing_id: str) -> dict:
        ...

    def get_provider_metadata(self) -> dict:
        ...
```

---

## 3. HOW TO CONNECT A NEW LICENSED FEED (STEP-BY-STEP)

1. **Implement Adapter Class**:
   Create a new adapter file in `backend/app/providers/my_licensed_feed_provider.py` implementing `PropertyProviderBase`.

2. **Supply API Credentials**:
   Configure environment variables in `.env`:
   ```env
   LICENSED_FEED_API_KEY=your_authorized_api_key_here
   LICENSED_FEED_ENDPOINT=https://api.licensedpartner.com/v1
   ```

3. **Register Adapter**:
   In `backend/app/main.py` or startup routine, register your provider with the global `ProviderRegistry`:
   ```python
   from app.providers.provider_registry import ProviderRegistry
   from app.providers.my_licensed_feed_provider import MyLicensedFeedProvider

   ProviderRegistry.register_provider(
       "licensed_feed",
       MyLicensedFeedProvider(api_key=os.getenv("LICENSED_FEED_API_KEY"))
   )
   ```

4. **Provenance Classification**:
   Listings returned by external feeds MUST set `source_type="CURRENT_AUTHORIZED_LISTING"` and `listing_status="CURRENT"`.

---

## 4. STRICT LEGAL & COMPLIANCE RULES

- **No Unauthorized Scraping**: Scraping or parsing unprotected web portals (e.g., NoBroker, MagicBricks, 99acres) without written authorization is strictly prohibited.
- **Robot & Access Controls**: Always respect `robots.txt`, rate limits, API paywalls, and authentication controls.
- **Attribution & Images**: Rehosting portal images or contact details is forbidden unless explicitly allowed by the licensing agreement.

---

## 5. CURRENT CONNECTION STATUS

> **CURRENT STATUS**: `CURRENT AUTHORIZED EXTERNAL INVENTORY NOT YET CONNECTED`  
> The adapter template (`AuthorizedProviderTemplate`) is active in `backend/app/providers/` and ready for plug-and-play connection when legal authorization is established.
