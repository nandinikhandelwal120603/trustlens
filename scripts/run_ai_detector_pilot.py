"""TrustLens Phase G.1 — AI Detector Pilot Execution Script.

Runs a deterministic 40-image stratified pilot across diverse image types
to validate detector performance, compute agreement, evaluate recompression robustness,
and generate the Phase G.1 Gate Review Report.
"""

from collections import Counter
import datetime
import json
import logging
from pathlib import Path
import time
import pandas as pd
import pyarrow.parquet as pq

from trustlens.marketplace.ai_image_detector import AIImageDetectorPipeline

logger = logging.getLogger("trustlens.pilot")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    pipeline = AIImageDetectorPipeline()

    logger.info("--- PHASE G.1: SELECTING PILOT DATASET ---")
    pilot_df = pipeline.select_pilot_dataset(total_target=40)
    logger.info("Sampled %d images across types:\n%s", len(pilot_df), pilot_df["image_type"].value_counts())

    records = pilot_df.to_dict(orient="records")

    logger.info("--- PHASE G.1: RUNNING DETECTOR A (ViT-Base) ---")
    t0_a = time.time()
    results_a = pipeline.run_detector_a_batch(records, batch_size=8)
    elapsed_a = time.time() - t0_a
    logger.info("Detector A finished in %.2fs (%.2f ms/img)", elapsed_a, (elapsed_a / len(records)) * 1000)

    logger.info("--- PHASE G.1: RUNNING DETECTOR B (Swin-Base) ---")
    t0_b = time.time()
    results_b = pipeline.run_detector_b_batch(records, batch_size=8)
    elapsed_b = time.time() - t0_b
    logger.info("Detector B finished in %.2fs (%.2f ms/img)", elapsed_b, (elapsed_b / len(records)) * 1000)

    logger.info("--- PHASE G.1: COMBINING AND EVALUATING AGREEMENT ---")
    combined_df = pipeline.combine_and_build_dataset(pilot_df, results_a, results_b)

    agreement_counts = Counter(combined_df["detector_agreement"])
    logger.info("Agreement Breakdown: %s", dict(agreement_counts))
    logger.info("Assessment Status Breakdown: %s", dict(Counter(combined_df["assessment_status"])))

    escalated_count = combined_df["puter_escalated"].sum()
    logger.info("Puter Escalations: %d / %d (%.1f%%)", escalated_count, len(combined_df), (escalated_count / len(combined_df)) * 100)

    logger.info("--- PHASE G.1: RUNNING ROBUSTNESS RECOMPRESSION TEST (10 samples) ---")
    sample_10 = records[:10]
    robustness_res = pipeline.run_recompression_robustness_test(sample_10)
    rob_df = pd.DataFrame(robustness_res)
    logger.info("Robustness Status:\n%s", rob_df["robustness_status"].value_counts())

    # Save pilot metrics to a JSON report for gate review
    gate_metrics = {
        "pilot_images": len(combined_df),
        "detector_a_name": pipeline.DETECTOR_A_NAME,
        "detector_a_version": pipeline.DETECTOR_A_VERSION,
        "detector_a_total_time_s": round(elapsed_a, 2),
        "detector_a_avg_time_ms": round((elapsed_a / len(records)) * 1000, 2),
        "detector_b_name": pipeline.DETECTOR_B_NAME,
        "detector_b_version": pipeline.DETECTOR_B_VERSION,
        "detector_b_total_time_s": round(elapsed_b, 2),
        "detector_b_avg_time_ms": round((elapsed_b / len(records)) * 1000, 2),
        "agreement_distribution": dict(agreement_counts),
        "assessment_distribution": dict(Counter(combined_df["assessment_status"])),
        "puter_escalated_count": int(escalated_count),
        "robustness_summary": dict(rob_df["robustness_status"].value_counts()),
        "pilot_samples": combined_df[[
            "media_id", "image_type", "detector_a_raw_score", "detector_a_result",
            "detector_b_raw_score", "detector_b_result", "detector_agreement",
            "assessment_status", "puter_escalated"
        ]].to_dict(orient="records"),
        "robustness_records": robustness_res,
    }

    def json_serialize(obj):
        if hasattr(obj, "item"):
            return obj.item()
        if isinstance(obj, (pd.Timestamp, datetime.datetime)):
            return obj.isoformat()
        return str(obj)

    metrics_path = Path("data/olx_analysis/reports/pilot_gate_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(gate_metrics, f, indent=2, default=json_serialize)
    logger.info("Pilot gate metrics saved to %s", metrics_path)


if __name__ == "__main__":
    main()
