"""Unit tests for TrustLens Phase G.1 AI Image Detection Pipeline."""

import os
from pathlib import Path
import pytest
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from trustlens.marketplace.ai_image_detector import AIImageDetectorPipeline


def test_classify_score_logic():
    """Validates raw score classification thresholds without fake probability conversions."""
    pipeline = AIImageDetectorPipeline()

    assert pipeline.classify_score(0.95) == "AI_GENERATION_CANDIDATE"
    assert pipeline.classify_score(0.70) == "AI_GENERATION_CANDIDATE"
    assert pipeline.classify_score(0.69) == "BORDERLINE"
    assert pipeline.classify_score(0.31) == "BORDERLINE"
    assert pipeline.classify_score(0.30) == "REAL_IMAGE_CANDIDATE"
    assert pipeline.classify_score(0.05) == "REAL_IMAGE_CANDIDATE"
    assert pipeline.classify_score(None) == "UNREADABLE"
    assert pipeline.classify_score(np.nan) == "UNREADABLE"


def test_determine_agreement_logic():
    """Tests transparent agreement and assessment status resolution."""
    pipeline = AIImageDetectorPipeline()

    # Both AI
    agr, status = pipeline.determine_agreement("AI_GENERATION_CANDIDATE", "AI_GENERATION_CANDIDATE")
    assert agr == "AGREEMENT_AI"
    assert status == "AI_GENERATION_CANDIDATE"

    # Both Real
    agr, status = pipeline.determine_agreement("REAL_IMAGE_CANDIDATE", "REAL_IMAGE_CANDIDATE")
    assert agr == "AGREEMENT_REAL"
    assert status == "REAL_IMAGE_CANDIDATE"

    # Disagreement
    agr, status = pipeline.determine_agreement("AI_GENERATION_CANDIDATE", "REAL_IMAGE_CANDIDATE")
    assert agr == "DETECTOR_DISAGREEMENT"
    assert status == "DETECTOR_DISAGREEMENT"

    agr, status = pipeline.determine_agreement("REAL_IMAGE_CANDIDATE", "AI_GENERATION_CANDIDATE")
    assert agr == "DETECTOR_DISAGREEMENT"
    assert status == "DETECTOR_DISAGREEMENT"

    # Borderline
    agr, status = pipeline.determine_agreement("BORDERLINE", "REAL_IMAGE_CANDIDATE")
    assert agr == "BORDERLINE"
    assert status == "BORDERLINE"

    agr, status = pipeline.determine_agreement("AI_GENERATION_CANDIDATE", "BORDERLINE")
    assert agr == "BORDERLINE"
    assert status == "BORDERLINE"

    # Unreadable / Failures
    agr, status = pipeline.determine_agreement("FAILED", "REAL_IMAGE_CANDIDATE")
    assert agr == "NO_CONCLUSIVE_SIGNAL"
    assert status == "NO_CONCLUSIVE_SIGNAL"


def test_format_puter_escalation_schema():
    """Ensures Puter escalation payloads adhere to standardized neutral prompt."""
    pipeline = AIImageDetectorPipeline()

    payload = pipeline.format_puter_escalation(
        media_id="MED-123",
        agreement="DETECTOR_DISAGREEMENT",
        image_type="PHOTO",
        score_a=0.12,
        score_b=0.88,
    )

    assert payload["media_id"] == "MED-123"
    assert payload["escalation_reason"] == "DETECTOR_DISAGREEMENT"
    assert "Do not claim provenance that cannot be established from the image" in payload["standardized_prompt"]
    assert "visible image content" in payload["standardized_prompt"]
    assert "uncertainty" in payload["standardized_prompt"]


def test_combine_and_build_dataset_schema():
    """Verifies output dataset compliance with the exact required 19-field schema."""
    pipeline = AIImageDetectorPipeline()

    base_df = pd.DataFrame([
        {
            "media_id": "MED-001",
            "sha256": "abcdef1234567890",
            "c2pa_status": "ABSENT",
            "image_type": "PHOTO",
        }
    ])
    results_a = [
        {
            "media_id": "MED-001",
            "sha256": "abcdef1234567890",
            "detector_a_raw_score": 0.05,
            "detector_a_result": "REAL_IMAGE_CANDIDATE",
            "runtime_a_ms": 95.0,
        }
    ]
    results_b = [
        {
            "media_id": "MED-001",
            "sha256": "abcdef1234567890",
            "detector_b_raw_score": 0.15,
            "detector_b_result": "REAL_IMAGE_CANDIDATE",
            "runtime_b_ms": 70.0,
        }
    ]

    out_df = pipeline.combine_and_build_dataset(base_df, results_a, results_b)

    expected_cols = [
        "media_id",
        "sha256",
        "detector_a_name",
        "detector_a_version",
        "detector_a_raw_score",
        "detector_a_result",
        "detector_b_name",
        "detector_b_version",
        "detector_b_raw_score",
        "detector_b_result",
        "detector_agreement",
        "assessment_status",
        "puter_escalated",
        "puter_result",
        "c2pa_status",
        "image_type",
        "runtime_a_ms",
        "runtime_b_ms",
        "created_at",
    ]

    assert list(out_df.columns) == expected_cols
    assert len(out_df) == 1
    assert out_df.iloc[0]["detector_agreement"] == "AGREEMENT_REAL"
    assert out_df.iloc[0]["assessment_status"] == "REAL_IMAGE_CANDIDATE"
    assert bool(out_df.iloc[0]["puter_escalated"]) is False


def test_frozen_artifacts_integrity():
    """Confirms Phase A-G prior artifacts remain untouched and present."""
    frozen_files = [
        "data/olx_processed/fingerprints.parquet",
        "data/olx_processed/image_relationships.parquet",
        "data/olx_processed/image_clusters.parquet",
        "data/olx_processed/image_embeddings.parquet",
        "data/olx_processed/image_authenticity.parquet",
        "data/olx_processed/image_ocr.parquet",
        "data/olx_processed/text_features.parquet",
    ]

    for ff in frozen_files:
        p = Path(ff)
        assert p.exists(), f"Frozen prerequisite file missing: {p}"
        table = pq.read_table(p)
        assert table.num_rows > 0, f"Frozen table empty: {p}"


def test_results_table_integrity():
    """Validates the produced ai_detector_results.parquet has 2280 rows and valid data."""
    results_path = Path("data/olx_processed/ai_detector_results.parquet")
    assert results_path.exists()
    table = pq.read_table(results_path)
    assert table.num_rows == 2280

    df = table.to_pandas()
    # Check no duplicate media_ids
    assert df["media_id"].nunique() == 2280

    # Ensure no PII leakage (no phone numbers or email patterns in strings)
    assert not df["media_id"].str.contains(r"@|\+91\d{10}", regex=True).any()

    # Raw scores are preserved and in [0, 1]
    valid_a = df["detector_a_raw_score"].dropna()
    assert (valid_a >= 0.0).all() and (valid_a <= 1.0).all()
    valid_b = df["detector_b_raw_score"].dropna()
    assert (valid_b >= 0.0).all() and (valid_b <= 1.0).all()

    # Verify Puter escalation flag aligns with agreement
    escalated = df[df["puter_escalated"]]
    assert (escalated["detector_agreement"].isin(["DETECTOR_DISAGREEMENT", "BORDERLINE"])).all()
