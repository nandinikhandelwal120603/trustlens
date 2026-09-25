"""OLX Integration Interface & Compliance Placeholder.

COMPLIANCE & TERMS OF SERVICE NOTICE:
====================================
OLX India's Terms of Service strictly restrict unauthorized scraping, automated
data mining, and collection of user personal information without express permission.

TrustLens DOES NOT implement an unauthorized or aggressive mass scraper for OLX.
This module defines the architectural interface for authorized OLX integration,
such as an official partner API, authorized research data grant, or individual
user-authorized listing exports.
"""

from typing import Any, AsyncGenerator, Optional

from trustlens.connectors.base import MarketplaceConnector
from trustlens.models.listing import CanonicalListing
from trustlens.utils.logging import logger


class OLXConnector(MarketplaceConnector):
    """Compliant connector interface for future authorized OLX data integrations."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(source_name="olx")
        self.api_key = api_key
        self.is_authorized = bool(api_key)

    async def fetch_listings(self, **kwargs: Any) -> AsyncGenerator[CanonicalListing, None]:
        """Authorized listing retrieval placeholder."""
        if not self.is_authorized:
            logger.warning(
                "OLX automated mass scraping is strictly disallowed by platform terms. "
                "To ingest OLX listings, use authorized partner API credentials or ingest "
                "via user submission (`trustlens ingest --file ...`)."
            )
            return
            yield  # pragma: no cover

        # Future official API implementation will be wired here
        raise NotImplementedError(
            "Authorized OLX API client requires verified partner credentials."
        )

    async def fetch_listing_by_id(self, listing_id: str) -> Optional[CanonicalListing]:
        """Authorized single listing lookup."""
        if not self.is_authorized:
            logger.warning("Direct OLX scraping is disabled per terms of service.")
            return None

        raise NotImplementedError(
            "Authorized OLX API client requires verified partner credentials."
        )
