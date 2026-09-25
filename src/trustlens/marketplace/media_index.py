"""Marketplace Observation Index and Search Repository."""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session

from trustlens.marketplace.models import (
    FingerprintStatus,
    ImageMatchRecord,
    MediaFingerprint,
    SimilarityThresholds,
)
from trustlens.marketplace.orm_models import (
    MarketplaceMediaFingerprintORM,
    MarketplaceMediaMatchORM,
    MarketplaceObservationORM,
)
from trustlens.marketplace.similarity import MediaSimilarityComparator
from trustlens.marketplace.text_normalizer import TextNormalizer
from trustlens.storage.orm_models import ListingORM


class MarketplaceObservationIndex:
    """Searchable observation index backed by SQLite."""

    def __init__(self, session: Session):
        self.session = session

    def upsert_fingerprint(self, fp: MediaFingerprint) -> MarketplaceMediaFingerprintORM:
        """
        Idempotent upsert of media fingerprint.
        If existing (by media_id or source_url), update last_seen_at and observation_count.
        """
        stmt = select(MarketplaceMediaFingerprintORM).where(
            (MarketplaceMediaFingerprintORM.media_id == fp.media_id)
            | (
                (MarketplaceMediaFingerprintORM.source_url.is_not(None))
                & (MarketplaceMediaFingerprintORM.source_url == fp.source_url)
            )
        )
        existing = self.session.execute(stmt).scalar_one_or_none()

        if existing:
            existing.last_seen_at = fp.last_seen_at or datetime.now(timezone.utc)
            existing.observation_count += 1
            # Update hashes if they were computed in this pass
            if fp.fingerprint_status == FingerprintStatus.COMPUTED and existing.fingerprint_status != FingerprintStatus.COMPUTED:
                existing.sha256 = fp.sha256
                existing.phash = fp.phash
                existing.dhash = fp.dhash
                existing.ahash = fp.ahash
                existing.width = fp.width
                existing.height = fp.height
                existing.file_size = fp.file_size
                existing.mime_type = fp.mime_type
                existing.download_status = fp.download_status.value
                existing.fingerprint_status = fp.fingerprint_status.value
                existing.local_path = fp.local_path
            self.session.flush()
            return existing

        orm = MarketplaceMediaFingerprintORM(
            fingerprint_id=f"FP-{fp.media_id}",
            media_id=fp.media_id,
            listing_id=fp.listing_id,
            source_url=fp.source_url,
            local_path=fp.local_path,
            download_status=fp.download_status.value,
            fingerprint_status=fp.fingerprint_status.value,
            download_error=fp.download_error,
            sha256=fp.sha256,
            phash=fp.phash,
            dhash=fp.dhash,
            ahash=fp.ahash,
            width=fp.width,
            height=fp.height,
            file_size=fp.file_size,
            mime_type=fp.mime_type,
            first_seen_at=fp.first_seen_at,
            last_seen_at=fp.last_seen_at,
            observation_count=1,
            metadata_=fp.metadata,
        )
        self.session.add(orm)
        self.session.flush()
        return orm

    def find_exact_sha256_matches(self, sha256_hash: str, exclude_media_id: str) -> List[MediaFingerprint]:
        """Find all media fingerprints sharing exact SHA-256."""
        if not sha256_hash:
            return []

        stmt = select(MarketplaceMediaFingerprintORM).where(
            MarketplaceMediaFingerprintORM.sha256 == sha256_hash,
            MarketplaceMediaFingerprintORM.media_id != exclude_media_id,
        )
        records = self.session.execute(stmt).scalars().all()
        return [self._orm_to_domain(r) for r in records]

    def find_all_computed_fingerprints(self, exclude_media_id: Optional[str] = None) -> List[MediaFingerprint]:
        """Fetch all computed fingerprints for similarity evaluation."""
        stmt = select(MarketplaceMediaFingerprintORM).where(
            MarketplaceMediaFingerprintORM.fingerprint_status == "computed"
        )
        if exclude_media_id:
            stmt = stmt.where(MarketplaceMediaFingerprintORM.media_id != exclude_media_id)
        records = self.session.execute(stmt).scalars().all()
        return [self._orm_to_domain(r) for r in records]

    def compare_and_match(
        self,
        current_fp: MediaFingerprint,
        thresholds: Optional[SimilarityThresholds] = None,
    ) -> List[ImageMatchRecord]:
        """
        Compare a media fingerprint against all previously indexed media.
        Returns list of ImageMatchRecord matches (exact SHA-256 and perceptual candidates).
        """
        if current_fp.fingerprint_status != FingerprintStatus.COMPUTED:
            return []

        candidates = self.find_all_computed_fingerprints(exclude_media_id=current_fp.media_id)
        matches: List[ImageMatchRecord] = []

        for cand in candidates:
            match_rec = MediaSimilarityComparator.compare_fingerprints(
                current_fp, cand, thresholds=thresholds
            )
            if match_rec:
                matches.append(match_rec)
                self._record_media_match(match_rec)

        return matches

    def _record_media_match(self, match: ImageMatchRecord) -> None:
        """Persist pairwise match record idempotently."""
        m1, m2 = sorted([match.media_a, match.media_b])
        stmt = select(MarketplaceMediaMatchORM).where(
            MarketplaceMediaMatchORM.media_a == m1,
            MarketplaceMediaMatchORM.media_b == m2,
        )
        existing = self.session.execute(stmt).scalar_one_or_none()
        if existing:
            return

        orm = MarketplaceMediaMatchORM(
            match_id=match.match_id,
            media_a=m1,
            media_b=m2,
            listing_a=match.listing_a,
            listing_b=match.listing_b,
            match_type=match.match_type.value,
            sha256_match=match.sha256_match,
            phash_distance=match.phash_distance,
            dhash_distance=match.dhash_distance,
            ahash_distance=match.ahash_distance,
            thresholds_used=match.thresholds_used,
            similarity_status=match.similarity_status,
            verification_status=match.verification_status.value,
            created_at=match.created_at,
        )
        self.session.add(orm)
        self.session.flush()

    def find_text_reuse(
        self, current_listing_id: str, current_title: str, threshold: float = 0.70
    ) -> List[Tuple[str, str, float, bool]]:
        """
        Find listings sharing exact or similar titles.
        Returns list of (matched_listing_id, matched_title, jaccard_score, is_exact)
        """
        stmt = select(ListingORM).where(ListingORM.listing_id != current_listing_id)
        existing_listings = self.session.execute(stmt).scalars().all()

        results = []
        for l in existing_listings:
            is_exact, is_similar, score = TextNormalizer.compare_titles(
                current_title, l.raw_title, threshold=threshold
            )
            if is_exact or is_similar:
                results.append((l.listing_id, l.raw_title, score, is_exact))

        return results

    @staticmethod
    def _orm_to_domain(orm: MarketplaceMediaFingerprintORM) -> MediaFingerprint:
        return MediaFingerprint(
            media_id=orm.media_id,
            listing_id=orm.listing_id,
            source_url=orm.source_url,
            local_path=orm.local_path,
            download_status=orm.download_status,
            fingerprint_status=orm.fingerprint_status,
            download_error=orm.download_error,
            sha256=orm.sha256,
            phash=orm.phash,
            dhash=orm.dhash,
            ahash=orm.ahash,
            width=orm.width,
            height=orm.height,
            file_size=orm.file_size,
            mime_type=orm.mime_type,
            first_seen_at=orm.first_seen_at,
            last_seen_at=orm.last_seen_at,
            observation_count=orm.observation_count,
            metadata=orm.metadata_,
        )
