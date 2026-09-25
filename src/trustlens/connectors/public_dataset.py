"""Public research dataset connector for academic and open benchmarks."""

from pathlib import Path
from typing import Any, AsyncGenerator, Optional

from trustlens.connectors.base import MarketplaceConnector
from trustlens.connectors.user_submission import UserSubmissionConnector
from trustlens.models.listing import CanonicalListing


class PublicDatasetConnector(MarketplaceConnector):
    """Loads standardized open-source or academic research datasets."""

    def __init__(self, dataset_name: str = "public_research_dataset"):
        super().__init__(source_name=dataset_name)
        self.delegate = UserSubmissionConnector(source_name=dataset_name)

    async def fetch_listings(self, **kwargs: Any) -> AsyncGenerator[CanonicalListing, None]:
        """Load listings from dataset file path."""
        file_path = kwargs.get("file_path")
        if not file_path:
            return

        path = Path(file_path)
        if path.suffix.lower() == ".csv":
            async for item in self.delegate.from_csv(path):
                yield item
        else:
            async for item in self.delegate.from_json(path):
                yield item

    async def fetch_listing_by_id(self, listing_id: str) -> Optional[CanonicalListing]:
        """Dataset lookup by source ID."""
        return None
