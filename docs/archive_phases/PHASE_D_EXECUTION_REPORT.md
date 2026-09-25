# TrustLens — Phase D Execution Report
## Pretrained Deep Visual Embeddings & Dense Nearest-Neighbor Search

- **Execution Date:** 2026-09-24T05:06:37.753955
- **Status:** COMPLETED & VERIFIED

---

### 1. Model & Index Execution Summary
- **Model Checkpoint:** `facebook/dinov2-small`
- **Search Engine:** Exact cosine similarity via L2-normalized NumPy matrix multiplication (No FAISS dependency)
- **Images Embedded:** 2,280 (384 dimensions)
- **Top-10 Neighbors Retrieved:** 22,800
- **Inference Throughput:** 53.01 images/sec (cpu)

### 2. Candidate Generation & Relationship Summary
- **Unique Cross-Listing Visual Candidate Pairs (s ≥ 0.70):** 9,492
- **Cross-City Visual Candidates:** 3,607
- **Disagreement Candidates for Human Review:** 0

### 3. Threshold Sensitivity Bins (Directed Edges vs Unique Undirected Pairs)
- **s ≥ 0.70:** 12,403 directed edges (5,822 reciprocal, 6,581 non-reciprocal) | 9,492 unique pairs (46.94% reciprocal)
- **s ≥ 0.75:** 9,224 directed edges (4,932 reciprocal, 4,292 non-reciprocal) | 6,758 unique pairs (53.47% reciprocal)
- **s ≥ 0.80:** 5,456 directed edges (3,564 reciprocal, 1,892 non-reciprocal) | 3,674 unique pairs (65.32% reciprocal)
- **s ≥ 0.85:** 1,941 directed edges (1,638 reciprocal, 303 non-reciprocal) | 1,122 unique pairs (84.39% reciprocal; Standard Candidate Threshold)
- **s ≥ 0.90:** 390 directed edges (390 reciprocal, 0 non-reciprocal) | 195 unique pairs (100.00% reciprocal)
- **s ≥ 0.95:** 238 directed edges (238 reciprocal, 0 non-reciprocal) | 119 unique pairs (100.00% reciprocal)

### 4. Phase E Readiness
All deep visual artifacts and nearest-neighbor indices are fully prepared for Phase E (Multimodal Text, Title & OCR Intelligence).
