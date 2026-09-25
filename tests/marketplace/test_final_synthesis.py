"""TrustLens Phase K — Final Synthesis & Evidence Verification Tests.

Validates:
1. Authoritative dataset ledger contents and hierarchy
2. Multi-signal evidence table (213 pairs, valid columns, no risk scores)
3. Research review queue deterministic ranking
4. Publication figures 62 through 73
5. Final research report and marketplace findings
6. Standalone visual research dashboard
7. Strict scientific guardrails (no fraud scores, no probability of fraud)
8. Immutability of frozen Phase A–J artifacts
"""

from pathlib import Path
import pytest
import pyarrow.parquet as pq
import pandas as pd


@pytest.fixture(scope="module")
def base_dir():
    return Path(__file__).resolve().parent.parent.parent


@pytest.fixture(scope="module")
def reports_dir(base_dir):
    return base_dir / "data" / "olx_analysis" / "reports"


@pytest.fixture(scope="module")
def processed_dir(base_dir):
    return base_dir / "data" / "olx_processed"


def test_dataset_ledger_exists_and_accurate(reports_dir):
    ledger_path = reports_dir / "TRUSTLENS_DATASET_LEDGER.md"
    assert ledger_path.exists(), "TRUSTLENS_DATASET_LEDGER.md must exist"
    content = ledger_path.read_text(encoding="utf-8")
    assert "2,980" in content, "Ledger must record 2,980 canonical listings"
    assert "2,491" in content, "Ledger must record 2,491 media references"
    assert "2,323" in content, "Ledger must record 2,323 unique Apollo assets"
    assert "2,282" in content, "Ledger must record 2,282 downloaded assets"
    assert "2,280" in content, "Ledger must record 2,280 evaluated media assets"
    assert "Raw Observation Events" in content


def test_multi_signal_evidence_table(reports_dir):
    table_path = reports_dir / "multi_signal_evidence.parquet"
    assert table_path.exists(), "multi_signal_evidence.parquet must exist"
    df = pq.read_table(table_path).to_pandas()

    # Invariance: exactly 213 multi-signal pairs
    assert len(df) == 213, f"Expected 213 multi-signal pairs, got {len(df)}"

    required_cols = [
        "listing_id", "related_listing_id", "product", "city", "state",
        "price_signal", "text_signal", "exact_image_signal", "perceptual_image_signal",
        "deep_visual_signal", "ocr_signal", "multimodal_signal", "ai_detector_signal",
        "network_signal", "statistical_anomaly_signal", "evidence_count",
        "evidence_types", "verification_status", "interpretation", "limitations"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required column: {col}"

    # Verify no index artifact column
    assert "__index_level_0__" not in df.columns

    # Verify evidence count >= 2
    assert (df["evidence_count"] >= 2).all(), "All pairs must have evidence_count >= 2"

    # Verify layer breakdown: 4 layers: 5, 3 layers: 63, 2 layers: 145
    tier_counts = df["evidence_count"].value_counts().to_dict()
    assert tier_counts.get(4) == 5, f"Expected 5 pairs with 4 layers, got {tier_counts.get(4)}"
    assert tier_counts.get(3) == 63, f"Expected 63 pairs with 3 layers, got {tier_counts.get(3)}"
    assert tier_counts.get(2) == 145, f"Expected 145 pairs with 2 layers, got {tier_counts.get(2)}"


def test_multi_signal_markdown_report(reports_dir):
    md_path = reports_dir / "MULTI_SIGNAL_EVIDENCE.md"
    assert md_path.exists(), "MULTI_SIGNAL_EVIDENCE.md must exist"
    content = md_path.read_text(encoding="utf-8")
    assert "213" in content
    assert "Strongly Cross-Corroborated" in content
    assert "Multi-Signal Observations" in content


def test_research_review_queue(reports_dir):
    queue_path = reports_dir / "research_review_queue.parquet"
    assert queue_path.exists(), "research_review_queue.parquet must exist"
    df = pq.read_table(queue_path).to_pandas()

    assert len(df) == 213, f"Expected 213 review queue items, got {len(df)}"
    assert "evidence_count" in df.columns
    assert "missingness" in df.columns
    assert "relevant_observations" in df.columns
    assert "unknowns" in df.columns
    assert "source_references" in df.columns

    # Check deterministic ordering: evidence_count must be sorted descending
    ev_counts = df["evidence_count"].tolist()
    assert ev_counts == sorted(ev_counts, reverse=True), "Queue must be sorted by evidence_count descending"


def test_publication_figures_62_through_73(reports_dir):
    figures_dir = reports_dir / "figures"
    assert figures_dir.exists(), "Figures directory must exist"

    expected_figures = [
        "62_dataset_population_funnel.png",
        "63_product_category_composition.png",
        "64_price_distribution_by_normalized_product.png",
        "65_text_reuse_landscape.png",
        "66_image_reuse_landscape.png",
        "67_multimodal_evidence_relationships.png",
        "68_ai_detector_agreement_disagreement.png",
        "69_network_relationship_overview.png",
        "70_statistical_anomaly_experiment_overlap.png",
        "71_anomaly_persistence.png",
        "72_multi_signal_evidence_distribution.png",
        "73_geographic_observation_map.png",
    ]
    for fig_name in expected_figures:
        fig_path = figures_dir / fig_name
        assert fig_path.exists(), f"Figure {fig_name} must exist"
        assert fig_path.stat().st_size > 1000, f"Figure {fig_name} must not be empty"


def test_final_marketplace_findings(reports_dir):
    findings_path = reports_dir / "FINAL_MARKETPLACE_FINDINGS.md"
    assert findings_path.exists(), "FINAL_MARKETPLACE_FINDINGS.md must exist"
    content = findings_path.read_text(encoding="utf-8")
    for sec_num in range(1, 16):
        assert f"{sec_num}. " in content, f"Section {sec_num} must be present in findings"


def test_final_research_report_at_root(base_dir):
    report_path = base_dir / "FINAL_TRUSTLENS_RESEARCH_REPORT.md"
    assert report_path.exists(), "FINAL_TRUSTLENS_RESEARCH_REPORT.md must exist at root"
    content = report_path.read_text(encoding="utf-8")
    assert "2,980 Canonical OLX Listings" in content
    assert "Representative Research Case Studies" in content
    assert "What TrustLens Can Establish" in content
    assert "What TrustLens Cannot Establish" in content
    assert "TrustLens provides evidence organization" in content


def test_final_research_dashboard_html(reports_dir):
    html_path = reports_dir / "final_research_dashboard.html"
    assert html_path.exists(), "final_research_dashboard.html must exist"
    content = html_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "TrustLens — Final Research Intelligence Dashboard" in content
    assert "62_dataset_population_funnel.png" in content


def test_guardrails_no_fraud_or_risk_scores(reports_dir):
    for filename in ["multi_signal_evidence.parquet", "research_review_queue.parquet"]:
        df = pq.read_table(reports_dir / filename).to_pandas()
        forbidden_substrings = ["fraud_score", "scam_score", "risk_score", "probability_of_fraud", "trust_score"]
        for col in df.columns:
            for sub in forbidden_substrings:
                assert sub not in col.lower(), f"Forbidden scoring column found: {col} in {filename}"


def test_frozen_phases_immutability(processed_dir):
    # Verify Phase I unified feature store is unchanged
    unified = pq.read_table(processed_dir / "unified_features.parquet")
    assert unified.num_rows == 2980
    assert unified.num_columns == 137

    # Verify Phase J anomaly results are unchanged
    anomaly = pq.read_table(processed_dir / "anomaly_results.parquet")
    assert anomaly.num_rows == 2980

    # Verify Phase H edges are unchanged
    edges = pq.read_table(processed_dir / "relationship_edges.parquet")
    assert edges.num_rows == 21395

    # Verify Phase G.1 AI detector results are unchanged
    ai = pq.read_table(processed_dir / "ai_detector_results.parquet")
    assert ai.num_rows == 2280
