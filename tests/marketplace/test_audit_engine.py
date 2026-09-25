"""Unit tests for Phase A Marketplace Data Audit & Ingestion Engine."""

import json
from pathlib import Path
import tempfile
import pandas as pd
import pytest

from trustlens.marketplace.audit_engine import (
    INDIAN_CITY_STATE_MAP,
    MarketplaceAuditEngine,
    parse_location_hierarchy,
)


def test_parse_location_hierarchy():
    # 1. High confidence known city
    geo1 = parse_location_hierarchy("Indiranagar, Bengaluru")
    assert geo1["city"] == "Bengaluru"
    assert geo1["state"] == "Karnataka"
    assert geo1["geography_confidence"] == "high"
    assert geo1["country"] == "India"

    # 2. Mumbai suburb
    geo2 = parse_location_hierarchy("Andheri West, Mumbai")
    assert geo2["city"] == "Mumbai"
    assert geo2["state"] == "Maharashtra"
    assert geo2["geography_confidence"] == "high"

    # 3. Trailing token unknown
    geo3 = parse_location_hierarchy("Sector 4, UnknownTown")
    assert geo3["city"] == "Unknowntown"
    assert geo3["state"] is None
    assert geo3["geography_confidence"] == "medium"

    # 4. Null / Empty
    geo4 = parse_location_hierarchy(None)
    assert geo4["city"] is None
    assert geo4["geography_confidence"] == "unknown"


def test_audit_engine_ingest_and_parquet_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        source_dir = tmp_path / "raw_source"
        vault_dir = tmp_path / "vault"
        processed_dir = tmp_path / "processed"
        reports_dir = tmp_path / "reports"

        source_dir.mkdir()

        # Create mock capture file
        mock_payload = {
            "schema_version": "1.0",
            "source": "olx.in",
            "exported_at": "2026-09-21T17:11:28Z",
            "captures_count": 1,
            "captures": [
                {
                    "capture_id": "cap-test-001",
                    "captured_at": "2026-09-21T17:11:28Z",
                    "page_type": "search",
                    "capture_context": {
                        "search_query": "iphone",
                        "category_id": 1453,
                        "total_rendered_cards": 2,
                    },
                    "listings": [
                        {
                            "listing_id": "1855001",
                            "source_url": "https://www.olx.in/item/1855001",
                            "raw": {
                                "title": "iPhone 15 Pro Max 256GB",
                                "price": "₹ 85,000",
                                "location": "Koramangala, Bengaluru",
                                "date": "Today",
                            },
                            "normalized": {
                                "title": "iPhone 15 Pro Max 256GB",
                                "price": {"amount": 85000.0, "currency": "INR"},
                                "location": "Koramangala, Bengaluru",
                            },
                            "badges": {"featured": True, "verified": False, "elite": False},
                            "contact_actions": {"chat_available": True, "call_available": True},
                            "media": [
                                {
                                    "file_id": "apollo-file-101",
                                    "src": "https://apollo.olx.in/v1/files/apollo-file-101/image",
                                    "gallery_index": 0,
                                }
                            ],
                        },
                        {
                            "listing_id": "1855002",
                            "source_url": "https://www.olx.in/item/1855002",
                            "raw": {
                                "title": "iPhone 14 128GB Blue",
                                "price": "₹ 45,000",
                                "location": "Bandra, Mumbai",
                                "date": "Yesterday",
                            },
                            "normalized": {
                                "title": "iPhone 14 128GB Blue",
                                "price": {"amount": 45000.0, "currency": "INR"},
                                "location": "Bandra, Mumbai",
                            },
                            "badges": {"featured": False, "verified": False, "elite": False},
                            "contact_actions": {"chat_available": True, "call_available": False},
                            "media": [],
                        },
                    ],
                }
            ],
        }

        file1 = source_dir / "test_capture_1.json"
        with open(file1, "w") as fp:
            json.dump(mock_payload, fp)

        # Duplicate file
        file2 = source_dir / "test_capture_1_copy.json"
        with open(file2, "w") as fp:
            json.dump(mock_payload, fp)

        engine = MarketplaceAuditEngine(
            raw_source_dir=source_dir,
            raw_vault_dir=vault_dir,
            processed_dir=processed_dir,
            reports_dir=reports_dir,
        )

        audit = engine.ingest_and_audit()

        assert audit["source_files_count"] == 2
        assert audit["unique_files_count"] == 1
        assert audit["duplicate_files_count"] == 1
        assert audit["observation_count"] == 2
        assert audit["unique_listing_count"] == 2
        assert audit["unique_media_count"] == 1
        assert audit["media_availability"]["listings_with_media"] == 1
        assert audit["media_availability"]["listings_without_media"] == 1

        # Check Parquet files
        obs_df = pd.read_parquet(processed_dir / "observations.parquet")
        assert len(obs_df) == 2
        assert "city" in obs_df.columns
        assert "geography_confidence" in obs_df.columns

        listings_df = pd.read_parquet(processed_dir / "listings.parquet")
        assert len(listings_df) == 2

        media_df = pd.read_parquet(processed_dir / "media.parquet")
        assert len(media_df) == 1
        assert media_df.iloc[0]["file_id"] == "apollo-file-101"
