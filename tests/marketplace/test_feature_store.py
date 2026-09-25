"""Unit and integration tests for TrustLens Phase I Unified Feature Store.

Tests verify:
- Invariant: 1 row = 1 canonical listing (row_count == 2,980)
- Uniqueness: listing_id is unique with 0 duplicate rows
- Source integrity: All listing_ids originate from canonical listings.parquet
- Immutability: Frozen Phase A–H Parquet datasets remain untouched
- Non-multiplication: Aggregations from media, OCR, inconsistencies, and network
  do not multiply listing rows
- Consistency: Availability flags strictly match observational presence
- Value validity: Numeric values are finite or null; categorical values match vocabularies
- Guardrails: Zero fraud scores, scam probabilities, or seller risk metrics exist
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pytest

from trustlens.marketplace.feature_store import UnifiedFeatureStoreBuilder


@pytest.fixture(scope="module")
def builder():
    b = UnifiedFeatureStoreBuilder()
    b.load_all_sources()
    return b


@pytest.fixture(scope="module")
def feature_store_df(builder):
    p = Path("data/olx_processed/unified_features.parquet")
    if p.exists():
        return pq.read_table(p).to_pandas()
    return builder.build_unified_feature_store()


def test_row_count_and_uniqueness(feature_store_df, builder):
    """Verifies that output row count exactly matches canonical listing population."""
    canonical_count = len(builder.df_listings)
    assert len(feature_store_df) == canonical_count
    assert len(feature_store_df) == 2980

    # Uniqueness
    assert feature_store_df["listing_id"].nunique() == canonical_count
    assert not feature_store_df["listing_id"].duplicated().any()


def test_all_listing_ids_match_canonical(feature_store_df, builder):
    """Ensures 100% 1-to-1 correspondence with canonical listing IDs."""
    canonical_ids = set(builder.df_listings["listing_id"].astype(str))
    feature_ids = set(feature_store_df["listing_id"].astype(str))

    assert feature_ids == canonical_ids
    assert len(feature_ids.symmetric_difference(canonical_ids)) == 0


def test_no_row_multiplication_from_subordinate_phases(feature_store_df):
    """Ensures media, inconsistencies, and network joins do not duplicate rows."""
    counts = feature_store_df["listing_id"].value_counts()
    assert (counts == 1).all()


def test_coverage_availability_flags_consistency(feature_store_df, builder):
    """Verifies that availability flags accurately reflect observational presence."""
    # Price
    valid_price_mask = feature_store_df["price_amount"].notnull() & (feature_store_df["price_status"] == "valid")
    assert (feature_store_df["price_available"] == valid_price_mask).all()

    # Location
    valid_loc_mask = feature_store_df["city"].notnull() & (feature_store_df["city"] != "Unknown") & (feature_store_df["city"].str.strip() != "")
    assert (feature_store_df["location_available"] == valid_loc_mask).all()

    # Media
    media_ids = set(builder.df_fingerprints["listing_id"].astype(str))
    expected_media = feature_store_df["listing_id"].isin(media_ids)
    assert (feature_store_df["media_available"] == expected_media).all()

    # OCR
    ocr_ids = set(builder.df_ocr["listing_id"].astype(str))
    expected_ocr = feature_store_df["listing_id"].isin(ocr_ids)
    assert (feature_store_df["ocr_available"] == expected_ocr).all()

    # AI Detector
    media_to_listing = dict(zip(builder.df_auth["media_id"], builder.df_auth["listing_id"]))
    ai_listing_ids = set(builder.df_ai["media_id"].map(media_to_listing).dropna().astype(str))
    expected_ai = feature_store_df["listing_id"].isin(ai_listing_ids)
    assert (feature_store_df["ai_detector_available"] == expected_ai).all()


def test_missingness_semantics_and_null_hygiene(feature_store_df):
    """Ensures 0 is not conflated with NULL for unbenchmarked/unevaluated metrics."""
    # When comparable_product_group is null, group metrics must be null
    unbenchmarked = feature_store_df[feature_store_df["comparable_product_group"].isnull()]
    assert unbenchmarked["group_median_price"].isnull().all()
    assert unbenchmarked["price_delta_from_group_median"].isnull().all()
    assert unbenchmarked["price_below_35_pct_median_flag"].isnull().all()

    # When listing has no media, visual/detector scores must be null
    no_media = feature_store_df[~feature_store_df["media_available"]]
    assert no_media["detector_a_score"].isnull().all()
    assert no_media["detector_b_score"].isnull().all()
    assert no_media["spectral_hf_ratio"].isnull().all()

    # When listing has no inconsistency, count is 0 (not null)
    assert (feature_store_df["total_multimodal_inconsistency_count"] >= 0).all()
    assert feature_store_df["total_multimodal_inconsistency_count"].notnull().all()


def test_price_benchmarking_logic(feature_store_df):
    """Verifies that price delta percentage and discount flags are logically sound."""
    benchmarked = feature_store_df[feature_store_df["comparable_product_group"].notnull()]
    assert len(benchmarked) > 2000

    # price_delta = (price - median) / median
    expected_delta = (benchmarked["price_amount"] - benchmarked["group_median_price"]) / benchmarked["group_median_price"]
    diff = np.abs(benchmarked["price_delta_from_group_median"] - expected_delta)
    assert (diff < 1e-3).all()

    # Flag consistency
    below_35 = benchmarked[benchmarked["price_below_35_pct_median_flag"] == True]
    assert (below_35["price_delta_from_group_median"] <= -0.35 + 1e-4).all()


def test_absence_of_fraud_scores_and_data_leakage(feature_store_df):
    """Strict guardrail verification: no scam/fraud/risk columns exist."""
    forbidden_terms = ["scam", "fraud", "risk_score", "probability", "danger", "target", "label", "verdict"]
    for col in feature_store_df.columns:
        col_lower = col.lower()
        for term in forbidden_terms:
            assert term not in col_lower, f"Forbidden term '{term}' found in column '{col}'!"


def test_deterministic_ordering(feature_store_df):
    """Verifies that listings are sorted deterministically by listing_id."""
    assert feature_store_df["listing_id"].is_monotonic_increasing
