"""Unit and integration tests for Phase F Text Normalization & Lexical Linguistics."""

from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
import pytest

from trustlens.marketplace.text_intelligence import TextIntelligenceEngine


def test_text_normalization_preserving_specs():
    """Verify Unicode NFKC normalization, spec retention, and whitespace handling."""
    raw = "   Apple \u201ciPhone 15 Pro Max\u201d  256GB   (Brand New) \u2014 \u20b985,000   "
    raw_out, norm_out, red_out = TextIntelligenceEngine.normalize_listing_text(raw)

    assert "iphone 15 pro max" in norm_out
    assert "256gb" in norm_out
    assert "85 000" in norm_out or "85000" in norm_out


def test_tokenization_preserving_specs():
    """Verify that numbers, models, GB storage, and currencies are preserved as tokens."""
    norm = "apple iphone 15 pro max 256gb 5g ₹85000 sealed pack"
    tokens = TextIntelligenceEngine.tokenize_preserving_specs(norm)

    assert "iphone" in tokens
    assert "15" in tokens
    assert "256gb" in tokens
    assert "sealed" in tokens


def test_lexicon_feature_extraction():
    """Verify deterministic extraction of controlled marketplace lexicons."""
    norm = "urgent sale iphone 13 128gb sealed box pack with bill in mint condition call on whatsapp"
    tokens = TextIntelligenceEngine.tokenize_preserving_specs(norm)
    feats = TextIntelligenceEngine.extract_lexicon_features(tokens, norm)

    assert feats["has_urgency"] is True
    assert feats["has_contact_redirection"] is True
    assert feats["has_warranty_authenticity"] is True
    assert feats["has_condition_lexicon"] is True
    assert feats["has_delivery_logistics"] is False


def test_script_detection():
    """Verify script classification between Latin, Devanagari, and mixed scripts."""
    latin = "Apple iPhone 15 Pro Max"
    devanagari = "आईफोन १५ प्रो"
    mixed = "Apple iPhone १५"

    assert TextIntelligenceEngine.detect_script(latin) == "latin_english"
    assert TextIntelligenceEngine.detect_script(devanagari) == "devanagari"
    assert TextIntelligenceEngine.detect_script(mixed) == "mixed_latin_devanagari"


def test_text_reuse_detection():
    """Verify detection of exact title duplicates and Jaccard near-duplicate candidates."""
    engine = TextIntelligenceEngine()

    df_sample = pd.DataFrame([
        {
            "listing_id": "LST-001",
            "title_text_raw": "Apple iPhone 15 Pro Max 256GB Natural Titanium",
            "title_text_normalized": "apple iphone 15 pro max 256gb natural titanium",
            "tokens": ["apple", "iphone", "15", "pro", "max", "256gb", "natural", "titanium"],
            "search_query": "iphone",
        },
        {
            "listing_id": "LST-002",
            "title_text_raw": "Apple iPhone 15 Pro Max 256GB Natural Titanium",
            "title_text_normalized": "apple iphone 15 pro max 256gb natural titanium",
            "tokens": ["apple", "iphone", "15", "pro", "max", "256gb", "natural", "titanium"],
            "search_query": "iphone",
        },
        {
            "listing_id": "LST-003",
            "title_text_raw": "Apple iPhone 15 Pro Max 256GB Blue Titanium",
            "title_text_normalized": "apple iphone 15 pro max 256gb blue titanium",
            "tokens": ["apple", "iphone", "15", "pro", "max", "256gb", "blue", "titanium"],
            "search_query": "iphone",
        },
    ])

    df_reuse = engine.detect_text_reuse_candidates(df_sample, jaccard_threshold=0.75)

    assert len(df_reuse) >= 2
    types = df_reuse["candidate_type"].tolist()
    assert "EXACT_TITLE_REUSE" in types
    assert "HIGH_TEXT_OVERLAP" in types
    for _, r in df_reuse.iterrows():
        assert r["verification_status"] == "UNVERIFIED_CANDIDATE"
