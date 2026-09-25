"""Seller entity schema with strict privacy protections."""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from trustlens.utils.privacy import hash_identifier


class Seller(BaseModel):
    """Privacy-conscious seller model.

    Raw phone numbers and email addresses are NEVER stored. Only presence flags
    and salted HMAC-SHA256 hashes are retained for duplicate/cluster detection.
    """

    seller_id: str = Field(
        default_factory=lambda: f"sel_{uuid4().hex[:12]}",
        description="Internal unique seller identifier",
    )
    source: str = Field(..., description="Source platform or dataset")
    source_seller_id: Optional[str] = Field(
        default=None, description="Platform-native seller identifier"
    )
    display_name: Optional[str] = Field(
        default=None, description="Public display name on the platform"
    )
    account_age: Optional[str] = Field(
        default=None, description="Human readable or raw account age string"
    )
    profile_location: Optional[str] = Field(
        default=None, description="Location declared on seller profile"
    )
    verification_status: Optional[str] = Field(
        default="unverified",
        description="Platform verification status, e.g. verified, unverified",
    )
    seller_type: Optional[str] = Field(
        default="individual",
        description="Type of seller: individual, business, or unknown",
    )
    listing_count: Optional[int] = Field(
        default=None, ge=0, description="Total active or lifetime listings count"
    )
    business_name_claim: Optional[str] = Field(
        default=None, description="Claimed registered business name"
    )
    gstin_claim: Optional[str] = Field(
        default=None, description="Claimed GSTIN tax registration number"
    )

    # Privacy protections: boolean flags + salted hashes
    phone_present: bool = Field(
        default=False, description="Whether a phone number was found/provided"
    )
    phone_hash: Optional[str] = Field(
        default=None, description="HMAC-SHA256 salted hash of phone number (never raw)"
    )
    email_present: bool = Field(
        default=False, description="Whether an email address was found/provided"
    )
    email_hash: Optional[str] = Field(
        default=None, description="HMAC-SHA256 salted hash of email (never raw)"
    )
    website_claim: Optional[str] = Field(
        default=None, description="Claimed external website or social link"
    )
    collected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when seller info was collected",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional non-PII platform metadata"
    )

    @classmethod
    def from_raw(
        cls,
        source: str,
        display_name: Optional[str] = None,
        source_seller_id: Optional[str] = None,
        raw_phone: Optional[str] = None,
        raw_email: Optional[str] = None,
        account_age: Optional[str] = None,
        profile_location: Optional[str] = None,
        verification_status: Optional[str] = None,
        seller_type: Optional[str] = "individual",
        listing_count: Optional[int] = None,
        business_name_claim: Optional[str] = None,
        gstin_claim: Optional[str] = None,
        website_claim: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "Seller":
        """Factory method to construct a Seller, securely hashing any raw PII."""
        phone_present = bool(raw_phone and raw_phone.strip())
        phone_hash = hash_identifier(raw_phone) if phone_present else None

        email_present = bool(raw_email and raw_email.strip())
        email_hash = hash_identifier(raw_email) if email_present else None

        return cls(
            source=source,
            source_seller_id=source_seller_id,
            display_name=display_name,
            account_age=account_age,
            profile_location=profile_location,
            verification_status=verification_status or "unverified",
            seller_type=seller_type,
            listing_count=listing_count,
            business_name_claim=business_name_claim,
            gstin_claim=gstin_claim,
            phone_present=phone_present,
            phone_hash=phone_hash,
            email_present=email_present,
            email_hash=email_hash,
            website_claim=website_claim,
            metadata=metadata or {},
        )
