"""Unit tests for connectors (UserSubmission, PublicDataset, OLX)."""

from pathlib import Path

import pytest

from trustlens.connectors.olx import OLXConnector
from trustlens.connectors.public_dataset import PublicDatasetConnector
from trustlens.connectors.user_submission import UserSubmissionConnector


@pytest.mark.asyncio
async def test_user_submission_json(tmp_path: Path):
    """Test reading from a JSON listing file."""
    json_file = Path("examples/single_listing.json")
    connector = UserSubmissionConnector()

    items = []
    async for item in connector.from_json(json_file):
        items.append(item)

    assert len(items) == 1
    listing = items[0]
    assert listing.source == "user_submission"
    assert listing.source_listing_id == "SYN-DEMO-999"
    assert listing.category == "Smartphones"
    assert listing.subcategory == "iPhone"
    assert listing.normalized_price == 38500.0
    assert listing.is_synthetic is True
    assert listing.seller is not None
    assert listing.seller.display_name == "Demo Seller"
    assert listing.seller.phone_present is True


@pytest.mark.asyncio
async def test_user_submission_csv():
    """Test reading from a CSV listing file."""
    csv_file = Path("examples/synthetic_listings.csv")
    connector = UserSubmissionConnector()

    items = []
    async for item in connector.from_csv(csv_file):
        items.append(item)

    assert len(items) == 5
    first = items[0]
    assert first.source_listing_id == "CSV-IPH-101"
    assert first.category == "Smartphones"
    assert first.normalized_price == 46000.0
    assert first.is_synthetic is True


@pytest.mark.asyncio
async def test_public_dataset_connector():
    """Test public dataset connector loading sample file."""
    dataset = PublicDatasetConnector("stanford_marketplace_benchmark")
    items = []
    async for item in dataset.fetch_listings(file_path="examples/synthetic_listings.json"):
        items.append(item)

    assert len(items) >= 20
    assert all(item.is_synthetic for item in items)


@pytest.mark.asyncio
async def test_olx_connector_compliance():
    """Test OLXConnector warns and blocks mass scraping without authorized API key."""
    connector = OLXConnector(api_key=None)
    assert connector.is_authorized is False

    listings = []
    async for item in connector.fetch_listings():
        listings.append(item)

    # Yields nothing and logs warning per Terms of Service compliance
    assert len(listings) == 0
