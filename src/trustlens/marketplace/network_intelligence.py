"""TrustLens Marketplace Intelligence — Relationship & Network Intelligence Engine (Phase H).

Builds a deterministic, explainable multi-modal relationship graph connecting listings,
media assets, products, locations, and OCR observations without inventing risk scores or
seller guilt.

Implements:
1. Entity Model: Deterministic prefix-based IDs (listing:, media:, product:, city:, state:, ocr_phrase:).
2. Edge Taxonomy:
   - Containment: LISTING_HAS_MEDIA, LISTING_HAS_PRODUCT, LISTING_IN_CITY, CITY_IN_STATE
   - Observational Media: MEDIA_EXACT_REUSE, MEDIA_PERCEPTUAL_REUSE_CANDIDATE, MEDIA_VISUAL_SIMILARITY_CANDIDATE
   - Observational Text: LISTING_TEXT_EXACT_REUSE, LISTING_TEXT_SIMILARITY_CANDIDATE
   - Observational OCR: LISTING_SHARED_OCR_PHRASE, LISTING_SHARED_CLAIM_DRIFT
3. Multi-Signal Relationship Aggregation (identifying listings sharing >= 2 independent evidence types).
4. Connected Component Analysis via NetworkX.
5. Export of:
   - relationship_edges.parquet
   - relationship_components.parquet
   - relationship_features.parquet
6. Publication figures (43–50) and interactive HTML graph dashboards.
"""

from collections import Counter, defaultdict
import datetime
import hashlib
import json
import logging
import math
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

logger = logging.getLogger("trustlens.network_intelligence")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class NetworkIntelligenceEngine:
    """Master deterministic engine for cross-modal marketplace relationship graph intelligence."""

    def __init__(
        self,
        processed_dir: Path = Path("data/olx_processed"),
        reports_dir: Path = Path("data/olx_analysis/reports"),
        figures_dir: Path = Path("data/olx_analysis/reports/figures"),
    ):
        self.processed_dir = Path(processed_dir)
        self.reports_dir = Path(reports_dir)
        self.figures_dir = Path(figures_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

        # In-memory graph structures
        self.G_multimodal = nx.Graph()  # Heterogeneous graph with all entities
        self.G_listings = nx.Graph()    # Homogeneous listing-to-listing relationship graph

        # Caches
        self.listings_df: Optional[pd.DataFrame] = None
        self.normalized_df: Optional[pd.DataFrame] = None
        self.fingerprints_df: Optional[pd.DataFrame] = None
        self.image_rel_df: Optional[pd.DataFrame] = None
        self.deep_rel_df: Optional[pd.DataFrame] = None
        self.text_sim_df: Optional[pd.DataFrame] = None
        self.ocr_df: Optional[pd.DataFrame] = None
        self.incons_df: Optional[pd.DataFrame] = None
        self.authenticity_df: Optional[pd.DataFrame] = None
        self.ai_detector_df: Optional[pd.DataFrame] = None

    def load_frozen_datasets(self) -> None:
        """Loads all prerequisite frozen Parquet datasets strictly without modification."""
        logger.info("Loading frozen Phase A-G.1 datasets...")
        self.listings_df = pq.read_table(self.processed_dir / "listings.parquet").to_pandas()
        self.normalized_df = pq.read_table(self.processed_dir / "normalized_listings.parquet").to_pandas()
        self.fingerprints_df = pq.read_table(self.processed_dir / "fingerprints.parquet").to_pandas()
        self.image_rel_df = pq.read_table(self.processed_dir / "image_relationships.parquet").to_pandas()
        self.deep_rel_df = pq.read_table(self.processed_dir / "deep_visual_relationships.parquet").to_pandas()
        self.text_sim_df = pq.read_table(self.processed_dir / "text_similarity_candidates.parquet").to_pandas()
        self.ocr_df = pq.read_table(self.processed_dir / "image_ocr.parquet").to_pandas()
        self.incons_df = pq.read_table(self.processed_dir / "multimodal_inconsistencies.parquet").to_pandas()
        self.authenticity_df = pq.read_table(self.processed_dir / "image_authenticity.parquet").to_pandas()
        self.ai_detector_df = pq.read_table(self.processed_dir / "ai_detector_results.parquet").to_pandas()
        logger.info("All prerequisite Parquet datasets loaded successfully.")

    @staticmethod
    def normalize_id(prefix: str, val: Any) -> str:
        """Generates deterministic clean node identifier."""
        clean_val = str(val).strip().lower().replace(" ", "_").replace("/", "_").replace(":", "_")
        return f"{prefix}:{clean_val}"

    def build_entity_nodes(self) -> Dict[str, Dict[str, Any]]:
        """Constructs deterministic entity nodes for listings, media, products, and locations."""
        nodes: Dict[str, Dict[str, Any]] = {}

        # 1. Listing Nodes
        merged_listings = self.listings_df.merge(
            self.normalized_df[["listing_id", "product_category", "brand", "product_family", "model"]],
            on="listing_id",
            how="left",
        )

        for _, r in merged_listings.iterrows():
            lid = str(r["listing_id"])
            node_id = f"listing:{lid}"
            nodes[node_id] = {
                "node_id": node_id,
                "node_type": "LISTING",
                "entity_id": lid,
                "title": str(r.get("raw_title", "")),
                "price": float(r["price_amount"]) if pd.notnull(r.get("price_amount")) else None,
                "city": str(r.get("city", "Unknown")),
                "state": str(r.get("state", "Unknown")),
                "product_family": str(r.get("product_family", "Unknown")),
                "model": str(r.get("model", "Unknown")),
                "has_media": bool(r.get("has_media", False)),
                "media_count": int(r.get("media_count", 0)),
            }

        # 2. Media Nodes
        merged_media = self.fingerprints_df.merge(
            self.authenticity_df[["media_id", "image_type", "c2pa_status"]],
            on="media_id",
            how="left",
        )
        merged_media = merged_media.merge(
            self.ai_detector_df[["media_id", "detector_agreement", "assessment_status"]],
            on="media_id",
            how="left",
        )

        for _, r in merged_media.iterrows():
            mid = str(r["media_id"])
            node_id = f"media:{mid}"
            nodes[node_id] = {
                "node_id": node_id,
                "node_type": "MEDIA",
                "entity_id": mid,
                "listing_id": str(r.get("listing_id", "")),
                "sha256": str(r.get("sha256", "")),
                "width": int(r["width"]) if pd.notnull(r.get("width")) else None,
                "height": int(r["height"]) if pd.notnull(r.get("height")) else None,
                "image_type": str(r.get("image_type", "UNKNOWN")),
                "c2pa_status": str(r.get("c2pa_status", "ABSENT")),
                "detector_agreement": str(r.get("detector_agreement", "UNKNOWN")),
                "assessment_status": str(r.get("assessment_status", "UNKNOWN")),
            }

        # 3. Product & Product Family Nodes
        for _, r in merged_listings.iterrows():
            model = str(r.get("model", "Unknown"))
            family = str(r.get("product_family", "Unknown"))
            p_node = self.normalize_id("product", model)
            if p_node not in nodes:
                nodes[p_node] = {
                    "node_id": p_node,
                    "node_type": "PRODUCT",
                    "entity_id": model,
                    "product_family": family,
                    "brand": str(r.get("brand", "Unknown")),
                }
            pf_node = self.normalize_id("product_family", family)
            if pf_node not in nodes:
                nodes[pf_node] = {
                    "node_id": pf_node,
                    "node_type": "PRODUCT_FAMILY",
                    "entity_id": family,
                }

        # 4. Geographic Nodes (City & State)
        for _, r in merged_listings.iterrows():
            c = str(r.get("city", "Unknown"))
            s = str(r.get("state", "Unknown"))
            if c and c != "Unknown":
                c_node = self.normalize_id("city", c)
                if c_node not in nodes:
                    nodes[c_node] = {
                        "node_id": c_node,
                        "node_type": "CITY",
                        "entity_id": c,
                        "state": s,
                    }
            if s and s != "Unknown":
                s_node = self.normalize_id("state", s)
                if s_node not in nodes:
                    nodes[s_node] = {
                        "node_id": s_node,
                        "node_type": "STATE",
                        "entity_id": s,
                    }

        logger.info("Constructed %d total entity nodes", len(nodes))
        return nodes

    def extract_distinctive_ocr_phrases(self) -> List[Dict[str, Any]]:
        """Extracts distinctive shared OCR n-grams connecting multiple listings."""
        text_rows = self.ocr_df[self.ocr_df["ocr_status"] == "success_text"]
        phrases_by_listing: Dict[str, Set[str]] = defaultdict(set)
        listing_phrase_details: Dict[Tuple[str, str], str] = {}

        for _, r in text_rows.iterrows():
            lid = str(r["listing_id"])
            txt = str(r.get("ocr_text_normalized", "")).lower()
            tokens = [w for w in txt.split() if len(w) >= 2]
            # 3 to 5 word ngrams
            for n in range(3, 6):
                for i in range(len(tokens) - n + 1):
                    ngram = " ".join(tokens[i : i + n])
                    if len(ngram) >= 12:
                        phrases_by_listing[ngram].add(lid)
                        listing_phrase_details[(lid, ngram)] = str(r["media_id"])

        shared_ocr_edges = []
        for phrase, lids in phrases_by_listing.items():
            if 2 <= len(lids) <= 30:  # Distinctive, shared by multiple listings but not universal noise
                lids_list = sorted(list(lids))
                for i in range(len(lids_list)):
                    for j in range(i + 1, len(lids_list)):
                        l1, l2 = lids_list[i], lids_list[j]
                        shared_ocr_edges.append({
                            "listing_id_a": l1,
                            "listing_id_b": l2,
                            "phrase": phrase,
                            "media_a": listing_phrase_details.get((l1, phrase), ""),
                            "media_b": listing_phrase_details.get((l2, phrase), ""),
                        })

        logger.info("Extracted %d pairwise shared OCR phrase links", len(shared_ocr_edges))
        return shared_ocr_edges

    def build_relationship_edges(self, nodes: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Constructs all explicit relationship edges conforming to the Phase H14 schema."""
        edges: List[Dict[str, Any]] = []
        seen_edge_keys: Set[Tuple[str, str, str]] = set()

        # Metadata lookup by listing_id
        listing_meta: Dict[str, Dict[str, Any]] = {}
        for nid, nd in nodes.items():
            if nd["node_type"] == "LISTING":
                lid = nd["entity_id"]
                listing_meta[lid] = {
                    "city": nd.get("city", "Unknown"),
                    "state": nd.get("state", "Unknown"),
                    "product": nd.get("model", "Unknown"),
                    "product_family": nd.get("product_family", "Unknown"),
                }

        def get_geo_and_prod(l1: Optional[str], l2: Optional[str]) -> Tuple[Any, Any, Any, Any, Any, Any, bool, bool, bool]:
            m1 = listing_meta.get(l1 or "", {})
            m2 = listing_meta.get(l2 or "", {})
            c1, c2 = m1.get("city"), m2.get("city")
            s1, s2 = m1.get("state"), m2.get("state")
            p1, p2 = m1.get("product"), m2.get("product")
            f1, f2 = m1.get("product_family"), m2.get("product_family")

            cross_c = bool(c1 and c2 and c1 != "Unknown" and c2 != "Unknown" and c1 != c2)
            cross_s = bool(s1 and s2 and s1 != "Unknown" and s2 != "Unknown" and s1 != s2)
            cross_p = bool(f1 and f2 and f1 != "Unknown" and f2 != "Unknown" and f1 != f2)
            return c1, c2, s1, s2, p1, p2, cross_c, cross_s, cross_p

        created_now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # ---------------------------------------------------------------------
        # 1. Structural Containment Edges
        # ---------------------------------------------------------------------
        for nid, nd in nodes.items():
            if nd["node_type"] == "LISTING":
                lid = nd["entity_id"]
                # LISTING_IN_CITY
                c = nd.get("city")
                if c and c != "Unknown":
                    c_nid = self.normalize_id("city", c)
                    edges.append({
                        "edge_id": f"EDGE-STRUCT-{lid}-{c_nid}",
                        "source_node_id": nid,
                        "target_node_id": c_nid,
                        "source_type": "LISTING",
                        "target_type": "CITY",
                        "relationship_type": "LISTING_IN_CITY",
                        "evidence_source": "phase_a_geography",
                        "evidence_id": f"geo_{lid}",
                        "score": 1.0,
                        "score_type": "deterministic_containment",
                        "threshold": 1.0,
                        "threshold_basis": "verified_geography",
                        "listing_a_id": lid,
                        "listing_b_id": None,
                        "city_a": c,
                        "city_b": c,
                        "state_a": nd.get("state"),
                        "state_b": nd.get("state"),
                        "product_a": nd.get("model"),
                        "product_b": None,
                        "cross_city": False,
                        "cross_state": False,
                        "cross_product": False,
                        "verification_status": "OBSERVED_STRUCTURAL",
                        "created_at": created_now,
                    })

                # LISTING_HAS_PRODUCT
                m = nd.get("model")
                if m and m != "Unknown":
                    p_nid = self.normalize_id("product", m)
                    edges.append({
                        "edge_id": f"EDGE-STRUCT-{lid}-{p_nid}",
                        "source_node_id": nid,
                        "target_node_id": p_nid,
                        "source_type": "LISTING",
                        "target_type": "PRODUCT",
                        "relationship_type": "LISTING_HAS_PRODUCT",
                        "evidence_source": "phase_b_normalization",
                        "evidence_id": f"prod_{lid}",
                        "score": 1.0,
                        "score_type": "deterministic_containment",
                        "threshold": 1.0,
                        "threshold_basis": "normalized_product",
                        "listing_a_id": lid,
                        "listing_b_id": None,
                        "city_a": nd.get("city"),
                        "city_b": None,
                        "state_a": nd.get("state"),
                        "state_b": None,
                        "product_a": m,
                        "product_b": m,
                        "cross_city": False,
                        "cross_state": False,
                        "cross_product": False,
                        "verification_status": "OBSERVED_STRUCTURAL",
                        "created_at": created_now,
                    })

            elif nd["node_type"] == "MEDIA":
                mid = nd["entity_id"]
                lid = nd.get("listing_id")
                if lid and f"listing:{lid}" in nodes:
                    edges.append({
                        "edge_id": f"EDGE-STRUCT-{lid}-media-{mid}",
                        "source_node_id": f"listing:{lid}",
                        "target_node_id": nid,
                        "source_type": "LISTING",
                        "target_type": "MEDIA",
                        "relationship_type": "LISTING_HAS_MEDIA",
                        "evidence_source": "phase_a_media",
                        "evidence_id": f"media_{mid}",
                        "score": 1.0,
                        "score_type": "deterministic_containment",
                        "threshold": 1.0,
                        "threshold_basis": "listing_media_gallery",
                        "listing_a_id": lid,
                        "listing_b_id": None,
                        "city_a": listing_meta.get(lid, {}).get("city"),
                        "city_b": None,
                        "state_a": listing_meta.get(lid, {}).get("state"),
                        "state_b": None,
                        "product_a": listing_meta.get(lid, {}).get("product"),
                        "product_b": None,
                        "cross_city": False,
                        "cross_state": False,
                        "cross_product": False,
                        "verification_status": "OBSERVED_STRUCTURAL",
                        "created_at": created_now,
                    })

            elif nd["node_type"] == "CITY":
                c = nd["entity_id"]
                s = nd.get("state")
                if s and s != "Unknown":
                    s_nid = self.normalize_id("state", s)
                    edges.append({
                        "edge_id": f"EDGE-STRUCT-{nid}-{s_nid}",
                        "source_node_id": nid,
                        "target_node_id": s_nid,
                        "source_type": "CITY",
                        "target_type": "STATE",
                        "relationship_type": "CITY_IN_STATE",
                        "evidence_source": "phase_a_geography",
                        "evidence_id": f"state_map_{c}",
                        "score": 1.0,
                        "score_type": "deterministic_containment",
                        "threshold": 1.0,
                        "threshold_basis": "administrative_hierarchy",
                        "listing_a_id": None,
                        "listing_b_id": None,
                        "city_a": c,
                        "city_b": c,
                        "state_a": s,
                        "state_b": s,
                        "product_a": None,
                        "product_b": None,
                        "cross_city": False,
                        "cross_state": False,
                        "cross_product": False,
                        "verification_status": "OBSERVED_STRUCTURAL",
                        "created_at": created_now,
                    })

        # ---------------------------------------------------------------------
        # 2. Phase C Exact & Perceptual Image Relationships
        # ---------------------------------------------------------------------
        for _, r in self.image_rel_df.iterrows():
            m1, m2 = str(r["media_a_id"]), str(r["media_b_id"])
            l1, l2 = str(r["listing_a_id"]), str(r["listing_b_id"])
            if m1 == m2 or (m2, m1, "img") in seen_edge_keys:
                continue
            seen_edge_keys.add((m1, m2, "img"))

            is_exact = bool(r.get("sha_equality", False))
            rel_type = "MEDIA_EXACT_REUSE" if is_exact else "MEDIA_PERCEPTUAL_REUSE_CANDIDATE"
            score = 1.0 if is_exact else float(r.get("phash_distance", 0))
            score_type = "sha256_exact_match" if is_exact else "phash_hamming_distance"
            thresh = 0.0 if is_exact else 10.0
            thresh_basis = "binary_sha256_equality" if is_exact else "phash_distance_le_10"

            c1, c2, s1, s2, p1, p2, cc, cs, cp = get_geo_and_prod(l1, l2)
            edge_id = f"EDGE-C-{r['relationship_id']}"

            edges.append({
                "edge_id": edge_id,
                "source_node_id": f"media:{m1}",
                "target_node_id": f"media:{m2}",
                "source_type": "MEDIA",
                "target_type": "MEDIA",
                "relationship_type": rel_type,
                "evidence_source": "phase_c_image_relationships",
                "evidence_id": str(r["relationship_id"]),
                "score": score,
                "score_type": score_type,
                "threshold": thresh,
                "threshold_basis": thresh_basis,
                "listing_a_id": l1,
                "listing_b_id": l2,
                "city_a": c1,
                "city_b": c2,
                "state_a": s1,
                "state_b": s2,
                "product_a": p1,
                "product_b": p2,
                "cross_city": cc,
                "cross_state": cs,
                "cross_product": cp,
                "verification_status": "UNVERIFIED_RELATIONSHIP_CANDIDATE",
                "created_at": created_now,
            })

        # ---------------------------------------------------------------------
        # 3. Phase D Deep Visual Similarity Relationships
        # ---------------------------------------------------------------------
        for _, r in self.deep_rel_df.iterrows():
            m1, m2 = str(r["media_a_id"]), str(r["media_b_id"])
            l1, l2 = str(r["listing_a_id"]), str(r["listing_b_id"])
            if m1 == m2 or (m2, m1, "deep") in seen_edge_keys:
                continue
            seen_edge_keys.add((m1, m2, "deep"))

            sim = float(r.get("dino_similarity", 0.0))
            c1, c2, s1, s2, p1, p2, cc, cs, cp = get_geo_and_prod(l1, l2)
            edge_id = f"EDGE-D-{r['relationship_id']}"

            edges.append({
                "edge_id": edge_id,
                "source_node_id": f"media:{m1}",
                "target_node_id": f"media:{m2}",
                "source_type": "MEDIA",
                "target_type": "MEDIA",
                "relationship_type": "MEDIA_VISUAL_SIMILARITY_CANDIDATE",
                "evidence_source": "phase_d_deep_visual_relationships",
                "evidence_id": str(r["relationship_id"]),
                "score": round(sim, 6),
                "score_type": "dinov2_cosine_similarity",
                "threshold": 0.70,
                "threshold_basis": "dino_similarity_ge_0.70",
                "listing_a_id": l1,
                "listing_b_id": l2,
                "city_a": c1,
                "city_b": c2,
                "state_a": s1,
                "state_b": s2,
                "product_a": p1,
                "product_b": p2,
                "cross_city": cc,
                "cross_state": cs,
                "cross_product": cp,
                "verification_status": "UNVERIFIED_RELATIONSHIP_CANDIDATE",
                "created_at": created_now,
            })

        # ---------------------------------------------------------------------
        # 4. Phase F Text Similarity Relationships
        # ---------------------------------------------------------------------
        for _, r in self.text_sim_df.iterrows():
            l1, l2 = str(r["listing_id_a"]), str(r["listing_id_b"])
            if l1 == l2 or (l2, l1, "text") in seen_edge_keys:
                continue
            seen_edge_keys.add((l1, l2, "text"))

            is_exact = (r.get("candidate_type") == "EXACT_TITLE_REUSE") or (r.get("similarity_score") == 1.0)
            rel_type = "LISTING_TEXT_EXACT_REUSE" if is_exact else "LISTING_TEXT_SIMILARITY_CANDIDATE"
            sim = float(r.get("similarity_score", 0.0))
            c1, c2, s1, s2, p1, p2, cc, cs, cp = get_geo_and_prod(l1, l2)
            edge_id = f"EDGE-F-{r['candidate_id']}"

            edges.append({
                "edge_id": edge_id,
                "source_node_id": f"listing:{l1}",
                "target_node_id": f"listing:{l2}",
                "source_type": "LISTING",
                "target_type": "LISTING",
                "relationship_type": rel_type,
                "evidence_source": "phase_f_text_similarity_candidates",
                "evidence_id": str(r["candidate_id"]),
                "score": round(sim, 6),
                "score_type": "pairwise_jaccard_similarity",
                "threshold": 1.0 if is_exact else 0.75,
                "threshold_basis": "exact_title_match" if is_exact else "jaccard_ge_0.75",
                "listing_a_id": l1,
                "listing_b_id": l2,
                "city_a": c1,
                "city_b": c2,
                "state_a": s1,
                "state_b": s2,
                "product_a": p1,
                "product_b": p2,
                "cross_city": cc,
                "cross_state": cs,
                "cross_product": cp,
                "verification_status": "UNVERIFIED_RELATIONSHIP_CANDIDATE",
                "created_at": created_now,
            })

        # ---------------------------------------------------------------------
        # 5. Phase E Shared OCR Phrases
        # ---------------------------------------------------------------------
        ocr_links = self.extract_distinctive_ocr_phrases()
        for idx, item in enumerate(ocr_links):
            l1, l2 = item["listing_id_a"], item["listing_id_b"]
            if l1 == l2 or (l2, l1, "ocr") in seen_edge_keys:
                continue
            seen_edge_keys.add((l1, l2, "ocr"))

            c1, c2, s1, s2, p1, p2, cc, cs, cp = get_geo_and_prod(l1, l2)
            phrase_hash = hashlib.sha256(item["phrase"].encode()).hexdigest()[:12]
            edge_id = f"EDGE-E-OCR-{l1}-{l2}-{phrase_hash}"

            edges.append({
                "edge_id": edge_id,
                "source_node_id": f"listing:{l1}",
                "target_node_id": f"listing:{l2}",
                "source_type": "LISTING",
                "target_type": "LISTING",
                "relationship_type": "LISTING_SHARED_OCR_PHRASE",
                "evidence_source": "phase_e_image_ocr",
                "evidence_id": f"ocr_ngram_{phrase_hash}",
                "score": 1.0,
                "score_type": "distinctive_ngram_match",
                "threshold": 1.0,
                "threshold_basis": "shared_ngram_len_ge_12",
                "listing_a_id": l1,
                "listing_b_id": l2,
                "city_a": c1,
                "city_b": c2,
                "state_a": s1,
                "state_b": s2,
                "product_a": p1,
                "product_b": p2,
                "cross_city": cc,
                "cross_state": cs,
                "cross_product": cp,
                "verification_status": "UNVERIFIED_RELATIONSHIP_CANDIDATE",
                "created_at": created_now,
            })

        logger.info("Constructed %d total relationship and structural edges", len(edges))
        return edges

    def extract_connected_components(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Dict[str, Any]],
        include_visual_similarity: bool = False,
    ) -> Tuple[List[Dict[str, Any]], pd.DataFrame]:
        """Calculates connected components and listing-level relationship features.
        
        Args:
            nodes: Entity node lookup.
            edges: List of relationship and structural edges.
            include_visual_similarity: If False (default), connected components are
                formed strictly from direct observational reuse relationships
                (exact image reuse, pHash perceptual candidates, exact text reuse,
                high lexical overlap, and shared OCR phrases). This prevents
                transitive catastrophic overconnection where 1,700+ listings chain
                together merely due to stock device photos on white backgrounds.
                Visual similarity candidate counts are still fully preserved in
                listing features and relationship edge records.
        """
        # Build homogeneous listing-level graph for component analysis
        G = nx.Graph()
        for nid, nd in nodes.items():
            if nd["node_type"] == "LISTING":
                G.add_node(nd["entity_id"])

        # Map to track edges per listing pair
        pair_edge_types: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
        pair_edge_counts: Dict[Tuple[str, str], int] = defaultdict(int)

        for e in edges:
            l1, l2 = e.get("listing_a_id"), e.get("listing_b_id")
            rtype = e["relationship_type"]
            # Skip structural self-listing containment edges for listing-to-listing connectivity
            if l1 and l2 and l1 != l2:
                pair = tuple(sorted([str(l1), str(l2)]))
                pair_edge_types[pair].add(rtype)
                pair_edge_counts[pair] += 1
                
                # Add edge to component graph G
                if include_visual_similarity or rtype != "MEDIA_VISUAL_SIMILARITY_CANDIDATE":
                    G.add_edge(pair[0], pair[1])

        components_raw = list(nx.connected_components(G))
        components_raw.sort(key=lambda c: len(c), reverse=True)

        logger.info(
            "Identified %d total connected components across %d listings (include_visual_similarity=%s)",
            len(components_raw),
            G.number_of_nodes(),
            include_visual_similarity,
        )

        component_records = []
        listing_features = []

        # Mapping for quick lookup
        listing_to_comp: Dict[str, Tuple[str, int]] = {}

        for idx, comp in enumerate(components_raw):
            comp_id = f"COMP-{idx + 1:04d}"
            c_listings = list(comp)
            comp_size = len(c_listings)
            for lid in c_listings:
                listing_to_comp[lid] = (comp_id, comp_size)

            # Metadata aggregations
            c_cities = set()
            c_states = set()
            c_prods = set()
            c_families = set()
            c_media_count = 0

            # Edge type aggregations inside this component
            comp_edges = 0
            comp_edge_types = set()
            exact_img = 0
            percept_img = 0
            vis_sim = 0
            text_sim = 0
            ocr_count = 0
            cross_c_count = 0
            cross_s_count = 0
            cross_p_count = 0

            for lid in c_listings:
                l_node = nodes.get(f"listing:{lid}", {})
                if l_node.get("city") and l_node["city"] != "Unknown":
                    c_cities.add(l_node["city"])
                if l_node.get("state") and l_node["state"] != "Unknown":
                    c_states.add(l_node["state"])
                if l_node.get("model") and l_node["model"] != "Unknown":
                    c_prods.add(l_node["model"])
                if l_node.get("product_family") and l_node["product_family"] != "Unknown":
                    c_families.add(l_node["product_family"])
                c_media_count += l_node.get("media_count", 0)

            # Analyze internal edges between listings in this component
            for i in range(len(c_listings)):
                for j in range(i + 1, len(c_listings)):
                    pair = tuple(sorted([c_listings[i], c_listings[j]]))
                    if pair in pair_edge_types:
                        comp_edges += pair_edge_counts[pair]
                        rtypes = pair_edge_types[pair]
                        comp_edge_types.update(rtypes)

                        if "MEDIA_EXACT_REUSE" in rtypes:
                            exact_img += 1
                        if "MEDIA_PERCEPTUAL_REUSE_CANDIDATE" in rtypes:
                            percept_img += 1
                        if "MEDIA_VISUAL_SIMILARITY_CANDIDATE" in rtypes:
                            vis_sim += 1
                        if any("TEXT" in t for t in rtypes):
                            text_sim += 1
                        if any("OCR" in t for t in rtypes):
                            ocr_count += 1

                        # Cross checks
                        m1 = nodes.get(f"listing:{pair[0]}", {})
                        m2 = nodes.get(f"listing:{pair[1]}", {})
                        if m1.get("city") and m2.get("city") and m1["city"] != "Unknown" and m2["city"] != "Unknown" and m1["city"] != m2["city"]:
                            cross_c_count += 1
                        if m1.get("state") and m2.get("state") and m1["state"] != "Unknown" and m2["state"] != "Unknown" and m1["state"] != m2["state"]:
                            cross_s_count += 1
                        if m1.get("product_family") and m2.get("product_family") and m1["product_family"] != "Unknown" and m2["product_family"] != "Unknown" and m1["product_family"] != m2["product_family"]:
                            cross_p_count += 1

            component_records.append({
                "component_id": comp_id,
                "node_count": comp_size,
                "listing_count": comp_size,
                "media_count": c_media_count,
                "city_count": len(c_cities),
                "state_count": len(c_states),
                "product_family_count": len(c_families),
                "edge_count": comp_edges,
                "edge_type_count": len(comp_edge_types),
                "exact_image_edges": exact_img,
                "perceptual_image_edges": percept_img,
                "visual_similarity_edges": vis_sim,
                "text_similarity_edges": text_sim,
                "ocr_edges": ocr_count,
                "cross_city_edges": cross_c_count,
                "cross_state_edges": cross_s_count,
                "cross_product_edges": cross_p_count,
                "status": "UNVERIFIED_RELATIONSHIP_COMPONENT",
            })

        # ---------------------------------------------------------------------
        # Listing-Level Features (Phase H16)
        # ---------------------------------------------------------------------
        for nid, nd in nodes.items():
            if nd["node_type"] == "LISTING":
                lid = nd["entity_id"]
                comp_id, comp_size = listing_to_comp.get(lid, ("COMP-SINGLETON", 1))

                # Neighbors in G
                neighbors = list(G.neighbors(lid)) if lid in G else []
                degree = len(neighbors)

                exact_img_c = 0
                percept_img_c = 0
                vis_sim_c = 0
                text_sim_c = 0
                ocr_c = 0
                connected_cities = set()
                connected_states = set()
                connected_families = set()

                for nb in neighbors:
                    pair = tuple(sorted([lid, nb]))
                    rtypes = pair_edge_types.get(pair, set())
                    if "MEDIA_EXACT_REUSE" in rtypes:
                        exact_img_c += 1
                    if "MEDIA_PERCEPTUAL_REUSE_CANDIDATE" in rtypes:
                        percept_img_c += 1
                    if "MEDIA_VISUAL_SIMILARITY_CANDIDATE" in rtypes:
                        vis_sim_c += 1
                    if any("TEXT" in t for t in rtypes):
                        text_sim_c += 1
                    if any("OCR" in t for t in rtypes):
                        ocr_c += 1

                    nb_node = nodes.get(f"listing:{nb}", {})
                    if nb_node.get("city") and nb_node["city"] != "Unknown":
                        connected_cities.add(nb_node["city"])
                    if nb_node.get("state") and nb_node["state"] != "Unknown":
                        connected_states.add(nb_node["state"])
                    if nb_node.get("product_family") and nb_node["product_family"] != "Unknown":
                        connected_families.add(nb_node["product_family"])

                listing_features.append({
                    "listing_id": lid,
                    "relationship_degree": degree,
                    "unique_connected_listings": degree,
                    "exact_image_reuse_count": exact_img_c,
                    "perceptual_image_candidate_count": percept_img_c,
                    "visual_similarity_candidate_count": vis_sim_c,
                    "text_similarity_candidate_count": text_sim_c,
                    "shared_ocr_candidate_count": ocr_c,
                    "distinct_cities_connected": len(connected_cities),
                    "distinct_states_connected": len(connected_states),
                    "distinct_product_families_connected": len(connected_families),
                    "component_id": comp_id,
                    "component_size": comp_size,
                })

        return component_records, pd.DataFrame(listing_features)

    def extract_multi_signal_candidates(self, edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifies pairs of listings connected through MULTIPLE independent evidence layers."""
        pair_evidence: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
        pair_details: Dict[Tuple[str, str], Dict[str, Any]] = {}

        for e in edges:
            l1, l2 = e.get("listing_a_id"), e.get("listing_b_id")
            rtype = e["relationship_type"]
            if l1 and l2 and l1 != l2:
                pair = tuple(sorted([str(l1), str(l2)]))

                # Group into independent evidence classes
                if "EXACT_REUSE" in rtype and "MEDIA" in rtype:
                    pair_evidence[pair].add("MEDIA_EXACT_REUSE")
                elif "PERCEPTUAL" in rtype:
                    pair_evidence[pair].add("MEDIA_PERCEPTUAL_REUSE_CANDIDATE")
                elif "VISUAL_SIMILARITY" in rtype:
                    pair_evidence[pair].add("MEDIA_VISUAL_SIMILARITY_CANDIDATE")
                elif "TEXT_EXACT" in rtype:
                    pair_evidence[pair].add("LISTING_TEXT_EXACT_REUSE")
                elif "TEXT_SIMILARITY" in rtype:
                    pair_evidence[pair].add("LISTING_TEXT_SIMILARITY_CANDIDATE")
                elif "OCR" in rtype:
                    pair_evidence[pair].add("LISTING_SHARED_OCR_PHRASE")

                pair_details[pair] = {
                    "city_a": e.get("city_a"),
                    "city_b": e.get("city_b"),
                    "state_a": e.get("state_a"),
                    "state_b": e.get("state_b"),
                    "product_a": e.get("product_a"),
                    "product_b": e.get("product_b"),
                    "cross_city": e.get("cross_city", False),
                    "cross_state": e.get("cross_state", False),
                    "cross_product": e.get("cross_product", False),
                }

        multi_signal = []
        for pair, ev_set in pair_evidence.items():
            if len(ev_set) >= 2:
                d = pair_details[pair]
                multi_signal.append({
                    "listing_a": pair[0],
                    "listing_b": pair[1],
                    "relationship_types": sorted(list(ev_set)),
                    "evidence_count": len(ev_set),
                    "city_a": d.get("city_a"),
                    "city_b": d.get("city_b"),
                    "state_a": d.get("state_a"),
                    "state_b": d.get("state_b"),
                    "product_a": d.get("product_a"),
                    "product_b": d.get("product_b"),
                    "cross_city": d.get("cross_city", False),
                    "cross_state": d.get("cross_state", False),
                    "cross_product": d.get("cross_product", False),
                    "status": "UNVERIFIED_RELATIONSHIP_CANDIDATE",
                })

        multi_signal.sort(key=lambda x: x["evidence_count"], reverse=True)
        logger.info("Identified %d multi-signal relationship candidate pairs (evidence_count >= 2)", len(multi_signal))
        return multi_signal

    def export_parquet_tables(
        self,
        edges: List[Dict[str, Any]],
        components: List[Dict[str, Any]],
        features_df: pd.DataFrame,
    ) -> None:
        """Saves relationship edges, components, and features Parquet tables."""
        # 1. relationship_edges.parquet
        df_edges = pd.DataFrame(edges)
        p_edges = self.processed_dir / "relationship_edges.parquet"
        pq.write_table(pa.Table.from_pandas(df_edges), p_edges)
        logger.info("Saved %d edges to %s", len(df_edges), p_edges)

        # 2. relationship_components.parquet
        df_comp = pd.DataFrame(components)
        p_comp = self.processed_dir / "relationship_components.parquet"
        pq.write_table(pa.Table.from_pandas(df_comp), p_comp)
        logger.info("Saved %d components to %s", len(df_comp), p_comp)

        # 3. relationship_features.parquet
        p_feat = self.processed_dir / "relationship_features.parquet"
        pq.write_table(pa.Table.from_pandas(features_df), p_feat)
        logger.info("Saved %d listing features to %s", len(features_df), p_feat)

    def generate_figures(
        self,
        edges_df: pd.DataFrame,
        comp_df: pd.DataFrame,
        feat_df: pd.DataFrame,
    ) -> None:
        """Generates publication-quality charts (Figures 43–50)."""
        logger.info("Generating publication figures 43-50...")

        # Figure 43: Relationship Type Distribution
        plt.figure(figsize=(9, 4.5))
        r_counts = edges_df["relationship_type"].value_counts()
        colors = plt.cm.tab10(np.linspace(0, 1, len(r_counts)))
        plt.barh(r_counts.index[::-1], r_counts.values[::-1], color=colors[::-1], edgecolor="black")
        for i, v in enumerate(r_counts.values[::-1]):
            plt.text(v + max(r_counts.values)*0.01, i, f"{v:,}", va="center", fontsize=9, fontweight="bold")
        plt.title("Figure 43: Distribution of Observed Relationship & Structural Edge Types", fontsize=11, fontweight="bold")
        plt.xlabel("Edge Count")
        plt.grid(axis="x", linestyle=":", alpha=0.6)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "43_relationship_type_distribution.png", dpi=150)
        plt.close()

        # Figure 44: Connected Component Size Distribution
        plt.figure(figsize=(7.5, 4.5))
        sizes = comp_df[comp_df["node_count"] > 1]["node_count"]
        plt.hist(sizes, bins=25, color="#2563EB", edgecolor="black", alpha=0.85)
        plt.title("Figure 44: Connected Component Size Distribution (Non-Singletons)", fontsize=11, fontweight="bold")
        plt.xlabel("Component Size (Listings in Component)")
        plt.ylabel("Component Frequency")
        plt.yscale("log")
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "44_connected_component_size_distribution.png", dpi=150)
        plt.close()

        # Figure 45: Image Reuse Breakdown (Exact vs Perceptual vs Visual Similarity)
        plt.figure(figsize=(7, 4.5))
        img_edges = edges_df[edges_df["relationship_type"].str.contains("MEDIA")]
        img_counts = img_edges["relationship_type"].value_counts()
        plt.bar(img_counts.index, img_counts.values, color=["#7C3AED", "#10B981", "#3B82F6"][:len(img_counts)], edgecolor="black")
        for i, v in enumerate(img_counts.values):
            plt.text(i, v + max(img_counts.values)*0.02, f"{v:,}", ha="center", fontsize=9, fontweight="bold")
        plt.title("Figure 45: Observational Image Reuse & Similarity Distribution", fontsize=11, fontweight="bold")
        plt.ylabel("Relationship Count")
        plt.xticks(rotation=15, ha="right")
        plt.grid(axis="y", linestyle=":", alpha=0.6)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "45_image_reuse_distribution.png", dpi=150)
        plt.close()

        # Figure 46: Text Similarity Distribution
        plt.figure(figsize=(7, 4.5))
        text_edges = edges_df[edges_df["relationship_type"].str.contains("TEXT")]
        scores = text_edges["score"].dropna()
        plt.hist(scores, bins=20, color="#EC4899", edgecolor="black", alpha=0.85)
        plt.axvline(1.0, color="red", linestyle="--", label="Exact Match (1.0)")
        plt.title("Figure 46: Text Reuse & Similarity Score Distribution", fontsize=11, fontweight="bold")
        plt.xlabel("Pairwise Jaccard Similarity Score")
        plt.ylabel("Candidate Pair Count")
        plt.legend()
        plt.grid(axis="y", linestyle=":", alpha=0.6)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "46_text_similarity_distribution.png", dpi=150)
        plt.close()

        # Figure 47: Top Cross-City Relationship Pairs
        plt.figure(figsize=(8.5, 4.5))
        cross_city_edges = edges_df[edges_df["cross_city"]].copy()
        if len(cross_city_edges) > 0:
            city_pairs = cross_city_edges.apply(
                lambda r: " <-> ".join(sorted([str(r["city_a"]), str(r["city_b"])])), axis=1
            ).value_counts().head(8)
            plt.barh(city_pairs.index[::-1], city_pairs.values[::-1], color="#F59E0B", edgecolor="black")
            for i, v in enumerate(city_pairs.values[::-1]):
                plt.text(v + 1, i, f"{v}", va="center", fontsize=9, fontweight="bold")
            plt.title("Figure 47: Top Observed Cross-City Relationship Corridors", fontsize=11, fontweight="bold")
            plt.xlabel("Cross-City Relationship Count")
        else:
            plt.text(0.5, 0.5, "No cross-city relationships detected", ha="center")
        plt.grid(axis="x", linestyle=":", alpha=0.6)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "47_cross_city_relationships.png", dpi=150)
        plt.close()

        # Figure 48: Top Cross-State Relationship Pairs
        plt.figure(figsize=(8.5, 4.5))
        cross_state_edges = edges_df[edges_df["cross_state"]].copy()
        if len(cross_state_edges) > 0:
            state_pairs = cross_state_edges.apply(
                lambda r: " <-> ".join(sorted([str(r["state_a"]), str(r["state_b"])])), axis=1
            ).value_counts().head(8)
            plt.barh(state_pairs.index[::-1], state_pairs.values[::-1], color="#06B6D4", edgecolor="black")
            for i, v in enumerate(state_pairs.values[::-1]):
                plt.text(v + 1, i, f"{v}", va="center", fontsize=9, fontweight="bold")
            plt.title("Figure 48: Top Observed Cross-State Relationship Corridors", fontsize=11, fontweight="bold")
            plt.xlabel("Cross-State Relationship Count")
        else:
            plt.text(0.5, 0.5, "No cross-state relationships detected", ha="center")
        plt.grid(axis="x", linestyle=":", alpha=0.6)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "48_cross_state_relationships.png", dpi=150)
        plt.close()

        # Figure 49: Component Product Family Diversity
        plt.figure(figsize=(7.5, 4.5))
        prod_dist = comp_df[comp_df["node_count"] > 1]["product_family_count"].value_counts().sort_index()
        plt.bar([str(x) for x in prod_dist.index], prod_dist.values, color="#6366F1", edgecolor="black")
        for i, v in enumerate(prod_dist.values):
            plt.text(i, v + max(prod_dist.values)*0.02, f"{v}", ha="center", fontsize=9, fontweight="bold")
        plt.title("Figure 49: Product Family Diversity per Component (Non-Singletons)", fontsize=11, fontweight="bold")
        plt.xlabel("Number of Distinct Product Families Represented")
        plt.ylabel("Component Count")
        plt.grid(axis="y", linestyle=":", alpha=0.6)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "49_component_product_distribution.png", dpi=150)
        plt.close()

        # Figure 50: Component Geographic Span
        plt.figure(figsize=(7.5, 4.5))
        geo_span = comp_df[comp_df["node_count"] > 1]["city_count"].apply(
            lambda c: "Single City" if c == 1 else ("2-3 Cities" if c <= 3 else "4+ Cities")
        ).value_counts()
        plt.bar(geo_span.index, geo_span.values, color=["#10B981", "#F59E0B", "#EF4444"][:len(geo_span)], edgecolor="black")
        for i, v in enumerate(geo_span.values):
            plt.text(i, v + max(geo_span.values)*0.02, f"{v}", ha="center", fontsize=9, fontweight="bold")
        plt.title("Figure 50: Geographic Span of Non-Singleton Connected Components", fontsize=11, fontweight="bold")
        plt.ylabel("Component Count")
        plt.grid(axis="y", linestyle=":", alpha=0.6)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "50_component_geography_distribution.png", dpi=150)
        plt.close()

        logger.info("Figures 43-50 generated successfully in %s", self.figures_dir)
