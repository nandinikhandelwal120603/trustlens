# TrustLens: Building an Evidence-First Multimodal Marketplace Fraud Intelligence System

**Author:** Nandini Khandelwal  
**Domain:** Applied Machine Learning • Trust & Safety Intelligence • Multimodal Systems  
**Status:** Research Pipeline Complete (Phases A–K Frozen)  
**Artifact Repository:** `trustlens/`  

---

## 01 — The Problem

Online peer-to-peer marketplaces operate under severe information asymmetry. Every day, millions of consumer electronics transactions are negotiated on platforms like OLX, Craigslist, and Facebook Marketplace based on nothing more than a title, a thumbnail photo, a declared price, and an anonymous seller profile. 

When fraudulent listings, deceptive product representations, or syndicated duplicate networks appear, they exploit this opacity. However, detecting deceptive marketplace listings is notoriously difficult:
* **No immediate ground-truth labels:** At the moment of listing creation, neither the platform nor the buyer knows with mathematical certainty whether a seller has physical custody of the item or plans to fulfill the transaction.
* **Adversarial adaptation:** Deceptive actors quickly learn to bypass naive lexical filters (e.g. replacing phone numbers with words or phonetic spellings).
* **Multi-modal contradictions:** A listing title may claim one product model (e.g. "iPhone 13"), while the uploaded photo displays a completely different device packaging box (e.g. "iPhone 13 Mini").
* **Cross-market syndication:** The same photo may be duplicated across dozens of listings in different cities to capture upfront deposits from unsuspecting buyers.

Most existing solutions attempt to slap a supervised "scam probability" classifier on top of this messy reality. TrustLens was built to demonstrate a fundamentally different, more rigorous paradigm.

---

## 02 — Why Existing Approaches Are Insufficient

Through extensive research across academic literature and commercial implementations, I identified four fatal flaws in traditional marketplace anti-fraud systems:

1. **The "Scam Score" Fallacy:** Producing an uncalibrated score like "92% Scam Probability" creates an illusion of precision. Without verified transaction outcomes, such numbers are mathematically ungrounded and destroy investigator trust.
2. **Single-Signal Brittleness:**
   * Price heuristics flag damaged items, accessories, and urgent sales as scams.
   * Keyword filters flag legitimate buyers who mention off-platform communication.
   * Single AI image detectors fail: our empirical evaluation showed that two leading vision transformers disagreed on **24.5% of marketplace images**.
3. **Siloed Analysis:** Fraud detection systems evaluate listings in complete isolation, failing to notice when the exact same image binary is posted across 14 different cities simultaneously.
4. **Black-Box Opacity:** When a machine learning model flags a listing without showing *why* (e.g., showing the packaging box contradiction or the shared image hash), human trust and safety teams cannot take confident operational action.

---

## 03 — My Approach: Evidence-First Intelligence

Instead of asking *"Is this listing a scam?"*, TrustLens asks:

> **"What observable evidence exists in this listing, what independent relationships connect it to other listings, and what cannot be established from this data?"**

I structured TrustLens around four engineering principles:
1. **Multimodal Triangulation:** Extract independent forensic signals across Price, Text, Image Fingerprints, Deep Vision Embeddings, OCR, and Network Graphs.
2. **Strict Epistemological Hierarchy:** Categorize every finding as **Observed** (byte-verified), **Derived** (deterministically calculated), **Candidate** (model hypothesis), **Unverified** (unsubstantiated claims), or **Unknown** (unobserved metadata).
3. **Cross-Corroboration Over Weighting:** Rather than inventing arbitrary scoring weights, prioritize listings by **integer counts of independent forensic layers** (e.g. 4 layers: Exact Image + Text Similarity + Shared OCR Phrase + DINO Embedding).
4. **Human-in-the-Loop Review:** Output structured evidence boards that empower human investigators to verify claims in seconds.

---

## 04 — System Architecture

TrustLens is architected as an end-to-end, multi-stage pipeline:

```
[Raw Search Captures] ──> [Product Normalizer & Price Median Engine]
         │
         ├──> [Media Pipeline: SHA-256 / pHash / DINOv2 / Dual-AI]
         │
         ├──> [Text Engine: N-Grams / TF-IDF / Contact Regexes]
         │
         ├──> [Multimodal OCR: Tesseract 5.5 Packaging Verification]
         │
         └──> [Heterogeneous Network Graph: 5,709 Nodes / 21,395 Edges]
                     │
                     ▼
       [Unified Feature Store: 2,980 × 137 Features]
                     │
                     ▼
       [Isolation Forest Novelty Modeling across 4 Spaces]
                     │
                     ▼
       [Multi-Signal Evidence Synthesis & Review Queue]
```

---

## 05 — Data Pipeline & Ingestion Rigor

I built a client-side capture pipeline that extracted real-world search cards from OLX India across three core hardware queries: `iphone`, `macbook`, and `ps5 controller`.

To guarantee absolute integrity, I instituted a formal **Dataset Ledger** enforcing strict entity boundaries:
* **2,980 Canonical Listings:** 100% deduplicated across 5 raw capture batches. Exactly one row per listing.
* **2,491 Media References:** 83.59% of listings contained search-card image thumbnails; 489 were text-only.
* **2,323 Unique Apollo CDN Assets:** Deduplicated by infrastructure asset IDs.
* **2,282 Downloaded Image Files:** Deterministically acquired locally (98.24% success rate).
* **2,280 Evaluated Media Cohort:** Validated binaries passed to downstream models (2 corrupt/truncated downloads excluded).

---

## 06 — Multimodal Forensic Intelligence

The core of TrustLens is the extraction of independent, orthogonal forensic signals:

### 1. Price Normalization & Comparable Benchmarks
I engineered a deterministic taxonomy parser that normalizes raw titles into structured attributes (Brand, Model, Generation, Storage, RAM, Battery Health). The pipeline computes model-specific price medians (e.g. 350 iPhone 13 listings; median ₹38,500) and measures percentage deviations, filtering out query-contaminating accessories (e.g. ₹200 phone cases).

### 2. Dual-Track Visual Forensics
* **Cryptographic Binary Identity:** SHA-256 hashing identified **164 pairwise exact image reuse instances** across 242 listings. Crucially, **78.0% of these pairs spanned different metropolitan cities**.
* **Perceptual Hashing:** pHash and dHash ($d \le 10$) identified 78 candidate pairs where images underwent recompression or minor dimensional cropping.
* **Dense Visual Representation:** 384-dimensional DINOv2 (`dinov2_vits14`) embeddings identified 9,492 visual similarity relationships ($\ge 0.70$), successfully capturing identical devices photographed from varying angles where hash-based methods fail.

### 3. Cross-Modal Packaging OCR Verification
Using Tesseract 5.5, the pipeline extracted visible text strings across 2,280 images (82.7% text-positive rate). An automated consistency engine compared declared title claims against extracted packaging text, discovering:
* **1 Explicit Model Mismatch:** Listing `1856180547` declared an "iPhone 13 128", while OCR detected "iPhone 13 Mini" on the box.
* **1 Demo Unit Lock Screen:** Listing `1848124756` displayed a device showing an uppercase "ACTIVATION LOCK" screen.
* **66 Shared-Image Claim Drifts:** Pairs of listings sharing identical images while asserting conflicting storage capacities.

### 4. Dual-Detector AI Image Evaluation
To test for generative AI imagery, I deployed two distinct vision architectures: ViT-Base (Detector A) and Swin-Base (Detector B). Rather than trusting a single model, I required mutual consensus ($\ge 0.70$). The evaluation yielded:
* 958 Mutual Real Agreements
* 6 Mutual AI Candidates (manual audit revealed commercial 3D graphic renders and promotional flyers)
* **559 Detector Disagreements (24.5%):** Proving conclusively that single-detector AI classification on compressed e-commerce images produces unacceptable false positive rates.

---

## 07 — Relationship & Network Analysis

In Phase H, I projected the individual forensic signals into a heterogeneous entity graph containing **5,709 nodes and 21,395 edges**:
* **Topology:** 2,133 connected components, including 266 multi-listing clusters.
* **Macro-Components:** The largest cluster linked 122 listings across 14 cities via shared templates, images, and text.
* **Analytical Interpretation:** These clusters represent commercial merchant syndication, multi-branch refurbishers, or marketing automation scripts—providing platforms with an automated view of commercial footprint.

---

## 08 — Statistical Novelty Modeling

In Phase J, I consolidated all signals into a **Unified Feature Store (2,980 rows $\times$ 137 validated columns)** and trained unsupervised Isolation Forest models across four primary feature spaces:
1. `J_PRICE` (7 features)
2. `J_PRICE_TEXT` (28 features)
3. `J_PRICE_IMAGE` (37 features)
4. `J_FULL_MULTIMODAL` (85 features)

Evaluating outlier persistence across spaces revealed:
* 2,574 listings (86.38%) were inliers across all spaces.
* 270 listings were outliers in only 1 feature space.
* **Only 3 listings (0.10%) were persistently anomalous across all 4 feature spaces** (including an unreleased "iPhone 17 Pro" placeholder at ₹350 and a ₹110,000 console bundle).

---

## 09 — Evidence Synthesis & The Review Queue

In Phase K, I synthesized the relationship network and cross-modal signals into an authoritative **Multi-Signal Evidence Table**:
* **213 Multi-Signal Listing Pairs:** Listing pairs connected through $\ge 2$ independent forensic layers:
  * 4 Layers: 5 pairs
  * 3 Layers: 63 pairs
  * 2 Layers: 145 pairs
* **Dominant Pattern:** Exact Image Reuse + Exact Title Reuse + DINO Visual Similarity accounted for 48 pairs.
* **Review Queue:** The pairs were compiled into a prioritized `research_review_queue.parquet` ranked strictly by `evidence_count descending, missingness ascending` for human trust and safety investigation.

---

## 10 — Summary of Empirical Results

| Metric Dimension | Measured Value | Definitive Research Meaning |
| :--- | :---: | :--- |
| **Canonical Dataset** | 2,980 listings | Fully deduplicated, verified cohort |
| **Evaluated Images** | 2,280 assets | Complete pHash, DINO, OCR & AI evaluation |
| **Exact Image Duplicates** | 164 pairs | Cryptographic byte equality (78% cross-city) |
| **Visual Similarity Pairs** | 9,492 pairs | DINOv2 cosine similarity $\ge 0.70$ |
| **OCR Discrepancies** | 68 candidates | 66 claim drift, 1 model mismatch, 1 demo lock |
| **AI Detector Consensus** | 6 mutual candidates | Dual ViT & Swin agreement (559 disagreements) |
| **Multi-Signal Pairs** | 213 pairs | $\ge 2$ independent forensic evidence layers |
| **Persistent Outliers** | 3 listings | Persistent across all 4 Isolation Forest spaces |
| **Automated Tests** | 124 passed | 100% passing test suite across entire pipeline |

---

## 11 — Engineering Challenges Overcome

1. **Memory & Compute Constraints on Apple Silicon:** Executing deep vision transformers (DINOv2, ViT-Base, Swin-Base) on a 16 GB unified memory machine required strict sequential model loading, immediate memory reclamation, and batch optimization.
2. **Deterministic Preprocessing:** Handling missingness without introducing data leakage. I enforced a strict distinction between observed absence (`0`) and uncaptured data (`NULL`), ensuring zero target leakage.
3. **Graph Scaling:** Calculating pairwise relationships across 2,980 listings and 2,280 images produces millions of potential combinations. I implemented threshold indexing and nearest-neighbor pruning to evaluate over 21,000 edges in seconds.

---

## 12 — What I Refused To Automate (The Core Engineering Decision)

Perhaps the most important architectural decision in TrustLens is what I **refused** to build:

* **I refused to output a "Scam Score":** Generating a fake probability like "87% Fraud" without verified transaction outcome data is scientifically irresponsible.
* **I refused to infer seller identity:** Public search cards omit persistent account IDs. Pretending that two listings with the same photo belong to the same person without legal entity verification is an ungrounded assumption.
* **I refused to automate account banning:** TrustLens is designed as an **investigator copilot**, not an autonomous executioner. It organizes evidence so human experts can make fair, defensible decisions.

---

## 13 — Methodological Limitations

True engineering credibility requires acknowledging constraints:
1. **Search-Card Metadata Boundaries:** Full item descriptions and seller account ages were unobserved in search-card captures.
2. **Targeted Sample Scope:** Findings reflect electronics queries (`iphone`, `macbook`, `ps5 controller`) and cannot be extrapolated to all marketplace categories.
3. **No External Fraud Ground Truth:** Findings represent **statistical novelty, cross-listing duplication, and multimodal inconsistencies**, not proven criminal guilt.

---

## 14 — What I Would Build Next in Production

If deploying this architecture inside a commercial marketplace like OLX:
1. **Authenticated Seller Ingestion:** Ingest internal account IDs, device fingerprints, and KYC status to resolve network clusters into verified commercial merchant entities.
2. **Streaming Kafka / Flink Pipeline:** Move from batch Parquet evaluation to real-time listing ingestion, computing hashes and OCR checks at the moment of publish.
3. **Investigator Feedback Loop:** Implement active learning where trust & safety reviewer confirmations feed back into calibrated supervised models.
4. **Hardware Serial Verification:** Deploy private OCR models to cross-reference partially masked IMEI and serial numbers against global stolen-device databases.
