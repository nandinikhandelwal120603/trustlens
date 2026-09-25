"""Unit tests for media similarity comparison and observation index."""

import io
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from trustlens.marketplace.media_fingerprint import MediaFingerprinter
from trustlens.marketplace.media_index import MarketplaceObservationIndex
from trustlens.marketplace.models import MatchType, SimilarityThresholds
from trustlens.marketplace.similarity import MediaSimilarityComparator
from trustlens.storage.database import Base


def create_in_memory_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def create_test_image(color=(255, 0, 0), size=(100, 100)) -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_similarity_exact_sha256():
    img_bytes = create_test_image((255, 0, 0))
    fp1 = MediaFingerprinter.fingerprint_media("M1", "L1", content_bytes=img_bytes)
    fp2 = MediaFingerprinter.fingerprint_media("M2", "L2", content_bytes=img_bytes)

    match = MediaSimilarityComparator.compare_fingerprints(fp1, fp2)
    assert match is not None
    assert match.match_type == MatchType.EXACT_SHA256
    assert match.sha256_match is True
    assert match.phash_distance == 0


def test_similarity_perceptual_candidate():
    # Same content at different sizes has different SHA-256 but identical pHash
    img_large = create_test_image((10, 200, 50), (300, 300))
    img_small = create_test_image((10, 200, 50), (80, 80))

    fp1 = MediaFingerprinter.fingerprint_media("M1", "L1", content_bytes=img_large)
    fp2 = MediaFingerprinter.fingerprint_media("M2", "L2", content_bytes=img_small)

    match = MediaSimilarityComparator.compare_fingerprints(fp1, fp2)
    assert match is not None
    assert match.match_type == MatchType.PERCEPTUAL_SIMILARITY
    assert match.sha256_match is False
    assert match.phash_distance == 0


def test_similarity_unrelated_images():
    img_red = create_test_image((255, 0, 0))
    img_gradient = Image.new("RGB", (100, 100))
    for x in range(100):
        for y in range(100):
            img_gradient.putpixel((x, y), (x * 2, y * 2, (x + y)))
    buf = io.BytesIO()
    img_gradient.save(buf, format="JPEG")

    fp1 = MediaFingerprinter.fingerprint_media("M1", "L1", content_bytes=img_red)
    fp2 = MediaFingerprinter.fingerprint_media("M2", "L2", content_bytes=buf.getvalue())

    match = MediaSimilarityComparator.compare_fingerprints(fp1, fp2, thresholds=SimilarityThresholds(phash_max_distance=2))
    assert match is None


def test_observation_index_upsert_and_matching():
    session = create_in_memory_session()
    index = MarketplaceObservationIndex(session)

    img_bytes = create_test_image((50, 100, 150))
    fp1 = MediaFingerprinter.fingerprint_media("M1", "L1", content_bytes=img_bytes)
    index.upsert_fingerprint(fp1)

    # Re-upserting same fingerprint increments observation count and updates timestamp
    fp1_again = MediaFingerprinter.fingerprint_media("M1", "L1", content_bytes=img_bytes)
    updated = index.upsert_fingerprint(fp1_again)
    assert updated.observation_count == 2

    # Ingesting second media with same image finds match
    fp2 = MediaFingerprinter.fingerprint_media("M2", "L2", content_bytes=img_bytes)
    matches = index.compare_and_match(fp2)
    assert len(matches) == 1
    assert matches[0].media_a == "M1" or matches[0].media_b == "M1"
