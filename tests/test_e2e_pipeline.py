"""End-to-end integration tests for the full ingestion pipeline."""

import json
from pathlib import Path

from sqlalchemy.orm import Session

from trustlens.connectors.user_submission import UserSubmissionConnector
from trustlens.ingestion.pipeline import IngestionPipeline
from trustlens.storage.filesystem import StorageManager
from trustlens.storage.repository import Repository


def test_end_to_end_synthetic_ingestion(db_session: Session, storage_mgr: StorageManager):
    """E2E Test: synthetic JSON -> validation -> normalization -> database -> stats."""
    json_path = Path("examples/synthetic_listings.json")
    assert json_path.exists()

    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    connector = UserSubmissionConnector()
    listings = [connector.dict_to_canonical(r) for r in raw_data]

    pipeline = IngestionPipeline(session=db_session, storage=storage_mgr)
    result = pipeline.ingest_batch(listings, raw_records=raw_data)

    assert result.total_received == len(raw_data)
    assert result.persisted_count > 0
    assert result.valid_count == len(raw_data)
    assert result.duplicates_detected >= 1  # synthetic data contains duplicate records

    # Query stats from Repository
    repo = Repository(db_session)
    stats = repo.get_stats()

    assert stats["total_listings"] == result.persisted_count
    assert stats["synthetic_listings"] == result.persisted_count
    assert stats["duplicate_count"] >= 1
    assert "Smartphones" in stats["by_category"]
    assert "Gaming" in stats["by_category"]
    assert stats["listings_with_images"] > 0
    assert stats["missing_descriptions"] >= 1  # record 23 has empty description
    assert stats["missing_prices"] >= 1  # record 22 has negotiable / None price

    # Verify filesystem outputs
    assert (storage_mgr.normalized_dir / "listings.jsonl").exists()
    assert (storage_mgr.normalized_dir / "listings.parquet").exists()

    # Verify raw cases were preserved
    first_case_id = result.case_ids[0]
    assert (storage_mgr.raw_dir / first_case_id / "source.json").exists()
