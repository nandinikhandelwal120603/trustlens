"""Connectors package for TrustLens data ingestion."""

from trustlens.connectors.base import MarketplaceConnector
from trustlens.connectors.crawl4ai_adapter import Crawl4AIWebExtractor
from trustlens.connectors.olx import OLXConnector
from trustlens.connectors.public_dataset import PublicDatasetConnector
from trustlens.connectors.user_submission import UserSubmissionConnector
from trustlens.connectors.web_extractor import RawPage, WebExtractor

__all__ = [
    "MarketplaceConnector",
    "UserSubmissionConnector",
    "PublicDatasetConnector",
    "OLXConnector",
    "WebExtractor",
    "Crawl4AIWebExtractor",
    "RawPage",
]
