# TrustLens — System Architecture & Technical Specifications

**System:** TrustLens Evidence-Based Fraud Intelligence Platform  
**Architecture Version:** 1.0.0 (Post-Phase K Synthesis)  
**Target Environments:** Python 3.11+, PyArrow / Parquet, PyTorch, Tesseract 5.5, Scikit-Learn  

---

## 1. Architectural Overview

TrustLens is architected as an **evidence-first, multi-stage analytical pipeline** designed to ingest unconstrained online marketplace search captures, extract forensic features across multiple modalities, build an interconnected relationship graph, and detect statistical novelty without relying on uncalibrated "scam probability" scores.

```
                    TRUSTLENS
                       │
             Marketplace Observation
                       │
              ┌────────┴────────┐
              │                 │
           Listing             Media
              │                 │
       ┌──────┼──────┐     ┌────┼─────┐
       │      │      │     │    │     │
     Price   Text   Geo   SHA  pHash DINO
       │      │            │    │     │
       │     OCR           └────┼─────┘
       │      │                 │
       └──────┼─────────────────┘
              │
       Multimodal Evidence
              │
       Relationship Network
              │
       Unified Feature Store
              │
     Statistical Novelty
              │
       Evidence Synthesis
              │
       Human Review Queue
              │
       Explainable Report
```

---

## 2. Ingestion & Preprocessing Subsystem (Phases A & B)

### Ingestion Protocol
* **Input Vault:** Multi-batch JSON captures from browser-based search card captures (`iphone`, `macbook`, `ps5 controller`).
* **Entity Disambiguation:** Strict boundary enforcement:
  * `2,980` Canonical Listings (1 row = 1 unique listing ID).
  * `2,491` Media References (83.59% of listings contain thumbnail URLs).
  * `2,323` Unique Apollo CDN Assets.
  * `2,280` Validated Local Image Files (2 corrupt downloads excluded).

### Product Taxonomy Normalizer
* **Deterministic Regex Parsing:** Normalizes hardware models into standardized taxonomy entities (Brand, Family, Model, Variant, Generation, Storage, RAM, Battery Health).
* **Accessory Isolation:** Filters query contamination (e.g. ₹200 phone cases appearing under iPhone search cards) into an accessory category to prevent baseline price distortion.
* **Comparable Median Modeling:** Calculates model-specific price medians and deviation metrics ($\Delta$ from median, price ratio, flags for $\le -35\%$ and $\le -50\%$).

---

## 3. Media Forensics Subsystem (Phases C, D, G, G.1)

The media pipeline executes four complementary levels of visual inspection:

### Level 1: Cryptographic Binary Identity (SHA-256)
* Computes exact SHA-256 hashes of image binaries.
* Uncovers byte-for-byte identical images published across multiple listings without re-encoding.
* **Measured:** 164 pairwise exact reuse instances across 242 listings (78.0% cross-city).

### Level 2: Perceptual Hashing (pHash, dHash, aHash)
* Generates 64-bit perceptual hashes to detect image recompression, minor resizing, and thumbnail artifacts.
* Uses normalized Hamming distance threshold ($d \le 10$).
* **Measured:** 78 candidate perceptual similarity pairs.

### Level 3: Deep Vision Embeddings (DINOv2)
* Employs `dinov2_vits14` (384-dimensional dense representation) to capture semantic visual affinity invariant to camera perspective, lighting, and angles.
* Cosine similarity threshold ($\ge 0.70$) with exact nearest-neighbor search.
* **Measured:** 9,492 visual similarity candidate pairs.

### Level 4: Dual-Detector Synthetic Image Consensus (Phase G.1)
* Sequential execution of two distinct vision architectures:
  * **Detector A:** ViT-Base (50M parameters)
  * **Detector B:** Swin-Base (88M parameters)
* **Consensus Logic:** Requires mutual agreement ($\ge 0.70$) to classify as an `AI_GENERATION_CANDIDATE`.
* **Empirical Finding:** 958 mutual real, 6 mutual AI candidates, and 559 detector disagreements, demonstrating why single-detector evaluation is brittle.

---

## 4. Text & OCR Intelligence Subsystem (Phases E & F)

### Lexical Feature Extraction
* Computes unigram, bigram, and trigram term frequencies across normalized listing titles.
* TF-IDF keyword distinctiveness isolating commercial phrases (e.g. "sealed pack", "under warranty", "urgent sale").
* Deterministic regex extractors for contact-redirection cues (WhatsApp digits, off-platform communication triggers).

### Cross-Modal OCR Claim Verification (Phase E)
* Tesseract 5.5 OCR extraction over all 2,280 media assets (82.7% yielded legible text strings).
* **Cross-Modal Consistency Engine:** Compares OCR strings extracted from packaging boxes and screens against declared title attributes.
* **Inconsistency Candidates:** 68 total (66 shared-image claim drift, 1 packaging model mismatch, 1 demo lock screen).

---

## 5. Relationship Network Engine (Phase H)

* **Graph Representation:** Heterogeneous multi-modal network comprising **5,709 entity nodes** and **21,395 relationship edges**.
* **Node Types:** Listings (`listing`), Media Assets (`image`), Cities (`city`), States (`state`), Product Families (`product`), Distinctive OCR Phrases (`ocr_phrase`).
* **Edge Semantics:**
  * Containment edges: Listing $\rightarrow$ Media, Listing $\rightarrow$ Location.
  * Observational edges: SHA-256 Exact Reuse, Exact Title Reuse, Shared OCR Phrase.
  * Candidate edges: DINOv2 Visual Similarity ($\ge 0.70$), Lexical Similarity (Jaccard $\ge 0.75$).
* **Topology:** 2,133 connected components (266 non-singleton). Largest component spans 122 listings across 14 cities.
* **Multi-Signal Identification:** Isolates the **213 listing pairs** connected through $\ge 2$ independent forensic layers.

---

## 6. Unified Feature Store (Phase I)

* **Schema Invariant:** Exactly **1 row = 1 canonical listing** (2,980 rows $\times$ 137 columns).
* **Column Breakdown:** 63 numeric, 40 categorical, 34 binary.
* **Pre-processing Semantics:** Strict distinction between observed absence (`0`) and unavailable/uncaptured metadata (`NULL`). Zero data leakage, zero future variables.

---

## 7. Multivariate Statistical Novelty Modeling (Phase J)

* **Algorithm:** Unsupervised Isolation Forest (`n_estimators=150`, `random_state=42`, `max_samples='auto'`).
* **Feature Spaces Evaluated:**
  1. `J_PRICE` (7 features): Price-only baseline.
  2. `J_PRICE_TEXT` (28 features): Price + deterministic linguistic structure.
  3. `J_PRICE_IMAGE` (37 features): Price + media coverage, reuse, OCR, and AI candidate indicators.
  4. `J_FULL_MULTIMODAL` (85 features): Complete cross-modal representation.
* **Score Normalization:** Stored as `anomaly_score = -decision_function(X)` (higher score = greater multivariate distance from normal density).
* **Persistence Analysis:**
  * 0 spaces (Inliers): 2,574 listings (86.38%).
  * 1 space: 270 listings (9.06%).
  * 2 spaces: 88 listings (2.95%).
  * 3 spaces: 45 listings (1.51%).
  * All 4 spaces: **3 listings (0.10%)**.

---

## 8. Final Evidence Synthesis & Review Queue (Phase K)

* **Multi-Signal Evidence Table:** Consolidates all 213 multi-signal pairs annotated with cross-modal signals.
* **Prioritized Research Review Queue:** Deterministically sorted by `evidence_count descending, missingness ascending` for human trust and safety review.
* **Zero Accusation Guardrail:** Refuses to output fraud probabilities or seller reputation scores without external ground-truth transaction logs.
