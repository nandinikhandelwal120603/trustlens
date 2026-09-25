"""SQLAlchemy ORM models for Marketplace Media Intelligence."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from trustlens.storage.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MarketplaceObservationORM(Base):
    """Provenance tracking for each capture event."""

    __tablename__ = "marketplace_observations"

    observation_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    listing_id: Mapped[str] = mapped_column(String(64), index=True)
    source: Mapped[str] = mapped_column(String(64), default="olx", index=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    search_query: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    category_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    investigation_id: Mapped[str] = mapped_column(String(64), default="INV-002", index=True)
    capture_id: Mapped[str] = mapped_column(String(64), index=True)
    collection_type: Mapped[str] = mapped_column(String(64), default="search_capture", index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    metadata_: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class MarketplaceMediaFingerprintORM(Base):
    """Persistent cryptographic and perceptual fingerprints for marketplace media."""

    __tablename__ = "marketplace_media_fingerprints"

    fingerprint_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    media_id: Mapped[str] = mapped_column(String(64), index=True)
    listing_id: Mapped[str] = mapped_column(String(64), index=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    local_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    
    # Acquisition and computation statuses
    download_status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    fingerprint_status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    download_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Hashes
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    phash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    dhash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    ahash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Image specs
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Temporal history
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    observation_count: Mapped[int] = mapped_column(Integer, default=1)
    metadata_: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class MarketplaceMediaMatchORM(Base):
    """Pairwise match records between two media assets."""

    __tablename__ = "marketplace_media_matches"

    match_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    media_a: Mapped[str] = mapped_column(String(64), index=True)
    media_b: Mapped[str] = mapped_column(String(64), index=True)
    listing_a: Mapped[str] = mapped_column(String(64), index=True)
    listing_b: Mapped[str] = mapped_column(String(64), index=True)

    match_type: Mapped[str] = mapped_column(String(32), index=True)  # exact_sha256 | perceptual_similarity
    sha256_match: Mapped[bool] = mapped_column(Boolean, default=False)
    phash_distance: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dhash_distance: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ahash_distance: Mapped[int | None] = mapped_column(Integer, nullable=True)
    thresholds_used: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    similarity_status: Mapped[str] = mapped_column(String(32), default="candidate_match", index=True)
    verification_status: Mapped[str] = mapped_column(String(32), default="unverified", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class MarketplaceMediaClusterORM(Base):
    """Relational image/media cluster."""

    __tablename__ = "marketplace_media_clusters"

    cluster_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    match_count: Mapped[int] = mapped_column(Integer, default=0)
    verification_status: Mapped[str] = mapped_column(String(32), default="unverified", index=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    members: Mapped[list["MarketplaceClusterMemberORM"]] = relationship(
        "MarketplaceClusterMemberORM", back_populates="cluster", cascade="all, delete-orphan"
    )


class MarketplaceClusterMemberORM(Base):
    """Individual member in a media cluster."""

    __tablename__ = "marketplace_cluster_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cluster_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("marketplace_media_clusters.cluster_id"), index=True
    )
    media_id: Mapped[str] = mapped_column(String(64), index=True)
    listing_id: Mapped[str] = mapped_column(String(64), index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    cluster: Mapped[MarketplaceMediaClusterORM] = relationship(
        "MarketplaceMediaClusterORM", back_populates="members"
    )


class MarketplaceListingRelationshipORM(Base):
    """Observable relationships between listings (media reuse, title reuse, description reuse)."""

    __tablename__ = "marketplace_listing_relationships"

    relationship_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    listing_a: Mapped[str] = mapped_column(String(64), index=True)
    listing_b: Mapped[str] = mapped_column(String(64), index=True)
    relationship_type: Mapped[str] = mapped_column(
        String(64), index=True
    )  # same_image, similar_image, same_title, similar_description
    evidence_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    similarity_status: Mapped[str] = mapped_column(String(32), default="candidate_match", index=True)
    verification_status: Mapped[str] = mapped_column(String(32), default="unverified", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
