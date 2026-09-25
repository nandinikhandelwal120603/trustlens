"""Pydantic domain models for marketplace intelligence."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DownloadStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADED = "downloaded"
    FAILED = "failed"
    NOT_ATTEMPTED = "not_attempted"


class FingerprintStatus(str, Enum):
    COMPUTED = "computed"
    UNAVAILABLE = "unavailable"
    PENDING = "pending"


class MatchType(str, Enum):
    EXACT_SHA256 = "exact_sha256"
    PERCEPTUAL_SIMILARITY = "perceptual_similarity"


class RelationshipType(str, Enum):
    SAME_IMAGE = "same_image"
    SIMILAR_IMAGE = "similar_image"
    SAME_TITLE = "same_title"
    SIMILAR_DESCRIPTION = "similar_description"


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    CORROBORATED = "corroborated"
    CONTRADICTED = "contradicted"


class MediaFingerprint(BaseModel):
    """Cryptographic and perceptual fingerprint for a media asset."""

    media_id: str
    listing_id: str
    source_url: Optional[str] = None
    local_path: Optional[str] = None
    download_status: DownloadStatus = DownloadStatus.NOT_ATTEMPTED
    fingerprint_status: FingerprintStatus = FingerprintStatus.UNAVAILABLE
    download_error: Optional[str] = None

    sha256: Optional[str] = None
    phash: Optional[str] = None
    dhash: Optional[str] = None
    ahash: Optional[str] = None

    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

    first_seen_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    observation_count: int = 1
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimilarityThresholds(BaseModel):
    """Configurable perceptual hash distance thresholds."""

    phash_max_distance: int = 8
    dhash_max_distance: int = 10
    ahash_max_distance: int = 10
    text_jaccard_threshold: float = 0.70


class ImageMatchRecord(BaseModel):
    """Deterministic match record between two media assets."""

    match_id: str
    media_a: str
    media_b: str
    listing_a: str
    listing_b: str
    match_type: MatchType
    sha256_match: bool = False
    phash_distance: Optional[int] = None
    dhash_distance: Optional[int] = None
    ahash_distance: Optional[int] = None
    thresholds_used: Dict[str, Any] = Field(default_factory=dict)
    similarity_status: str = "candidate_match"
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ClusterMember(BaseModel):
    media_id: str
    listing_id: str
    first_seen_at: datetime
    last_seen_at: datetime


class MediaCluster(BaseModel):
    """Relational image/media cluster."""

    cluster_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    match_count: int = 0
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    members: List[ClusterMember] = Field(default_factory=list)


class ListingRelationship(BaseModel):
    """Observed relationship between two marketplace listings."""

    relationship_id: str
    listing_a: str
    listing_b: str
    relationship_type: RelationshipType
    evidence_data: Dict[str, Any] = Field(default_factory=dict)
    similarity_status: str = "candidate_match"
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MarketplaceObservation(BaseModel):
    """Provenance tracking for a capture event."""

    observation_id: str
    listing_id: str
    source: str = "olx"
    source_url: Optional[str] = None
    search_query: Optional[str] = None
    category_id: Optional[str] = None
    investigation_id: str = "INV-002"
    capture_id: str
    collection_type: str = "search_capture"
    captured_at: datetime
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IngestionReport(BaseModel):
    """Summary of marketplace ingestion results."""

    capture_id: str
    source_url: Optional[str] = None
    search_query: Optional[str] = None
    listings_observed: int = 0
    new_listings: int = 0
    existing_listings_updated: int = 0
    images_observed: int = 0
    images_fingerprinted: int = 0
    exact_image_matches: int = 0
    perceptual_candidate_matches: int = 0
    clusters_created: int = 0
    clusters_updated: int = 0
    exact_title_reuse_count: int = 0
    similar_title_count: int = 0
    relationships_recorded: int = 0
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    detailed_matches: List[Dict[str, Any]] = Field(default_factory=list)
