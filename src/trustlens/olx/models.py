"""
TrustLens — OLX Marketplace Models and Data Schemas (Phase 3).
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CollectionType(str, Enum):
    TARGETED = "targeted"
    BASELINE = "baseline"


class CollectionMethod(str, Enum):
    CRAWL4AI = "crawl4ai"
    HTTP_CLIENT = "http_client"
    BROWSER_EXTENSION = "browser_extension"
    RESEARCHER_ASSISTED = "researcher_assisted"


class ClaimStatus(str, Enum):
    REPORTED = "reported"
    OBSERVED = "observed"
    VERIFIED = "verified"
    CONTRADICTED = "contradicted"
    UNKNOWN = "unknown"


class SignalStatus(str, Enum):
    OBSERVED = "observed"
    REPORTED = "reported"
    VERIFIED = "verified"
    CONTRADICTED = "contradicted"
    UNKNOWN = "unknown"


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    CORROBORATED = "corroborated"
    CONTRADICTED = "contradicted"
    INCONCLUSIVE = "inconclusive"
    NOT_CHECKED = "not_checked"


class HumanReviewStatus(str, Enum):
    UNREVIEWED = "unreviewed"
    REVIEWED = "reviewed"
    CORRECTED = "corrected"
    REJECTED = "rejected"


class DiscoveryContext(BaseModel):
    investigation_id: str = Field(..., description="e.g. INV-001, INV-002, BASELINE")
    query: Optional[str] = None
    category: Optional[str] = None
    search_url: Optional[str] = None
    run_id: Optional[str] = None
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OLXProduct(BaseModel):
    category: str = "other"
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    variant: Optional[str] = None
    storage: Optional[str] = None
    ram: Optional[str] = None
    year: Optional[int] = None
    condition: Optional[str] = None
    color: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)


class OLXSeller(BaseModel):
    seller_id: Optional[str] = None
    display_name: Optional[str] = None
    profile_url: Optional[str] = None
    location: Optional[str] = None
    account_age: Optional[str] = None
    listing_count: Optional[int] = None
    seller_type: Optional[str] = None
    verification_badges: List[str] = Field(default_factory=list)
    business_claim: Optional[str] = None


class OLXClaim(BaseModel):
    claim_id: str
    claim_text: str
    source: str = "listing_description"
    status: ClaimStatus = ClaimStatus.REPORTED


class OLXMedia(BaseModel):
    media_id: str
    listing_id: str
    source_url: str
    local_path: Optional[str] = None
    media_type: str = "image"
    sha256: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    mime_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    download_status: str = "pending"
    collection_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OLXEvidence(BaseModel):
    evidence_id: str
    investigation_id: str
    source_type: str = "olx_listing"
    source_reference: str
    description: str
    evidence_text: Optional[str] = None
    related_media_id: Optional[str] = None
    claim_or_observation: str = "observation"
    relationship_to_claim: str = "supports"
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OLXSignal(BaseModel):
    signal_id: str
    investigation_id: str
    signal_type: str
    status: SignalStatus = SignalStatus.OBSERVED
    description: str
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: str = "medium"


class OLXVerificationCheck(BaseModel):
    check_id: str
    investigation_id: str
    check_type: str  # e.g. business_identity, invoice_authenticity, price_comparison
    target_claim: str
    external_observation: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.NOT_CHECKED
    notes: Optional[str] = None


class OLXCollectionMetadata(BaseModel):
    source: str = "olx"
    collection_method: CollectionMethod = CollectionMethod.HTTP_CLIENT
    discovered_via: str = "targeted_search"
    run_id: Optional[str] = None
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    collector_version: str = "0.3.0"


class OLXListing(BaseModel):
    listing_id: str
    source: str = "olx"
    source_listing_id: Optional[str] = None
    listing_url: str
    investigation_id: str = "INV-002"
    collection_type: CollectionType = CollectionType.TARGETED

    title: str
    description: str
    category: str = "other"
    subcategory: Optional[str] = None

    price: Optional[float] = None
    currency: str = "INR"
    location: Optional[str] = None

    posted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    product: OLXProduct = Field(default_factory=OLXProduct)
    seller: OLXSeller = Field(default_factory=OLXSeller)
    claims: List[OLXClaim] = Field(default_factory=list)
    media: List[OLXMedia] = Field(default_factory=list)
    contact_signals: List[str] = Field(default_factory=list)

    discovery_context: Optional[DiscoveryContext] = None
    collection_metadata: OLXCollectionMetadata = Field(default_factory=OLXCollectionMetadata)


class OLXCollectionRun(BaseModel):
    run_id: str
    investigation_id: str
    query: Optional[str] = None
    category: Optional[str] = None
    collection_type: CollectionType = CollectionType.TARGETED
    search_url: Optional[str] = None
    collection_method: CollectionMethod = CollectionMethod.HTTP_CLIENT
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    discovered_count: int = 0
    collected_count: int = 0
    failed_count: int = 0
    duplicate_count: int = 0
    listing_ids: List[str] = Field(default_factory=list)
    failure_reasons: List[Dict[str, str]] = Field(default_factory=list)


class OLXInvestigation(BaseModel):
    investigation_id: str
    source: str = "olx"
    listing: OLXListing
    seller: OLXSeller
    claims: List[OLXClaim] = Field(default_factory=list)
    media: List[OLXMedia] = Field(default_factory=list)
    signals: List[OLXSignal] = Field(default_factory=list)
    evidence: List[OLXEvidence] = Field(default_factory=list)
    verification_checks: List[OLXVerificationCheck] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    human_review_status: HumanReviewStatus = HumanReviewStatus.UNREVIEWED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
