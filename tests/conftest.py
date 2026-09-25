"""Pytest fixtures and configuration for TrustLens test suite."""

from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from trustlens.models.listing import CanonicalListing, LineageMetadata
from trustlens.storage.database import Base
from trustlens.storage.filesystem import StorageManager
from trustlens.storage.repository import Repository


@pytest.fixture
def tmp_dirs(tmp_path: Path):
    """Temporary storage paths fixture."""
    raw_dir = tmp_path / "raw"
    norm_dir = tmp_path / "normalized"
    raw_dir.mkdir(parents=True, exist_ok=True)
    norm_dir.mkdir(parents=True, exist_ok=True)
    return raw_dir, norm_dir


@pytest.fixture
def storage_mgr(tmp_dirs) -> StorageManager:
    """Storage manager pointing to temporary directory."""
    raw_dir, norm_dir = tmp_dirs
    return StorageManager(raw_dir=raw_dir, normalized_dir=norm_dir)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """In-memory SQLite database session for fast, isolated unit tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def repository(db_session: Session) -> Repository:
    """Repository bound to in-memory test database."""
    return Repository(db_session)


@pytest.fixture
def sample_canonical() -> CanonicalListing:
    """Sample valid CanonicalListing."""
    lineage = LineageMetadata(
        pipeline_version="0.1.0",
        schema_version="1.0.0",
        source="test_source",
    )
    return CanonicalListing(
        listing_id="lst_test_001",
        case_id="case_test_001",
        source="test_source",
        source_listing_id="EXT-1234",
        source_url="https://example.com/item/1234",
        raw_title="Sony PlayStation 5 Console 825GB",
        normalized_title="sony playstation 5 console 825gb",
        category="Gaming",
        subcategory="PlayStation",
        raw_price=45000.0,
        normalized_price=45000.0,
        raw_currency="₹",
        normalized_currency="INR",
        collection_metadata=lineage,
        is_synthetic=True,
    )
