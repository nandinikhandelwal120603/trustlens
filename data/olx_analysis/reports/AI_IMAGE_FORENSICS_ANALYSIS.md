# TrustLens — AI Image, Provenance & Authenticity Forensics Report (Phase G)
## Multi-Layer Provenance, EXIF Metadata & Deterministic Forensics

- **Generated At:** 2026-09-24T05:56:15.461970
- **Forensic Pipeline:** C2PA Inspection + EXIF Extraction + 2D FFT Spectral Forensics + Semantic Concordance
- **Status:** COMPLETED & VERIFIED (Phase G)

---

## 1. Population & Provenance Hierarchy

| Processing Stage | Entity Count | Percentage / Rate | Methodological Context |
| :--- | :---: | :---: | :--- |
| **Media References** | **2,491** | 100.0% | Total image references across 2,980 listings. |
| **Unique Apollo Assets** | **2,323** | 100.0% | Unique Apollo image IDs in capture corpus. |
| **Download-Successful Assets** | **2,282** | 98.24% | Local WebP files downloaded to `data/olx_media/`. |
| **Fingerprinted & Evaluated Assets** | **2,280** | **100.0%** | Valid, non-corrupted images evaluated across Phase G. |
| **C2PA / Content Credentials Present** | **0** | **0.00%** | Zero marketplace images contained C2PA metadata containers. |
| **C2PA Provenance Absent** | **2,280** | **100.00%** | Normal marketplace recompression strips provenance containers. |

---

## 2. EXIF Metadata Availability & Stripping

| Metadata Category | Available Count | Rate (%) | Evidentiary Interpretation |
| :--- | :---: | :---: | :--- |
| **EXIF Headers Present** | **0** | **0.00%** | Marketplace ingestion pipeline re-encodes assets to WebP and strips EXIF. |
| **Camera Make / Model Tagged** | **0** | **0.00%** | No hardware device tags preserved in web delivery stream. |
| **GPS Geolocation Present** | **0** | **0.00%** | Zero geographic coordinates exposed (100% privacy preserved). |

> **Scientific Rule on Metadata Stripping:**
> Absence of EXIF metadata is standard marketplace platform behavior (platforms optimize image bandwidth via WebP conversion) and must **never** be cited as evidence of manipulation or fraud.

---

## 3. Deterministic Image Type Classification

| Image Type | Asset Count | Percentage (%) | Classification Basis |
| :--- | :---: | :---: | :--- |
| **`PHOTO` (Product Photograph)** | **1,670** | **73.25%** | Natural photographic framing with low/moderate packaging text. |
| **`SCREENSHOT` (Screen UI Capture)** | **174** | **7.63%** | Tall mobile UI aspect ratio ($\le 0.60$) with substantial visible OCR text. |
| **`TEXT_HEAVY` (Dense Text Subject)** | **417** | **18.29%** | Dense text bounding-box layout or high OCR character count ($\ge 50$). |
| **`DOCUMENT_LIKE` (Invoices/Bills)** | **19** | **0.83%** | Printed receipt/bill aspect ratio with dense tabular OCR text. |

---

## 4. Multi-Signal Forensic Evaluation (Status: UNVERIFIED)

| Forensic Status | Asset Count | Percentage (%) | Scientific Meaning |
| :--- | :---: | :---: | :--- |
| **`REAL_IMAGE_CANDIDATE`** | **587** | **25.75%** | Harmonic 2D FFT spectral decay consistent with natural optical lens capture. |
| **`BORDERLINE`** | **43** | **1.89%** | Very smooth studio backgrounds or low colorfulness requiring human review. |
| **`NO_CONCLUSIVE_SIGNAL`** | **1,650** | **72.37%** | Severe platform compression artifacts preventing high-confidence classification. |

---

## 5. Analytical Parquet Artifacts

1. **`data/olx_processed/image_authenticity.parquet`**: Master forensic table (2,280 rows).
2. **`data/olx_analysis/reports/image_forensics_gallery.html`**: Inspectable gallery.
3. **`PHASE_G_RESOURCE_AUDIT.md`**: Machine resource and system stability audit.
