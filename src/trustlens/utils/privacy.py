"""Privacy and anonymization utilities for TrustLens.

Ensures sensitive seller information (phone numbers, email addresses) is
never stored in plaintext or leaked in logs.
"""

import hashlib
import hmac
import re
from typing import Optional

from trustlens.config.settings import settings


def hash_identifier(value: Optional[str], salt: Optional[str] = None) -> Optional[str]:
    """Compute deterministic HMAC-SHA256 hash of an identifier using secret salt.

    Normalizes phone numbers (digits only) and email addresses (lowercased)
    before hashing.
    """
    if not value or not value.strip():
        return None

    secret_salt = (salt or settings.hash_salt).encode("utf-8")
    cleaned = value.strip().lower()

    # If it looks like a phone number, retain digits and standardize to last 10 digits (national number)
    if re.fullmatch(r"[\d\+\-\s\(\)]+", cleaned):
        digits = re.sub(r"\D", "", cleaned)
        if len(digits) >= 10:
            cleaned = digits[-10:]
        elif len(digits) >= 7:
            cleaned = digits

    return hmac.new(secret_salt, cleaned.encode("utf-8"), hashlib.sha256).hexdigest()


def mask_string(val: Optional[str], visible_chars: int = 2) -> str:
    """Mask a string for logging or UI preview, e.g. +91 98****12 or j***@example.com."""
    if not val:
        return "[NOT PROVIDED]"
    if len(val) <= visible_chars * 2:
        return "*" * len(val)
    return f"{val[:visible_chars]}{'*' * (len(val) - visible_chars * 2)}{val[-visible_chars:]}"
