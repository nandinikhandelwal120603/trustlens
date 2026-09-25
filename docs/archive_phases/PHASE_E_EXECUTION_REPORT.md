# TrustLens — Phase E Execution Report
## Multimodal Text, OCR Extraction & Observational Inconsistency Analysis

- **Execution Date:** 2026-09-24T05:35:22.391337
- **Status:** COMPLETED & VERIFIED

---

### 1. Population & Processing Metrics
- **Media References:** 2,491 total references across 2,980 listings
- **Unique Apollo Assets:** 2,323 unique Apollo image IDs in capture corpus
- **Downloaded Assets:** 2,282 (98.24% of 2,323 unique Apollo assets)
- **Fingerprinted & Embedded Assets:** 2,280 (99.91% of 2,282 downloaded; 2 corrupted/0-byte excluded)
- **OCR Processed Assets:** 2,280 (100.0% of 2,280 fingerprinted/embedded assets)
- **OCR Success with Detectable Text:** 1,885 (82.68% of 2,280 evaluated)
- **OCR Success with No Text:** 395 (17.32% of 2,280 evaluated — clean visual subjects)
- **OCR Failures:** 0 (0.00%)
- **Engine / Version:** Tesseract OCR `5.5.2` (Local / Offline)
- **Processing Runtime:** 77.08 seconds (29.58 images/sec on Apple Silicon CPU, 4 workers)

### 2. Extracted Visual Observations
- **Model Observations:** 4
- **Storage Observations:** 1
- **Condition / Demo Observations:** 1

### 3. Inconsistency Candidate Counts (Status: UNVERIFIED_CANDIDATE)
- **TEXT_IMAGE_MODEL_MISMATCH:** 1
- **TEXT_IMAGE_STORAGE_MISMATCH:** 0
- **TEXT_IMAGE_VARIANT_MISMATCH:** 0
- **TEXT_IMAGE_CONDITION_MISMATCH:** 0
- **TEXT_IMAGE_DEMO_CLUE:** 1
- **SHARED_IMAGE_CLAIM_DRIFT:** 66
- **SHARED_IMAGE_PRICE_VARIANCE:** 0
- **Total Inconsistency Signals:** 68

### 4. Methodological Limitations
1. **Resolution & Stylization:** Low-resolution search card images or highly stylized text may escape deterministic OCR detection.
2. **Text-Positive Representation:** An image lacking text is a normal, valid result (e.g. clean product photograph without packaging).
3. **Provable Provenance:** All OCR detections represent visual text observations (`visual_text_observation`) and do not independently establish seller intent, counterfeit status, or fraud.
