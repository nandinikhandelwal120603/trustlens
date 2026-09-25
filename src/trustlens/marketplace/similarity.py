"""Deterministic media similarity comparators and distance metrics."""

import uuid
from datetime import datetime, timezone
from typing import Optional

import imagehash

from trustlens.marketplace.models import (
    FingerprintStatus,
    ImageMatchRecord,
    MatchType,
    MediaFingerprint,
    SimilarityThresholds,
    VerificationStatus,
)


class MediaSimilarityComparator:
    """Computes exact and perceptual hash distances between media fingerprints."""

    @staticmethod
    def calculate_hash_distance(hash_a: Optional[str], hash_b: Optional[str]) -> Optional[int]:
        """Calculate Hamming distance between two hex perceptual hash strings."""
        if not hash_a or not hash_b:
            return None
        try:
            h1 = imagehash.hex_to_hash(hash_a)
            h2 = imagehash.hex_to_hash(hash_b)
            return int(h1 - h2)
        except Exception:
            return None

    @classmethod
    def compare_fingerprints(
        cls,
        fp_a: MediaFingerprint,
        fp_b: MediaFingerprint,
        thresholds: Optional[SimilarityThresholds] = None,
    ) -> Optional[ImageMatchRecord]:
        """
        Compare two media fingerprints.
        Returns ImageMatchRecord if exact SHA-256 or perceptual threshold is met, else None.
        """
        if fp_a.media_id == fp_b.media_id:
            return None

        # Cannot compare if either fingerprint is unavailable
        if (
            fp_a.fingerprint_status != FingerprintStatus.COMPUTED
            or fp_b.fingerprint_status != FingerprintStatus.COMPUTED
        ):
            return None

        thresh = thresholds or SimilarityThresholds()

        # 1. Exact SHA-256 match
        is_exact = bool(fp_a.sha256 and fp_b.sha256 and fp_a.sha256 == fp_b.sha256)

        # 2. Perceptual distances
        p_dist = cls.calculate_hash_distance(fp_a.phash, fp_b.phash)
        d_dist = cls.calculate_hash_distance(fp_a.dhash, fp_b.dhash)
        a_dist = cls.calculate_hash_distance(fp_a.ahash, fp_b.ahash)

        # Check perceptual candidate thresholds
        is_perceptual_candidate = False
        if p_dist is not None and p_dist <= thresh.phash_max_distance:
            is_perceptual_candidate = True
        elif d_dist is not None and d_dist <= thresh.dhash_max_distance:
            is_perceptual_candidate = True
        elif a_dist is not None and a_dist <= thresh.ahash_max_distance:
            is_perceptual_candidate = True

        if not is_exact and not is_perceptual_candidate:
            return None

        match_type = MatchType.EXACT_SHA256 if is_exact else MatchType.PERCEPTUAL_SIMILARITY
        match_id = f"MATCH-{uuid.uuid4().hex[:12].upper()}"

        return ImageMatchRecord(
            match_id=match_id,
            media_a=fp_a.media_id,
            media_b=fp_b.media_id,
            listing_a=fp_a.listing_id,
            listing_b=fp_b.listing_id,
            match_type=match_type,
            sha256_match=is_exact,
            phash_distance=p_dist,
            dhash_distance=d_dist,
            ahash_distance=a_dist,
            thresholds_used=thresh.model_dump(),
            similarity_status="candidate_match",
            verification_status=VerificationStatus.UNVERIFIED,
            created_at=datetime.now(timezone.utc),
        )
