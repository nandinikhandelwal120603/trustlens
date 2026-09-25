"""SQLAlchemy ORM models representing the TrustLens database schema."""

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


class CaseORM(Base):
    """SQLAlchemy model for an investigation Case."""

    __tablename__ = "cases"

    case_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), default="new", index=True)
    source: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    labels: Mapped[list[str]] = mapped_column(JSON, default=list)
    metadata_: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Relationships
    listings: Mapped[list["ListingORM"]] = relationship(
        "ListingORM", back_populates="case", cascade="all, delete-orphan"
    )
    evidences: Mapped[list["EvidenceORM"]] = relationship(
        "EvidenceORM", back_populates="case", cascade="all, delete-orphan"
    )


class SellerORM(Base):
    """SQLAlchemy model for a privacy-protected Seller."""

    __tablename__ = "sellers"

    seller_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source: Mapped[str] = mapped_column(String(64), index=True)
    source_seller_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    account_age: Mapped[str | None] = mapped_column(String(64), nullable=True)
    profile_location: Mapped[str | None] = mapped_column(String(256), nullable=True)
    verification_status: Mapped[str | None] = mapped_column(String(64), default="unverified")
    seller_type: Mapped[str | None] = mapped_column(String(64), default="individual")
    listing_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    business_name_claim: Mapped[str | None] = mapped_column(String(256), nullable=True)
    gstin_claim: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Privacy fields: flags + hashes only
    phone_present: Mapped[bool] = mapped_column(Boolean, default=False)
    phone_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    email_present: Mapped[bool] = mapped_column(Boolean, default=False)
    email_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    website_claim: Mapped[str | None] = mapped_column(String(512), nullable=True)

    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Relationships
    listings: Mapped[list["ListingORM"]] = relationship("ListingORM", back_populates="seller")


class ListingORM(Base):
    """SQLAlchemy model for a canonical marketplace Listing."""

    __tablename__ = "listings"

    listing_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(64), ForeignKey("cases.case_id"), index=True)
    seller_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("sellers.seller_id"), nullable=True, index=True
    )

    source: Mapped[str] = mapped_column(String(64), index=True)
    source_listing_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True, index=True)

    # Titles & Descriptions
    raw_title: Mapped[str] = mapped_column(Text)
    normalized_title: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    raw_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Classification
    category: Mapped[str] = mapped_column(String(128), index=True)
    subcategory: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    brand: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)

    # Financials
    raw_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    normalized_price: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    raw_currency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    normalized_currency: Mapped[str | None] = mapped_column(String(8), default="INR")

    # Condition & Geography
    condition: Mapped[str] = mapped_column(String(32), default="unknown", index=True)
    location_raw: Mapped[str | None] = mapped_column(String(256), nullable=True)
    location_city: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    location_state: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)

    # Timestamps
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Lineage & Synthetic flag
    pipeline_version: Mapped[str] = mapped_column(String(32), default="0.1.0")
    schema_version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    extracted_claims: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    collection_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Relationships
    case: Mapped["CaseORM"] = relationship("CaseORM", back_populates="listings")
    seller: Mapped[SellerORM | None] = relationship("SellerORM", back_populates="listings")
    media: Mapped[list["MediaORM"]] = relationship(
        "MediaORM", back_populates="listing", cascade="all, delete-orphan"
    )


class MediaORM(Base):
    """SQLAlchemy model for media assets (images/videos)."""

    __tablename__ = "medias"

    media_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    listing_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("listings.listing_id"), nullable=True, index=True
    )
    media_type: Mapped[str] = mapped_column(String(16), default="image", index=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    local_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    perceptual_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    collection_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Relationships
    listing: Mapped[ListingORM | None] = relationship("ListingORM", back_populates="media")


class EvidenceORM(Base):
    """SQLAlchemy model for Evidence items."""

    __tablename__ = "evidences"

    evidence_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(64), ForeignKey("cases.case_id"), index=True)
    source_type: Mapped[str] = mapped_column(String(64), index=True)
    source_name: Mapped[str] = mapped_column(String(128))
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    claim: Mapped[str] = mapped_column(Text)
    evidence_text: Mapped[str] = mapped_column(Text)
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    verification_status: Mapped[str] = mapped_column(String(32), default="unverified", index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Relationships
    case: Mapped[CaseORM] = relationship("CaseORM", back_populates="evidences")


class ListingDuplicateORM(Base):
    """SQLAlchemy model recording duplicate listing detections."""

    __tablename__ = "listing_duplicates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    original_listing_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("listings.listing_id"), index=True
    )
    duplicate_listing_id: Mapped[str] = mapped_column(String(64), index=True)
    duplicate_type: Mapped[str] = mapped_column(String(32), default="exact", index=True)
    similarity_score: Mapped[float] = mapped_column(Float, default=1.0)
    match_reason: Mapped[str] = mapped_column(String(256))
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
