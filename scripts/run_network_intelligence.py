"""TrustLens Phase H — Full Network Intelligence Pipeline Runner.

Executes:
1. Loads frozen datasets from Phases A–G.1.
2. Constructs deterministic entity nodes (LISTING, MEDIA, PRODUCT, CITY, STATE).
3. Builds controlled relationship edges across Image, Text, OCR, and Containment layers.
4. Analyzes connected components and listing-level structural features.
5. Identifies multi-signal relationship candidate pairs (evidence_count >= 2).
6. Exports Parquet tables:
   - `data/olx_processed/relationship_edges.parquet`
   - `data/olx_processed/relationship_components.parquet`
   - `data/olx_processed/relationship_features.parquet`
7. Generates publication figures 43–50.
8. Generates interactive HTML dashboards:
   - `image_reuse_network.html`
   - `text_similarity_network.html`
   - `geographic_relationship_map.html`
   - `relationship_graph.html`
"""

import logging
from pathlib import Path
import time

import pandas as pd

from trustlens.marketplace.network_dashboards import NetworkDashboardGenerator
from trustlens.marketplace.network_intelligence import NetworkIntelligenceEngine

logger = logging.getLogger("trustlens.phase_h_runner")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def run_phase_h_pipeline():
    start_time = time.time()
    logger.info("=================================================================")
    logger.info("STARTING TRUSTLENS PHASE H: RELATIONSHIP & NETWORK INTELLIGENCE")
    logger.info("=================================================================")

    engine = NetworkIntelligenceEngine()

    # 1. Load frozen datasets
    engine.load_frozen_datasets()

    # 2. Build deterministic entity nodes
    nodes = engine.build_entity_nodes()

    # 3. Build controlled relationship edges
    edges = engine.build_relationship_edges(nodes)

    # 4. Extract connected components and listing-level features
    # include_visual_similarity=False ensures topological components represent
    # cohesive observational reuse rather than chaining 1,700+ listings across
    # generic stock device photos on white backgrounds.
    components, features_df = engine.extract_connected_components(
        nodes, edges, include_visual_similarity=False
    )

    # Attach component_id to listing nodes for graph dashboards
    listing_comp_map = dict(zip(features_df["listing_id"], features_df["component_id"]))
    for nid, nd in nodes.items():
        if nd["node_type"] == "LISTING":
            lid = nd["entity_id"]
            nd["component_id"] = listing_comp_map.get(lid, "COMP-SINGLETON")

    # 5. Extract multi-signal candidates (>= 2 independent evidence types)
    multi_signal = engine.extract_multi_signal_candidates(edges)

    # 6. Export Parquet tables
    engine.export_parquet_tables(edges, components, features_df)

    # 7. Generate publication figures 43–50
    edges_df = pd.DataFrame(edges)
    comp_df = pd.DataFrame(components)
    engine.generate_figures(edges_df, comp_df, features_df)

    # 8. Generate 4 interactive HTML forensic dashboards
    dashboard_gen = NetworkDashboardGenerator(
        output_dir=Path("data/olx_analysis/reports"),
        root_dir=Path("."),
    )
    dashboards = dashboard_gen.generate_all(
        nodes=nodes,
        edges=edges,
        components=components,
        features_df=features_df,
        multi_signal=multi_signal,
    )

    elapsed = time.time() - start_time

    # Compute breakdown counts
    r_counts = edges_df["relationship_type"].value_counts()
    exact_img = r_counts.get("MEDIA_EXACT_REUSE", 0)
    percept_img = r_counts.get("MEDIA_PERCEPTUAL_REUSE_CANDIDATE", 0)
    vis_sim = r_counts.get("MEDIA_VISUAL_SIMILARITY_CANDIDATE", 0)
    text_exact = r_counts.get("LISTING_TEXT_EXACT_REUSE", 0)
    text_sim = r_counts.get("LISTING_TEXT_SIMILARITY_CANDIDATE", 0)
    ocr_rel = r_counts.get("LISTING_SHARED_OCR_PHRASE", 0)

    cross_city = edges_df["cross_city"].sum()
    cross_state = edges_df["cross_state"].sum()
    cross_product = edges_df["cross_product"].sum()

    non_singleton_comps = [c for c in components if c["node_count"] > 1]
    largest_comp = components[0]["node_count"] if components else 0

    print("\n" + "=" * 65)
    print("PHASE H EXECUTION SUMMARY")
    print("=" * 65)
    print(f"Elapsed Time:                     {elapsed:.2f} seconds")
    print(f"Canonical Listings:               {len(engine.listings_df):,}")
    print(f"Entity Nodes:                     {len(nodes):,}")
    print(f"Total Relationship Edges:         {len(edges):,}")
    print(f"Total Connected Components:       {len(components):,}")
    print(f"Non-Singleton Components:         {len(non_singleton_comps):,}")
    print(f"Largest Component Size:           {largest_comp:,} listings")
    print("-" * 65)
    print(f"Exact Image Reuse (SHA-256):      {exact_img:,}")
    print(f"Perceptual Image Candidates:      {percept_img:,}")
    print(f"DINO Visual Similarity Cand:      {vis_sim:,}")
    print(f"Exact Title Reuse:                {text_exact:,}")
    print(f"Text Similarity Candidates:       {text_sim:,}")
    print(f"Shared OCR Phrases:               {ocr_rel:,}")
    print("-" * 65)
    print(f"Cross-City Relationships:         {cross_city:,}")
    print(f"Cross-State Relationships:        {cross_state:,}")
    print(f"Cross-Product Relationships:      {cross_product:,}")
    print(f"Multi-Signal Candidates (>=2):    {len(multi_signal):,}")
    print("-" * 65)
    print("Artifacts Created:")
    print("  - data/olx_processed/relationship_edges.parquet")
    print("  - data/olx_processed/relationship_components.parquet")
    print("  - data/olx_processed/relationship_features.parquet")
    print("  - data/olx_analysis/reports/figures/43_relationship_type_distribution.png ... 50_...")
    print("  - image_reuse_network.html")
    print("  - text_similarity_network.html")
    print("  - geographic_relationship_map.html")
    print("  - relationship_graph.html")
    print("=" * 65)


if __name__ == "__main__":
    run_phase_h_pipeline()
