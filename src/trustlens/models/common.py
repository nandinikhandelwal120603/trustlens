"""Common enumerations and types used across TrustLens models."""

from enum import Enum


class ItemCondition(str, Enum):
    """Normalized condition categories for marketplace listings."""

    NEW = "new"
    LIKE_NEW = "like_new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"


class MediaType(str, Enum):
    """Type of media asset."""

    IMAGE = "image"
    VIDEO = "video"


class CaseStatus(str, Enum):
    """Investigation case lifecycle states."""

    NEW = "new"
    COLLECTING = "collecting"
    PROCESSING = "processing"
    REVIEW = "review"
    LABELED = "labeled"
    COMPLETED = "completed"


class VerificationStatus(str, Enum):
    """Evidence verification status."""

    UNVERIFIED = "unverified"
    CORROBORATED = "corroborated"
    CONTRADICTED = "contradicted"
    INCONCLUSIVE = "inconclusive"


class DuplicateType(str, Enum):
    """Type of duplicate detected."""

    EXACT = "exact"
    NEAR = "near"
