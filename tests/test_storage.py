"""Unit tests for StorageManager (filesystem) and Repository (database)."""

from trustlens.models.listing import CanonicalListing
from trustlens.models.media import Media
from trustlens.models.seller import Seller
from trustlens.storage.filesystem import StorageManager
from trustlens.storage.repository import Repository


def test_filesystem_raw_and_normalized(
    storage_mgr: StorageManager, sample_canonical: CanonicalListing
):
    """Test filesystem persistence of raw and normalized assets."""
    # 1. Save raw artifact
    raw_path = storage_mgr.save_raw_artifact(
        case_id=sample_canonical.case_id,
        filename="source.json",
        content={"title": sample_canonical.raw_title},
    )
    assert raw_path.exists()
    assert "source.json" in raw_path.name

    # 2. Append validation error
    err_path = storage_mgr.append_validation_error(
        source="test",
        raw_record={"bad": "data"},
        errors=["Missing field: title"],
        case_id=sample_canonical.case_id,
    )
    assert err_path.exists()

    # 3. Append normalized listing
    jsonl_path = storage_mgr.append_normalized_listing(sample_canonical)
    assert jsonl_path.exists()

    # 4. Export to parquet
    parquet_path = storage_mgr.export_normalized_to_parquet()
    assert parquet_path is not None
    assert parquet_path.exists()
    assert parquet_path.suffix == ".parquet"


def test_database_repository_persistence(
    repository: Repository, sample_canonical: CanonicalListing
):
    """Test repository CRUD operations on SQLite."""
    # Add seller and media
    seller = Seller.from_raw(
        source=sample_canonical.source,
        display_name="Store Seller",
        raw_phone="+91 9999999999",
    )
    sample_canonical.seller = seller
    sample_canonical.media = [
        Media(
            media_type="image",
            source_url="https://example.com/item.jpg",
            sha256="hash123",
        )
    ]

    orm_listing = repository.save_listing(sample_canonical)
    assert orm_listing.listing_id == sample_canonical.listing_id

    # Verify stats
    stats = repository.get_stats()
    assert stats["total_listings"] == 1
    assert stats["synthetic_listings"] == 1
    assert stats["by_category"].get("Gaming") == 1
    assert stats["listings_with_images"] == 1
    assert stats["missing_prices"] == 0
