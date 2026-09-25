"""Deterministic deduplication engine for marketplace listings."""

from typing import Optional, Tuple

from trustlens.models.common import DuplicateType
from trustlens.models.listing import CanonicalListing
from trustlens.storage.repository import Repository


class Deduplicator:
    """Detects exact and near duplicate listings using deterministic keys and hashes."""

    def __init__(self, repository: Repository):
        self.repo = repository

    def check_duplicate(
        self, listing: CanonicalListing
    ) -> Optional[Tuple[str, DuplicateType, str]]:
        """Check if listing matches an existing listing in the database.

        Returns (original_listing_id, duplicate_type, match_reason) or None.
        """
        seller_phone_hash = listing.seller.phone_hash if listing.seller else None
        media_hashes = [m.sha256 for m in listing.media if m.sha256]

        match = self.repo.find_duplicate(
            source=listing.source,
            source_listing_id=listing.source_listing_id,
            source_url=str(listing.source_url) if listing.source_url else None,
            normalized_title=listing.normalized_title,
            seller_phone_hash=seller_phone_hash,
            media_sha256_list=media_hashes,
        )

        if match:
            orig_id, dup_type_str, reason = match
            dup_type = DuplicateType.EXACT if dup_type_str == "exact" else DuplicateType.NEAR
            return (orig_id, dup_type, reason)

        return None

    def record_duplicate(
        self,
        original_listing_id: str,
        duplicate_listing_id: str,
        duplicate_type: DuplicateType,
        match_reason: str,
    ) -> None:
        """Record a detected duplicate pair in the repository."""
        self.repo.record_duplicate(
            original_listing_id=original_listing_id,
            duplicate_listing_id=duplicate_listing_id,
            duplicate_type=duplicate_type.value,
            similarity_score=1.0 if duplicate_type == DuplicateType.EXACT else 0.85,
            match_reason=match_reason,
        )
