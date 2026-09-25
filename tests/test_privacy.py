"""Unit tests for privacy protections and deterministic HMAC-SHA256 hashing."""

from trustlens.models.seller import Seller
from trustlens.utils.privacy import hash_identifier, mask_string


def test_hash_deterministic_consistency():
    """Verify same phone number formatted differently yields the exact same hash."""
    h1 = hash_identifier("+91 9876543210", salt="test_salt")
    h2 = hash_identifier("9876543210", salt="test_salt")
    h3 = hash_identifier("+91-98765-43210", salt="test_salt")

    assert h1 is not None
    assert h1 == h2 == h3


def test_hash_different_salts():
    """Verify different salts produce different hashes."""
    h1 = hash_identifier("9876543210", salt="salt_a")
    h2 = hash_identifier("9876543210", salt="salt_b")
    assert h1 != h2


def test_hash_empty_or_none():
    """Verify empty or None inputs return None."""
    assert hash_identifier(None) is None
    assert hash_identifier("") is None
    assert hash_identifier("   ") is None


def test_seller_never_exposes_raw_pii():
    """Ensure raw phone numbers and emails are completely absent from serialization."""
    phone = "+91 98765 11223"
    email = "secret.seller@domain.com"

    seller = Seller.from_raw(
        source="test",
        display_name="Private Seller",
        raw_phone=phone,
        raw_email=email,
    )

    dumped = seller.model_dump_json()

    # Raw phone and email should not appear anywhere in dumped json
    assert phone not in dumped
    assert "9876511223" not in dumped
    assert email not in dumped
    assert "secret.seller" not in dumped

    # Presence flags and hashes must exist
    assert seller.phone_present is True
    assert seller.email_present is True
    assert seller.phone_hash is not None
    assert seller.email_hash is not None


def test_mask_string():
    """Test UI/Log string masking utility."""
    assert mask_string("9876543210", visible_chars=2) == "98******10"
    assert mask_string("abc", visible_chars=2) == "***"
    assert mask_string(None) == "[NOT PROVIDED]"
