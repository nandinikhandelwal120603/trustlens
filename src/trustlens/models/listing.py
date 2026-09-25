"""Canonical Listing schema for TrustLens data ingestion."""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from trustlens.models.common import ItemCondition
from trustlens.models.media import Media
from trustlens.models.seller import Seller


class LineageMetadata(BaseModel):
    """Provenance and lineage metadata for normalized records."""

    pipeline_version: str = Field(default="0.1.0", description="TrustLens pipeline version")
    schema_version: str = Field(default="1.0.0", description="Canonical schema definition version")
    source: str = Field(..., description="Original platform or ingestion channel")
    collected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Collection timestamp in UTC",
    )
    source_url: Optional[str] = Field(
        default=None, description="Source URL where listing was acquired"
    )
    ingestion_batch_id: Optional[str] = Field(
        default=None, description="Batch identifier if part of bulk ingestion"
    )
    extra: dict[str, Any] = Field(
        default_factory=dict, description="Additional provenance attributes"
    )


class CanonicalListing(BaseModel):
    """The canonical representation of a marketplace listing.

    Preserves raw inputs alongside normalized values to ensure no information loss.
    """

    listing_id: str = Field(
        default_factory=lambda: f"lst_{uuid4().hex[:12]}",
        description="Internal unique identifier for the listing",
    )
    case_id: str = Field(
        default_factory=lambda: f"case_{uuid4().hex[:12]}",
        description="Associated investigation case identifier",
    )
    source: str = Field(
        ..., description="Source origin (e.g. olx, user_submission, public_dataset)"
    )
    source_listing_id: Optional[str] = Field(
        default=None, description="Original listing ID from the source platform"
    )
    source_url: Optional[str] = Field(
        default=None, description="Direct URL of the listing if available"
    )

    # Title
    raw_title: str = Field(..., description="Original, unedited title text")
    normalized_title: Optional[str] = Field(default=None, description="Cleaned, standardized title")

    # Description
    raw_description: Optional[str] = Field(
        default=None, description="Original, unedited description text"
    )
    normalized_description: Optional[str] = Field(
        default=None, description="Cleaned, standardized description"
    )

    # Categorization
    category: str = Field(..., description="Canonical category (e.g. Smartphones, Gaming)")
    subcategory: Optional[str] = Field(
        default=None, description="Canonical subcategory (e.g. iPhone, PlayStation)"
    )
    brand: Optional[str] = Field(
        default=None, description="Extracted or declared brand (e.g. Apple, Sony)"
    )
    model: Optional[str] = Field(
        default=None,
        description="Extracted or declared model (e.g. iPhone 15 Pro, PS5 Disc Edition)",
    )

    # Pricing & Currency
    raw_price: Optional[float] = Field(
        default=None, description="Raw price as numeric value if parsed from raw string"
    )
    normalized_price: Optional[float] = Field(
        default=None, ge=0, description="Normalized numeric price in standard currency"
    )
    raw_currency: Optional[str] = Field(
        default=None, description="Raw currency symbol or code (e.g. ₹, Rs., INR, $)"
    )
    normalized_currency: Optional[str] = Field(
        default="INR", description="Standard 3-letter ISO currency code (default: INR)"
    )

    # Condition & Location
    condition: ItemCondition = Field(
        default=ItemCondition.UNKNOWN,
        description="Standardized item condition",
    )
    location_raw: Optional[str] = Field(
        default=None, description="Raw location string declared in listing"
    )
    location_city: Optional[str] = Field(default=None, description="Extracted or normalized city")
    location_state: Optional[str] = Field(
        default=None, description="Extracted or normalized state/region"
    )

    # Timestamps (always UTC timezone-aware)
    posted_at: Optional[datetime] = Field(
        default=None, description="When the listing was posted on the platform"
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="When the listing was last updated on the platform"
    )
    collected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when TrustLens collected this listing",
    )

    # Related entities
    seller: Optional[Seller] = Field(default=None, description="Attached seller profile and claims")
    media: list[Media] = Field(
        default_factory=list, description="Attached image/video media references"
    )

    # Claims & Lineage
    extracted_claims: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured claims (e.g. bill_available, box_available, warranty_months)",
    )
    collection_metadata: LineageMetadata = Field(
        ..., description="Full provenance and collection context"
    )
    is_synthetic: bool = Field(
        default=False, description="Flag indicating if this is mock/synthetic development data"
    )
