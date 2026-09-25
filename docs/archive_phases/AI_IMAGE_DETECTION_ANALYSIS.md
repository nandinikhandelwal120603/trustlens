# TrustLens — Dedicated AI Image Detection Forensic Analysis (Phase G.1)

**Execution Date:** 2026-09-24  
**Runtime Environment:** Apple Mac (Apple M4, 16 GB unified RAM, macOS Darwin 25)  
**Evaluated Cohort:** 2,280 local marketplace media assets (`data/olx_media/`)  
**Parquet Primary Artifact:** `data/olx_processed/ai_detector_results.parquet`  
**Prior Phase Integrity:** Phases A–G strictly frozen and verified unchanged.  

---

## 1. Executive Summary & Forensic Findings

Phase G.1 deploys **two dedicated, architecturally distinct open-source neural image detectors** trained specifically to discriminate real camera captures from synthetic generative imagery:

1. **Detector A:** `dima806/ai_vs_human_generated_image_detection`  
   *Architecture:* Vision Transformer (ViT-Base-16-224, ~86M parameters).  
   *Class Semantics:* Logit / Softmax probability of `AI-generated` class (class 1).
2. **Detector B:** `umm-maybe/AI-image-detector`  
   *Architecture:* Hierarchical Swin Transformer (Swin-Base-224, ~87M parameters).  
   *Class Semantics:* Logit / Softmax probability of `artificial` class (class 0).

### Key Aggregate Statistics (N = 2,280 Evaluated Assets)

| Forensic Agreement Classification | Asset Count | Population % | Assessment Status Category |
| :--- | :--- | :--- | :--- |
| **`AGREEMENT_REAL`** | **958** | **42.02%** | `REAL_IMAGE_CANDIDATE` |
| **`BORDERLINE`** | **757** | **33.20%** | `BORDERLINE` |
| **`DETECTOR_DISAGREEMENT`** | **559** | **24.52%** | `DETECTOR_DISAGREEMENT` |
| **`AGREEMENT_AI`** | **6** | **0.26%** | `AI_GENERATION_CANDIDATE` |
| **Total Cohort** | **2,280** | **100.0%** | — |

---

## 2. In-Depth Detector Comparison & Disagreement Dynamics

### Detector A vs. Detector B Performance Profiles

| Metric | Detector A (`dima806/...`) | Detector B (`umm-maybe/...`) |
| :--- | :--- | :--- |
| **Model Family** | Standard Vision Transformer (ViT) | Hierarchical Swin Transformer (Shifted Windows) |
| **Patch / Window Mechanism** | Fixed non-overlapping 16x16 patches | Multi-scale shifted 7x7 windows |
| **Inference Runtime (2,280 Assets)** | 102.87 s (45.12 ms/image) | 132.81 s (58.25 ms/image) |
| **Mean Raw Score** | 0.0814 (heavily skewed to Real) | 0.4418 (bimodal / elevated sensitivity) |
| **Median Raw Score** | 0.0162 | 0.3951 |
| **AI Candidates (Score >= 0.70)** | 7 assets (0.31%) | 623 assets (27.32%) |
| **Real Candidates (Score <= 0.30)** | 2,126 assets (93.25%) | 1,023 assets (44.87%) |
| **Borderline (0.30 < Score < 0.70)** | 147 assets (6.45%) | 634 assets (27.81%) |

### Asymmetric Disagreement Breakdown
Out of 559 direct disagreements:
- **Detector A = REAL & Detector B = AI:** **558 assets (99.82%)**
- **Detector A = AI & Detector B = REAL:** **1 asset (0.18%)**

### Methodological Interpretation
The strong detector divergence observed on this OLX-derived cohort demonstrates the practical value of retaining multiple independent detector signals. The observed asymmetry is consistent with sensitivity to image-processing artifacts, but the specific causal mechanism was not independently established. 

Because we do not have a verified ground-truth benchmark for this specific marketplace cohort, we **cannot declare Detector A correct and Detector B wrong**, nor vice versa. Keeping both raw signals separately without averaging provides transparent evidence rather than unjustified certainty.

---

## 3. Manual Cross-Layer Inspection of the 6 Mutual Candidates

Across the entire dataset of 2,280 images, exactly **6 assets** crossed the operational candidate threshold ($\ge 0.70$) on both independent neural architectures. 

A multi-phase manual cross-reference was conducted against Phase C (hashes/clusters), Phase D (DINOv2 similarity), Phase E (OCR text/cues), and Phase G (image type classification):

| Media ID | Listing Title | Product | Dim & Size | Det A Score | Det B Score | Image Type (Phase G) | OCR Status (Phase E) | Cross-Listing / Visual Neighbors (Phase C & D) | Forensic Finding & Context |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `MED-1835966549-0` | Dead kharab Purane Phone lete sell krne ke liye call kre achha rate pe | iPhone | 150x200 (11.4 KB) | 0.7038 | 0.9984 | `DOCUMENT_LIKE` | `success_text` (53.0% conf, text: "war aet ne dea phone") | High DINO similarity (**0.7674**) to `MED-1849662426-0` | **Commercial Buyer Banner:** Digital graphic card advertising old phone purchasing. Contains digital typography and layout elements, not a natural camera photo. |
| `MED-1842975565-0` | Iphone 13 pro max for exchange | iPhone | 150x198 (2.2 KB) | 0.9750 | 0.7724 | `PHOTO` | `success_no_text` (0.0% conf) | 0 visual neighbors $\ge 0.70$ | **Heavily Compressed Thumbnail:** Low-resolution thumbnail (2.2 KB) exhibiting extreme lossy WebP quantization and complete lack of camera sensor grain. |
| `MED-1849662426-0` | All types of mobile repairing done here | iPhone | 150x213 (10.0 KB) | 0.9051 | 0.9922 | `DOCUMENT_LIKE` | `success_text` (30.3% conf, text: "876703602") | High DINO similarity (**0.7674**) to `MED-1835966549-0` | **Commercial Repair Graphic:** Digital flyer/card advertising repair services with phone number. Synthetic digital graphic card, not a physical product photo. |
| `MED-1855112256-0` | PS5 CONTROLLER EXCELLENT CONDITION | PS5 Controller | 150x113 (2.6 KB) | 0.7832 | 0.9817 | `TEXT_HEAVY` | `success_text` (66.0% conf) | 10 high visual similarity edges in Phase D ($\ge 0.70$) | **Digital Banner / Crop:** Low-res cropped accessory graphic (2.6 KB) with digital text overlays. Appears in multiple visually related listings. |
| `MED-1855210274-0` | MacBook Pro 16-inch 2019 / Core i7 / 32GB RAM / 512GB SSD | MacBook | 150x200 (5.3 KB) | 0.8831 | 0.9959 | `PHOTO` | `success_text` (35.0% conf) | 1 visual neighbor >= 0.70 | **Downscaled Laptop Render/Shot:** High-contrast clean framing with peripheral text. Very low file size (5.3 KB) suppresses sensor noise. |
| `MED-1856372030-0` | Iphone 15 128gb blue colour with box & bill | iPhone | 150x205 (1.9 KB) | 0.9437 | 0.7917 | `PHOTO` | `success_no_text` (0.0% conf) | 5 high visual similarity edges in Phase D (sim up to **0.8866**) | **Sub-2KB Downscaled Stock/Box Shot:** Extremely compressed 1.9 KB thumbnail. DINOv2 links it strongly to standard retail packaging images. |

### Critical Forensic Synthesis:
1. **Digital Graphic Flyers vs. AI Deepfakes:** Two of the six assets (`MED-1835966549-0` and `MED-1849662426-0`) are commercial repair/buyer flyers composed in digital layout software (Canva/Photoshop). Because they are digitally generated graphics with flat vector fills and clean typography, neural classifiers trained to distinguish photographic grain from artificial generation flag them as "synthetic/artificial".
2. **Impact of Extreme Downsampling:** The remaining four assets are downscaled to 150-pixel width with file sizes between 1.9 KB and 5.3 KB. Severe WebP compression strips out physical camera sensor noise and creates block boundary patterns that can influence transformer patch embeddings.
3. **Scientific Terminology:** These 6 assets are classified strictly as **multi-detector AI-generation candidates** under the operational threshold ($\ge 0.70$). They are **not** proven AI-generated images, and they are **not** labeled as fraud.

---

## 4. Multimodal Puter Escalation Gateway Status

| Parameter | Metric Value | Notes |
| :--- | :--- | :--- |
| **Escalation Trigger Criteria** | `DETECTOR_DISAGREEMENT` or `BORDERLINE` | Transparent multi-source criteria |
| **Total Candidates Queued** | **1,316 assets** (57.72%) | Formatted with standardized prompt |
| **Disagreement Sub-Queue** | 559 assets | ViT vs. Swin conflict |
| **Borderline Sub-Queue** | 757 assets | Indeterminate score in (0.30, 0.70) |
| **Consensus Assets (Not Queued)** | 964 assets (42.28%) | Mutual real agreement or conclusive consensus |
| **Puter Live Execution Status** | **UNEXECUTED QUEUE (Offline Local Run)** | No cloud inference dispatched |
| **Sent to Puter** | **0** | No live API credentials configured |
| **Successful Responses** | **0** | — |
| **Failed Requests** | **0** | — |

**Standardized Neutral Prompt Configured in Escalation Payloads:**
> *"Provide an independent visual assessment and list observable evidence and uncertainty. Do not claim provenance that cannot be established from the image. Separately describe: 1. visible image content, 2. whether there are visual characteristics commonly associated with synthetic imagery, 3. whether the image contains obvious generative artifacts, 4. whether the image appears to be a screenshot/document/render/product photo, 5. whether provenance can be inferred from the visible image, 6. uncertainty"*

---

## 5. Recompression & Resizing Robustness Evaluation

On a controlled 10-image stratified benchmark evaluated across original WebP, JPEG recompression (Quality 70), and bilinear resizing (0.75x scale):
- **`DETECTOR_STABLE` (Delta < 0.15):** 6 / 10 images (60%)
- **`DETECTOR_SENSITIVE_TO_RECOMPRESSION` (Delta >= 0.15):** 4 / 10 images (40%)

Under this specific test set, Detector B exhibited an observed mean score shift of $ar{\Delta} = 0.142$ under JPEG recompression, while Detector A demonstrated $ar{\Delta} = 0.048$. This empirical sensitivity underlines the importance of documenting recompression behavior rather than assuming model invariance across different image formats.

---

## 6. Controlled Validation & Benchmark Limitations

1. **Local Ground Truth Absence:** Search of the local repository confirmed that no verified ground-truth AI vs. Real benchmark exists locally (`controlled_validation_available = false`).
2. **Domain Shift:** Models trained on synthetic benchmarks (e.g. Midjourney, Stable Diffusion, DALL-E) experience domain shift when applied to compressed, re-encoded OLX user uploads.
3. **No Uncalibrated Averaging:** Detector scores were never averaged (`(score_a + score_b) / 2` was strictly rejected). Raw scores are preserved verbatim.

---

## 7. Generated Publication Figures

- `fig_ai_detector_a_distribution.png`: Histogram of ViT-Base raw scores.
- `fig_ai_detector_b_distribution.png`: Histogram of Swin-Base raw scores.
- `fig_detector_agreement_matrix.png`: Agreement tier distribution.
- `fig_agreement_by_image_type.png`: Agreement proportions stacked by image type.
- `fig_ai_candidate_rate_by_product.png`: Breakdown across iPhone, MacBook, iPad, etc.
- `fig_detector_disagreements.png`: Bivariate scatter plot showing Puter escalation queue boundary.
- `fig_score_stability_recompression.png`: Observed score shift under recompression.
