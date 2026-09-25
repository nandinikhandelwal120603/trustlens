"""Abstract WebExtractor interface for authorized web page ingestion."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class RawPage:
    """Raw extracted web page payload."""

    url: str
    html: str
    text: str
    title: Optional[str] = None
    status_code: int = 200
    metadata: dict[str, Any] = field(default_factory=dict)


class WebExtractor(ABC):
    """Abstract interface for extracting raw content from permitted URLs."""

    @abstractmethod
    async def extract(self, url: str) -> RawPage:
        """Extract page content from a permitted web URL."""
        pass
