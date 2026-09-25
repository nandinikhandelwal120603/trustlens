# TrustLens Phase G.1 — Execution Report: Actual AI Image Detection

**Status:** COMPLETE  
**Execution Timestamp:** 2026-09-24T12:35:00+05:30  
**Phase Boundary Enforcement:** Phases A–G intact and unmodified.  

---

## 1. Pipeline Execution Metrics

| Pipeline Stage | Parameter / Model | Target Count | Processed | Elapsed Time | Speed | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Detector A** | `dima806/ai_vs_human_generated_image_detection` (ViT-Base) | 2,280 | 2,280 | 102.87 s | 45.12 ms/img | **PASSED** |
| **Memory Purge** | Sequential unload, gc.collect(), cache purge | — | — | < 1.0 s | — | **PASSED** |
| **Detector B** | `umm-maybe/AI-image-detector` (Swin-Base) | 2,280 | 2,280 | 132.81 s | 58.25 ms/img | **PASSED** |
| **Memory Purge** | Sequential unload, gc.collect(), cache purge | — | — | < 1.0 s | — | **PASSED** |
| **Agreement Eval** | Multi-source transparent tier classification | 2,280 | 2,280 | 0.85 s | — | **PASSED** |
| **Puter Queue** | Disagreement / Borderline queue generation | 1,316 | 1,316 | 0.12 s | — | **PASSED** |
| **Parquet Export** | `data/olx_processed/ai_detector_results.parquet` | 2,280 | 2,280 | 0.15 s | — | **PASSED** |
| **Gallery Export** | `data/olx_analysis/reports/ai_detector_gallery.html` | 71 | 71 | 0.20 s | — | **PASSED** |

---

## 2. Resource & Safety Audit Verification

- **Host Machine:** Apple Mac (Apple M4, 10 cores, ARM64)
- **Unified RAM:** 16 GB total (~4.91 GB available prior to run)
- **Peak Model Memory:** ~360 MB (strictly one model in memory at any point)
- **Total Memory Footprint:** < 800 MB (well within 4.91 GB budget)
- **Crashes / OOM / SIGSEGV:** **0 crashes** (PyTorch MPS / CPU execution verified without OpenMP thread contention)
- **Local Validation Status:** `controlled_validation_available = false` (explicitly documented)

---

## 3. Puter Multimodal Escalation Execution Status

```text
sent_to_puter: 0
successful_responses: 0
failed_requests: 0
escalation_queue_size: 1,316 assets
  - DETECTOR_DISAGREEMENT: 559 assets
  - BORDERLINE: 757 assets
execution_status: UNEXECUTED_QUEUE (Offline local pipeline run)
```

---

## 4. Results Table Schema Conformance (19 Fields)

The primary dataset `data/olx_processed/ai_detector_results.parquet` strictly adheres to the Section 17 schema:
```text
1. media_id (str)
2. sha256 (str)
3. detector_a_name (str)
4. detector_a_version (str)
5. detector_a_raw_score (float64)
6. detector_a_result (str)
7. detector_b_name (str)
8. detector_b_version (str)
9. detector_b_raw_score (float64)
10. detector_b_result (str)
11. detector_agreement (str)
12. assessment_status (str)
13. puter_escalated (bool)
14. puter_result (str)
15. c2pa_status (str)
16. image_type (str)
17. runtime_a_ms (float64)
18. runtime_b_ms (float64)
19. created_at (str)
```

---

## 5. Test Suite Pass Rate

```text
tests/marketplace/test_ai_detector.py ...... [100%]
Full Project Test Suite: 87 passed, 1 skipped (0 failures)
```

---

## 6. Deliverable Links

- Primary Parquet: [`ai_detector_results.parquet`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/data/olx_processed/ai_detector_results.parquet)
- Analysis Report: [`AI_IMAGE_DETECTION_ANALYSIS.md`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/AI_IMAGE_DETECTION_ANALYSIS.md)
- Execution Report: [`PHASE_G1_EXECUTION_REPORT.md`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/PHASE_G1_EXECUTION_REPORT.md)
- Resource Audit: [`PHASE_G1_DETECTOR_RESOURCE_AUDIT.md`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/PHASE_G1_DETECTOR_RESOURCE_AUDIT.md)
- Visual Gallery: [`ai_detector_gallery.html`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/ai_detector_gallery.html)
- Figures Directory: [`data/olx_analysis/reports/figures/`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/data/olx_analysis/reports/figures)

---

```text
PHASE G.1: COMPLETE
PHASE H: NOT STARTED
```
