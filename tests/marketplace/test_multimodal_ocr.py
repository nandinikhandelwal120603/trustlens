"""Unit and integration tests for Phase E Multimodal OCR & Observational Inconsistencies."""

from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
import pytest

from trustlens.marketplace.multimodal_ocr import MultimodalOCREngine
from trustlens.marketplace.pii_redactor import PIIRedactor


def test_pii_redactor_deterministic():
    """Verify deterministic redaction of phone numbers, emails, UPI IDs, and IMEIs."""
    sample = "Call me at +91 9876543210 or 98765 43210 or email test.user@example.com. UPI: payuser@okhdfcbank, IMEI: 352099001761482"
    redacted = PIIRedactor.redact_text(sample)

    assert "+91 9876543210" not in redacted
    assert "test.user@example.com" not in redacted
    assert "payuser@okhdfcbank" not in redacted
    assert "352099001761482" not in redacted

    assert "[PHONE_REDACTED]" in redacted
    assert "[EMAIL_REDACTED]" in redacted
    assert "[UPI_REDACTED]" in redacted
    assert "[IMEI_REDACTED]" in redacted


def test_ocr_text_normalization():
    """Verify deterministic Unicode NFKC normalization and whitespace cleanup."""
    raw = "   Apple   \u201ciPhone 15 Pro\u201d   \n\n  256 GB   "
    norm = MultimodalOCREngine.normalize_ocr_text(raw)
    assert norm == "apple \"iphone 15 pro\" 256 gb" or "apple iphone 15 pro 256 gb" in norm


def test_extract_visual_technical_specs():
    """Verify extraction of model, storage, chip, and condition/demo cues from OCR text."""
    text_iphone = "iPhone 15 Pro Max 256GB sealed pack"
    norm_iphone = MultimodalOCREngine.normalize_ocr_text(text_iphone)
    specs = MultimodalOCREngine.extract_visual_technical_specs(text_iphone, norm_iphone)

    assert "iPhone 15 Pro Max" in specs["observed_models"]
    assert "256GB" in specs["observed_storages"]
    assert "Sealed" in specs["observed_conditions"]

    text_macbook = "MacBook Air M2 512GB Demo Unit"
    norm_macbook = MultimodalOCREngine.normalize_ocr_text(text_macbook)
    specs_mb = MultimodalOCREngine.extract_visual_technical_specs(text_macbook, norm_macbook)

    assert any("MacBook Air" in m for m in specs_mb["observed_models"])
    assert "512GB" in specs_mb["observed_storages"]
    assert "M2" in specs_mb["observed_chips"]
    assert "DEMO UNIT" in specs_mb["observed_demo_cues"]


def test_inconsistency_detection_model_and_storage_mismatch():
    """Verify that contradictory model and storage claims produce unverified candidates."""
    engine = MultimodalOCREngine()

    df_ocr = pd.DataFrame([
        {
            "media_id": "MED-001",
            "listing_id": "LST-001",
            "file_id": "FILE-001",
            "ocr_status": "success_text",
            "ocr_text_raw": "iPhone 11 64GB",
            "ocr_text_normalized": "iphone 11 64gb",
            "ocr_text_redacted": "iphone 11 64gb",
            "ocr_mean_confidence": 85.0,
            "confidence_band": "high",
            "observed_models": ["iPhone 11"],
            "observed_storages": ["64GB"],
            "observed_chips": [],
            "observed_demo_cues": [],
            "observed_conditions": [],
        }
    ])

    df_listings = pd.DataFrame([
        {
            "listing_id": "LST-001",
            "raw_title": "Apple iPhone 15 Pro Max 256GB Natural Titanium",
            "normalized_title": "apple iphone 15 pro max 256gb natural titanium",
            "model": "iPhone 15 Pro Max",
            "product_family": "iPhone",
            "storage": "256GB",
            "price_numeric": 95000.0,
        }
    ])

    df_inc = engine.analyze_multimodal_inconsistencies(df_ocr, df_listings, pd.DataFrame(), pd.DataFrame())

    assert len(df_inc) == 2
    types = df_inc["inconsistency_type"].tolist()
    assert "TEXT_IMAGE_MODEL_MISMATCH" in types
    assert "TEXT_IMAGE_STORAGE_MISMATCH" in types

    for _, r in df_inc.iterrows():
        assert r["verification_status"] == "UNVERIFIED_CANDIDATE"


def test_shared_image_claim_drift_and_price_variance():
    """Verify that listings sharing visual assets with divergent models/prices produce drift candidates."""
    engine = MultimodalOCREngine()

    df_ocr = pd.DataFrame()
    df_listings = pd.DataFrame([
        {
            "listing_id": "LST-A",
            "raw_title": "iPhone 15 Pro 128GB",
            "model": "iPhone 15 Pro",
            "product_family": "iPhone",
            "storage": "128GB",
            "price_numeric": 80000.0,
        },
        {
            "listing_id": "LST-B",
            "raw_title": "iPhone 13 128GB",
            "model": "iPhone 13",
            "product_family": "iPhone",
            "storage": "128GB",
            "price_numeric": 35000.0,
        },
    ])

    df_rel_c = pd.DataFrame([
        {
            "relationship_id": "REL-01",
            "listing_a_id": "LST-A",
            "listing_b_id": "LST-B",
            "media_a_id": "MED-A",
            "media_b_id": "MED-B",
            "sha_equality": True,
        }
    ])

    df_inc = engine.analyze_multimodal_inconsistencies(df_ocr, df_listings, df_rel_c, pd.DataFrame())

    assert len(df_inc) >= 2
    types = df_inc["inconsistency_type"].tolist()
    assert "SHARED_IMAGE_CLAIM_DRIFT" in types
    assert "SHARED_IMAGE_PRICE_VARIANCE" in types
