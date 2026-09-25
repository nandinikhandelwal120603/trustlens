"""TrustLens Phase I — Unified Listing-Level Feature Store.

Consolidates all deterministic forensic observations from Phases A through H into
a single canonical analytical table where:
    1 ROW = 1 CANONICAL OLX LISTING

Strict Guardrails:
- No fraud scores, scam probabilities, or risk indexes.
- No seller profiling or identity inferences.
- Missingness is explicit: 0 = observed absence, NULL = unavailable/unevaluated.
- Immutability: Consumes frozen artifacts without modification.
- Zero data leakage: No post-hoc target variables or future anomaly labels.
"""

from collections import Counter, defaultdict
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

logger = logging.getLogger("trustlens.feature_store")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class UnifiedFeatureStoreBuilder:
    """Builds and validates the unified canonical listing-level feature store."""

    def __init__(
        self,
        processed_dir: Path = Path("data/olx_processed"),
        reports_dir: Path = Path("data/olx_analysis/reports"),
        root_dir: Path = Path("."),
    ):
        self.processed_dir = Path(processed_dir)
        self.reports_dir = Path(reports_dir)
        self.root_dir = Path(root_dir)

        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Caches for source dataframes
        self.df_listings: Optional[pd.DataFrame] = None
        self.df_norm: Optional[pd.DataFrame] = None
        self.df_fingerprints: Optional[pd.DataFrame] = None
        self.df_deep_rel: Optional[pd.DataFrame] = None
        self.df_ocr: Optional[pd.DataFrame] = None
        self.df_incons: Optional[pd.DataFrame] = None
        self.df_text: Optional[pd.DataFrame] = None
        self.df_auth: Optional[pd.DataFrame] = None
        self.df_ai: Optional[pd.DataFrame] = None
        self.df_rel_feat: Optional[pd.DataFrame] = None

    def load_all_sources(self) -> None:
        """Loads all prerequisite frozen Parquet datasets strictly read-only."""
        logger.info("Loading frozen Phase A-H datasets...")
        self.df_listings = pq.read_table(self.processed_dir / "listings.parquet").to_pandas()
        self.df_norm = pq.read_table(self.processed_dir / "normalized_listings.parquet").to_pandas()
        self.df_fingerprints = pq.read_table(self.processed_dir / "fingerprints.parquet").to_pandas()
        self.df_deep_rel = pq.read_table(self.processed_dir / "deep_visual_relationships.parquet").to_pandas()
        self.df_ocr = pq.read_table(self.processed_dir / "image_ocr.parquet").to_pandas()
        self.df_incons = pq.read_table(self.processed_dir / "multimodal_inconsistencies.parquet").to_pandas()
        self.df_text = pq.read_table(self.processed_dir / "text_features.parquet").to_pandas()
        self.df_auth = pq.read_table(self.processed_dir / "image_authenticity.parquet").to_pandas()
        self.df_ai = pq.read_table(self.processed_dir / "ai_detector_results.parquet").to_pandas()
        self.df_rel_feat = pq.read_table(self.processed_dir / "relationship_features.parquet").to_pandas()
        logger.info("All prerequisite Parquet datasets loaded successfully.")

    def compute_price_benchmarks(self) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, np.ndarray]]:
        """Computes Phase B comparable product group benchmarks (N >= 5 devices)."""
        df_valid = self.df_norm[self.df_norm["price_status"] == "valid"].copy()
        df_devices = df_valid[df_valid["accessory_or_device"] == "device"].copy()

        model_stats: Dict[str, Dict[str, Any]] = {}
        group_prices_map: Dict[str, np.ndarray] = {}

        for model_name, grp in df_devices.groupby("model"):
            if len(grp) >= 5 and model_name not in ["Unknown Product", "Generic Smartphone", "Generic Laptop"]:
                prices = grp["price_amount"].dropna().values
                q1, median, q3 = np.percentile(prices, [25, 50, 75])
                iqr = q3 - q1
                model_stats[model_name] = {
                    "count": int(len(prices)),
                    "min": float(np.min(prices)),
                    "q1": float(q1),
                    "median": float(median),
                    "q3": float(q3),
                    "max": float(np.max(prices)),
                    "mean": float(np.mean(prices)),
                    "std": float(np.std(prices)),
                    "iqr": float(iqr),
                }
                group_prices_map[model_name] = np.sort(prices)

        logger.info("Computed price benchmarks across %d comparable product groups", len(model_stats))
        return model_stats, group_prices_map

    def build_unified_feature_store(self) -> pd.DataFrame:
        """Constructs the canonical 1-row-per-listing unified feature store."""
        if self.df_listings is None:
            self.load_all_sources()

        logger.info("Constructing unified listing-level feature store...")

        # Authoritative base population: listings.parquet
        base_df = self.df_listings.copy().sort_values("listing_id").reset_index(drop=True)
        canonical_count = len(base_df)
        logger.info("Canonical listing population: %d rows", canonical_count)

        # ---------------------------------------------------------------------
        # Precompute Lookups & Aggregations
        # ---------------------------------------------------------------------
        # 1. Product & Price Normalization (Phase B)
        norm_map = self.df_norm.set_index("listing_id").to_dict(orient="index")
        model_stats, group_prices_map = self.compute_price_benchmarks()

        # 2. Media Fingerprints (Phase C)
        fp_map = self.df_fingerprints.set_index("listing_id").to_dict(orient="index")

        # 3. Deep Visual Relationships (Phase D)
        # Gather max and mean DINO similarity per listing
        dino_a = self.df_deep_rel[["listing_a_id", "dino_similarity"]].rename(columns={"listing_a_id": "listing_id"})
        dino_b = self.df_deep_rel[["listing_b_id", "dino_similarity"]].rename(columns={"listing_b_id": "listing_id"})
        dino_all = pd.concat([dino_a, dino_b], ignore_index=True)
        dino_stats = dino_all.groupby("listing_id")["dino_similarity"].agg(["count", "max", "mean"]).to_dict(orient="index")

        # 4. Image OCR (Phase E)
        ocr_map = self.df_ocr.set_index("listing_id").to_dict(orient="index")

        # 5. Multimodal Inconsistencies (Phase E)
        incons_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for _, r in self.df_incons.iterrows():
            lid = str(r["listing_id"])
            itype = str(r["inconsistency_type"])
            incons_counts[lid]["total"] += 1
            if itype in ["MODEL_MISMATCH", "TEXT_IMAGE_MODEL_MISMATCH"]:
                incons_counts[lid]["model"] += 1
            elif itype in ["STORAGE_MISMATCH", "TEXT_IMAGE_STORAGE_MISMATCH"]:
                incons_counts[lid]["storage"] += 1
            elif itype in ["CONDITION_MISMATCH", "TEXT_IMAGE_CONDITION_MISMATCH"]:
                incons_counts[lid]["condition"] += 1
            elif itype in ["DEMO_CLUE", "TEXT_IMAGE_DEMO_CLUE"]:
                incons_counts[lid]["demo"] += 1
            elif itype == "SHARED_IMAGE_CLAIM_DRIFT":
                incons_counts[lid]["drift"] += 1

        # 6. Text Features (Phase F)
        text_map = self.df_text.set_index("listing_id").to_dict(orient="index")

        # 7. Image Authenticity (Phase G)
        auth_map = self.df_auth.set_index("listing_id").to_dict(orient="index")

        # 8. AI Detector Results (Phase G.1)
        # Note: ai_detector_results links via media_id; map media_id to listing_id via auth or fingerprints
        media_to_listing = dict(zip(self.df_auth["media_id"], self.df_auth["listing_id"]))
        ai_df = self.df_ai.copy()
        ai_df["listing_id"] = ai_df["media_id"].map(media_to_listing)
        ai_map = ai_df.dropna(subset=["listing_id"]).set_index("listing_id").to_dict(orient="index")

        # 9. Relationship Network Features (Phase H)
        rel_feat_map = self.df_rel_feat.set_index("listing_id").to_dict(orient="index")

        # ---------------------------------------------------------------------
        # Assemble Rows Deterministically
        # ---------------------------------------------------------------------
        rows: List[Dict[str, Any]] = []

        for _, row in base_df.iterrows():
            lid = str(row["listing_id"])

            # Lookups
            n_row = norm_map.get(lid, {})
            fp_row = fp_map.get(lid, {})
            dino_row = dino_stats.get(lid, {})
            ocr_row = ocr_map.get(lid, {})
            incons_row = incons_counts.get(lid, {})
            t_row = text_map.get(lid, {})
            auth_row = auth_map.get(lid, {})
            ai_row = ai_map.get(lid, {})
            h_row = rel_feat_map.get(lid, {})

            # -----------------------------------------------------------------
            # Family A: Listing & Coverage Features
            # -----------------------------------------------------------------
            price_val = row.get("price_amount")
            p_status = n_row.get("price_status", "missing")
            has_price = bool(pd.notnull(price_val) and p_status == "valid")
            
            city_val = row.get("city")
            has_location = bool(pd.notnull(city_val) and city_val != "Unknown" and str(city_val).strip() != "")
            
            has_media = bool(row.get("has_media", False) and (row.get("media_count", 0) or 0) > 0)
            has_desc = bool(t_row.get("description_available", False))
            has_ocr = bool(lid in ocr_map)
            has_fingerprint = bool(lid in fp_map)
            has_embedding = bool(lid in dino_stats)
            has_ai_detector = bool(lid in ai_map)
            has_text = bool(t_row.get("title_available", False) or has_desc)

            rec: Dict[str, Any] = {
                # Primary Key & Identification
                "listing_id": lid,
                "source_url": row.get("source_url"),
                "first_seen_at": row.get("first_seen_at"),
                "last_seen_at": row.get("last_seen_at"),
                "observation_count": int(row.get("observation_count", 1)),
                "search_query": row.get("search_queries") or n_row.get("search_query"),
                "category_id": row.get("category_ids") or n_row.get("category_id"),
                "raw_title": row.get("raw_title"),
                "normalized_title": row.get("normalized_title"),
                
                # Geography (Preserved as observations, not risk scores)
                "location_raw": row.get("raw_location"),
                "city": city_val if pd.notnull(city_val) else "Unknown",
                "state": row.get("state") if pd.notnull(row.get("state")) else "Unknown",
                "country": row.get("country", "India"),
                "geography_confidence": row.get("geography_confidence"),

                # Coverage Flags
                "price_available": has_price,
                "location_available": has_location,
                "description_available": has_desc,
                "seller_available": False,  # Seller metadata unobserved in capture
                "media_available": has_media,
                "ocr_available": has_ocr,
                "text_available": has_text,
                "visual_embedding_available": has_embedding,
                "ai_detector_available": has_ai_detector,
            }

            # -----------------------------------------------------------------
            # Family B: Product Features (Phase B)
            # -----------------------------------------------------------------
            rec.update({
                "product_domain": n_row.get("product_domain", "Electronics"),
                "product_category": n_row.get("product_category", "Unknown"),
                "brand": n_row.get("brand", "Unknown"),
                "product_family": n_row.get("product_family", "Unknown"),
                "model": n_row.get("model", "Unknown Product"),
                "variant": n_row.get("variant"),
                "generation": n_row.get("generation"),
                "storage_gb": float(n_row["storage_gb"]) if pd.notnull(n_row.get("storage_gb")) else None,
                "ram_gb": float(n_row["ram_gb"]) if pd.notnull(n_row.get("ram_gb")) else None,
                "screen_size_inches": float(n_row["screen_size_inches"]) if pd.notnull(n_row.get("screen_size_inches")) else None,
                "battery_health_percent": float(n_row["battery_health_percent"]) if pd.notnull(n_row.get("battery_health_percent")) else None,
                "condition": n_row.get("condition", "unknown"),
                "condition_cues_str": n_row.get("condition_cues_str"),
                "accessory_or_device": n_row.get("accessory_or_device", "unknown"),
                "query_match_status": n_row.get("query_match_status", "unknown"),
                "normalization_confidence": str(n_row.get("normalization_confidence", "unknown")),
            })

            # -----------------------------------------------------------------
            # Family C: Price Features (Phase B Benchmarking)
            # -----------------------------------------------------------------
            model_name = n_row.get("model")
            is_device = n_row.get("accessory_or_device") == "device"
            is_benchmarked = bool(has_price and is_device and model_name in model_stats)

            if is_benchmarked and price_val is not None:
                stats = model_stats[model_name]
                med = stats["median"]
                delta = (float(price_val) - med) / med
                ratio = float(price_val) / med if med > 0 else None
                
                # Percentile rank
                grp_prices = group_prices_map[model_name]
                pct = float(np.searchsorted(grp_prices, float(price_val), side="right") / len(grp_prices) * 100.0)

                rec.update({
                    "price_amount": float(price_val),
                    "price_currency": row.get("price_currency", "INR"),
                    "price_status": p_status,
                    "price_valid": True,
                    "comparable_product_group": model_name,
                    "group_median_price": float(med),
                    "group_mean_price": float(stats["mean"]),
                    "group_min_price": float(stats["min"]),
                    "group_max_price": float(stats["max"]),
                    "group_std_price": float(stats["std"]),
                    "group_iqr_price": float(stats["iqr"]),
                    "price_delta_from_group_median": round(delta, 4),
                    "price_ratio_to_group_median": round(ratio, 4) if ratio else None,
                    "price_percentile_in_group": round(pct, 2),
                    "price_below_35_pct_median_flag": bool(delta <= -0.35),
                    "price_below_50_pct_median_flag": bool(delta <= -0.50),
                })
            else:
                rec.update({
                    "price_amount": float(price_val) if price_val is not None and pd.notnull(price_val) else None,
                    "price_currency": row.get("price_currency", "INR"),
                    "price_status": p_status,
                    "price_valid": has_price,
                    "comparable_product_group": None,
                    "group_median_price": None,
                    "group_mean_price": None,
                    "group_min_price": None,
                    "group_max_price": None,
                    "group_std_price": None,
                    "group_iqr_price": None,
                    "price_delta_from_group_median": None,
                    "price_ratio_to_group_median": None,
                    "price_percentile_in_group": None,
                    "price_below_35_pct_median_flag": None,
                    "price_below_50_pct_median_flag": None,
                })

            # -----------------------------------------------------------------
            # Family D: Media & Visual Features (Phase C / D)
            # -----------------------------------------------------------------
            m_count = int(row.get("media_count", 0) or 0)
            rec.update({
                "media_count": m_count,
                "media_downloaded": bool(fp_row.get("download_status") == "DOWNLOADED"),
                "media_fingerprinted": bool(fp_row.get("fingerprint_status") == "FINGERPRINTED"),
                "media_width": float(fp_row["width"]) if pd.notnull(fp_row.get("width")) else None,
                "media_height": float(fp_row["height"]) if pd.notnull(fp_row.get("height")) else None,
                "media_file_size_bytes": float(fp_row["file_size_bytes"]) if pd.notnull(fp_row.get("file_size_bytes")) else None,
                "media_mime_type": fp_row.get("mime_type"),
                "exact_image_reuse_count": int(h_row.get("exact_image_reuse_count", 0)),
                "perceptual_reuse_candidate_count": int(h_row.get("perceptual_image_candidate_count", 0)),
                "visual_similarity_candidate_count": int(h_row.get("visual_similarity_candidate_count", 0)),
                "max_visual_similarity_score": float(dino_row["max"]) if pd.notnull(dino_row.get("max")) else None,
                "mean_visual_similarity_score": float(dino_row["mean"]) if pd.notnull(dino_row.get("mean")) else None,
            })

            # -----------------------------------------------------------------
            # Family E: OCR & Inconsistency Features (Phase E)
            # -----------------------------------------------------------------
            if has_ocr:
                txt_len = ocr_row.get("character_count", 0) or 0
                tok_len = ocr_row.get("token_count", 0) or 0
                mean_conf = ocr_row.get("ocr_mean_confidence")
                rec.update({
                    "ocr_evaluated": True,
                    "ocr_status": ocr_row.get("ocr_status", "SUCCESS"),
                    "ocr_text_positive": bool(txt_len > 0),
                    "ocr_mean_confidence": float(mean_conf) if pd.notnull(mean_conf) else None,
                    "ocr_character_count": int(txt_len),
                    "ocr_token_count": int(tok_len),
                    "ocr_model_mention_count": len(ocr_row.get("observed_models", [])) if isinstance(ocr_row.get("observed_models"), (list, np.ndarray)) else 0,
                    "ocr_storage_mention_count": len(ocr_row.get("observed_storages", [])) if isinstance(ocr_row.get("observed_storages"), (list, np.ndarray)) else 0,
                    "ocr_condition_mention_count": len(ocr_row.get("observed_conditions", [])) if isinstance(ocr_row.get("observed_conditions"), (list, np.ndarray)) else 0,
                    "ocr_demo_cue_count": len(ocr_row.get("observed_demo_cues", [])) if isinstance(ocr_row.get("observed_demo_cues"), (list, np.ndarray)) else 0,
                })
            else:
                rec.update({
                    "ocr_evaluated": False,
                    "ocr_status": None,
                    "ocr_text_positive": False,
                    "ocr_mean_confidence": None,
                    "ocr_character_count": None,
                    "ocr_token_count": None,
                    "ocr_model_mention_count": 0,
                    "ocr_storage_mention_count": 0,
                    "ocr_condition_mention_count": 0,
                    "ocr_demo_cue_count": 0,
                })

            # Inconsistencies (All remain UNVERIFIED_CANDIDATE)
            total_incons = incons_row.get("total", 0)
            rec.update({
                "model_mismatch_candidate_count": incons_row.get("model", 0),
                "storage_mismatch_candidate_count": incons_row.get("storage", 0),
                "condition_mismatch_candidate_count": incons_row.get("condition", 0),
                "demo_clue_count": incons_row.get("demo", 0),
                "shared_image_claim_drift_count": incons_row.get("drift", 0),
                "total_multimodal_inconsistency_count": total_incons,
                "has_inconsistency_candidate": bool(total_incons > 0),
            })

            # -----------------------------------------------------------------
            # Family F: Text Features (Phase F)
            # -----------------------------------------------------------------
            rec.update({
                "title_char_count": int(t_row.get("title_char_count", 0)),
                "token_count": int(t_row.get("token_count", 0)),
                "unique_token_count": int(t_row.get("unique_token_count", 0)),
                "description_char_count": int(t_row.get("description_char_count", 0)),
                "has_urgency": bool(t_row.get("has_urgency", False)),
                "urgency_term_count": int(t_row.get("urgency_term_count", 0)),
                "has_contact_redirection": bool(t_row.get("has_contact_redirection", False)),
                "contact_redirection_term_count": int(t_row.get("contact_redirection_term_count", 0)),
                "has_transaction_payment": bool(t_row.get("has_transaction_payment", False)),
                "transaction_payment_term_count": int(t_row.get("transaction_payment_term_count", 0)),
                "has_clearance_commercial": bool(t_row.get("has_clearance_commercial", False)),
                "clearance_commercial_term_count": int(t_row.get("clearance_commercial_term_count", 0)),
                "has_warranty_authenticity": bool(t_row.get("has_warranty_authenticity", False)),
                "warranty_authenticity_term_count": int(t_row.get("warranty_authenticity_term_count", 0)),
                "has_delivery_logistics": bool(t_row.get("has_delivery_logistics", False)),
                "delivery_logistics_term_count": int(t_row.get("delivery_logistics_term_count", 0)),
                "has_condition_lexicon": bool(t_row.get("has_condition_lexicon", False)),
                "condition_lexicon_term_count": int(t_row.get("condition_lexicon_term_count", 0)),
                "has_relocation": bool(t_row.get("has_relocation", False)),
                "relocation_term_count": int(t_row.get("relocation_term_count", 0)),
                "has_company_claims": bool(t_row.get("has_company_claims", False)),
                "company_claims_term_count": int(t_row.get("company_claims_term_count", 0)),
                "exact_title_reuse_count": int(h_row.get("text_similarity_candidate_count", 0)),
                "text_similarity_candidate_count": int(h_row.get("text_similarity_candidate_count", 0)),
            })

            # -----------------------------------------------------------------
            # Family G: Image Authenticity & Provenance (Phase G)
            # -----------------------------------------------------------------
            if has_media and auth_row:
                rec.update({
                    "c2pa_present": bool(auth_row.get("c2pa_present", False)),
                    "exif_present": bool(auth_row.get("exif_present", False)),
                    "camera_make": auth_row.get("camera_make"),
                    "camera_model": auth_row.get("camera_model"),
                    "gps_present": bool(auth_row.get("gps_present", False)),
                    "image_type": auth_row.get("image_type", "UNKNOWN"),
                    "spectral_hf_ratio": float(auth_row["spectral_hf_ratio"]) if pd.notnull(auth_row.get("spectral_hf_ratio")) else None,
                    "colorfulness_index": float(auth_row["colorfulness_index"]) if pd.notnull(auth_row.get("colorfulness_index")) else None,
                    "forensic_assessment_status": auth_row.get("forensic_status", "NO_CONCLUSIVE_SIGNAL"),
                })
            else:
                rec.update({
                    "c2pa_present": None,
                    "exif_present": None,
                    "camera_make": None,
                    "camera_model": None,
                    "gps_present": None,
                    "image_type": None,
                    "spectral_hf_ratio": None,
                    "colorfulness_index": None,
                    "forensic_assessment_status": None,
                })

            # -----------------------------------------------------------------
            # Family H: AI Detector Features (Phase G.1)
            # -----------------------------------------------------------------
            if has_ai_detector and ai_row:
                raw_a = ai_row.get("detector_a_raw_score")
                raw_b = ai_row.get("detector_b_raw_score")
                agreement = ai_row.get("detector_agreement", "BORDERLINE")
                
                is_ai_cand = bool(pd.notnull(raw_a) and pd.notnull(raw_b) and float(raw_a) >= 0.70 and float(raw_b) >= 0.70)
                is_borderline = bool(agreement == "BORDERLINE")
                is_disagree = bool(agreement == "DISAGREEMENT")

                rec.update({
                    "ai_detector_evaluated": True,
                    "detector_a_name": ai_row.get("detector_a_name", "ViT-Base"),
                    "detector_a_score": float(raw_a) if pd.notnull(raw_a) else None,
                    "detector_a_result": ai_row.get("detector_a_result"),
                    "detector_b_name": ai_row.get("detector_b_name", "Swin-Base"),
                    "detector_b_score": float(raw_b) if pd.notnull(raw_b) else None,
                    "detector_b_result": ai_row.get("detector_b_result"),
                    "detector_agreement": agreement,
                    "ai_generation_candidate_flag": is_ai_cand,
                    "borderline_detector_flag": is_borderline,
                    "detector_disagreement_flag": is_disagree,
                })
            else:
                rec.update({
                    "ai_detector_evaluated": False,
                    "detector_a_name": None,
                    "detector_a_score": None,
                    "detector_a_result": None,
                    "detector_b_name": None,
                    "detector_b_score": None,
                    "detector_b_result": None,
                    "detector_agreement": None,
                    "ai_generation_candidate_flag": False,
                    "borderline_detector_flag": False,
                    "detector_disagreement_flag": False,
                })

            # -----------------------------------------------------------------
            # Family I: Relationship & Network Features (Phase H)
            # -----------------------------------------------------------------
            comp_size = int(h_row.get("component_size", 1))
            rec.update({
                "relationship_degree": int(h_row.get("relationship_degree", 0)),
                "unique_connected_listings": int(h_row.get("unique_connected_listings", 0)),
                "distinct_cities_connected": int(h_row.get("distinct_cities_connected", 0)),
                "distinct_states_connected": int(h_row.get("distinct_states_connected", 0)),
                "distinct_product_families_connected": int(h_row.get("distinct_product_families_connected", 0)),
                "component_id": h_row.get("component_id", "COMP-SINGLETON"),
                "component_size": comp_size,
                "is_singleton_listing": bool(comp_size <= 1),
                "shared_ocr_candidate_count": int(h_row.get("shared_ocr_candidate_count", 0)),
            })

            rows.append(rec)

        df_unified = pd.DataFrame(rows)
        # Ensure deterministic sort order
        df_unified = df_unified.sort_values("listing_id").reset_index(drop=True)

        logger.info(
            "Unified feature store constructed: %d listings, %d features",
            len(df_unified),
            len(df_unified.columns),
        )
        return df_unified

    def export_parquet(self, df_unified: pd.DataFrame) -> Path:
        """Exports unified feature store table to data/olx_processed/unified_features.parquet."""
        out_path = self.processed_dir / "unified_features.parquet"
        pq.write_table(pa.Table.from_pandas(df_unified), out_path)
        logger.info("Saved unified feature store to %s (%d rows, %d cols)", out_path, len(df_unified), len(df_unified.columns))
        return out_path
