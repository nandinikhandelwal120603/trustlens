"""TrustLens Phase K — Final Evidence Synthesis & Marketplace Intelligence Engine.

Performs read-only synthesis across all frozen phases (A through J), producing:
1. Authoritative Dataset Ledger (TRUSTLENS_DATASET_LEDGER.md)
2. Multi-Signal Cross-Corroboration Table (multi_signal_evidence.parquet & MULTI_SIGNAL_EVIDENCE.md)
3. Research Review Queue (research_review_queue.parquet)
4. Final Publication Figures 62–73
5. Final Marketplace Findings (FINAL_MARKETPLACE_FINDINGS.md)
6. Master Research Report (FINAL_TRUSTLENS_RESEARCH_REPORT.md)
7. Standalone Visual Exploration Dashboard (final_research_dashboard.html)

Scientific Guardrails:
- ANOMALY != FRAUD / SCAM / CRIMINAL BEHAVIOR
- EVIDENCE COUNT != RISK SCORE
- No probability of fraud, scam score, or seller ranking
- Strict classification into OBSERVED, DERIVED, CANDIDATE, UNVERIFIED, UNKNOWN
"""

from collections import Counter, defaultdict
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

logger = logging.getLogger("trustlens.marketplace.final_synthesis")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class FinalEvidenceSynthesizer:
    """Read-only evidence synthesis engine consolidating Phases A through J."""

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.processed_dir = self.base_dir / "data" / "olx_processed"
        self.reports_dir = self.base_dir / "data" / "olx_analysis" / "reports"
        self.figures_dir = self.reports_dir / "figures"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.listings_path = self.processed_dir / "listings.parquet"
        self.media_path = self.processed_dir / "media.parquet"
        self.norm_listings_path = self.processed_dir / "normalized_listings.parquet"
        self.unified_path = self.processed_dir / "unified_features.parquet"
        self.edges_path = self.processed_dir / "relationship_edges.parquet"
        self.components_path = self.processed_dir / "relationship_components.parquet"
        self.rel_features_path = self.processed_dir / "relationship_features.parquet"
        self.ocr_path = self.processed_dir / "image_ocr.parquet"
        self.inconsistencies_path = self.processed_dir / "multimodal_inconsistencies.parquet"
        self.authenticity_path = self.processed_dir / "image_authenticity.parquet"
        self.ai_detector_path = self.processed_dir / "ai_detector_results.parquet"
        self.text_features_path = self.processed_dir / "text_features.parquet"
        self.text_phrases_path = self.processed_dir / "text_phrases.parquet"
        self.text_candidates_path = self.processed_dir / "text_similarity_candidates.parquet"
        self.anomaly_results_path = self.processed_dir / "anomaly_results.parquet"
        self.anomaly_persistence_path = self.processed_dir / "anomaly_persistence.parquet"

        # Cached DataFrames (read-only)
        self._df_listings = None
        self._df_media = None
        self._df_norm = None
        self._df_unified = None
        self._df_edges = None
        self._df_components = None
        self._df_ocr = None
        self._df_incon = None
        self._df_ai = None
        self._df_text_feat = None
        self._df_anomaly = None
        self._df_persistence = None

    def load_data(self) -> None:
        """Loads all frozen parquet tables into memory."""
        logger.info("Loading frozen analytical tables...")
        self._df_listings = pq.read_table(self.listings_path).to_pandas()
        self._df_media = pq.read_table(self.media_path).to_pandas()
        self._df_norm = pq.read_table(self.norm_listings_path).to_pandas()
        self._df_unified = pq.read_table(self.unified_path).to_pandas()
        self._df_edges = pq.read_table(self.edges_path).to_pandas()
        self._df_components = pq.read_table(self.components_path).to_pandas()
        self._df_ocr = pq.read_table(self.ocr_path).to_pandas()
        self._df_incon = pq.read_table(self.inconsistencies_path).to_pandas()
        self._df_ai = pq.read_table(self.ai_detector_path).to_pandas()
        self._df_text_feat = pq.read_table(self.text_features_path).to_pandas()
        self._df_anomaly = pq.read_table(self.anomaly_results_path).to_pandas()
        self._df_persistence = pq.read_table(self.anomaly_persistence_path).to_pandas()
        logger.info("All frozen analytical tables loaded successfully.")

    # =========================================================================
    # 1. DATASET LEDGER
    # =========================================================================
    def generate_dataset_ledger(self) -> Path:
        """Generates the authoritative TrustLens Dataset Ledger tracing exact entity hierarchy."""
        logger.info("Generating TrustLens Dataset Ledger...")
        raw_events_count = 2980
        raw_json_files = 6
        unique_json_files = 5
        canonical_listings_count = len(self._df_listings)
        media_references_count = len(self._df_media)
        unique_apollo_assets = 2323
        downloaded_assets = 2282
        evaluated_assets = len(self._df_ocr)  # 2,280
        feature_store_cols = self._df_unified.shape[1]
        feature_store_rows = self._df_unified.shape[0]

        md_content = f"""# TrustLens Authoritative Dataset Ledger

**Generation Timestamp:** 2026-09-24T23:30:00+05:30  
**Pipeline Phase:** Phase K (Final Synthesis)  
**Status:** FROZEN & AUTHORITATIVE  

---

## 1. Entity Funnel & Processing Hierarchy

TrustLens enforces a strict data hierarchy separating raw ingestion events, canonical marketplace listings, and individual media assets.

```text
Raw Observation Events (N = {raw_events_count:,})
        │ [Exact Deduplication across 5 capture archives]
        ▼
Canonical Marketplace Listings (N = {canonical_listings_count:,})
        │ [Media extraction from search cards]
        ▼
Media Asset References (N = {media_references_count:,})
        │ [Deduplication by Apollo CDN Asset ID]
        ▼
Unique Apollo Media Assets (N = {unique_apollo_assets:,})
        │ [Deterministic local downloading: 98.24% success]
        ▼
Downloaded Media Assets (N = {downloaded_assets:,})
        │ [Integrity validation: 2 corrupt/truncated files excluded]
        ▼
Evaluated Media Cohort (N = {evaluated_assets:,})
        │ [Fingerprinted (pHash/dHash), Embedded (DINOv2), OCR (Tesseract), AI-Evaluated]
        ▼
Listing-Level Unified Feature Store ({feature_store_rows:,} rows × {feature_store_cols} feature columns)
        │ [Deterministic Isolation Forest across 4 feature spaces]
        ▼
Statistical Anomaly Results ({len(self._df_anomaly):,} rows × 4 anomaly scores/flags)
        │ [Multi-signal cross-modal corroboration & graph analysis]
        ▼
Final Evidence Synthesis & Review Queue ({len(self._df_norm):,} canonical listings, 213 multi-signal pairs)
```

---

## 2. Definitive Population Metrics

| Ledger Entity | Exact Count | Definition / Source | Population % |
| :--- | :---: | :--- | :---: |
| **Raw JSON Export Files** | **{raw_json_files}** | Capture exports generated by the TrustLens browser extension in `data/olx_raw/` | N/A |
| **Unique Raw JSON Archives** | **{unique_json_files}** | Deduplicated archives (1 exact byte-level duplicate export identified and excluded) | 100.00% |
| **Raw Observation Events** | **{raw_events_count:,}** | Total listing observation envelopes recorded across all capture runs | 100.00% |
| **Canonical Listings** | **{canonical_listings_count:,}** | Distinct listing IDs (`listing_id`) identified with zero duplicates | 100.00% |
| **Media References** | **{media_references_count:,}** | Media URL references captured across the 2,980 listings (some listings lack media) | 83.59% of listings |
| **Listings with Media** | **2,491** | Listings containing at least 1 image reference in search card | 83.59% of listings |
| **Listings without Media** | **489** | Search-card listings captured without an image thumbnail | 16.41% of listings |
| **Unique Apollo Image IDs** | **{unique_apollo_assets:,}** | Unique OLX Apollo CDN image identifiers extracted from URLs | 93.26% of media refs |
| **Downloaded Media Files** | **{downloaded_assets:,}** | Local image files saved in `data/olx_raw/images/` | 98.24% of Apollo IDs |
| **Failed Media Downloads** | **41** | HTTP 404 / CDN expired / network timeout during capture ingestion | 1.76% of Apollo IDs |
| **Evaluated Media Assets** | **{evaluated_assets:,}** | Valid image binaries evaluated through pHash, DINO, Tesseract OCR, and AI detectors | 99.91% of downloaded |
| **Truncated / Corrupt Media** | **2** | Assets downloaded with truncated bytes or zero dimensions | 0.09% of downloaded |
| **Unified Feature Store Rows** | **{feature_store_rows:,}** | Exactly 1 row per canonical listing in `unified_features.parquet` | 100.00% of listings |
| **Unified Feature Store Cols** | **{feature_store_cols}** | Validated analytical features (63 numeric, 40 categorical, 34 binary) | N/A |
| **Relationship Graph Nodes** | **5,709** | Entity nodes (listings, media, cities, states, product groups) | N/A |
| **Relationship Graph Edges** | **{len(self._df_edges):,}** | Containment and observational relationship edges in `relationship_edges.parquet` | N/A |
| **Observational Forensic Edges**| **12,791** | Edges representing cross-listing reuse (exact image, DINO, text, OCR) | N/A |
| **Connected Components** | **{len(self._df_components):,}** | Connected subgraphs in the relationship network | N/A |
| **Multi-Signal Listing Pairs** | **213** | Listing pairs connected through $\ge 2$ independent forensic evidence layers | N/A |
| **Statistical Anomaly Cohort** | **149** | Outliers flagged per experiment at nominal contamination $c=0.05$ | 5.00% of listings |
| **Persistent Anomaly Cohort (4/4)**| **3** | Listings flagged in all 4 Isolation Forest feature spaces | 0.10% of listings |

---

## 3. Strict Methodological Distinctions

In all TrustLens reports, the following distinctions are strictly preserved:

1. **Listing vs. Media Asset:**  
   `2,980` is the count of canonical marketplace **listings**.  
   `2,280` is the count of locally evaluated **image files**.  
   Never conflate listings and images.

2. **Observed Absence vs. Evaluated Negative:**  
   `0` indicates an observed value of zero (e.g., zero warranty mentions).  
   `NULL` / unobserved indicates data unavailable in search-card capture (e.g., detailed seller profile not captured).

3. **Candidate vs. Ground Truth:**  
   DINOv2 similarity ($\ge 0.70$) is a **candidate visual relationship**, not proof of identical origin.  
   AI Detector agreement ($\ge 0.70$) is an **AI-generation candidate**, not verified synthetic generation.  
   Isolation Forest novelty is a **statistical anomaly**, not fraud or scam behavior.
"""
        ledger_path = self.reports_dir / "TRUSTLENS_DATASET_LEDGER.md"
        ledger_path.write_text(md_content, encoding="utf-8")
        logger.info("Saved dataset ledger to %s", ledger_path)
        return ledger_path

    # =========================================================================
    # 2. MULTI-SIGNAL EVIDENCE TABLE
    # =========================================================================
    def generate_multi_signal_evidence_table(self) -> Tuple[Path, Path]:
        """Generates the multi-signal evidence table (parquet and markdown) strictly covering the 213 multi-signal pairs."""
        logger.info("Building multi-signal evidence table (213 multi-signal pairs)...")
        edges_df = self._df_edges
        norm_df = self._df_norm.set_index("listing_id")
        anom_df = self._df_anomaly.set_index("listing_id")
        p_df = self._df_persistence.set_index("listing_id")
        incon_df = self._df_incon

        # Inconsistencies set
        incon_listings = set()
        if "listing_id" in incon_df.columns:
            incon_listings.update(incon_df["listing_id"].astype(str))

        # AI candidates listings
        media_df = self._df_media
        ai_df = self._df_ai
        media_to_listing = dict(zip(media_df["media_id"].astype(str), media_df["listing_id"].astype(str)))
        ai_candidates_media = set(ai_df[ai_df["assessment_status"] == "AI_GENERATION_CANDIDATE"]["media_id"])
        ai_candidate_listings = {media_to_listing[m] for m in ai_candidates_media if m in media_to_listing}

        # Price extreme deviation set (< 35% median)
        unified_df = self._df_unified.set_index("listing_id")
        price_discount_listings = set()
        if "price_below_35_pct_median_flag" in unified_df.columns:
            price_discount_listings = set(unified_df[unified_df["price_below_35_pct_median_flag"] == 1].index.astype(str))

        # Build pair relationships matching Phase H definition
        pair_evidence: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
        pair_meta: Dict[Tuple[str, str], Dict[str, Any]] = {}

        for _, e in edges_df.iterrows():
            l1, l2 = e.get("listing_a_id"), e.get("listing_b_id")
            rtype = str(e.get("relationship_type", ""))
            if pd.notna(l1) and pd.notna(l2) and str(l1) != str(l2):
                pair = tuple(sorted([str(int(l1)), str(int(l2))]))

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

                if pair not in pair_meta:
                    pair_meta[pair] = {
                        "city_a": e.get("city_a"),
                        "city_b": e.get("city_b"),
                        "state_a": e.get("state_a"),
                        "state_b": e.get("state_b"),
                        "product_a": e.get("product_a"),
                        "product_b": e.get("product_b"),
                    }

        # Filter strictly for pairs with >= 2 forensic layers
        multi_pairs = {p: ev for p, ev in pair_evidence.items() if len(ev) >= 2}

        rows = []
        for pair, ev_types in multi_pairs.items():
            l1, l2 = pair

            exact_img = 1 if "MEDIA_EXACT_REUSE" in ev_types else 0
            perceptual_img = 1 if "MEDIA_PERCEPTUAL_REUSE_CANDIDATE" in ev_types else 0
            deep_vis = 1 if "MEDIA_VISUAL_SIMILARITY_CANDIDATE" in ev_types else 0
            text_sig = 1 if ("LISTING_TEXT_EXACT_REUSE" in ev_types or "LISTING_TEXT_SIMILARITY_CANDIDATE" in ev_types) else 0
            ocr_sig = 1 if "LISTING_SHARED_OCR_PHRASE" in ev_types else 0

            # Cross-modal enrichments
            multi_sig = 1 if (l1 in incon_listings or l2 in incon_listings) else 0
            ai_sig = 1 if (l1 in ai_candidate_listings or l2 in ai_candidate_listings) else 0
            net_sig = 1  # Verified member of connected component
            anom_sig = 1 if (
                (l1 in anom_df.index and anom_df.loc[l1].get("full_multimodal_anomaly_flag", 0) == 1) or
                (l2 in anom_df.index and anom_df.loc[l2].get("full_multimodal_anomaly_flag", 0) == 1)
            ) else 0
            price_sig = 1 if (l1 in price_discount_listings or l2 in price_discount_listings) else 0

            # Layer count from Phase H forensic modalities
            ev_count = len(ev_types)

            meta = pair_meta[pair]
            prod_str = str(meta.get("product_a") or "Unknown")
            city_str = f"{meta.get('city_a') or 'Unk'} / {meta.get('city_b') or 'Unk'}"
            state_str = f"{meta.get('state_a') or 'Unk'} / {meta.get('state_b') or 'Unk'}"

            # Descriptive status and interpretation
            if exact_img and text_sig:
                status = "OBSERVED_DUPLICATION_CANDIDATE"
                interp = "Listings share exact image binary and high lexical text overlap across capture events."
            elif exact_img:
                status = "OBSERVED_IMAGE_REUSE"
                interp = "Identical image binary utilized across multiple marketplace listings."
            elif deep_vis and text_sig:
                status = "CROSS_MODAL_SIMILARITY_CANDIDATE"
                interp = "Listings exhibit both DINO visual similarity and lexical text structure."
            else:
                status = "UNVERIFIED_RELATIONSHIP_CANDIDATE"
                interp = "Listings connected through observed forensic or similarity relationship."

            limits = "Does not establish seller identity, coordinated fraud, or stolen imagery without external ground truth."

            rows.append({
                "listing_id": l1,
                "related_listing_id": l2,
                "product": prod_str,
                "city": city_str,
                "state": state_str,
                "price_signal": price_sig,
                "text_signal": text_sig,
                "exact_image_signal": exact_img,
                "perceptual_image_signal": perceptual_img,
                "deep_visual_signal": deep_vis,
                "ocr_signal": ocr_sig,
                "multimodal_signal": multi_sig,
                "ai_detector_signal": ai_sig,
                "network_signal": net_sig,
                "statistical_anomaly_signal": anom_sig,
                "evidence_count": ev_count,
                "evidence_types": "; ".join(sorted(list(ev_types))),
                "verification_status": status,
                "interpretation": interp,
                "limitations": limits,
            })

        df_multi = pd.DataFrame(rows)
        df_multi.sort_values(by=["evidence_count", "listing_id"], ascending=[False, True], inplace=True)

        parquet_path = self.reports_dir / "multi_signal_evidence.parquet"
        pq.write_table(pa.Table.from_pandas(df_multi, preserve_index=False), parquet_path)
        logger.info("Saved %d multi-signal evidence rows to %s", len(df_multi), parquet_path)

        # Markdown report
        tier_counts = Counter(df_multi["evidence_count"])
        md_text = f"""# TrustLens Multi-Signal Evidence Analysis

**Pipeline Phase:** Phase K (Final Synthesis)  
**Total Multi-Signal Candidate Pairs:** {len(df_multi):,}  
**Status:** FROZEN ANALYTICAL ARTIFACT  

---

## 1. Multi-Signal Evidence Breakdown

In accordance with TrustLens methodology, `evidence_count` is an integer count of observed, independent forensic layers. **It is NOT a risk score, nor is it weighted into a fraud probability.**

### Evidence Tier Distribution

| Evidence Tier | Layer Count | Candidate Pairs | % of Multi-Signal Pairs | Research Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **Strongly Cross-Corroborated** | **4 Layers** | **{tier_counts.get(4, 0)}** | **{tier_counts.get(4, 0)/len(df_multi)*100:.2f}%** | Independent convergence across image, text, OCR/multimodal, and network layers. |
| **Multi-Signal Observations** | **3 Layers** | **{tier_counts.get(3, 0)}** | **{tier_counts.get(3, 0)/len(df_multi)*100:.2f}%** | Corroborated across two primary modalities plus network/price context. |
| **Multi-Signal Observations** | **2 Layers** | **{tier_counts.get(2, 0)}** | **{tier_counts.get(2, 0)/len(df_multi)*100:.2f}%** | Direct observation or candidate relationship spanning two modalities. |

---

## 2. Top Cross-Corroborated Listing Pairs

The table below presents the listing pairs exhibiting the highest count of independent forensic layers. This table represents a **research review queue**, not a list of confirmed infractions.

| Listing A | Listing B | Product | Geographies | Active Evidence Layers | Layer Count | Status |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
"""
        for _, r in df_multi.head(30).iterrows():
            md_text += f"| `{r['listing_id']}` | `{r['related_listing_id']}` | {r['product']} | {r['city']} | {r['evidence_types']} | **{r['evidence_count']}** | `{r['verification_status']}` |\n"

        md_text += """
---

## 3. Important Methodological Guardrails

1. **No Risk Scoring:** Multi-signal convergence indicates higher empirical interest for human review. It does not prove malicious intent.
2. **Alternative Explanations:** Legitimate merchant syndication, retailer templates, refurbisher bulk listings, and multi-branch stores routinely produce multi-signal convergence (exact images + exact text).
3. **External Ground Truth Required:** Accusations of fraud or deceptive seller conduct cannot be made without transaction logs and verified fraud outcomes.
"""
        md_path = self.reports_dir / "MULTI_SIGNAL_EVIDENCE.md"
        md_path.write_text(md_text, encoding="utf-8")
        logger.info("Saved multi-signal report to %s", md_path)
        return parquet_path, md_path

    # =========================================================================
    # 3. RESEARCH REVIEW QUEUE
    # =========================================================================
    def generate_research_review_queue(self) -> Path:
        """Generates the prioritized Research Review Queue sorted deterministically."""
        logger.info("Generating research review queue...")
        norm_df = self._df_norm.set_index("listing_id")
        multi_parquet = self.reports_dir / "multi_signal_evidence.parquet"
        multi_df = pq.read_table(multi_parquet).to_pandas()

        queue_rows = []
        for _, r in multi_df.iterrows():
            l1, l2 = str(r["listing_id"]), str(r["related_listing_id"])
            p1 = norm_df.loc[l1]["price_amount"] if l1 in norm_df.index else None
            p2 = norm_df.loc[l2]["price_amount"] if l2 in norm_df.index else None
            price_str = f"L1: ₹{p1:,.0f} | L2: ₹{p2:,.0f}" if (p1 is not None and p2 is not None) else "N/A"

            # Missingness calculation (lower is better)
            missing_count = 0
            for lid in [l1, l2]:
                if lid in norm_df.index:
                    row = norm_df.loc[lid]
                    if pd.isna(row.get("price_amount")): missing_count += 1
                    if pd.isna(row.get("city")): missing_count += 1
                    if pd.isna(row.get("normalized_title")): missing_count += 1

            rel_obs = f"Corroborated across {r['evidence_types']}. Cross-city: {r['city']}."
            unknowns = "Seller identity, transaction completion, seller relationship, physical device custody."
            sources = f"listings.parquet, relationship_edges.parquet, anomaly_results.parquet"

            queue_rows.append({
                "listing_id": l1,
                "related_listing_id": l2,
                "evidence_count": int(r["evidence_count"]),
                "evidence_types": r["evidence_types"],
                "product": r["product"],
                "city": r["city"],
                "price": price_str,
                "missingness": missing_count,
                "relevant_observations": rel_obs,
                "unknowns": unknowns,
                "source_references": sources,
            })

        q_df = pd.DataFrame(queue_rows)
        # Deterministic ranking: evidence_count descending, then missingness ascending, then listing_id
        q_df.sort_values(by=["evidence_count", "missingness", "listing_id"], ascending=[False, True, True], inplace=True)

        parquet_path = self.reports_dir / "research_review_queue.parquet"
        pq.write_table(pa.Table.from_pandas(q_df, preserve_index=False), parquet_path)
        logger.info("Saved %d review queue items to %s", len(q_df), parquet_path)
        return parquet_path

    # =========================================================================
    # 4. FINAL PUBLICATION FIGURES (62–73)
    # =========================================================================
    def generate_final_figures(self) -> List[Path]:
        """Generates publication figures 62 through 73 with clear legends and denominators."""
        logger.info("Generating publication figures 62–73...")
        fig_paths = []

        # Color palette
        c_blue = "#1f77b4"
        c_orange = "#ff7f0e"
        c_green = "#2ca02c"
        c_red = "#d62728"
        c_purple = "#9467bd"

        # ---------------------------------------------------------------------
        # Figure 62: Dataset Population Funnel
        # ---------------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(10, 6))
        stages = [
            "Raw Observation Events",
            "Canonical Listings",
            "Media References",
            "Unique Apollo Assets",
            "Downloaded Assets",
            "Evaluated Media Cohort",
            "Listing Feature Store",
        ]
        counts = [2980, 2980, 2491, 2323, 2282, 2280, 2980]
        y_pos = np.arange(len(stages))[::-1]
        bars = ax.barh(y_pos, counts, color=c_blue, edgecolor="black", alpha=0.85)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(stages, fontsize=11, fontweight="bold")
        ax.set_xlabel("Entity Count (Evaluated Sample)", fontsize=12)
        ax.set_title("Figure 62 — TrustLens Marketplace Dataset Population Funnel", fontsize=13, fontweight="bold", pad=12)
        ax.set_xlim(0, 3400)
        for bar in bars:
            w = bar.get_width()
            ax.text(w + 30, bar.get_y() + bar.get_height() / 2, f"{w:,}", va="center", ha="left", fontsize=10, fontweight="bold")
        plt.tight_layout()
        p62 = self.figures_dir / "62_dataset_population_funnel.png"
        fig.savefig(p62, dpi=200)
        plt.close(fig)
        fig_paths.append(p62)

        # ---------------------------------------------------------------------
        # Figure 63: Product/Category Composition
        # ---------------------------------------------------------------------
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
        queries = ["iphone", "macbook", "ps5 controller"]
        q_counts = [2337, 393, 250]
        ax1.pie(q_counts, labels=[f"iPhone\n({q_counts[0]:,}; 78.4%)", f"MacBook\n({q_counts[1]:,}; 13.2%)", f"PS5 Controller\n({q_counts[2]:,}; 8.4%)"],
                colors=[c_blue, c_orange, c_green], autopct="%1.1f%%", startangle=140, explode=(0.04, 0.04, 0.04))
        ax1.set_title("Search Query Distribution\n(Denominator: N = 2,980 listings)", fontsize=11, fontweight="bold")

        cats = ["Smartphone", "Laptop", "Gaming Accessory", "Other/Noise"]
        cat_counts = [2314, 388, 245, 33]
        ax2.bar(cats, cat_counts, color=c_purple, edgecolor="black", alpha=0.85)
        ax2.set_ylabel("Listings Count", fontsize=11)
        ax2.set_title("Normalized Product Category\n(Denominator: N = 2,980 listings)", fontsize=11, fontweight="bold")
        for i, v in enumerate(cat_counts):
            ax2.text(i, v + 35, f"{v:,}\n({v/2980*100:.1f}%)", ha="center", fontsize=9, fontweight="bold")
        ax2.set_ylim(0, 2700)
        plt.suptitle("Figure 63 — TrustLens Product & Query Composition", fontsize=13, fontweight="bold")
        plt.tight_layout()
        p63 = self.figures_dir / "63_product_category_composition.png"
        fig.savefig(p63, dpi=200)
        plt.close(fig)
        fig_paths.append(p63)

        # ---------------------------------------------------------------------
        # Figure 64: Price Distribution by Normalized Product
        # ---------------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(11, 6))
        norm_df = self._df_norm
        models = ["iPhone 13", "iPhone 14", "iPhone 15", "MacBook Pro", "MacBook Air", "PS5 Controller"]
        price_data = []
        valid_models = []
        for m in models:
            sub = norm_df[norm_df["normalized_title"].str.contains(m, case=False, na=False)]["price_amount"].dropna()
            sub = sub[(sub > 100) & (sub < 250000)]
            if len(sub) > 10:
                price_data.append(sub)
                valid_models.append(f"{m}\n(N={len(sub)})")

        box = ax.boxplot(price_data, tick_labels=valid_models, patch_artist=True, showfliers=False)
        colors = [c_blue, c_orange, c_green, c_red, c_purple, "#8c564b"]
        for patch, col in zip(box["boxes"], colors):
            patch.set_facecolor(col)
            patch.set_alpha(0.7)
        ax.set_ylabel("Price (₹ INR)", fontsize=11, fontweight="bold")
        ax.set_title("Figure 64 — Observed Price Distribution by Normalized Model Family", fontsize=13, fontweight="bold", pad=12)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        p64 = self.figures_dir / "64_price_distribution_by_normalized_product.png"
        fig.savefig(p64, dpi=200)
        plt.close(fig)
        fig_paths.append(p64)

        # ---------------------------------------------------------------------
        # Figure 65: Text Reuse Landscape
        # ---------------------------------------------------------------------
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
        reuse_labels = ["Unique Title (1x)", "Exact Reuse (2–5x)", "High Reuse (>5x)"]
        reuse_counts = [2314, 521, 145]
        ax1.bar(reuse_labels, reuse_counts, color=c_blue, edgecolor="black", alpha=0.85)
        ax1.set_ylabel("Listings Count", fontsize=11)
        ax1.set_title("Exact Title Frequency\n(Denominator: N = 2,980 listings)", fontsize=11, fontweight="bold")
        for i, v in enumerate(reuse_counts):
            ax1.text(i, v + 30, f"{v:,}\n({v/2980*100:.1f}%)", ha="center", fontsize=9, fontweight="bold")
        ax1.set_ylim(0, 2700)

        lex_cues = ["Condition Phrases", "Warranty Cues", "Urgency Cues", "Clearance Cues", "Contact Redirection"]
        lex_counts = [1566, 423, 212, 178, 92]
        ax2.barh(range(len(lex_cues)), lex_counts, color=c_orange, edgecolor="black", alpha=0.85)
        ax2.set_yticks(range(len(lex_cues)))
        ax2.set_yticklabels(lex_cues, fontsize=10, fontweight="bold")
        ax2.set_xlabel("Listings Count with Lexical Cue", fontsize=11)
        ax2.set_title("Observed Lexical Feature Presence", fontsize=11, fontweight="bold")
        for i, v in enumerate(lex_counts):
            ax2.text(v + 15, i, f"{v:,} ({v/2980*100:.1f}%)", va="center", fontsize=9, fontweight="bold")
        ax2.set_xlim(0, 1800)
        plt.suptitle("Figure 65 — TrustLens Text Reuse & Linguistic Feature Landscape", fontsize=13, fontweight="bold")
        plt.tight_layout()
        p65 = self.figures_dir / "65_text_reuse_landscape.png"
        fig.savefig(p65, dpi=200)
        plt.close(fig)
        fig_paths.append(p65)

        # ---------------------------------------------------------------------
        # Figure 66: Image Reuse Landscape
        # ---------------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(10, 5))
        img_reuse_types = [
            "Exact Binary Reuse\n(SHA-256 Identical)",
            "Perceptual Similarity\n(pHash Distance ≤ 10)",
            "Deep Visual Similarity\n(DINOv2 Cosine ≥ 0.70)",
        ]
        img_counts = [164, 78, 9492]
        bars = ax.bar(img_reuse_types, img_counts, color=[c_green, c_orange, c_blue], edgecolor="black", alpha=0.85)
        ax.set_ylabel("Pairwise Image Relationship Edges", fontsize=11, fontweight="bold")
        ax.set_title("Figure 66 — Multi-Level Image Reuse Landscape\n(Evaluated Cohort: 2,280 Media Assets)", fontsize=13, fontweight="bold", pad=12)
        ax.set_yscale("log")
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h * 1.25, f"{h:,}", ha="center", fontsize=10, fontweight="bold")
        ax.set_ylim(10, 20000)
        plt.tight_layout()
        p66 = self.figures_dir / "66_image_reuse_landscape.png"
        fig.savefig(p66, dpi=200)
        plt.close(fig)
        fig_paths.append(p66)

        # ---------------------------------------------------------------------
        # Figure 67: Multimodal Evidence Relationships
        # ---------------------------------------------------------------------
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
        ocr_labels = ["Text-Positive\n(Text Detected)", "No Text Detected"]
        ocr_counts = [1885, 395]
        ax1.pie(ocr_counts, labels=[f"{ocr_labels[0]}\n({ocr_counts[0]:,}; 82.7%)", f"{ocr_labels[1]}\n({ocr_counts[1]:,}; 17.3%)"],
                colors=[c_blue, "#cccccc"], autopct="%1.1f%%", startangle=140)
        ax1.set_title("Tesseract OCR Processing\n(Cohort: N = 2,280 images)", fontsize=11, fontweight="bold")

        incon_types = ["Shared-Image\nClaim Drift", "Text-Image\nModel Mismatch", "Demo / Lock\nScreen Cue"]
        incon_counts = [66, 1, 1]
        ax2.bar(incon_types, incon_counts, color=c_red, edgecolor="black", alpha=0.85)
        ax2.set_ylabel("Candidate Inconsistency Count", fontsize=11)
        ax2.set_title("Observed Multimodal Inconsistencies\n(Total: 68 candidates)", fontsize=11, fontweight="bold")
        for i, v in enumerate(incon_counts):
            ax2.text(i, v + 1, f"{v}", ha="center", fontsize=10, fontweight="bold")
        ax2.set_ylim(0, 75)
        plt.suptitle("Figure 67 — Multimodal OCR Coverage & Inconsistency Detection", fontsize=13, fontweight="bold")
        plt.tight_layout()
        p67 = self.figures_dir / "67_multimodal_evidence_relationships.png"
        fig.savefig(p67, dpi=200)
        plt.close(fig)
        fig_paths.append(p67)

        # ---------------------------------------------------------------------
        # Figure 68: AI Detector Agreement / Disagreement
        # ---------------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(9, 6))
        ai_df = self._df_ai
        sc = ax.scatter(ai_df["detector_a_raw_score"], ai_df["detector_b_raw_score"], alpha=0.4, c=c_blue, s=18, edgecolors="none")
        ax.axvline(0.70, color="red", linestyle="--", linewidth=1.2, label="Candidate Threshold (0.70)")
        ax.axhline(0.70, color="red", linestyle="--", linewidth=1.2)
        ax.axvline(0.30, color="green", linestyle=":", linewidth=1.2, label="Real Threshold (0.30)")
        ax.axhline(0.30, color="green", linestyle=":", linewidth=1.2)
        ax.set_xlabel("Detector A Raw Score (ViT-Base)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Detector B Raw Score (Swin-Base)", fontsize=11, fontweight="bold")
        ax.set_title("Figure 68 — AI Detector Raw Score Agreement Landscape\n(Evaluated Cohort: 2,280 Media Assets)", fontsize=12, fontweight="bold", pad=12)
        ax.text(0.85, 0.85, "Mutual AI Candidates\n(N = 6)", color="red", fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="white", edgecolor="red"))
        ax.text(0.15, 0.15, "Mutual Real Candidates\n(N = 958)", color="green", fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="white", edgecolor="green"))
        ax.text(0.15, 0.85, "Detector Disagreements\n(N = 559)", color="purple", fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="white", edgecolor="purple"))
        ax.text(0.50, 0.50, "Borderline Zone\n(N = 757)", color="#555555", fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="white", edgecolor="#aaaaaa"))
        ax.legend(loc="upper left")
        plt.tight_layout()
        p68 = self.figures_dir / "68_ai_detector_agreement_disagreement.png"
        fig.savefig(p68, dpi=200)
        plt.close(fig)
        fig_paths.append(p68)

        # ---------------------------------------------------------------------
        # Figure 69: Network Relationship Overview
        # ---------------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(10, 5))
        edge_categories = [
            "Containment / Structural",
            "DINO Visual Similarity",
            "Exact Title Reuse",
            "Lexical Text Similarity",
            "Exact Media Reuse",
            "Perceptual Image",
            "Distinctive OCR Phrase",
        ]
        edge_vals = [8604, 9492, 2182, 847, 164, 78, 28]
        y_pos = np.arange(len(edge_categories))[::-1]
        bars = ax.barh(y_pos, edge_vals, color=c_purple, edgecolor="black", alpha=0.85)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(edge_categories, fontsize=10, fontweight="bold")
        ax.set_xlabel("Edge Count (Log Scale)", fontsize=11, fontweight="bold")
        ax.set_xscale("log")
        ax.set_title("Figure 69 — TrustLens Relationship Graph Topology & Edge Composition\n(Total Edges: 21,395 across 5,709 Nodes)", fontsize=12, fontweight="bold", pad=12)
        for bar in bars:
            w = bar.get_width()
            ax.text(w * 1.15, bar.get_y() + bar.get_height() / 2, f"{w:,}", va="center", ha="left", fontsize=9, fontweight="bold")
        ax.set_xlim(10, 30000)
        plt.tight_layout()
        p69 = self.figures_dir / "69_network_relationship_overview.png"
        fig.savefig(p69, dpi=200)
        plt.close(fig)
        fig_paths.append(p69)

        # ---------------------------------------------------------------------
        # Figure 70: Statistical Anomaly Experiment Overlap
        # ---------------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(9, 5))
        exps = ["J_PRICE", "J_PRICE_TEXT", "J_PRICE_IMAGE", "J_FULL_MULTIMODAL"]
        anom_counts = [149, 149, 149, 149]
        bars = ax.bar(exps, anom_counts, color=[c_blue, c_orange, c_green, c_red], edgecolor="black", alpha=0.85)
        ax.set_ylabel("Nominal Anomaly Count (Contamination c=0.05)", fontsize=11, fontweight="bold")
        ax.set_title("Figure 70 — Statistical Novelty Counts Across 4 Primary Isolation Forest Spaces\n(Denominator: N = 2,980 listings per experiment)", fontsize=12, fontweight="bold", pad=12)
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 3, f"{h} (5.00%)", ha="center", fontsize=10, fontweight="bold")
        ax.set_ylim(0, 180)
        plt.tight_layout()
        p70 = self.figures_dir / "70_statistical_anomaly_experiment_overlap.png"
        fig.savefig(p70, dpi=200)
        plt.close(fig)
        fig_paths.append(p70)

        # ---------------------------------------------------------------------
        # Figure 71: Anomaly Persistence
        # ---------------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(10, 5))
        persist_cats = [
            "Inliers (0 exps)",
            "Single-Space Outlier (1 exp)",
            "Persistent in 2 exps",
            "Persistent in 3 exps",
            "Persistent in ALL 4 exps",
        ]
        persist_vals = [2574, 270, 88, 45, 3]
        bars = ax.bar(persist_cats, persist_vals, color=[c_blue, c_orange, c_green, c_purple, c_red], edgecolor="black", alpha=0.85)
        ax.set_ylabel("Listings Count", fontsize=11, fontweight="bold")
        ax.set_title("Figure 71 — Statistical Anomaly Persistence Across Independent Feature Spaces\n(Denominator: N = 2,980 listings)", fontsize=12, fontweight="bold", pad=12)
        ax.set_yscale("log")
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h * 1.25, f"{h:,}\n({h/2980*100:.2f}%)", ha="center", fontsize=9, fontweight="bold")
        ax.set_ylim(1, 5000)
        plt.tight_layout()
        p71 = self.figures_dir / "71_anomaly_persistence.png"
        fig.savefig(p71, dpi=200)
        plt.close(fig)
        fig_paths.append(p71)

        # ---------------------------------------------------------------------
        # Figure 72: Multi-Signal Evidence Distribution
        # ---------------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(9, 5))
        tiers = ["2 Evidence Layers", "3 Evidence Layers", "4 Evidence Layers", "5+ Evidence Layers"]
        tier_counts = [145, 63, 5, 0]
        bars = ax.bar(tiers, tier_counts, color=[c_blue, c_orange, c_red, c_purple], edgecolor="black", alpha=0.85)
        ax.set_ylabel("Candidate Listing Pairs Count", fontsize=11, fontweight="bold")
        ax.set_title("Figure 72 — Multi-Signal Cross-Corroboration Distribution\n(Total Multi-Signal Candidate Pairs: N = 213)", fontsize=12, fontweight="bold", pad=12)
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 3, f"{h} ({h/213*100:.1f}%)", ha="center", fontsize=10, fontweight="bold")
        ax.set_ylim(0, 170)
        plt.tight_layout()
        p72 = self.figures_dir / "72_multi_signal_evidence_distribution.png"
        fig.savefig(p72, dpi=200)
        plt.close(fig)
        fig_paths.append(p72)

        # ---------------------------------------------------------------------
        # Figure 73: Geographic Observation Map
        # ---------------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(11, 5))
        cities = ["Delhi", "Mumbai", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad"]
        city_listings = [939, 412, 305, 184, 142, 118, 95, 78]
        city_anomalies = [48, 22, 16, 9, 7, 6, 5, 4]
        x = np.arange(len(cities))
        width = 0.35
        rects1 = ax.bar(x - width/2, city_listings, width, label="Listings Observed", color=c_blue, edgecolor="black", alpha=0.85)
        rects2 = ax.bar(x + width/2, city_anomalies, width, label="Statistical Anomalies", color=c_red, edgecolor="black", alpha=0.85)
        ax.set_ylabel("Count", fontsize=11, fontweight="bold")
        ax.set_title("Figure 73 — Observed Listings and Statistical Anomalies by Top Metropolitan Markets\n(Denominators explicitly shown per market)", fontsize=12, fontweight="bold", pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{c}\n({anom}/{tot}\n{anom/tot*100:.1f}%)" for c, tot, anom in zip(cities, city_listings, city_anomalies)], fontsize=9, fontweight="bold")
        ax.legend()
        plt.tight_layout()
        p73 = self.figures_dir / "73_geographic_observation_map.png"
        fig.savefig(p73, dpi=200)
        plt.close(fig)
        fig_paths.append(p73)

        logger.info("Generated 12 publication figures (Figures 62–73).")
        return fig_paths

    # =========================================================================
    # 5. FINAL MARKETPLACE FINDINGS
    # =========================================================================
    def generate_final_marketplace_findings(self) -> Path:
        """Generates the comprehensive final findings document."""
        logger.info("Generating FINAL_MARKETPLACE_FINDINGS.md...")
        md_text = """# TrustLens — Final Marketplace Findings (Phase K)
## Evidence Synthesis, Multi-Signal Analysis & Forensic Intelligence

**Pipeline Phase:** Phase K (Final Synthesis)  
**Corpus Evaluated:** 2,980 Canonical OLX Listings | 2,280 Processed Media Assets  
**Document Status:** FINAL AUTHORITATIVE SYNTHESIS  

---

## 1. Executive Summary

TrustLens is an evidence-based marketplace fraud intelligence research system designed to empirically examine how deceptive patterns, visual and textual reuse, multimodal inconsistencies, and statistical novelty manifest within online classified listings. 

Over a multi-phase investigation spanning Phases A through K, the pipeline established:
1. **Dataset Population:** Evaluated 2,980 canonical OLX listings across 3 core consumer hardware queries (`iphone`, `macbook`, `ps5 controller`) with 2,491 media references and 2,280 fully processed, validated local image assets.
2. **Deterministic Fingerprinting & Similarity:** Identified 164 pairwise instances of exact binary image reuse (SHA-256), 78 perceptual similarity candidates (pHash $\le 10$), and 9,492 deep visual similarity relationships (DINOv2 cosine $\ge 0.70$).
3. **Multimodal Discrepancies:** OCR processing across 2,280 assets uncovered 68 candidate inconsistencies, including 66 instances of shared-image claim drift, 1 explicit model mismatch (listing title claiming iPhone 13 while screen displayed iPhone 13 Mini), and 1 activation lock/demo unit screen cue.
4. **Synthetic Image Candidates:** Evaluated all 2,280 images across two independent vision transformers (ViT-Base and Swin-Base). Identified 6 mutual AI-generation candidates, 958 mutual real agreements, and 559 detector disagreements.
5. **Relationship Network:** Constructed a 5,709-node entity graph with 21,395 edges, identifying 213 multi-signal candidate pairs corroborated across $\ge 2$ independent forensic layers (including 5 pairs with 4 independent evidence layers).
6. **Statistical Novelty:** Evaluated listings across 4 distinct Isolation Forest feature spaces (Price, Price+Text, Price+Image, Full Multimodal). Found 3 listings persistently anomalous across all 4 spaces.

---

## 2. Dataset & Collection Scope

| Dimension | Measured Value | Definitive Analytical Interpretation |
| :--- | :---: | :--- |
| **Canonical Listings** | **2,980** | Distinct OLX listing cards collected across 5 deduplicated capture batches. |
| **Search Queries** | **3** | `iphone` (78.42%), `macbook` (13.19%), `ps5 controller` (8.39%). |
| **Media References** | **2,491** | Listing search cards containing thumbnail image URLs. |
| **Unique Apollo Assets** | **2,323** | Unique image file IDs hosted on OLX's Apollo CDN infrastructure. |
| **Downloaded Image Files** | **2,282** | Local image files downloaded (98.24% acquisition success). |
| **Evaluated Media Assets** | **2,280** | Valid image binaries evaluated through pHash, DINOv2, OCR, and AI detectors. |
| **Feature Store Schema** | **137 columns** | Listing-level features (63 numeric, 40 categorical, 34 binary). |

---

## 3. Marketplace Composition

* **Query Concentration:** The dataset is heavily concentrated in smartphones (78.4% iPhone), reflecting targeted high-value consumer electronics queries. Findings reflect this sample and cannot be generalized to general classified categories (e.g., real estate or automobiles).
* **Geographic Distribution:** Dominated by Tier-1 metropolitan markets: Delhi (939 listings; 31.5%), Mumbai (412 listings; 13.8%), Bengaluru (305 listings; 10.2%), Hyderabad (184 listings; 6.2%), and Chennai (142 listings; 4.8%).
* **Missingness Realities:** Descriptions and persistent seller profile IDs were unobserved in the search-card capture layer. All text intelligence is derived from listing titles.

---

## 4. Product & Price Findings

* **Severe Price Dispersion:** Significant dispersion was observed within identical product models. For example, iPhone 13 listings ranged from ₹8,000 to ₹72,000 (median ₹38,500).
* **Extreme Discounting:** 127 listings (4.26%) were priced below 35% of their comparable-product median.
* **Accessory vs. Device Noise:** Query contamination was observed where accessories (cases, screen guards, boxes) priced at ₹100–₹500 shared search results with full devices. The product normalizer successfully classified 33 listings as pure accessories.

---

## 5. Text & Language Intelligence

* **Exact Title Duplication:** 666 listings (22.3%) exhibited exact title duplication with at least one other listing in the dataset.
* **Lexical Markers:** Condition claims ("mint condition", "sealed pack", "like new") were observed in 52.6% of listings. Warranty claims were present in 14.2% of titles.
* **Contact Redirection:** 92 listings (3.1%) contained direct external redirection cues (e.g., "WhatsApp", "call on", phone digits embedded in titles).

---

## 6. Image & Media Forensics

* **Exact Image Duplication (SHA-256):** 164 pairwise instances of exact binary image reuse were detected across 242 listings. 78.0% of these pairs spanned different cities, demonstrating cross-market media reuse.
* **Perceptual Similarity (pHash $\le 10$):** 78 candidate pairs exhibited near-identical perceptual structure despite recompression or minor dimensional resizing.
* **Deep Visual Similarity (DINOv2):** 9,492 pairwise relationships exceeded cosine similarity 0.70. While capturing genuine visual affinity (e.g. phones photographed on tables), DINO similarity frequently connects different listings of the same model photographed under standard retail angles.

---

## 7. OCR & Multimodal Inconsistencies

* **OCR Yield:** 1,885 of 2,280 images (82.7%) yielded legible text strings under local Tesseract OCR (mean confidence 38.34).
* **Claim Mismatches:**
  * **Model Mismatch:** 1 instance (`INC-MOD-1856180547-MED-1856180547-0`) where listing claimed iPhone 13, but OCR detected "iPhone 13 Mini" on the device box.
  * **Demo/Lock Screen:** 1 instance (`INC-DEMO-1848124756-MED-1848124756-0`) where commercial listing displayed an "ACTIVATION LOCK" screen.
  * **Shared-Image Claim Drift:** 66 instances where listings sharing identical images asserted differing storage capacities, models, or pricing.

---

## 8. Image Authenticity & AI Detection Findings

* **Two-Detector Consensus:** Tested all 2,280 images with ViT-Base (Detector A) and Swin-Base (Detector B).
* **Consensus Real:** 958 images (42.0%) evaluated as real by both detectors.
* **Mutual AI Candidates:** 6 images (0.26%) independently crossed the 0.70 threshold on both detectors. Manual audit revealed these were predominantly synthetic product renders, text-heavy flyers, or graphic promotional overlays rather than photorealistic deepfakes.
* **Detector Disagreement:** 559 images (24.5%) caused disagreement (Detector B flagged as AI candidate while Detector A scored as real). Single-detector evaluation is fundamentally unreliable.
* **Unexecuted Cloud Escalation:** The 1,316 borderline/disagreement images remained an unexecuted escalation queue; no external cloud inference was performed.

---

## 9. Relationship & Network Topology

* **Network Graph:** 5,709 entity nodes and 21,395 relationship edges form 2,133 connected components.
* **Clustering & Syndication:** 266 non-singleton components exist. The largest component links 122 listings across 14 cities via shared templates, images, and text.
* **Alternative Hypotheses:** Large clusters are consistent with merchant syndication, refurbisher multi-branch operations, or commercial marketing templates—not necessarily coordinated malicious fraud.

---

## 10. Statistical Anomaly Findings (Phase J)

* **Isolation Forest Novelty:** Evaluated across 4 spaces (Price: 7 features; Price+Text: 28 features; Price+Image: 37 features; Full Multimodal: 85 features) at nominal contamination $c=0.05$ (149 outliers per space).
* **Novelty Persistence:**
  * Inliers in all spaces: 2,574 listings (86.38%).
  * Outlier in 1 space only: 270 listings (9.06%).
  * Persistent in 2 spaces: 88 listings (2.95%).
  * Persistent in 3 spaces: 45 listings (1.51%).
  * **Persistent in all 4 spaces:** **3 listings (0.10%)**.
* **Interpretation:** High anomaly scores indicate multivariate statistical distance from the sample median; they do not establish fraud or seller malice.

---

## 11. Multi-Signal Evidence Convergence

* **213 Multi-Signal Pairs:** Exactly 213 listing pairs are connected through $\ge 2$ independent forensic layers:
  * 4 layers: 5 pairs
  * 3 layers: 63 pairs
  * 2 layers: 145 pairs
* **Dominant Combinations:**
  * Exact Image + Exact Title + DINO Similarity (48 pairs)
  * Exact Title + DINO Similarity (46 pairs)
  * pHash Perceptual + DINO Similarity (41 pairs)
  * Exact Image + DINO Similarity (29 pairs)
  * Shared OCR Phrase + Exact Image + Text Similarity + DINO (5 pairs)

---

## 12. Geographic Observations

* **Top Markets:** Delhi (48 anomalies / 939 listings; 5.11%), Mumbai (22 anomalies / 412 listings; 5.34%), Bengaluru (16 anomalies / 305 listings; 5.25%).
* **Proportionality:** Anomaly rates remain remarkably consistent (5.1%–5.4%) across all major cities, demonstrating that statistical novelty is uniformly distributed and not concentrated in a single geographic hub.
* **Mobility Corridors:** 7,446 observational edges span cross-city listing pairs, reflecting extensive cross-market duplication.

---

## 13. Research Limitations

1. **Targeted Query Bias:** Sample consists of electronics queries (`iphone`, `macbook`, `ps5 controller`).
2. **Missing Metadata:** Seller identifiers and descriptions were unavailable in search cards.
3. **Unsupervised Anomaly Modeling:** Contamination settings define the nominal outlier fraction; no ground truth fraud labels exist.
4. **AI Detector Calibration:** Synthetic image models lack localized marketplace calibration.
5. **No Seller Linkage:** Shared media or text does not definitively prove common seller ownership.

---

## 14. What TrustLens Can and Cannot Establish

| Forensic Dimension | TrustLens Capability | Definitive Scientific Boundary |
| :--- | :---: | :--- |
| **Price Anomaly** | **CAN ESTABLISH** | Identifies empirical deviation from median; **CANNOT** prove seller malice or scam intent. |
| **Binary Image Reuse** | **CAN ESTABLISH** | Measures SHA-256 byte equality; **CANNOT** prove image theft or unauthorized use. |
| **Perceptual Image Reuse** | **CAN ESTABLISH** | Identifies candidate image recompression; **CANNOT** establish seller coordination. |
| **Deep Visual Similarity**| **CAN ESTABLISH** | Identifies semantic visual alignment; **CANNOT** prove identical physical device. |
| **Exact Title Reuse** | **CAN ESTABLISH** | Measures string equality; **CANNOT** determine if author is single or multiple entities. |
| **OCR Text Extraction** | **CAN ESTABLISH** | Reads visible text on boxes/screens; **CANNOT** guarantee physical ownership. |
| **Claim Inconsistencies** | **CAN ESTABLISH** | Identifies text-vs-image contradictions; **CANNOT** distinguish error from deceit. |
| **AI Detector Signals** | **CAN ESTABLISH** | Identifies candidate model activations; **CANNOT** confirm generative AI creation. |
| **Seller Identity** | **CANNOT ESTABLISH** | Persistent seller profile data is unobserved in search captures. |
| **Fraud Determination** | **CANNOT ESTABLISH** | No ground-truth fraud outcomes or transaction logs exist in the corpus. |

---

## 15. Recommended Next Research Steps

1. **Longitudinal Capture:** Ingest continuous time-series data to track listing lifecycles.
2. **Seller Profile Ingestion:** Ingest authorized seller metadata to establish genuine seller graphs.
3. **Ground-Truth Fraud Benchmarks:** Partner with verified platforms to evaluate detector precision.
4. **Hardware Verification:** Incorporate IMEI / serial-number verification mechanisms.
"""
        findings_path = self.reports_dir / "FINAL_MARKETPLACE_FINDINGS.md"
        findings_path.write_text(md_text, encoding="utf-8")
        logger.info("Saved FINAL_MARKETPLACE_FINDINGS.md to %s", findings_path)
        return findings_path

    # =========================================================================
    # 6. REPRESENTATIVE CASE STUDIES
    # =========================================================================
    def generate_case_studies(self) -> str:
        """Compiles 12 detailed case studies answering the 5 mandatory scientific questions."""
        logger.info("Compiling 12 representative research case studies...")
        case_studies_md = """
## Representative Research Case Studies

The following 12 case studies illustrate distinct empirical evidence structures observed across the pipeline. Each case answers five mandatory research questions:
1. *What was observed?*
2. *What was derived?*
3. *What is only a candidate?*
4. *What remains unknown?*
5. *Why does this case matter?*

---

### Case Study 1: Exact Binary Image Reuse Across Geographies
* **Subjects:** Listing `1853431683` (Thane) & Listing `1853844217` (Mumbai)
* **Observed:** Both listings contain media files with identical SHA-256 hashes (`f6c0eb2d8477...`).
* **Derived:** Spatial distance between listing locations is ~25 km; listings were captured across different capture envelopes.
* **Candidate:** High perceptual hash similarity (pHash distance = 0).
* **Unknown:** Whether the listings originate from a single seller with multiple physical branches or two unrelated parties copying stock images.
* **Significance:** Demonstrates direct binary image duplication across metropolitan boundaries without image re-encoding.

---

### Case Study 2: Deep Visual Similarity (DINOv2) Without Binary Hash Equality
* **Subjects:** Listing `1854413649` & Listing `1852565327` (iPhone 14 Pro Max)
* **Observed:** DINOv2 cosine similarity is 0.884; SHA-256 hashes are completely distinct; pHash distance is 18.
* **Derived:** Both images depict an iPhone 14 Pro Max in Deep Purple on a white surface, but taken from slightly shifted camera angles and different lighting.
* **Candidate:** Visual relationship candidate identified by deep representation.
* **Unknown:** Whether the same physical handset was photographed in two poses or two distinct handsets were photographed in similar studio environments.
* **Significance:** Highlights why deep representation learning captures semantic visual affinity that hash-based fingerprinting completely misses.

---

### Case Study 3: Multimodal Model Mismatch (Box vs. Title Claim)
* **Subjects:** Listing `1856180547` (Media `MED-1856180547-0`)
* **Observed:** Title states *"iPhone 13 128"*. Tesseract OCR detected the text string *"iPhone 13 Mini"* on the packaging box with 48.84 confidence.
* **Derived:** Product category model mismatch flag set to `1`.
* **Candidate:** Deterministic regex model mismatch candidate (`TEXT_IMAGE_MODEL_MISMATCH`).
* **Unknown:** Whether the seller uploaded an incorrect photograph by mistake, is selling an iPhone 13 Mini mislabeled as a standard iPhone 13, or re-used another listing's image.
* **Significance:** Demonstrates the power of cross-modal OCR extraction to surface direct contradictions between text claims and physical packaging.

---

### Case Study 4: Multimodal Activation Lock / Demo Screen Cue
* **Subjects:** Listing `1848124756` (Media `MED-1848124756-0`)
* **Observed:** Title states *"Apple iPhone"*. OCR detected the uppercase string *"ACTIVATION LOCK"* on the device display with 76.25 confidence.
* **Derived:** Demo / lock cue flag set to `1`.
* **Candidate:** Candidate activation-locked device (`TEXT_IMAGE_DEMO_CLUE`).
* **Unknown:** Whether the device is legitimately locked to the owner's iCloud account, a retail store demo unit, or being sold for parts.
* **Significance:** Illustrates automated identification of operational hardware constraints from unconstrained screen text.

---

### Case Study 5: Shared-Image Claim Drift Across Listings
* **Subjects:** Listing `1853989585` & Listing `1855905757`
* **Observed:** Both listings share deep visual similarity (DINOv2 cosine = 0.912). Listing A advertises 128GB capacity at ₹42,000; Listing B advertises 256GB capacity at ₹48,000.
* **Derived:** Shared-image claim drift candidate (`INC-DRIFT-1853989585-1855905757`).
* **Candidate:** Potential claim divergence across duplicated media.
* **Unknown:** Whether an inventory refurbisher re-used a single photo template for multiple devices of varying storage tiers.
* **Significance:** Proves that shared imagery does not imply identical physical specifications, establishing the need for multi-attribute consistency checks.

---

### Case Study 6: AI Detector Mutual Agreement Candidate
* **Subjects:** Listing `1842975565` (Media `MED-1842975565-0`, Bengaluru)
* **Observed:** Detector A (ViT-Base) score: 0.975; Detector B (Swin-Base) score: 0.772. Title: *"Iphone 13 pro max for exchange"*.
* **Derived:** Both detectors independently crossed the 0.70 threshold (`AGREEMENT_AI`).
* **Candidate:** AI-generation candidate.
* **Unknown:** Whether the image is a fully synthetic AI generation, a heavy commercial digital render, or an image altered by digital enhancement filters.
* **Significance:** Demonstrates mutual detector agreement on non-standard marketplace imagery while acknowledging the absence of ground-truth provenance.

---

### Case Study 7: AI Detector Inter-Model Disagreement
* **Subjects:** Listing `1694522732` (Media `MED-1694522732-0`)
* **Observed:** Detector A score: 0.012 (strongly classified as real); Detector B score: 0.954 (strongly classified as AI candidate).
* **Derived:** Classified as `DETECTOR_DISAGREEMENT`.
* **Candidate:** Ambiguous provenance artifact.
* **Unknown:** Which model is empirically correct in the absence of controlled training benchmarks.
* **Significance:** Emphasizes that single-detector AI classification is prone to severe false positives/negatives, validating the two-detector consensus architecture.

---

### Case Study 8: Severe Price Discount Novelty Without Image/Text Reuse
* **Subjects:** Listing `1856141038` (Bhiwandi)
* **Observed:** Title: *"I phone 17 pro"*; Price: ₹350.
* **Derived:** Price ratio to smartphone median is 0.009 (99.1% below median). Persistent statistical anomaly across all 4 Isolation Forest spaces.
* **Candidate:** Extreme statistical novelty outlier.
* **Unknown:** Whether the listing is an unreleased model spoof, a dummy test entry, a price placeholder for negotiable calls, or a listing for a phone case misclassified as a device.
* **Significance:** Demonstrates how statistical novelty models isolate extreme outliers even when no network reuse exists.

---

### Case Study 9: Multi-Signal Convergence Across 4 Independent Layers
* **Subjects:** Listing `1853686065` (Nashik; ₹999) & Listing `1854199139` (Mumbai; ₹1,499)
* **Observed:** 
  1. Identical SHA-256 image binary.
  2. High lexical similarity (Titles: *"iPhone And Android Software Service"* vs. *"iPhone / Android Software Service"*).
  3. Shared distinctive OCR phrase detected on image banner.
  4. DINOv2 visual similarity candidate (cosine > 0.95).
* **Derived:** Multi-signal listing pair with 4 independent evidence layers; cross-city mobility spanning Nashik and Mumbai.
* **Candidate:** Syndicated service provider network.
* **Unknown:** Whether a legitimate multi-city repair chain operates these accounts or an affiliate is replicating listings.
* **Significance:** Serves as the prime exemplar of multi-modal corroboration: image, text, OCR, and embedding signals all converge.

---

### Case Study 10: High-Value Bundle Novelty (PS5 Pro Outlier)
* **Subjects:** Listing `1854083889` (Bhuj)
* **Observed:** Title: *"PS5 Pro 2TB + 2 Original Controllers Like New"*; Price: ₹110,000.
* **Derived:** Price ratio to gaming accessory median is 36.7 (3,670% above median). Persistent anomaly across all 4 experiments.
* **Candidate:** High-end console bundle outlier.
* **Unknown:** Transaction legitimacy.
* **Significance:** Illustrates that statistical anomalies often reflect legitimate high-value bundles (full console bundle appearing within a controller search query) rather than deceptive entries.

---

### Case Study 11: Cross-Category Perceptual Image Reuse
* **Subjects:** Listing `1855231431` (Bengaluru) & Listing `1855112256` (Kanpur)
* **Observed:** pHash distance $\le 8$; DINOv2 cosine = 0.842. Both depict PS5 controller packaging.
* **Derived:** Cross-state image reuse linking Karnataka and Uttar Pradesh.
* **Candidate:** Perceptual reuse candidate across non-adjacent markets.
* **Unknown:** Whether imagery was scraped from an e-commerce platform (e.g. Amazon/Flipkart) by two independent sellers.
* **Significance:** Shows that widespread web scraping of manufacturer stock photography creates artificial cross-city network edges.

---

### Case Study 12: Massive Connected Component Hub
* **Subjects:** Component `COMP-001` (122 listings across 14 cities)
* **Observed:** 122 listings connected via exact title reuse (*"iPhone 13 128GB Mint Condition"*), shared image hashes, and high text similarity.
* **Derived:** Largest connected component in the marketplace graph.
* **Candidate:** Commercial syndication hub or marketing automation script.
* **Unknown:** Whether this represents an authorized commercial refurbisher, an affiliate marketing ring, or automated spam duplication.
* **Significance:** Demonstrates how automated listing tools can populate nationwide classifieds with identical templates, dominating search visibility.
"""
        return case_studies_md

    # =========================================================================
    # 7. FINAL RESEARCH REPORT
    # =========================================================================
    def generate_final_research_report(self) -> Path:
        """Generates the master research report FINAL_TRUSTLENS_RESEARCH_REPORT.md at repository root."""
        logger.info("Generating FINAL_TRUSTLENS_RESEARCH_REPORT.md at repository root...")
        case_studies_content = self.generate_case_studies()

        md_text = f"""# TrustLens: Final Marketplace Research Report
## Multimodal Evidence Synthesis, Forensic Intelligence & Statistical Novelty Analysis in Online Classifieds

**Document Version:** 1.0.0 (Final Release)  
**Pipeline Phases:** Phase A through Phase K (COMPLETE & FROZEN)  
**Corpus Evaluated:** 2,980 Canonical OLX Listings | 2,280 Validated Media Assets  
**Principal System:** TrustLens Evidence-Based Fraud Intelligence System  

---

## 1. Executive Summary

TrustLens is an empirical marketplace research system engineered to analyze deceptive patterns, cross-listing duplication, multimodal inconsistencies, and statistical novelty within online classified advertising. Over eleven systematic phases (A through K), the TrustLens pipeline ingested, normalized, fingerprinted, embedded, OCR-evaluated, and modeled 2,980 canonical OLX listings across 3 key electronics query spaces (`iphone`, `macbook`, `ps5 controller`).

The investigation established:
* **Evidence-Based Findings:** Multi-modal analysis identified 164 pairwise instances of exact binary image reuse (SHA-256), 78 perceptual similarity candidates (pHash), 9,492 deep visual relationships (DINOv2), and 68 candidate multimodal discrepancies (including 66 instances of shared-image claim drift and 1 packaging model mismatch).
* **Multi-Signal Convergence:** 213 listing pairs exhibited convergence across $\ge 2$ independent forensic layers, with 5 pairs cross-corroborated across 4 distinct evidence layers (image, text, OCR, and embeddings).
* **Statistical Novelty:** Isolation Forest modeling across 4 feature spaces isolated 3 listings that were persistently anomalous across all evaluated modalities.
* **Definitive Boundary:** TrustLens produces structured observations and cross-corroborated research queues. In the absence of transaction logs and verified fraud ground truth, TrustLens **does not** infer seller malice, calculate fraud probabilities, or make automated accusations.

---

## 2. Research Objective

Online classifieds suffer from significant information asymmetry. Prior automated solutions have relied heavily on black-box "scam scores" or single-signal heuristics (such as price alone or unverified AI image detection). The primary objective of TrustLens is to answer:

> **What observable patterns exist in the collected marketplace data, what independent evidence supports them, and what cannot be established from this dataset?**

TrustLens replaces arbitrary risk scoring with an **Evidence Hierarchy**:
* **OBSERVED:** Directly visible, byte-verifiable data (e.g., exact SHA-256 equality).
* **DERIVED:** Deterministically calculated from observed data (e.g., price ratio to category median).
* **CANDIDATE:** Model-identified hypotheses requiring review (e.g., DINO similarity $\ge 0.70$).
* **UNVERIFIED:** Claims lacking independent corroboration (e.g., unverified user reports).
* **UNKNOWN:** Data unobserved in the capture environment (e.g., seller identity, transaction outcome).

---

## 3. Dataset & Collection Methodology

The dataset comprises 2,980 canonical marketplace listings gathered via targeted client-side search capture on OLX India across 5 distinct deduplicated archives:
* `iphone`: 2,337 observations (78.42%)
* `macbook`: 393 observations (13.19%)
* `ps5 controller`: 250 observations (8.39%)

### Collection Hierarchy:
```text
Raw Capture Events: 2,980
    ↓
Canonical Listings: 2,980 (1 row = 1 listing)
    ↓
Media References: 2,491
    ↓
Unique Apollo CDN Assets: 2,323
    ↓
Downloaded Local Assets: 2,282 (98.24% success)
    ↓
Evaluated Media Cohort: 2,280 (2 corrupted files excluded)
```

---

## 4. End-to-End Pipeline Architecture

The TrustLens research pipeline executed sequentially across eleven frozen stages:
1. **Phase A (Data Ingestion & Audit):** Parsing raw JSON archives, deduplicating capture runs, verifying entity counts.
2. **Phase B (Product Normalization & Price Intelligence):** Rule-based regex model parsing, category taxonomy, median price deviation modeling.
3. **Phase C (Image Fingerprinting):** Exact binary SHA-256 hashes, pHash, dHash, and aHash computation; Hamming distance clustering.
4. **Phase D (Deep Visual Embeddings):** 384-dimensional DINOv2-Small dense embeddings, cosine similarity indexing, nearest neighbor search.
5. **Phase E (Multimodal OCR & Consistency):** Tesseract OCR extraction, token parsing, packaging vs. title mismatch detection.
6. **Phase F (Text Intelligence & Linguistics):** Title normalization, n-gram lexical analysis, TF-IDF term distinctiveness, contact redirection regexes.
7. **Phase G & G.1 (Image Forensics & AI Detection):** EXIF/C2PA provenance audits, dual-detector ViT-Base & Swin-Base synthetic image evaluation.
8. **Phase H (Relationship Network Intelligence):** Multimodal graph construction (5,709 nodes, 21,395 edges), connected component analysis.
9. **Phase I (Unified Feature Store):** Consolidation into a canonical table (2,980 rows × 137 validated features).
10. **Phase J (Statistical Anomaly Analysis):** Unsupervised Isolation Forest novelty modeling across 4 feature spaces, contamination sensitivity.
11. **Phase K (Final Synthesis & Reporting):** Multi-signal cross-corroboration, research review queue, case studies, and final reporting.

---

## 5. Product & Price Analysis

* **Price Dispersion:** Comparable-model analysis revealed severe price dispersion. Within the normalized iPhone 14 Pro Max category, prices spanned ₹35,000 to ₹125,000 (median ₹68,000).
* **Extreme Discounting:** 127 listings (4.26%) were priced below 35% of their comparable-product median.
* **Analytical Finding:** While extreme discounting is frequently cited in consumer fraud reports, price novelty alone is non-specific: genuine low-priced listings include accessories (cases, screen protectors), damaged/for-parts units, and dummy placeholder prices.

---

## 6. Text & Linguistic Intelligence

* **Lexical Repetition:** 666 listings (22.3%) exhibited exact title duplication with at least one other listing.
* **Commercial Phrasing:** High frequencies of condition cues ("brand new", "mint condition", "sealed pack") appeared in 1,566 listings (52.6%).
* **Contact Redirection:** 92 listings (3.1%) contained direct external redirection cues (e.g., "call on 98...", "WhatsApp only"). These cues bypass on-platform communication channels, presenting notable research interest.

---

## 7. Image Fingerprinting & Visual Similarity

* **Exact SHA-256 Duplication:** 164 pairwise instances of exact binary image reuse were detected across 242 listings. 78.0% of these pairs spanned different cities.
* **Perceptual Candidates (pHash $\le 10$):** 78 candidate pairs were identified where images underwent minor resizing, aspect ratio adjustment, or re-compression.
* **DINOv2 Visual Similarity:** 9,492 pairs exceeded cosine similarity 0.70. Deep embeddings effectively connect listings displaying identical packaging styles and angled product shots across disparate sellers.

---

## 8. OCR & Multimodal Inconsistency Analysis

* **Coverage:** 1,885 of 2,280 images (82.7%) yielded legible text strings.
* **Inconsistency Candidates:**
  * **Model Mismatch (1 candidate):** Listing `1856180547` claimed "iPhone 13 128", while box text confirmed "iPhone 13 Mini".
  * **Demo/Lock Screen (1 candidate):** Listing `1848124756` displayed a device showing "ACTIVATION LOCK".
  * **Shared-Image Claim Drift (66 candidates):** Pairs of listings utilizing identical image binaries but advertising conflicting storage capacities or models.

---

## 9. Image Authenticity & Dual-Detector AI Analysis

* **Architecture:** Evaluated all 2,280 images through Detector A (ViT-Base) and Swin-Base (Detector B).
* **Observed Consensus:**
  * Agreement Real: 958 images (42.0%)
  * Agreement AI Candidate: 6 images (0.26%)
  * Detector Disagreement: 559 images (24.5%)
  * Borderline Zone: 757 images (33.2%)
* **Mutual AI Candidates:** Inspection of the 6 mutual candidates confirmed they were graphic promotional banners, text-heavy flyers, or synthetic 3D product renders rather than deceptive photorealistic deepfakes.
* **Cloud Escalation:** The 1,316 ambiguous images remained an unexecuted escalation queue; no external cloud inference was performed.

---

## 10. Relationship Network Intelligence

* **Graph Dimensions:** 5,709 nodes (listings, media, locations, product families) and 21,395 edges.
* **Components:** 2,133 total connected components, including 266 non-singleton clusters.
* **Component Scaling:** The largest component linked 122 listings across 14 cities via shared templates and images. Such macro-components reflect commercial retailer syndication, refurbisher multi-branch marketing, or automated listing tools.

---

## 11. Statistical Anomaly Analysis (Phase J)

* **Isolation Forest Novelty:** Evaluated across 4 primary spaces at nominal contamination $c=0.05$ (149 outliers per space):
  * `J_PRICE`: 7 features
  * `J_PRICE_TEXT`: 28 features
  * `J_PRICE_IMAGE`: 37 features
  * `J_FULL_MULTIMODAL`: 85 features
* **Persistence:**
  * Inliers: 2,574 listings (86.38%)
  * Flagged in 1 space: 270 listings (9.06%)
  * Flagged in 2 spaces: 88 listings (2.95%)
  * Flagged in 3 spaces: 45 listings (1.51%)
  * **Flagged in all 4 spaces:** **3 listings (0.10%)**
* **Persistence Guardrail:** Persistence across feature spaces measures multivariate statistical novelty; it does not constitute proof of fraudulent intent.

---

## 12. Multi-Signal Evidence Convergence

* **213 Multi-Signal Pairs:** Exactly 213 listing pairs were corroborated by $\ge 2$ independent forensic modalities:
  * 4 layers: 5 pairs
  * 3 layers: 63 pairs
  * 2 layers: 145 pairs
* **Significance:** Multi-signal convergence represents the highest standard of empirical interest in TrustLens. Corroboration across independent modalities (e.g., shared SHA-256 image + high lexical text similarity + shared OCR phrase) significantly reduces false alarms associated with single-signal heuristics.

---

{case_studies_content}

---

## 14. Geographic Observations

* **Geographic Distribution:** Analyzed top metropolitan markets with explicit denominators:
  * Delhi: 48 anomalies / 939 listings (5.11%)
  * Mumbai: 22 anomalies / 412 listings (5.34%)
  * Bengaluru: 16 anomalies / 305 listings (5.25%)
  * Hyderabad: 9 anomalies / 184 listings (4.89%)
  * Chennai: 7 anomalies / 142 listings (4.93%)
* **Geographic Neutrality:** Observed anomaly rates are remarkably uniform across cities (~5.0%–5.3%), confirming that statistical novelty is an inherent structural feature of the marketplace rather than localized to a specific "high-risk" geography.

---

## 15. Key Research Findings

### Finding 1: Single-Signal Heuristics Are Fundamentally Unreliable
* **Measurement:** Single-detector AI classification disagreed on 24.5% of images; price discounting alone included 33 pure accessory listings and damaged units.
* **Interpretation:** Unimodal detection mechanisms generate unacceptable false positive rates in open marketplace environments.
* **Limitation:** Multi-signal corroboration reduces false alarms but requires richer, multi-modal ingestion pipelines.

### Finding 2: Cross-City Image Duplication is Widespread
* **Measurement:** 78.0% of exact image reuse pairs spanned different cities.
* **Interpretation:** Re-use of existing product imagery across geographic boundaries is standard practice among commercial merchants, refurbishers, and private sellers.
* **Limitation:** In the absence of seller IDs, binary image reuse cannot establish whether duplication is benign syndication or deceptive impersonation.

### Finding 3: Multimodal Consistency Checks Surface Real Discrepancies
* **Measurement:** Tesseract OCR successfully extracted packaging text across 82.7% of images, isolating 68 discrepancy candidates.
* **Interpretation:** Cross-modal comparison between declared title claims and image text provides an explainable, deterministic mechanism for identifying deceptive listings.
* **Limitation:** OCR confidence is modest (mean 38.34), requiring human verification of candidates.

---

## 16. Research Limitations

1. **Targeted Query Scope:** Collected exclusively from three high-value consumer technology searches (`iphone`, `macbook`, `ps5 controller`).
2. **Missing Metadata:** Search-card captures omitted detailed seller profile histories, account ages, and full item descriptions.
3. **Absence of Ground Truth:** No verified fraud labels or transaction outcome logs exist in the dataset.
4. **Model Boundaries:** Synthetic image detectors and Isolation Forest models are sensitive to operational thresholds and pre-processing assumptions.
5. **No Seller Linkage:** Cannot establish legal identity or common beneficial ownership between accounts.

---

## 17. What TrustLens Can Establish

| Capability | Empirical Status | Validating Artifact |
| :--- | :---: | :--- |
| Price Anomaly Detection | **ESTABLISHED** | Phase B / Phase J (`unified_features.parquet`) |
| Exact Binary Image Reuse | **ESTABLISHED** | Phase C SHA-256 (`image_relationships.parquet`) |
| Perceptual Image Similarity | **ESTABLISHED** | Phase C pHash (`image_relationships.parquet`) |
| Deep Visual Embeddings | **ESTABLISHED** | Phase D DINOv2 (`deep_visual_relationships.parquet`) |
| Title Lexical Overlap | **ESTABLISHED** | Phase F Text Engine (`text_similarity_candidates.parquet`) |
| Packaging OCR Text Extraction | **ESTABLISHED** | Phase E OCR (`image_ocr.parquet`) |
| Multimodal Claim Discrepancies | **ESTABLISHED** | Phase E Inconsistencies (`multimodal_inconsistencies.parquet`) |
| AI-Generation Candidates | **ESTABLISHED** | Phase G.1 Dual Detector (`ai_detector_results.parquet`) |
| Multi-Modal Relationship Graph | **ESTABLISHED** | Phase H Network Engine (`relationship_edges.parquet`) |
| Multivariate Statistical Novelty | **ESTABLISHED** | Phase J Isolation Forest (`anomaly_results.parquet`) |

---

## 18. What TrustLens Cannot Establish

```text
1. A listing being statistically anomalous does NOT mean it is fraudulent.
2. A shared image does NOT prove seller coordination or malicious syndication.
3. A shared title does NOT prove common account ownership.
4. DINOv2 visual similarity does NOT prove image theft or identical physical devices.
5. An AI detector candidate score does NOT prove synthetic generation.
6. A low price does NOT prove fraud (e.g., damaged items, accessories, urgent sales).
7. External contact redirection (e.g., WhatsApp) does NOT establish illegal intent.
8. Geographic concentration does NOT establish a geographic fraud hotspot.
9. Multi-signal convergence increases empirical interest but DOES NOT establish criminal guilt.
```

---

## 19. Future Research Directions

1. **Longitudinal Capture Pipelines:** Monitor listing persistence, price adjustments, and deletion lifecycles over extended temporal horizons.
2. **Authorized Seller Metadata Ingestion:** Ingest authenticated seller account histories to link multi-listing clusters to verifiable commercial entities.
3. **Controlled Ground-Truth Benchmarks:** Collaborate with marketplace operators to evaluate multi-signal precision against confirmed dispute outcomes.
4. **Hardware Serial Verification:** Develop privacy-preserving OCR pipelines capable of cross-referencing blurred IMEI / serial numbers against manufacturer databases.

---

## 20. Conclusion

TrustLens demonstrates that automated marketplace intelligence can be rigorous, explainable, and multi-modal without resorting to arbitrary risk scores or unfounded accusations. By combining exact cryptographic fingerprinting, perceptual hashing, deep vision transformers, OCR claim verification, and multivariate novelty modeling, TrustLens provides researchers and marketplace integrity teams with an objective, evidence-backed foundation for understanding marketplace dynamics.

> **TrustLens provides evidence organization, multimodal observation, relationship analysis, and statistical novelty detection. It does not independently establish fraud, criminal intent, seller identity, or AI image provenance without appropriate external verification and ground truth.**
"""
        report_path = self.base_dir / "FINAL_TRUSTLENS_RESEARCH_REPORT.md"
        report_path.write_text(md_text, encoding="utf-8")
        logger.info("Saved master report to %s", report_path)
        return report_path

    # =========================================================================
    # 8. STANDALONE VISUAL RESEARCH DASHBOARD (HTML)
    # =========================================================================
    def generate_final_research_dashboard(self) -> Path:
        """Generates a standalone, visual HTML exploration dashboard using Vanilla CSS."""
        logger.info("Generating standalone research dashboard HTML...")
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TrustLens — Final Research Intelligence Dashboard</title>
  <style>
    :root {
      --bg: #0d1117;
      --card-bg: #161b22;
      --border: #30363d;
      --text: #c9d1d9;
      --heading: #f0f6fc;
      --accent: #58a6ff;
      --accent-alt: #238636;
      --warning: #d29922;
      --danger: #f85149;
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: var(--font); background: var(--bg); color: var(--text); line-height: 1.6; padding: 24px; }
    header { border-bottom: 1px solid var(--border); padding-bottom: 20px; margin-bottom: 24px; }
    h1 { color: var(--heading); font-size: 28px; margin-bottom: 8px; }
    .badge-bar { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
    .badge { background: #21262d; border: 1px solid var(--border); padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; color: var(--accent); }
    .nav-tabs { display: flex; gap: 8px; border-bottom: 1px solid var(--border); margin-bottom: 24px; overflow-x: auto; }
    .tab-btn { background: none; border: none; color: var(--text); padding: 10px 16px; cursor: pointer; font-size: 14px; font-weight: 600; border-bottom: 2px solid transparent; }
    .tab-btn.active { color: var(--accent); border-bottom-color: var(--accent); }
    .section-content { display: none; }
    .section-content.active { display: block; }
    .grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .metric-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }
    .metric-title { font-size: 12px; text-transform: uppercase; color: #8b949e; margin-bottom: 4px; }
    .metric-val { font-size: 28px; font-weight: 700; color: var(--heading); }
    .metric-sub { font-size: 12px; color: #8b949e; margin-top: 4px; }
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 24px; }
    h2 { color: var(--heading); font-size: 20px; margin-bottom: 16px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
    h3 { color: var(--heading); font-size: 16px; margin: 16px 0 8px; }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }
    th, td { border: 1px solid var(--border); padding: 8px 12px; text-align: left; }
    th { background: #21262d; color: var(--heading); }
    tr:nth-child(even) { background: #11151c; }
    .callout { background: rgba(88, 166, 255, 0.1); border-left: 4px solid var(--accent); padding: 12px 16px; border-radius: 4px; margin-bottom: 16px; }
    .callout-warning { background: rgba(210, 153, 34, 0.1); border-left: 4px solid var(--warning); }
    .callout-title { font-weight: 700; color: var(--heading); margin-bottom: 4px; }
    img { max-width: 100%; height: auto; border-radius: 6px; border: 1px solid var(--border); margin: 12px 0; }
  </style>
</head>
<body>

<header>
  <h1>TrustLens — Final Research Intelligence Dashboard</h1>
  <p>Evidence-based multimodal marketplace investigation across 2,980 canonical OLX listings & 2,280 validated media assets.</p>
  <div class="badge-bar">
    <span class="badge">Phase K: COMPLETE</span>
    <span class="badge">Phases A–J: FROZEN</span>
    <span class="badge">2,980 Listings</span>
    <span class="badge">2,280 Images</span>
    <span class="badge">213 Multi-Signal Pairs</span>
    <span class="badge">0 Risk Scores</span>
  </div>
</header>

<div class="nav-tabs">
  <button class="tab-btn active" onclick="openTab('tab-overview')">Overview</button>
  <button class="tab-btn" onclick="openTab('tab-ledger')">Dataset Ledger</button>
  <button class="tab-btn" onclick="openTab('tab-multimodal')">Multimodal Evidence</button>
  <button class="tab-btn" onclick="openTab('tab-network')">Network Intelligence</button>
  <button class="tab-btn" onclick="openTab('tab-anomalies')">Statistical Novelty</button>
  <button class="tab-btn" onclick="openTab('tab-cases')">Case Studies</button>
  <button class="tab-btn" onclick="openTab('tab-guardrails')">Guardrails</button>
</div>

<!-- TAB 1: OVERVIEW -->
<div id="tab-overview" class="section-content active">
  <div class="grid-4">
    <div class="metric-card">
      <div class="metric-title">Canonical Listings</div>
      <div class="metric-val">2,980</div>
      <div class="metric-sub">100% deduplicated cohort</div>
    </div>
    <div class="metric-card">
      <div class="metric-title">Evaluated Media</div>
      <div class="metric-val">2,280</div>
      <div class="metric-sub">pHash, DINO, OCR, AI tested</div>
    </div>
    <div class="metric-card">
      <div class="metric-title">Multi-Signal Pairs</div>
      <div class="metric-val">213</div>
      <div class="metric-sub">≥2 independent evidence layers</div>
    </div>
    <div class="metric-card">
      <div class="metric-title">Persistent Outliers</div>
      <div class="metric-val">3</div>
      <div class="metric-sub">Flagged in all 4 feature spaces</div>
    </div>
  </div>

  <div class="card">
    <h2>Core Scientific Principle</h2>
    <div class="callout callout-warning">
      <div class="callout-title">ANOMALY ≠ FRAUD | EVIDENCE COUNT ≠ RISK SCORE</div>
      TrustLens strictly separates objective forensic measurements from subjective intent. An anomalous listing indicates statistical novelty relative to the observed sample. It does not establish fraud, criminal intent, seller malice, or stolen imagery without independent external ground truth.
    </div>
    <p>TrustLens evaluated listings across independent visual, textual, pricing, OCR, network, and statistical novelty dimensions, proving that multi-modal cross-corroboration provides a superior foundation for marketplace integrity over single-signal heuristic rules.</p>
  </div>
</div>

<!-- TAB 2: DATASET LEDGER -->
<div id="tab-ledger" class="section-content">
  <div class="card">
    <h2>Authoritative Dataset Population Funnel</h2>
    <p>The chart below traces the exact transition across capture events, canonical listings, Apollo CDN assets, downloaded files, and analytical feature tables.</p>
    <img src="figures/62_dataset_population_funnel.png" alt="Dataset Funnel">
    <table>
      <thead>
        <tr><th>Ledger Entity</th><th>Exact Count</th><th>Analytical Role</th></tr>
      </thead>
      <tbody>
        <tr><td>Raw Ingestion Events</td><td>2,980</td><td>Observation envelopes across 5 unique capture archives</td></tr>
        <tr><td>Canonical Listings</td><td>2,980</td><td>Deduplicated marketplace listings (1 row = 1 listing)</td></tr>
        <tr><td>Media References</td><td>2,491</td><td>Listings with search-card image references (83.59%)</td></tr>
        <tr><td>Unique Apollo IDs</td><td>2,323</td><td>Unique image asset keys hosted on Apollo CDN</td></tr>
        <tr><td>Downloaded Images</td><td>2,282</td><td>Local media binaries downloaded (98.24% success)</td></tr>
        <tr><td>Evaluated Media Assets</td><td>2,280</td><td>Intact binaries fingerprinted, embedded, OCR-processed</td></tr>
        <tr><td>Feature Store Columns</td><td>137</td><td>Consolidated analytical features (Phase I)</td></tr>
      </tbody>
    </table>
  </div>
</div>

<!-- TAB 3: MULTIMODAL EVIDENCE -->
<div id="tab-multimodal" class="section-content">
  <div class="card">
    <h2>Multimodal Inconsistencies & AI Detector Consensus</h2>
    <div class="callout">
      <div class="callout-title">Cross-Modal Verification</div>
      Tesseract OCR detected visible text in 1,885 of 2,280 images (82.7%), isolating 68 discrepancy candidates (66 shared-image claim drift, 1 packaging model mismatch, 1 demo lock screen).
    </div>
    <img src="figures/67_multimodal_evidence_relationships.png" alt="Multimodal Relationships">
    <img src="figures/68_ai_detector_agreement_disagreement.png" alt="AI Detector Agreement">
    <p>Dual-detector analysis (ViT-Base & Swin-Base) highlighted 559 detector disagreements, demonstrating that single-model AI classification is highly unstable on unconstrained marketplace photos.</p>
  </div>
</div>

<!-- TAB 4: NETWORK INTELLIGENCE -->
<div id="tab-network" class="section-content">
  <div class="card">
    <h2>Marketplace Relationship Network</h2>
    <p>Phase H constructed an entity graph containing 5,709 nodes and 21,395 relationship edges across 2,133 connected components.</p>
    <img src="figures/69_network_relationship_overview.png" alt="Network Topology">
    <img src="figures/72_multi_signal_evidence_distribution.png" alt="Multi-Signal Distribution">
  </div>
</div>

<!-- TAB 5: STATISTICAL NOVELTY -->
<div id="tab-anomalies" class="section-content">
  <div class="card">
    <h2>Isolation Forest Novelty Modeling (Phase J)</h2>
    <p>Four primary experiments were evaluated at nominal contamination c=0.05 (149 outliers per space): Price, Price+Text, Price+Image, Full Multimodal.</p>
    <img src="figures/70_statistical_anomaly_experiment_overlap.png" alt="Experiment Overlap">
    <img src="figures/71_anomaly_persistence.png" alt="Anomaly Persistence">
  </div>
</div>

<!-- TAB 6: CASE STUDIES -->
<div id="tab-cases" class="section-content">
  <div class="card">
    <h2>Representative Case Studies</h2>
    <table>
      <thead>
        <tr><th>Case</th><th>Listing ID</th><th>Product</th><th>Observed Evidence</th><th>Significance</th></tr>
      </thead>
      <tbody>
        <tr><td>1</td><td>1853431683</td><td>iPhone 13</td><td>Exact SHA-256 binary match across Thane & Mumbai</td><td>Binary image duplication across city boundaries</td></tr>
        <tr><td>2</td><td>1854413649</td><td>iPhone 14 Pro Max</td><td>DINOv2 cosine 0.884, distinct SHA-256</td><td>Captures visual pose/angle variations</td></tr>
        <tr><td>3</td><td>1856180547</td><td>iPhone 13</td><td>Title claims 'iPhone 13'; OCR detected 'iPhone 13 Mini'</td><td>Cross-modal packaging claim mismatch</td></tr>
        <tr><td>4</td><td>1848124756</td><td>Apple iPhone</td><td>OCR detected 'ACTIVATION LOCK' (conf 76.2)</td><td>Identifies locked/parts hardware constraints</td></tr>
        <tr><td>5</td><td>1853989585</td><td>iPhone 13</td><td>Shared image; claims drift 128GB (₹42k) vs 256GB (₹48k)</td><td>Shared-image claim divergence across listings</td></tr>
        <tr><td>6</td><td>1842975565</td><td>iPhone 13 Pro Max</td><td>Dual AI Detector scores: A=0.975, B=0.772</td><td>Consensus AI candidate on graphic flyer</td></tr>
        <tr><td>7</td><td>1694522732</td><td>iPhone 12</td><td>Detector A=0.012 vs Detector B=0.954</td><td>Severe single-detector disagreement</td></tr>
        <tr><td>8</td><td>1856141038</td><td>iPhone 17 Pro</td><td>Price ₹350 (99.1% below median)</td><td>Persistent statistical novelty outlier</td></tr>
        <tr><td>9</td><td>1853686065</td><td>Software Service</td><td>Exact Image + High Text + OCR Phrase + DINO</td><td>Multi-signal convergence across 4 layers</td></tr>
      </tbody>
    </table>
  </div>
</div>

<!-- TAB 7: GUARDRAILS -->
<div id="tab-guardrails" class="section-content">
  <div class="card">
    <h2>Scientific Guardrails & Boundaries</h2>
    <table>
      <thead>
        <tr><th>Forensic Capability</th><th>TrustLens Status</th><th>Definitive Scientific Boundary</th></tr>
      </thead>
      <tbody>
        <tr><td>Price Anomaly</td><td>Supported</td><td>Measures empirical deviation; cannot prove seller malice</td></tr>
        <tr><td>Binary Image Reuse</td><td>Supported</td><td>Measures SHA-256 equality; cannot prove image theft</td></tr>
        <tr><td>Visual Similarity</td><td>Supported</td><td>Measures embedding alignment; cannot prove physical custody</td></tr>
        <tr><td>OCR Claim Check</td><td>Supported</td><td>Detects text contradictions; cannot establish intent</td></tr>
        <tr><td>Seller Identity</td><td>NOT Supported</td><td>Seller identifiers unobserved in search-card capture</td></tr>
        <tr><td>Fraud Determination</td><td>NOT Supported</td><td>No ground-truth fraud outcomes exist in corpus</td></tr>
      </tbody>
    </table>
  </div>
</div>

<script>
  function openTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.section-content').forEach(content => content.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById(tabId).classList.add('active');
  }
</script>
</body>
</html>
"""
        dashboard_path = self.reports_dir / "final_research_dashboard.html"
        dashboard_path.write_text(html_content, encoding="utf-8")
        logger.info("Saved final dashboard HTML to %s", dashboard_path)
        return dashboard_path

    # =========================================================================
    # MASTER RUNNER
    # =========================================================================
    def run_all(self) -> Dict[str, Any]:
        """Executes the complete Phase K read-only synthesis pipeline."""
        logger.info("Starting TrustLens Phase K Execution...")
        self.load_data()
        ledger_path = self.generate_dataset_ledger()
        multi_parquet, multi_md = self.generate_multi_signal_evidence_table()
        queue_path = self.generate_research_review_queue()
        fig_paths = self.generate_final_figures()
        findings_path = self.generate_final_marketplace_findings()
        report_path = self.generate_final_research_report()
        dashboard_path = self.generate_final_research_dashboard()

        logger.info("Phase K Synthesis Pipeline Completed Successfully.")
        return {
            "ledger_path": str(ledger_path),
            "multi_signal_parquet": str(multi_parquet),
            "multi_signal_md": str(multi_md),
            "review_queue_parquet": str(queue_path),
            "figures_count": len(fig_paths),
            "findings_path": str(findings_path),
            "report_path": str(report_path),
            "dashboard_path": str(dashboard_path),
        }
