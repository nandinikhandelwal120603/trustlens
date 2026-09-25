"""Abstract Base Connector interface for all TrustLens marketplace data sources."""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Optional

from trustlens.models.listing import CanonicalListing


class MarketplaceConnector(ABC):
    """Abstract connector.

    The ingestion engine is source-agnostic; all connectors translate platform-specific
    data payloads into CanonicalListing objects.
    """

    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    async def fetch_listings(self, **kwargs: Any) -> AsyncGenerator[CanonicalListing, None]:
        """Asynchronously yield canonical listings from the source."""
        yield  # type: ignore

    @abstractmethod
    async def fetch_listing_by_id(self, listing_id: str) -> Optional[CanonicalListing]:
        """Retrieve a specific listing by its source platform ID."""
        pass
