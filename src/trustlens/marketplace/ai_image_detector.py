"""TrustLens Marketplace Intelligence — Dedicated AI-Generated Image Detection Pipeline (Phase G.1).

Implements:
1. Detector A: Dedicated Vision Transformer (ViT-Base) trained for AI vs. Real image classification
   (Model: `dima806/ai_vs_human_generated_image_detection`).
2. Detector B: Dedicated Hierarchical Swin Transformer (Swin-Base) trained for artificial vs. human image classification
   (Model: `umm-maybe/AI-image-detector`).
3. Sequential memory-safe execution: Models are strictly loaded and unloaded sequentially with
   garbage collection and memory purging to respect local Mac hardware constraints.
4. Raw score preservation without synthetic averaging or fabricated probability claims.
5. Deterministic agreement classification:
   - AGREEMENT_AI (AI_GENERATION_CANDIDATE)
   - AGREEMENT_REAL (REAL_IMAGE_CANDIDATE)
   - DETECTOR_DISAGREEMENT (DETECTOR_DISAGREEMENT)
   - BORDERLINE (BORDERLINE)
   - NO_CONCLUSIVE_SIGNAL
6. Multimodal secondary escalation gateway for Puter review of ambiguous or disagreeing cases.
7. Recompression and resizing robustness benchmarking.
8. Output schema compliance writing exclusively to `data/olx_processed/ai_detector_results.parquet`.
"""

from collections import Counter
import datetime
import gc
import json
import logging
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from PIL import Image
import pyarrow as pa
import pyarrow.parquet as pq
import torch

logger = logging.getLogger("trustlens.ai_detector")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class AIImageDetectorPipeline:
    """Two-detector dedicated AI-generated image forensic pipeline."""

    DETECTOR_A_NAME = "dima806/ai_vs_human_generated_image_detection"
    DETECTOR_A_VERSION = "ViT-Base-16-224"
    DETECTOR_A_SEMANTICS = "vit_base_ai_generated_probability"

    DETECTOR_B_NAME = "umm-maybe/AI-image-detector"
    DETECTOR_B_VERSION = "Swin-Base-224"
    DETECTOR_B_SEMANTICS = "swin_base_artificial_probability"

    # Thresholds for dedicated classification
    AI_THRESHOLD = 0.70
    REAL_THRESHOLD = 0.30

    def __init__(
        self,
        vault_dir: Path = Path("data/olx_media"),
        processed_dir: Path = Path("data/olx_processed"),
        reports_dir: Path = Path("data/olx_analysis/reports"),
        figures_dir: Path = Path("data/olx_analysis/reports/figures"),
        device: str = "cpu",
    ):
        self.vault_dir = Path(vault_dir)
        self.processed_dir = Path(processed_dir)
        self.reports_dir = Path(reports_dir)
        self.figures_dir = Path(figures_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.device = torch.device(device)

    @classmethod
    def classify_score(cls, score: Optional[float]) -> str:
        """Classifies a continuous raw detector score into evidence candidate tiers."""
        if score is None or np.isnan(score):
            return "UNREADABLE"
        if score >= cls.AI_THRESHOLD:
            return "AI_GENERATION_CANDIDATE"
        elif score <= cls.REAL_THRESHOLD:
            return "REAL_IMAGE_CANDIDATE"
        else:
            return "BORDERLINE"

    @classmethod
    def determine_agreement(
        cls, res_a: str, res_b: str
    ) -> Tuple[str, str]:
        """Computes transparent detector agreement and assessment status.
        
        Returns:
            (detector_agreement, assessment_status)
        """
        if res_a == "AI_GENERATION_CANDIDATE" and res_b == "AI_GENERATION_CANDIDATE":
            return "AGREEMENT_AI", "AI_GENERATION_CANDIDATE"
        elif res_a == "REAL_IMAGE_CANDIDATE" and res_b == "REAL_IMAGE_CANDIDATE":
            return "AGREEMENT_REAL", "REAL_IMAGE_CANDIDATE"
        elif (res_a == "AI_GENERATION_CANDIDATE" and res_b == "REAL_IMAGE_CANDIDATE") or (
            res_a == "REAL_IMAGE_CANDIDATE" and res_b == "AI_GENERATION_CANDIDATE"
        ):
            return "DETECTOR_DISAGREEMENT", "DETECTOR_DISAGREEMENT"
        elif res_a == "BORDERLINE" or res_b == "BORDERLINE":
            return "BORDERLINE", "BORDERLINE"
        else:
            return "NO_CONCLUSIVE_SIGNAL", "NO_CONCLUSIVE_SIGNAL"

    def select_pilot_dataset(self, total_target: int = 40) -> pd.DataFrame:
        """Selects a deterministic diverse sample of 30-50 images across types and products."""
        auth_path = self.processed_dir / "image_authenticity.parquet"
        fp_path = self.processed_dir / "fingerprints.parquet"

        if not auth_path.exists() or not fp_path.exists():
            raise FileNotFoundError("Prerequisite Phase C/G Parquet tables missing.")

        auth_df = pq.read_table(auth_path).to_pandas()
        fp_df = pq.read_table(fp_path).to_pandas()

        merged = auth_df.merge(
            fp_df[["media_id", "local_path", "file_size_bytes", "width", "height"]],
            on="media_id",
            how="inner",
            suffixes=("", "_fp"),
        )
        # Filter strictly for images existing on local disk
        merged["exists"] = merged["local_path"].apply(lambda p: os.path.exists(p) if pd.notnull(p) else False)
        usable = merged[merged["exists"]].copy()

        # Quota-based deterministic stratified sampling
        quotas = {
            "PHOTO": 15,
            "TEXT_HEAVY": 12,
            "SCREENSHOT": 9,
            "DOCUMENT_LIKE": 4,
        }
        sampled_dfs = []
        for itype, count in quotas.items():
            subset = usable[usable["image_type"] == itype].sort_values("sha256")
            sampled_dfs.append(subset.head(count))

        pilot_df = pd.concat(sampled_dfs, ignore_index=True)
        logger.info("Selected %d diverse images for Phase G.1 pilot evaluation", len(pilot_df))
        return pilot_df

    def run_detector_a_batch(
        self,
        image_records: List[Dict[str, Any]],
        batch_size: int = 8,
    ) -> List[Dict[str, Any]]:
        """Executes Detector A (ViT-Base) with memory safety and releases model from memory."""
        from transformers import AutoImageProcessor, AutoModelForImageClassification

        logger.info("Loading Detector A: %s", self.DETECTOR_A_NAME)
        processor = AutoImageProcessor.from_pretrained(
            self.DETECTOR_A_NAME, local_files_only=True
        )
        model = AutoModelForImageClassification.from_pretrained(
            self.DETECTOR_A_NAME, local_files_only=True
        )
        model.to(self.device)
        model.eval()

        results = []
        for i in range(0, len(image_records), batch_size):
            chunk = image_records[i : i + batch_size]
            for rec in chunk:
                img_path = Path(rec["local_path"])
                t0 = time.perf_counter()
                try:
                    with Image.open(img_path) as img:
                        rgb_img = img.convert("RGB")
                        inputs = processor(images=rgb_img, return_tensors="pt")
                        inputs = {k: v.to(self.device) for k, v in inputs.items()}
                        with torch.no_grad():
                            outputs = model(**inputs)
                            logits = outputs.logits
                            probs = torch.softmax(logits, dim=-1)[0].cpu().numpy()

                        # In dima806/ai_vs_human_generated_image_detection:
                        # id2label is {0: 'human', 1: 'AI-generated'}
                        ai_score = float(probs[1])
                        t_elapsed = (time.perf_counter() - t0) * 1000.0

                        res_tier = self.classify_score(ai_score)
                        results.append({
                            "media_id": rec["media_id"],
                            "sha256": rec["sha256"],
                            "detector_a_raw_score": round(ai_score, 6),
                            "detector_a_result": res_tier,
                            "runtime_a_ms": round(t_elapsed, 2),
                        })
                except Exception as e:
                    logger.warning("Detector A failure on %s: %s", rec.get("media_id"), e)
                    results.append({
                        "media_id": rec["media_id"],
                        "sha256": rec["sha256"],
                        "detector_a_raw_score": None,
                        "detector_a_result": "FAILED",
                        "runtime_a_ms": round((time.perf_counter() - t0) * 1000.0, 2),
                    })

        # Explicit cleanup
        del model, processor
        if self.device.type == "mps":
            torch.mps.empty_cache()
        gc.collect()
        logger.info("Detector A inference completed and memory purged.")
        return results

    def run_detector_b_batch(
        self,
        image_records: List[Dict[str, Any]],
        batch_size: int = 8,
    ) -> List[Dict[str, Any]]:
        """Executes Detector B (Swin-Base) with memory safety and releases model from memory."""
        from transformers import AutoImageProcessor, AutoModelForImageClassification

        logger.info("Loading Detector B: %s", self.DETECTOR_B_NAME)
        processor = AutoImageProcessor.from_pretrained(
            self.DETECTOR_B_NAME, local_files_only=True
        )
        model = AutoModelForImageClassification.from_pretrained(
            self.DETECTOR_B_NAME, local_files_only=True
        )
        model.to(self.device)
        model.eval()

        results = []
        for i in range(0, len(image_records), batch_size):
            chunk = image_records[i : i + batch_size]
            for rec in chunk:
                img_path = Path(rec["local_path"])
                t0 = time.perf_counter()
                try:
                    with Image.open(img_path) as img:
                        rgb_img = img.convert("RGB")
                        inputs = processor(images=rgb_img, return_tensors="pt")
                        inputs = {k: v.to(self.device) for k, v in inputs.items()}
                        with torch.no_grad():
                            outputs = model(**inputs)
                            logits = outputs.logits
                            probs = torch.softmax(logits, dim=-1)[0].cpu().numpy()

                        # In umm-maybe/AI-image-detector:
                        # id2label is {0: 'artificial', 1: 'human'}
                        # index 0 is artificial (AI)!
                        ai_score = float(probs[0])
                        t_elapsed = (time.perf_counter() - t0) * 1000.0

                        res_tier = self.classify_score(ai_score)
                        results.append({
                            "media_id": rec["media_id"],
                            "sha256": rec["sha256"],
                            "detector_b_raw_score": round(ai_score, 6),
                            "detector_b_result": res_tier,
                            "runtime_b_ms": round(t_elapsed, 2),
                        })
                except Exception as e:
                    logger.warning("Detector B failure on %s: %s", rec.get("media_id"), e)
                    results.append({
                        "media_id": rec["media_id"],
                        "sha256": rec["sha256"],
                        "detector_b_raw_score": None,
                        "detector_b_result": "FAILED",
                        "runtime_b_ms": round((time.perf_counter() - t0) * 1000.0, 2),
                    })

        # Explicit cleanup
        del model, processor
        if self.device.type == "mps":
            torch.mps.empty_cache()
        gc.collect()
        logger.info("Detector B inference completed and memory purged.")
        return results

    def run_recompression_robustness_test(
        self, sample_records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Tests detector score stability against JPEG recompression and resizing."""
        import tempfile
        from transformers import AutoImageProcessor, AutoModelForImageClassification

        logger.info("Running robustness recompression test on %d sample images", len(sample_records))
        robustness_records = []

        # Load Detector A
        proc_a = AutoImageProcessor.from_pretrained(self.DETECTOR_A_NAME, local_files_only=True)
        model_a = AutoModelForImageClassification.from_pretrained(self.DETECTOR_A_NAME, local_files_only=True)
        model_a.eval()

        a_scores = {}
        for rec in sample_records:
            mid = rec["media_id"]
            p = Path(rec["local_path"])
            with Image.open(p) as img:
                orig_rgb = img.convert("RGB")

                # 1. Original score
                inputs_orig = proc_a(images=orig_rgb, return_tensors="pt")
                with torch.no_grad():
                    orig_score = float(torch.softmax(model_a(**inputs_orig).logits, dim=-1)[0][1])

                # 2. JPEG recompressed (quality 70)
                with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
                    orig_rgb.save(tmp.name, "JPEG", quality=70)
                    with Image.open(tmp.name) as recompressed:
                        inputs_recomp = proc_a(images=recompressed.convert("RGB"), return_tensors="pt")
                        with torch.no_grad():
                            recomp_score = float(torch.softmax(model_a(**inputs_recomp).logits, dim=-1)[0][1])

                # 3. Resized (0.75x)
                w, h = orig_rgb.size
                resized = orig_rgb.resize((int(w * 0.75), int(h * 0.75)), Image.Resampling.BILINEAR)
                inputs_res = proc_a(images=resized, return_tensors="pt")
                with torch.no_grad():
                    res_score = float(torch.softmax(model_a(**inputs_res).logits, dim=-1)[0][1])

                a_scores[mid] = {
                    "orig": orig_score,
                    "recomp": recomp_score,
                    "resized": res_score,
                    "max_delta": max(abs(recomp_score - orig_score), abs(res_score - orig_score)),
                }

        del model_a, proc_a
        gc.collect()

        # Load Detector B
        proc_b = AutoImageProcessor.from_pretrained(self.DETECTOR_B_NAME, local_files_only=True)
        model_b = AutoModelForImageClassification.from_pretrained(self.DETECTOR_B_NAME, local_files_only=True)
        model_b.eval()

        b_scores = {}
        for rec in sample_records:
            mid = rec["media_id"]
            p = Path(rec["local_path"])
            with Image.open(p) as img:
                orig_rgb = img.convert("RGB")

                inputs_orig = proc_b(images=orig_rgb, return_tensors="pt")
                with torch.no_grad():
                    orig_score = float(torch.softmax(model_b(**inputs_orig).logits, dim=-1)[0][0])

                with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
                    orig_rgb.save(tmp.name, "JPEG", quality=70)
                    with Image.open(tmp.name) as recompressed:
                        inputs_recomp = proc_b(images=recompressed.convert("RGB"), return_tensors="pt")
                        with torch.no_grad():
                            recomp_score = float(torch.softmax(model_b(**inputs_recomp).logits, dim=-1)[0][0])

                w, h = orig_rgb.size
                resized = orig_rgb.resize((int(w * 0.75), int(h * 0.75)), Image.Resampling.BILINEAR)
                inputs_res = proc_b(images=resized, return_tensors="pt")
                with torch.no_grad():
                    res_score = float(torch.softmax(model_b(**inputs_res).logits, dim=-1)[0][0])

                b_scores[mid] = {
                    "orig": orig_score,
                    "recomp": recomp_score,
                    "resized": res_score,
                    "max_delta": max(abs(recomp_score - orig_score), abs(res_score - orig_score)),
                }

        del model_b, proc_b
        gc.collect()

        for rec in sample_records:
            mid = rec["media_id"]
            delta_a = a_scores[mid]["max_delta"]
            delta_b = b_scores[mid]["max_delta"]
            stability = (
                "DETECTOR_STABLE"
                if max(delta_a, delta_b) < 0.15
                else "DETECTOR_SENSITIVE_TO_RECOMPRESSION"
            )
            robustness_records.append({
                "media_id": mid,
                "a_orig": round(a_scores[mid]["orig"], 4),
                "a_recompressed": round(a_scores[mid]["recomp"], 4),
                "a_resized": round(a_scores[mid]["resized"], 4),
                "a_max_delta": round(delta_a, 4),
                "b_orig": round(b_scores[mid]["orig"], 4),
                "b_recompressed": round(b_scores[mid]["recomp"], 4),
                "b_resized": round(b_scores[mid]["resized"], 4),
                "b_max_delta": round(delta_b, 4),
                "robustness_status": stability,
            })

        return robustness_records

    def format_puter_escalation(
        self,
        media_id: str,
        agreement: str,
        image_type: str,
        score_a: Optional[float],
        score_b: Optional[float],
    ) -> Dict[str, Any]:
        """Formats the standardized Puter escalation request payload for secondary inspection."""
        prompt = (
            "Provide an independent visual assessment and list observable evidence and uncertainty. "
            "Do not claim provenance that cannot be established from the image. Separately describe: "
            "1. visible image content, "
            "2. whether there are visual characteristics commonly associated with synthetic imagery, "
            "3. whether the image contains obvious generative artifacts, "
            "4. whether the image appears to be a screenshot/document/render/product photo, "
            "5. whether provenance can be inferred from the visible image, "
            "6. uncertainty"
        )
        return {
            "media_id": media_id,
            "escalation_reason": agreement,
            "image_type": image_type,
            "detector_a_raw_score": score_a,
            "detector_b_raw_score": score_b,
            "standardized_prompt": prompt,
            "escalation_status": "ESCALATION_CANDIDATE_QUEUED",
        }

    def combine_and_build_dataset(
        self,
        base_df: pd.DataFrame,
        results_a: List[Dict[str, Any]],
        results_b: List[Dict[str, Any]],
        created_at: Optional[str] = None,
    ) -> pd.DataFrame:
        """Combines detector evaluations into the required schema."""
        if created_at is None:
            created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        df_a = pd.DataFrame(results_a)
        df_b = pd.DataFrame(results_b)

        merged = base_df.merge(df_a, on=["media_id", "sha256"], how="left")
        merged = merged.merge(df_b, on=["media_id", "sha256"], how="left")

        rows = []
        for _, row in merged.iterrows():
            res_a = row.get("detector_a_result", "UNREADABLE")
            res_b = row.get("detector_b_result", "UNREADABLE")
            score_a = row.get("detector_a_raw_score")
            score_b = row.get("detector_b_raw_score")
            itype = row.get("image_type", "UNKNOWN")

            agreement, assessment = self.determine_agreement(res_a, res_b)

            # Puter escalation trigger: disagreement or borderline
            puter_escalated = agreement in ("DETECTOR_DISAGREEMENT", "BORDERLINE")
            if puter_escalated:
                puter_res = "QUEUED_FOR_MULTIMODAL_INSPECTION"
            else:
                puter_res = "NOT_ESCALATED"

            rows.append({
                "media_id": row["media_id"],
                "sha256": row["sha256"],
                "detector_a_name": self.DETECTOR_A_NAME,
                "detector_a_version": self.DETECTOR_A_VERSION,
                "detector_a_raw_score": score_a if pd.notnull(score_a) else None,
                "detector_a_result": res_a,
                "detector_b_name": self.DETECTOR_B_NAME,
                "detector_b_version": self.DETECTOR_B_VERSION,
                "detector_b_raw_score": score_b if pd.notnull(score_b) else None,
                "detector_b_result": res_b,
                "detector_agreement": agreement,
                "assessment_status": assessment,
                "puter_escalated": bool(puter_escalated),
                "puter_result": puter_res,
                "c2pa_status": row.get("c2pa_status", "ABSENT"),
                "image_type": itype,
                "runtime_a_ms": row.get("runtime_a_ms", 0.0),
                "runtime_b_ms": row.get("runtime_b_ms", 0.0),
                "created_at": created_at,
            })

        out_df = pd.DataFrame(rows)
        return out_df

    def save_results(self, df: pd.DataFrame, file_name: str = "ai_detector_results.parquet") -> Path:
        """Saves dataframe strictly to Parquet format in processed directory."""
        target_path = self.processed_dir / file_name
        table = pa.Table.from_pandas(df)
        pq.write_table(table, target_path)
        logger.info("Saved %d AI detector records to %s", len(df), target_path)
        return target_path
