"""TrustLens Marketplace Intelligence — Redaction Utilities for PII & Sensitive Information."""

import re
from typing import Optional


class PIIRedactor:
    """Deterministic redactor for contact numbers, emails, UPI IDs, and device serials."""

    # Phone numbers: 10-digit Indian mobile numbers, formatted with +91, 0, or spaces/dashes
    PHONE_REGEX = re.compile(
        r"(?:\+?91[-.\s]*)?[6-9]\d{9}\b|(?:\+?91[-.\s]*)?\d{5}[-.\s]*\d{5}\b",
        re.IGNORECASE,
    )

    # Email addresses
    EMAIL_REGEX = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        re.IGNORECASE,
    )

    # UPI IDs (e.g. name@okhdfcbank, user@paytm, 9876543210@ybl)
    UPI_REGEX = re.compile(
        r"\b[a-zA-Z0-9.\-_]{2,256}@(okhdfcbank|okaxis|oksbi|okicici|paytm|ybl|ibl|axl|apl|upi)\b",
        re.IGNORECASE,
    )

    # IMEI numbers (15 digits)
    IMEI_REGEX = re.compile(
        r"\b(?:\d{2}[-\s]?\d{6}[-\s]?\d{6}[-\s]?\d{1}|\d{15})\b"
    )

    # Generic long numeric identifiers (credit cards, bank accounts, Aadhaar-like 12-16 digits)
    LONG_NUM_REGEX = re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}(?:[-\s]?\d{4})?\b")

    @classmethod
    def redact_text(cls, text: Optional[str]) -> str:
        """Deterministically redact sensitive PII patterns from text."""
        if not text:
            return ""

        redacted = text
        # Redact emails first
        redacted = cls.EMAIL_REGEX.sub("[EMAIL_REDACTED]", redacted)
        # Redact UPI IDs
        redacted = cls.UPI_REGEX.sub("[UPI_REDACTED]", redacted)
        # Redact IMEIs (15 digits) before 10-digit phone numbers
        redacted = cls.IMEI_REGEX.sub("[IMEI_REDACTED]", redacted)
        # Redact generic long numeric IDs (12-16 digits)
        redacted = cls.LONG_NUM_REGEX.sub("[NUMERIC_ID_REDACTED]", redacted)
        # Redact phone numbers (10 digits)
        redacted = cls.PHONE_REGEX.sub("[PHONE_REDACTED]", redacted)

        return redacted

    @classmethod
    def mask_phone_for_preview(cls, phone_str: Optional[str]) -> str:
        """Mask phone for UI preview while preserving last 2 digits."""
        if not phone_str:
            return ""
        digits = re.sub(r"\D", "", phone_str)
        if len(digits) >= 10:
            return f"+91 {digits[:2]}******{digits[-2:]}"
        return "[PHONE_REDACTED]"
