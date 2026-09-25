# TrustLens — Phase D Execution Report
## Pretrained Deep Visual Embeddings & FAISS Dense Nearest-Neighbor Search

- **Execution Date:** 2026-09-24T05:06:37.753955
- **Status:** COMPLETED & VERIFIED

---

### 1. Model & Index Execution Summary
- **Model Checkpoint:** `facebook/dinov2-small`
- **Images Embedded:** 2,280 (384 dimensions)
- **Top-10 Neighbors Retrieved:** 22,800
- **Inference Throughput:** 53.01 images/sec (cpu)

### 2. Candidate Generation & Relationship Summary
- **Unique Cross-Listing Visual Candidate Pairs (s ≥ 0.70):** 9,492
- **Cross-City Visual Candidates:** 3,607
- **Disagreement Candidates for Human Review:** 0

### 3. Threshold Sensitivity Bins (Directed Edges vs Unique Undirected Pairs)
- **s ≥ 0.70:** 12,403 directed edges | 9,492 unique pairs
- **s ≥ 0.75:** 9,224 directed edges | 6,758 unique pairs
- **s ≥ 0.80:** 5,456 directed edges | 3,674 unique pairs
- **s ≥ 0.85:** 1,941 directed edges | 1,122 unique pairs (Standard Candidate Threshold)
- **s ≥ 0.90:** 390 directed edges | 195 unique pairs
- **s ≥ 0.95:** 238 directed edges | 119 unique pairs

### 4. Phase E Readiness
All deep visual artifacts and nearest-neighbor indices are fully prepared for Phase E (Multimodal Text, Title & OCR Intelligence).
