"""Unit tests for the deterministic Deduplicator engine."""

from trustlens.ingestion.deduplicator import Deduplicator
from trustlens.models.common import DuplicateType
from trustlens.models.listing import CanonicalListing, LineageMetadata
from trustlens.models.media import Media
from trustlens.models.seller import Seller
from trustlens.storage.repository import Repository


def test_deduplicate_by_source_listing_id(
    repository: Repository, sample_canonical: CanonicalListing
):
    """Test exact match on source platform listing ID."""
    repository.save_listing(sample_canonical)

    dedup = Deduplicator(repository)

    # Incoming listing with same source and source_listing_id
    incoming = CanonicalListing(
        source=sample_canonical.source,
        source_listing_id=sample_canonical.source_listing_id,
        raw_title="Another Title",
        category="Gaming",
        collection_metadata=LineageMetadata(source=sample_canonical.source),
    )

    match = dedup.check_duplicate(incoming)
    assert match is not None
    orig_id, dup_type, reason = match
    assert orig_id == sample_canonical.listing_id
    assert dup_type == DuplicateType.EXACT
    assert "source listing ID" in reason


def test_deduplicate_by_url(repository: Repository, sample_canonical: CanonicalListing):
    """Test exact match on listing URL."""
    repository.save_listing(sample_canonical)

    dedup = Deduplicator(repository)

    incoming = CanonicalListing(
        source="another_source",
        source_url=sample_canonical.source_url,
        raw_title="Different Title",
        category="Gaming",
        collection_metadata=LineageMetadata(source="another_source"),
    )

    match = dedup.check_duplicate(incoming)
    assert match is not None
    orig_id, dup_type, reason = match
    assert orig_id == sample_canonical.listing_id
    assert dup_type == DuplicateType.EXACT
    assert "source URL" in reason


def test_deduplicate_by_media_sha256(repository: Repository, sample_canonical: CanonicalListing):
    """Test match when incoming listing shares media file SHA-256."""
    media_item = Media(
        listing_id=sample_canonical.listing_id,
        source_url="https://example.com/ps5.jpg",
        sha256="5d41402abc4b2a76b9719d911017c592a2a229a43a84dfa1d8212ec9103c8c67",
    )
    sample_canonical.media = [media_item]
    repository.save_listing(sample_canonical)

    dedup = Deduplicator(repository)

    # Incoming listing with different ID & URL but identical image SHA-256
    incoming = CanonicalListing(
        source="relisted_source",
        source_listing_id="NEW-999",
        source_url="https://example.com/new-listing",
        raw_title="Cheap PS5 Relisted",
        category="Gaming",
        media=[
            Media(
                source_url="https://cdn.other.com/scam_copy.jpg",
                sha256="5d41402abc4b2a76b9719d911017c592a2a229a43a84dfa1d8212ec9103c8c67",
            )
        ],
        collection_metadata=LineageMetadata(source="relisted_source"),
    )

    match = dedup.check_duplicate(incoming)
    assert match is not None
    orig_id, dup_type, reason = match
    assert orig_id == sample_canonical.listing_id
    assert dup_type == DuplicateType.EXACT
    assert "media file SHA256" in reason


def test_deduplicate_by_title_and_seller_phone(
    repository: Repository, sample_canonical: CanonicalListing
):
    """Test near match when same seller posts identical normalized title."""
    seller = Seller.from_raw(
        source="test",
        display_name="Seller One",
        raw_phone="+91 9876543210",
    )
    sample_canonical.seller = seller
    repository.save_listing(sample_canonical)

    dedup = Deduplicator(repository)

    # Incoming listing with different source ID but identical title and same seller phone
    same_seller = Seller.from_raw(
        source="test",
        display_name="Different Nickname",
        raw_phone="+91 9876543210",
    )
    incoming = CanonicalListing(
        source="test",
        source_listing_id="DIFFERENT-ID",
        raw_title="Sony PlayStation 5 Console 825GB",
        normalized_title=sample_canonical.normalized_title,
        category="Gaming",
        seller=same_seller,
        collection_metadata=LineageMetadata(source="test"),
    )

    match = dedup.check_duplicate(incoming)
    assert match is not None
    orig_id, dup_type, reason = match
    assert orig_id == sample_canonical.listing_id
    assert dup_type == DuplicateType.NEAR
    assert "same seller phone" in reason
