# TrustLens — Pretrained Deep Visual Embeddings Report (Phase D)
## DINOv2-ViT-S/14 & Dense Nearest-Neighbor Representation

- **Generated At:** 2026-09-24T05:06:37.753518
- **Model Checkpoint:** `facebook/dinov2-small` (384-dim, ViT-S/14)
- **Device & Throughput:** `cpu` (53.01 images/sec)
- **Status:** COMPLETED & VERIFIED (Phase D)

---

## 1. Asset Acquisition, Embedding & Indexing Hierarchy

| Processing Stage | Entity Count | Coverage / Population | Methodological Context |
| :--- | :---: | :---: | :--- |
| **Media References** | **2,491** | 100.0% | Total image references across 2,980 listings. |
| **Unique Apollo Assets** | **2,323** | 100.0% | Unique Apollo image IDs in capture corpus. |
| **Download-Successful Assets** | **2,282** | 98.24% | Local WebP files downloaded to `data/olx_media/`. |
| **Fingerprint-Successful Assets** | **2,280** | 98.15% | Assets with valid decoded pixels (SHA, pHash, dHash, aHash). |
| **Embedded Image Assets** | **2,280** | 100.0% | Dense 384-dim L2-normalized vectors extracted from `[CLS]` token. |
| **Retrieved Nearest-Neighbor Edges** | **22,800** | Top-10 / Asset | Directed query $\rightarrow$ neighbor edges (self-matches excluded). |
| **Unique Cross-Listing Candidate Pairs ($s \ge 0.70$)** | **9,492** | Candidate Filter | Deduplicated undirected candidate pairs across distinct listings. |

---

## 2. Multi-Method Validation Against Phase C

| Ground Truth Category | Sample Count | Mean Cosine Similarity | Validation Finding & Scientific Meaning |
| :--- | :---: | :---: | :--- |
| **Exact Binary Sanity Check (SHA-256 Identical, $d = 0$)** | **82 pairs** | **1.0000** | **Sanity Check:** Exact identical image files evaluate to $s = 1.0000$ (verifies deterministic numerical precision). |
| **Perceptual Concordance (pHash Candidates, $d \le 10$)** | **160 pairs** | **0.9003** | **Cross-Method Validation:** Strong alignment ($s = 0.9003$), proving high mutual recall across low-frequency and deep feature spaces. |

---

## 3. Threshold Sensitivity Bins (Candidate Filters)

> **Population Definition:**
> - **Directed Top-10 Edges:** Total directed nearest-neighbor query edges where query and neighbor belong to different listings (N_total = 22,800).
> - **Unique Undirected Pairs:** Deduplicated candidate pairs {A, B} across distinct listings (N_total = 9,492).

| Cosine Threshold | Directed Top-10 Edges | Unique Undirected Pairs | Sensitivity Tier | Visual Similarity Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **$s \ge 0.70$** | **12,403** | **9,492** | Broad Recall | General category, color palette, or standard framing similarity. |
| **$s \ge 0.75$** | **9,224** | **6,758** | Moderate Recall | Clear subject alignment across varying backgrounds. |
| **$s \ge 0.80$** | **5,456** | **3,674** | High Recall | Shared visual subject with slight angle/crop variation. |
| **$s \ge 0.85$ (Standard Candidate Filter)** | **1,941** | **1,122** | **Candidate Filter** | **Strong visual candidate for human review** (Status: `UNVERIFIED`). |
| **$s \ge 0.90$** | **390** | **195** | Precision Filter | Near-identical visual composition. |
| **$s \ge 0.95$** | **238** | **119** | Maximum Precision | Extremely high visual identity. |

---

## 4. Cross-City Visual Relationships

- **Total Cross-City Candidate Links ($s \ge 0.70$):** **3,607**
- **Inspectable Visual Gallery:** [`data/olx_analysis/reports/visual_gallery.html`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/data/olx_analysis/reports/visual_gallery.html)

---

## 5. Method Disagreement Analysis (pHash vs DINOv2)

- **Total Disagreement Review Candidates:** **0**
  - **High DINO / Low pHash:** Captures re-framed, cropped, or lighting-varied shots of identical product subjects missed by low-frequency perceptual hashing.
  - **High pHash / Low DINO:** Flags perceptual hash false positives caused by uniform studio backgrounds or solid color blocks.

---

## 6. Analytical Parquet Artifacts

1. **`data/olx_processed/image_embeddings.parquet`**: Master embedding table with metadata and 384-dim vectors.
2. **`data/olx_processed/image_embeddings.npy`**: Dense NumPy embedding matrix (2,280 × 384).
3. **`data/olx_processed/visual_neighbors.parquet`**: All top-10 nearest neighbor ranks with cosine scores.
4. **`data/olx_processed/deep_visual_relationships.parquet`**: Deduplicated cross-listing visual candidate pairs ($s \ge 0.70$).
