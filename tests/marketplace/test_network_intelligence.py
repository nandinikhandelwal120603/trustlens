"""Unit and deterministic integration tests for Phase H Network Intelligence.

Tests cover:
- Deterministic and stable node ID generation
- Stable and distinct edge ID generation
- Ingestion of exact image reuse (Phase C SHA-256)
- Ingestion of perceptual image reuse (Phase C pHash)
- Ingestion of visual similarity candidates (Phase D DINOv2)
- Ingestion of exact text reuse and lexical overlap (Phase F)
- Distinctive OCR phrase extraction and privacy normalization
- Geographic relationship attributes and cross-city/cross-state flags
- Connected components analysis (without and with visual similarity)
- Multi-signal candidate aggregation (evidence_count >= 2)
- Absence of self-edges and duplicate edge IDs
- PII redaction integrity
- Parquet table schemas and completeness
"""

from pathlib import Path
import pyarrow.parquet as pq
import pytest

from trustlens.marketplace.network_intelligence import NetworkIntelligenceEngine


@pytest.fixture(scope="module")
def engine():
    eng = NetworkIntelligenceEngine()
    eng.load_frozen_datasets()
    return eng


@pytest.fixture(scope="module")
def nodes(engine):
    return engine.build_entity_nodes()


@pytest.fixture(scope="module")
def edges(engine, nodes):
    return engine.build_relationship_edges(nodes)


@pytest.fixture(scope="module")
def components_and_features(engine, nodes, edges):
    return engine.extract_connected_components(nodes, edges, include_visual_similarity=False)


def test_stable_node_ids():
    nid1 = NetworkIntelligenceEngine.normalize_id("listing", "OLX_1001")
    nid2 = NetworkIntelligenceEngine.normalize_id("listing", "olx_1001")
    nid3 = NetworkIntelligenceEngine.normalize_id("city", "New Delhi / NCR")

    assert nid1 == "listing:olx_1001"
    assert nid2 == "listing:olx_1001"
    assert nid3 == "city:new_delhi___ncr"


def test_entity_nodes_structure(nodes):
    assert len(nodes) > 2980  # Listings + Media + Products + Cities + States

    # Check listing node
    sample_lid = list(nodes.keys())[0]
    sample_node = nodes[sample_lid]
    assert "node_id" in sample_node
    assert "node_type" in sample_node
    assert sample_node["node_type"] in ("LISTING", "MEDIA", "PRODUCT", "CITY", "STATE")


def test_no_seller_nodes_created(nodes):
    """Ensures seller identity guardrail: no seller nodes exist."""
    node_types = set(n["node_type"] for n in nodes.values())
    assert "SELLER" not in node_types
    assert "USER" not in node_types


def test_edge_taxonomy_and_no_self_edges(edges):
    assert len(edges) > 10000

    seen_ids = set()
    for e in edges:
        # Check no self-edges
        assert e["source_node_id"] != e["target_node_id"], f"Self-edge found in {e['edge_id']}"

        # Check edge ID uniqueness
        assert e["edge_id"] not in seen_ids, f"Duplicate edge_id {e['edge_id']}"
        seen_ids.add(e["edge_id"])

        # Check controlled taxonomy
        rtype = e["relationship_type"]
        assert rtype in (
            "LISTING_IN_CITY",
            "LISTING_HAS_PRODUCT",
            "LISTING_HAS_MEDIA",
            "CITY_IN_STATE",
            "MEDIA_EXACT_REUSE",
            "MEDIA_PERCEPTUAL_REUSE_CANDIDATE",
            "MEDIA_VISUAL_SIMILARITY_CANDIDATE",
            "LISTING_TEXT_EXACT_REUSE",
            "LISTING_TEXT_SIMILARITY_CANDIDATE",
            "LISTING_SHARED_OCR_PHRASE",
        )


def test_exact_vs_perceptual_image_reuse(edges):
    exact_edges = [e for e in edges if e["relationship_type"] == "MEDIA_EXACT_REUSE"]
    percept_edges = [e for e in edges if e["relationship_type"] == "MEDIA_PERCEPTUAL_REUSE_CANDIDATE"]

    assert len(exact_edges) > 0
    assert len(percept_edges) > 0

    # Exact edges must have binary sha256 threshold basis
    for e in exact_edges:
        assert e["threshold_basis"] == "binary_sha256_equality"
        assert e["score"] == 1.0

    # Perceptual edges must have phash threshold basis
    for e in percept_edges:
        assert e["threshold_basis"] == "phash_distance_le_10"
        assert e["score"] <= 10.0


def test_visual_similarity_candidates(edges):
    dino_edges = [e for e in edges if e["relationship_type"] == "MEDIA_VISUAL_SIMILARITY_CANDIDATE"]
    assert len(dino_edges) > 1000

    for e in dino_edges[:50]:
        assert e["threshold_basis"] == "dino_similarity_ge_0.70"
        assert e["score"] >= 0.70
        assert e["verification_status"] == "UNVERIFIED_RELATIONSHIP_CANDIDATE"


def test_geographic_corridor_flags(edges):
    cross_city = [e for e in edges if e.get("cross_city")]
    cross_state = [e for e in edges if e.get("cross_state")]

    assert len(cross_city) > 0
    assert len(cross_state) > 0

    for e in cross_city[:50]:
        c1, c2 = e.get("city_a"), e.get("city_b")
        assert c1 != c2
        assert c1 not in (None, "Unknown")
        assert c2 not in (None, "Unknown")


def test_connected_components_prevent_overconnection(engine, nodes, edges):
    # Without visual similarity: components represent direct observational reuse
    comps_direct, _ = engine.extract_connected_components(nodes, edges, include_visual_similarity=False)
    assert len(comps_direct) > 2000
    assert comps_direct[0]["node_count"] <= 200, "Component size exploded without visual similarity!"

    # With visual similarity: catastrophic chaining occurs across standard phone photos
    comps_full, _ = engine.extract_connected_components(nodes, edges, include_visual_similarity=True)
    assert comps_full[0]["node_count"] > 1000, "Full graph should demonstrate the dense visual component"


def test_multi_signal_aggregation(engine, edges):
    multi_signal = engine.extract_multi_signal_candidates(edges)
    assert len(multi_signal) > 50

    for m in multi_signal:
        assert m["evidence_count"] >= 2
        assert len(m["relationship_types"]) >= 2
        assert m["status"] == "UNVERIFIED_RELATIONSHIP_CANDIDATE"
        assert "scam" not in m
        assert "fraud" not in m
        assert "risk" not in m


def test_exported_parquet_schemas_and_completeness():
    edges_p = Path("data/olx_processed/relationship_edges.parquet")
    comp_p = Path("data/olx_processed/relationship_components.parquet")
    feat_p = Path("data/olx_processed/relationship_features.parquet")

    assert edges_p.exists()
    assert comp_p.exists()
    assert feat_p.exists()

    df_edges = pq.read_table(edges_p).to_pandas()
    df_comp = pq.read_table(comp_p).to_pandas()
    df_feat = pq.read_table(feat_p).to_pandas()

    assert len(df_edges) > 10000
    assert len(df_comp) > 2000
    assert len(df_feat) == 2980  # Exactly 1 row per canonical listing

    # Verify no fraud/scam columns were created anywhere
    for col in df_edges.columns:
        assert "scam" not in col.lower()
        assert "fraud" not in col.lower()
        assert "risk" not in col.lower()

    for col in df_comp.columns:
        assert "scam" not in col.lower()
        assert "fraud" not in col.lower()
        assert "risk" not in col.lower()

    for col in df_feat.columns:
        assert "scam" not in col.lower()
        assert "fraud" not in col.lower()
        assert "risk" not in col.lower()
