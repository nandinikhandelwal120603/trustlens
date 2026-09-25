# TrustLens — Multimodal Text, OCR Extraction & Inconsistency Report (Phase E)
## Deterministic Visual Text Intelligence & Listing Claim Comparison

- **Generated At:** 2026-09-24T05:35:22.391172
- **OCR Engine:** Tesseract OCR (Version: `5.5.2`)
- **OCR Configuration:** `--psm 11` (Sparse text with OSD)
- **Status:** COMPLETED & VERIFIED (Phase E)

---

## 1. Asset Acquisition & OCR Population Hierarchy

| Processing Stage | Entity Count | Percentage / Rate | Methodological Context |
| :--- | :---: | :---: | :--- |
| **Media References** | **2,491** | 100.0% | Total image references across 2,980 listings. |
| **Unique Apollo Assets** | **2,323** | 100.0% | Unique Apollo image IDs in capture corpus. |
| **Download-Successful Assets** | **2,282** | 98.24% | Local WebP files downloaded to `data/olx_media/`. |
| **Successfully OCR Processed** | **2,280** | **100.0%** | Total downloaded assets evaluated through OCR pipeline. |
| **Assets with Detectable Text (OCR Positive)** | **1,885** | **82.68%** | Images containing valid text tokens and bounding boxes. |
| **Assets with No Detectable Text** | **395** | **17.32%** | Clean image subjects with zero text detected (valid result). |
| **OCR Pipeline Failures** | **0** | **0.00%** | File decode or execution errors. |

---

## 2. OCR Quality & Confidence Distribution

| Confidence Quality Band | Score Range | Asset Count | Percentage | Evidentiary Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **High Confidence** | $\ge 70.0$ | **113** | **4.96%** | Clear, legible printed text on boxes, screens, or invoices. |
| **Medium Confidence** | $40.0 - 69.9$ | **700** | **30.70%** | Moderate resolution or angled text. |
| **Low Confidence** | $< 40.0$ | **1,072** | **47.02%** | Sparse background noise, watermarks, or partial reflections. |
| **No Text (None)** | N/A | **395** | **17.32%** | Zero detected characters. |

---

## 3. Extracted Visual Technical Observations

- **Images with Explicit Hardware Models Detected:** **4**
- **Images with Explicit Storage Specifications Detected:** **1**
- **Images with Explicit Condition / Demo Unit Cues Detected:** **1**

---

## 4. Observational Inconsistency Candidates (Status: UNVERIFIED)

| Inconsistency Category | Candidate Count | Evidentiary Strength | Methodological Meaning |
| :--- | :---: | :---: | :--- |
| **`TEXT_IMAGE_MODEL_MISMATCH`** | **1** | Explicit / Probable | Title claims specific model, but image OCR reveals a different model generation. |
| **`TEXT_IMAGE_STORAGE_MISMATCH`** | **0** | Explicit / Probable | Title claims storage capacity, but box/screen OCR displays different capacity. |
| **`TEXT_IMAGE_DEMO_CLUE`** | **1** | Explicit | Commercial listing contains explicit "Demo", "Display", or lock keyword in image. |
| **`SHARED_IMAGE_CLAIM_DRIFT`** | **66** | Explicit | Distinct listings sharing identical/near-identical visual assets claim conflicting product models. |
| **`SHARED_IMAGE_PRICE_VARIANCE`** | **0** | Explicit | Distinct listings sharing identical visual assets exhibit $> 50\%$ price divergence ($\ge ₹5,000$). |
| **Total Inconsistency Candidates** | **68** | **UNVERIFIED** | **Observational signals flagged for human audit (No automated fraud accusations).** |

---

## 5. Analytical Parquet Artifacts

1. **`data/olx_processed/image_ocr.parquet`**: Master OCR table (2,282 rows) with raw, normalized, redacted text and confidence scores.
2. **`data/olx_processed/multimodal_inconsistencies.parquet`**: Structured inconsistency candidate records.
3. **`data/olx_analysis/reports/multimodal_ocr_gallery.html`**: Inspectable gallery with PII redacted.
