"""Unit tests for Pydantic v2 schemas and validation logic."""

import pytest
from pydantic import ValidationError

from trustlens.ingestion.validators import ListingValidator
from trustlens.models.case import Case, CaseStatus
from trustlens.models.common import ItemCondition, MediaType, VerificationStatus
from trustlens.models.evidence import Evidence
from trustlens.models.listing import CanonicalListing, LineageMetadata
from trustlens.models.media import Media
from trustlens.models.seller import Seller


def test_valid_canonical_listing():
    """Verify CanonicalListing initializes with valid fields and generates defaults."""
    lineage = LineageMetadata(source="user_submission")
    listing = CanonicalListing(
        source="user_submission",
        raw_title="Apple iPhone 15 Pro",
        category="Smartphones",
        collection_metadata=lineage,
    )
    assert listing.listing_id.startswith("lst_")
    assert listing.case_id.startswith("case_")
    assert listing.raw_title == "Apple iPhone 15 Pro"
    assert listing.condition == ItemCondition.UNKNOWN
    assert listing.normalized_currency == "INR"
    assert listing.is_synthetic is False

    is_valid, errors = ListingValidator.validate_canonical(listing)
    assert is_valid is True
    assert len(errors) == 0


def test_missing_optional_fields():
    """Verify optional fields default to None or empty collections without errors."""
    lineage = LineageMetadata(source="test")
    listing = CanonicalListing(
        source="test",
        raw_title="Generic Item",
        category="Other",
        collection_metadata=lineage,
    )
    assert listing.raw_description is None
    assert listing.normalized_description is None
    assert listing.raw_price is None
    assert listing.normalized_price is None
    assert listing.seller is None
    assert listing.media == []


def test_invalid_negative_price():
    """Verify negative price is rejected by Pydantic schema validation."""
    lineage = LineageMetadata(source="test")
    with pytest.raises(ValidationError):
        CanonicalListing(
            source="test",
            raw_title="Invalid Price Item",
            category="Smartphones",
            normalized_price=-500.0,  # ge=0 constraint
            collection_metadata=lineage,
        )


def test_validator_raw_dict():
    """Test raw dictionary pre-validator."""
    # Valid dict
    valid, errors = ListingValidator.validate_raw_dict(
        {
            "source": "user_submission",
            "title": "Good Item",
            "price": "45000",
        }
    )
    assert valid is True

    # Missing title
    valid, errors = ListingValidator.validate_raw_dict(
        {
            "source": "user_submission",
            "price": "45000",
        }
    )
    assert valid is False
    assert any("title" in e for e in errors)

    # Missing source
    valid, errors = ListingValidator.validate_raw_dict(
        {
            "title": "Item Without Source",
        }
    )
    assert valid is False
    assert any("source" in e for e in errors)

    # Negative price
    valid, errors = ListingValidator.validate_raw_dict(
        {
            "source": "user_submission",
            "title": "Negative Price",
            "price": "-100",
        }
    )
    assert valid is False
    assert any("negative" in e.lower() for e in errors)


def test_seller_privacy_model():
    """Ensure Seller model hashes raw phone numbers and emails."""
    seller = Seller.from_raw(
        source="olx",
        display_name="John Doe",
        raw_phone="+91 9876543210",
        raw_email="john.doe@example.com",
    )
    assert seller.display_name == "John Doe"
    assert seller.phone_present is True
    assert seller.phone_hash is not None
    assert "+91 9876543210" not in seller.model_dump_json()
    assert "john.doe@example.com" not in seller.model_dump_json()
    assert seller.email_present is True


def test_media_model_defaults():
    """Verify Media schema instantiation."""
    m = Media(
        source_url="https://example.com/pic.jpg",
        media_type=MediaType.IMAGE,
        sha256="abc123sha",
    )
    assert m.media_id.startswith("med_")
    assert m.media_type == MediaType.IMAGE
    assert m.sha256 == "abc123sha"


def test_evidence_and_case_model():
    """Verify Evidence and Case schemas."""
    case = Case(
        source="user_submission",
        status=CaseStatus.NEW,
        labels=["suspected_duplicate"],
    )
    assert case.case_id.startswith("case_")
    assert case.status == CaseStatus.NEW

    evidence = Evidence(
        case_id=case.case_id,
        source_type="web",
        source_name="Official Catalog",
        claim="Original MSRP is 50000",
        evidence_text="Manufacturer listed MSRP: Rs 50,000",
        verification_status=VerificationStatus.CORROBORATED,
        confidence=0.95,
    )
    assert evidence.case_id == case.case_id
    assert evidence.verification_status == VerificationStatus.CORROBORATED
    assert evidence.confidence == 0.95
