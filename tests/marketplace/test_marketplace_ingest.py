"""Integration tests for Marketplace Ingestion using real capture-olx fixture."""

from pathlib import Path
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from trustlens.marketplace.ingestion import MarketplaceIngestionEngine
from trustlens.marketplace.orm_models import (
    MarketplaceMediaFingerprintORM,
    MarketplaceObservationORM,
)
from trustlens.storage.database import Base
from trustlens.storage.orm_models import ListingORM

import pytest

REAL_FIXTURE_PATH = Path("/Users/nandinikhandelwal/Downloads/trustlens_olx_iphone_2026-09-21T08-33-30.json")


def create_in_memory_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


@pytest.mark.skipif(not REAL_FIXTURE_PATH.exists(), reason="Local pilot capture fixture not found in Downloads")
def test_ingest_real_iphone_capture_fixture():
    session = create_in_memory_session()
    engine = MarketplaceIngestionEngine(session=session, download_media=False)

    # 1. First Ingestion
    report1 = engine.ingest_file(REAL_FIXTURE_PATH)

    assert report1.listings_observed == 240
    assert report1.new_listings == 240
    assert report1.existing_listings_updated == 0
    assert report1.images_observed == 208
    assert report1.search_query == "iphone"

    # Verify listings in database
    listings_count = session.scalar(select(func.count(ListingORM.listing_id)))
    assert listings_count == 240

    # Verify provenance observations
    obs_count = session.scalar(select(func.count(MarketplaceObservationORM.observation_id)))
    assert obs_count == 240

    # Verify media fingerprints table (208 image references map to 200 unique image assets due to cross-listing image reuse)
    fps_count = session.scalar(select(func.count(MarketplaceMediaFingerprintORM.fingerprint_id)))
    assert fps_count == 200

    # Verify that shared image b3jtvzyyojs12-IN has observation_count = 2
    shared_fp = session.get(MarketplaceMediaFingerprintORM, "FP-MED-b3jtvzyyojs12-IN")
    assert shared_fp is not None
    assert shared_fp.observation_count == 2

    # 2. Test Idempotency: Re-ingesting the same capture file
    report2 = engine.ingest_file(REAL_FIXTURE_PATH)

    assert report2.listings_observed == 240
    assert report2.new_listings == 0
    assert report2.existing_listings_updated == 240
    # Zero duplicate listing records created
    listings_count_after = session.scalar(select(func.count(ListingORM.listing_id)))
    assert listings_count_after == 240

    # Provenance observations should append 240 more records for the new observation event
    obs_count_after = session.scalar(select(func.count(MarketplaceObservationORM.observation_id)))
    assert obs_count_after == 480

    # Media fingerprints should remain 200 unique assets with updated observation count
    fps_count_after = session.scalar(select(func.count(MarketplaceMediaFingerprintORM.fingerprint_id)))
    assert fps_count_after == 200

    sample_fp = session.execute(select(MarketplaceMediaFingerprintORM)).scalars().first()
    assert sample_fp is not None
    assert sample_fp.observation_count == 2
