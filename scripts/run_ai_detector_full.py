"""TrustLens Phase G.1 — Full 2,280 Image AI Detector Pipeline Execution.

Executes:
1. Load all 2,280 local marketplace assets.
2. Checkpoint-supported sequential run:
   - Detector A (ViT-Base) -> Unload & Memory Purge
   - Detector B (Swin-Base) -> Unload & Memory Purge
3. Multi-detector agreement classification & Puter escalation candidate generation.
4. Output Parquet writing to `data/olx_processed/ai_detector_results.parquet`.
5. Publication figures generation.
"""

from collections import Counter
import datetime
import gc
import json
import logging
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
import pyarrow as pa
import pyarrow.parquet as pq
import torch

from trustlens.marketplace.ai_image_detector import AIImageDetectorPipeline

logger = logging.getLogger("trustlens.full_run")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def run_full_pipeline():
    pipeline = AIImageDetectorPipeline()

    auth_path = Path("data/olx_processed/image_authenticity.parquet")
    fp_path = Path("data/olx_processed/fingerprints.parquet")
    results_path = Path("data/olx_processed/ai_detector_results.parquet")
    checkpoint_path = Path("data/olx_processed/ai_detector_checkpoint.parquet")

    logger.info("Loading Phase C & G source metadata...")
    auth_df = pq.read_table(auth_path).to_pandas()
    fp_df = pq.read_table(fp_path).to_pandas()

    merged = auth_df[["media_id", "sha256", "c2pa_status", "image_type"]].merge(
        fp_df[["media_id", "local_path", "width", "height", "file_size_bytes"]],
        on="media_id",
        how="inner",
    )
    # Ensure local path exists
    merged["exists"] = merged["local_path"].apply(lambda p: os.path.exists(p) if pd.notnull(p) else False)
    usable_df = merged[merged["exists"]].sort_values("media_id").reset_index(drop=True)
    total_images = len(usable_df)
    logger.info("Total validated local images to process: %d", total_images)

    records = usable_df.to_dict(orient="records")

    # Step 1: Run Detector A (ViT-Base) with batching
    logger.info("=== STEP 1: EXECUTING DETECTOR A (ViT-Base) ON ALL %d IMAGES ===", total_images)
    t0_a = time.time()
    results_a = pipeline.run_detector_a_batch(records, batch_size=16)
    elapsed_a = time.time() - t0_a
    logger.info("Detector A complete: %d evaluations in %.2fs (%.2f ms/img)", len(results_a), elapsed_a, (elapsed_a / total_images) * 1000)

    # Step 2: Run Detector B (Swin-Base) with batching
    logger.info("=== STEP 2: EXECUTING DETECTOR B (Swin-Base) ON ALL %d IMAGES ===", total_images)
    t0_b = time.time()
    results_b = pipeline.run_detector_b_batch(records, batch_size=16)
    elapsed_b = time.time() - t0_b
    logger.info("Detector B complete: %d evaluations in %.2fs (%.2f ms/img)", len(results_b), elapsed_b, (elapsed_b / total_images) * 1000)

    # Step 3: Combine, Agreement Analysis, Puter Escalation
    logger.info("=== STEP 3: COMBINING SCORES & EVALUATING AGREEMENT ===")
    combined_df = pipeline.combine_and_build_dataset(usable_df, results_a, results_b)

    # Save to Parquet
    pipeline.save_results(combined_df, "ai_detector_results.parquet")

    # Stats
    agreement_counts = Counter(combined_df["detector_agreement"])
    assessment_counts = Counter(combined_df["assessment_status"])
    escalated_count = combined_df["puter_escalated"].sum()

    logger.info("Agreement Breakdown: %s", dict(agreement_counts))
    logger.info("Assessment Breakdown: %s", dict(assessment_counts))
    logger.info("Puter Escalation Total: %d / %d (%.2f%%)", escalated_count, len(combined_df), (escalated_count / len(combined_df)) * 100)

    # Step 4: Generate Publication Figures
    logger.info("=== STEP 4: GENERATING FORENSIC FIGURES ===")
    figures_dir = Path("data/olx_analysis/reports/figures")
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Figure 1: Score Distributions
    plt.figure(figsize=(10, 4.5))
    plt.subplot(1, 2, 1)
    a_scores = combined_df["detector_a_raw_score"].dropna()
    plt.hist(a_scores, bins=30, color="#2563EB", edgecolor="black", alpha=0.75)
    plt.axvline(0.70, color="red", linestyle="--", label="AI Thresh (0.70)")
    plt.axvline(0.30, color="green", linestyle="--", label="Real Thresh (0.30)")
    plt.title("Detector A (ViT-Base) Raw Score Distribution")
    plt.xlabel("Raw AI Score")
    plt.ylabel("Asset Count")
    plt.legend()

    plt.subplot(1, 2, 2)
    b_scores = combined_df["detector_b_raw_score"].dropna()
    plt.hist(b_scores, bins=30, color="#7C3AED", edgecolor="black", alpha=0.75)
    plt.axvline(0.70, color="red", linestyle="--", label="AI Thresh (0.70)")
    plt.axvline(0.30, color="green", linestyle="--", label="Real Thresh (0.30)")
    plt.title("Detector B (Swin-Base) Raw Score Distribution")
    plt.xlabel("Raw AI Score")
    plt.ylabel("Asset Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "fig_ai_detector_score_distributions.png", dpi=150)
    plt.close()

    # Figure 2: Agreement Matrix Breakdown by Image Type
    plt.figure(figsize=(8, 5))
    cross_tab = pd.crosstab(combined_df["image_type"], combined_df["detector_agreement"])
    cross_tab.plot(kind="bar", stacked=True, colormap="viridis", figsize=(9, 5), edgecolor="black")
    plt.title("Detector Agreement Breakdown by Deterministic Image Type")
    plt.xlabel("Image Type")
    plt.ylabel("Asset Count")
    plt.xticks(rotation=0)
    plt.legend(title="Detector Agreement", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(figures_dir / "fig_detector_agreement_by_image_type.png", dpi=150)
    plt.close()

    # Figure 3: Scatter Plot of Detector A vs Detector B Scores
    plt.figure(figsize=(7, 6))
    plt.scatter(
        combined_df["detector_a_raw_score"],
        combined_df["detector_b_raw_score"],
        c=combined_df["puter_escalated"].map({True: "#DC2626", False: "#059669"}),
        alpha=0.4,
        s=20,
    )
    plt.axvline(0.70, color="grey", linestyle=":")
    plt.axvline(0.30, color="grey", linestyle=":")
    plt.axhline(0.70, color="grey", linestyle=":")
    plt.axhline(0.30, color="grey", linestyle=":")
    plt.title("Detector A (ViT) vs Detector B (Swin) Score Correlation\n(Red: Puter Escalation)")
    plt.xlabel("Detector A Score")
    plt.ylabel("Detector B Score")
    plt.tight_layout()
    plt.savefig(figures_dir / "fig_detector_correlation_scatter.png", dpi=150)
    plt.close()

    logger.info("Figures successfully generated in %s", figures_dir)
    return combined_df


if __name__ == "__main__":
    run_full_pipeline()
