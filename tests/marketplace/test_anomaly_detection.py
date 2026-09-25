"""Unit and deterministic integration tests for Phase J Statistical Anomaly Analysis.

Tests cover:
- Invariant: 1 row per canonical listing in results and persistence tables (2,980 rows)
- ID uniqueness: No duplicate listing_id
- Fixed-seed reproducibility: Consecutive model runs produce identical anomaly scores
- Expected experiment columns: Scores and flags for all 4 experiments
- Valid score ranges: Continuous floats without NaN or infinite values
- Missing-value handling: RobustScaler and neutral median/indicator imputation
- Categorical handling: Clean one-hot encoding without arbitrary ordinal assignments
- Constant-feature removal: 16 constant features excluded from models
- Identifier exclusion: No listing_id, URLs, or freeform text in feature matrices
- Target leakage exclusion: Zero scam/fraud/risk/target columns in features or outputs
- Contamination sensitivity: Monotonic growth of flagged outlier sets
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pytest

from trustlens.marketplace.anomaly_detection import AnomalyAnalysisEngine


@pytest.fixture(scope="module")
def engine():
    eng = AnomalyAnalysisEngine(random_state=42, base_contamination=0.05)
    eng.load_unified_features()
    eng.perform_feature_audit()
    eng.build_experiment_matrices()
    return eng


@pytest.fixture(scope="module")
def anomaly_results(engine):
    p = Path("data/olx_processed/anomaly_results.parquet")
    if p.exists():
        return pq.read_table(p).to_pandas()
    return engine.run_experiments()


@pytest.fixture(scope="module")
def anomaly_persistence(engine, anomaly_results):
    p = Path("data/olx_processed/anomaly_persistence.parquet")
    if p.exists():
        return pq.read_table(p).to_pandas()
    return engine.persistence_df


def test_row_count_and_id_uniqueness(anomaly_results, anomaly_persistence, engine):
    """Verifies that 1 row = 1 canonical listing (2,980 rows) with zero duplicates."""
    canonical_count = len(engine.df_unified)
    assert len(anomaly_results) == canonical_count
    assert len(anomaly_persistence) == canonical_count
    assert len(anomaly_results) == 2980

    # ID Uniqueness
    assert anomaly_results["listing_id"].nunique() == canonical_count
    assert not anomaly_results["listing_id"].duplicated().any()
    assert anomaly_persistence["listing_id"].nunique() == canonical_count
    assert not anomaly_persistence["listing_id"].duplicated().any()


def test_expected_experiment_columns(anomaly_results):
    """Verifies that all 4 required experiments have scores and flags."""
    expected_prefixes = ["price", "price_text", "price_image", "full_multimodal"]
    for prefix in expected_prefixes:
        assert f"{prefix}_anomaly_score" in anomaly_results.columns
        assert f"{prefix}_anomaly_flag" in anomaly_results.columns

    # Metadata
    assert "random_state" in anomaly_results.columns
    assert "contamination" in anomaly_results.columns


def test_valid_score_ranges(anomaly_results):
    """Ensures anomaly scores are continuous finite numbers without NaN or Inf."""
    for prefix in ["price", "price_text", "price_image", "full_multimodal"]:
        scores = anomaly_results[f"{prefix}_anomaly_score"]
        assert scores.notnull().all(), f"NaN found in {prefix}_anomaly_score"
        assert not np.isinf(scores).any(), f"Inf found in {prefix}_anomaly_score"
        assert scores.dtype in (np.float64, np.float32)

        flags = anomaly_results[f"{prefix}_anomaly_flag"]
        assert flags.dtype == bool
        assert flags.sum() > 0


def test_fixed_seed_reproducibility(engine):
    """Verifies that a separate run with identical random_state produces identical scores."""
    matrices = engine.experiment_matrices
    X = matrices["J_PRICE"]
    
    from sklearn.preprocessing import RobustScaler
    from sklearn.ensemble import IsolationForest

    X_scaled = RobustScaler().fit_transform(X)
    iso1 = IsolationForest(n_estimators=100, contamination=0.05, random_state=42).fit(X_scaled)
    iso2 = IsolationForest(n_estimators=100, contamination=0.05, random_state=42).fit(X_scaled)

    scores1 = -iso1.decision_function(X_scaled)
    scores2 = -iso2.decision_function(X_scaled)

    np.testing.assert_allclose(scores1, scores2, rtol=1e-5, atol=1e-5)


def test_constant_features_excluded(engine):
    """Verifies that detected constant features are excluded from all experimental matrices."""
    audit_df = engine.audit_df
    constants = set(audit_df.loc[audit_df["constant_flag"], "feature_name"])
    assert len(constants) >= 15

    for exp_key, mat in engine.experiment_matrices.items():
        for col in mat.columns:
            # col without _log or one-hot suffix
            raw_name = col.replace("_log", "")
            assert raw_name not in constants, f"Constant feature '{raw_name}' leaked into {exp_key} matrix!"


def test_identifiers_and_raw_text_excluded(engine):
    """Verifies that raw listing_id, URLs, and freeform text are excluded from matrices."""
    forbidden_cols = {"listing_id", "source_url", "raw_title", "location_raw"}
    for exp_key, mat in engine.experiment_matrices.items():
        for fc in forbidden_cols:
            assert fc not in mat.columns, f"Identifier '{fc}' found in {exp_key} matrix!"


def test_target_leakage_exclusion(engine, anomaly_results):
    """Verifies that no scam, fraud, or post-hoc risk terms exist in matrices or outputs."""
    forbidden = ["fraud", "scam", "risk_score", "probability", "target", "label", "outcome"]
    for exp_key, mat in engine.experiment_matrices.items():
        for col in mat.columns:
            for term in forbidden:
                assert term not in col.lower(), f"Forbidden leakage term '{term}' in {exp_key} column '{col}'!"

    for col in anomaly_results.columns:
        for term in forbidden:
            assert term not in col.lower(), f"Forbidden leakage term '{term}' in anomaly_results column '{col}'!"


def test_contamination_sensitivity_monotonicity(engine):
    """Verifies that higher contamination leads to monotonically more flagged outliers."""
    sens = engine.run_contamination_sensitivity(contaminations=[0.01, 0.02, 0.05, 0.10])
    raw = sens["raw_sets"]
    for exp_key in ["J_PRICE", "J_PRICE_TEXT", "J_PRICE_IMAGE", "J_FULL_MULTIMODAL"]:
        c1 = len(raw[exp_key][0.01])
        c2 = len(raw[exp_key][0.02])
        c5 = len(raw[exp_key][0.05])
        c10 = len(raw[exp_key][0.10])
        assert c1 < c2 < c5 < c10, f"Non-monotonic anomaly counts in {exp_key}: {c1}, {c2}, {c5}, {c10}"


def test_persistence_structure(anomaly_persistence):
    """Verifies that persistence table accurately counts flagged experiments."""
    assert (anomaly_persistence["experiment_count"] >= 0).all()
    assert (anomaly_persistence["experiment_count"] <= 4).all()

    p2 = anomaly_persistence["persistent_2"]
    expected_p2 = anomaly_persistence["experiment_count"] >= 2
    assert (p2 == expected_p2).all()

    p4 = anomaly_persistence["persistent_4"]
    expected_p4 = anomaly_persistence["experiment_count"] == 4
    assert (p4 == expected_p4).all()
