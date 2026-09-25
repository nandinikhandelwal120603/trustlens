# TRUSTLENS: THE SUPER MASTER DOCUMENT
## End-to-End Chronicle, Methodology, Empirical Data & Technical Architecture of the Marketplace Fraud Intelligence Research Pipeline

**Author:** Nandini Khandelwal  
**System:** TrustLens Multimodal Marketplace Fraud Intelligence  
**Scope:** Chronological Research Record from Inception (Phase 1/2 Reddit Discovery) through Live OLX Captures to Final Synthesis (Phases A–K)  
**Status:** COMPLETE, AUDITED & FROZEN  
**Verification:** 124 Unit & Integration Tests Passing (0 Regressions)  

---

# TABLE OF CONTENTS
1. [Executive Summary & Core Scientific Philosophy](#1-executive-summary--core-scientific-philosophy)
2. [The Origin: Personal Motivation & Problem Statement](#2-the-origin-personal-motivation--problem-statement)
3. [The Reddit Research Foundation (Phases 1 & 2)](#3-the-reddit-research-foundation-phases-1--2)
4. [Targeted Marketplace Data Acquisition & Ingestion Audit (Phase 3 / Phase A)](#4-targeted-marketplace-data-acquisition--ingestion-audit-phase-3--phase-a)
5. [Product Taxonomy Normalization & Price Baseline Modeling (Phase B)](#5-product-taxonomy-normalization--price-baseline-modeling-phase-b)
6. [Cryptographic & Perceptual Image Fingerprinting (Phase C)](#6-cryptographic--perceptual-image-fingerprinting-phase-c)
7. [Deep Visual Embeddings & Semantic Similarity (Phase D)](#7-deep-visual-embeddings--semantic-similarity-phase-d)
8. [Multimodal Packaging OCR & Cross-Modal Consistency Engine (Phase E)](#8-multimodal-packaging-ocr--cross-modal-consistency-engine-phase-e)
9. [Text Intelligence & Lexical Linguistics (Phase F)](#9-text-intelligence--lexical-linguistics-phase-f)
10. [Image Authenticity, EXIF/C2PA & Dual AI Detector Consensus (Phase G & G.1)](#10-image-authenticity-exifc2pa--dual-ai-detector-consensus-phase-g--g1)
11. [Relationship Network Intelligence & Graph Topology (Phase H)](#11-relationship-network-intelligence--graph-topology-phase-h)
12. [Unified Listing-Level Feature Store Consolidation (Phase I)](#12-unified-listing-level-feature-store-consolidation-phase-i)
13. [Multivariate Statistical Novelty & Isolation Forest Modeling (Phase J)](#13-multivariate-statistical-novelty--isolation-forest-modeling-phase-j)
14. [Final Evidence Synthesis, Dataset Ledger & Review Queue (Phase K)](#14-final-evidence-synthesis-dataset-ledger--review-queue-phase-k)
15. [Representative Research Case Studies (The 12 In-Depth Investigations)](#15-representative-research-case-studies-the-12-in-depth-investigations)
16. [Comprehensive Visual Assets & Figures Catalogue (Figures 01 to 73)](#16-comprehensive-visual-assets--figures-catalogue-figures-01-to-73)
17. [Public Showcase, Career Artifacts & Industry Outreach](#17-public-showcase-career-artifacts--industry-outreach)
18. [Methodological Limitations & Production Roadmap](#18-methodological-limitations--production-roadmap)

---

# 1. Executive Summary & Core Scientific Philosophy

TrustLens is an empirical research system engineered to analyze deceptive listing patterns, multimodal contradictions, cross-market media reuse, and multivariate statistical novelty within online classified advertising.

### The Paradigm Shift: Evidence-First Intelligence
Traditional automated anti-fraud implementations typically rely on one of two flawed mechanisms:
1. **Naive Single-Signal Heuristics:** Hardcoded rules (e.g. price drops or keyword blacklists) that disproportionately flag legitimate sellers offering damaged goods, parts, accessories, or urgent clearance items.
2. **Uncalibrated "Scam Probability" Classifiers:** Supervised machine learning models trained on synthetic or proxy targets that output opaque scores like *"94% Scam Probability"*. In real-world peer-to-peer marketplaces, post-transaction fraud ground truth does not exist at listing creation time. Outputting unverified probabilities creates an illusion of certainty, generates high false-positive rates, and destroys investigator trust.

TrustLens replaces this with **Multimodal Evidence Triangulation**:
* Instead of asking: *"Is this listing a scam?"*
* TrustLens asks: **"What observable evidence exists in this listing, what independent relationships connect it to other listings, and what cannot be established from this data?"**

### The Five-Tier Evidence Hierarchy
To preserve scientific rigor, every finding in TrustLens is classified into one of five mutually exclusive epistemic tiers:
* **OBSERVED:** Directly visible, byte-verifiable empirical data (e.g., identical SHA-256 binary image hashes, exact title string equality).
* **DERIVED:** Deterministically calculated from observed data (e.g., price percentage deviation from comparable-model median).
* **CANDIDATE:** An algorithmic model or similarity calculation identifying a hypothesis requiring review (e.g., DINOv2 cosine similarity $\ge 0.70$, AI detector score $\ge 0.70$).
* **UNVERIFIED:** A reported claim lacking independent multi-modal corroboration (e.g., unverified user forum complaints).
* **UNKNOWN:** Data unobserved in the capture environment (e.g., persistent seller profile history, bank account details, physical device custody).

### Strict Scientific Guardrails
```text
ANOMALY != SCAM
ANOMALY != FRAUD
ANOMALY != MALICIOUS SELLER
ANOMALY != AI-GENERATED IMAGE
ANOMALY != STOLEN IMAGE
EVIDENCE COUNT != RISK SCORE
```
An anomalous listing merely indicates that its feature representation is statistically unusual relative to the observed marketplace distribution.

---

# 2. The Origin: Personal Motivation & Problem Statement

The TrustLens project was sparked by a firsthand consumer experience: losing ₹23,000 to an online classifieds advance-deposit scam while attempting to purchase a second-hand mobile device in India. 

The listing exhibited all the surface characteristics of a legitimate transaction: realistic photos, responsive communication, and pricing consistent with an urgent sale. However, once an advance deposit was transferred via UPI under the pretext of securing delivery, the communication was blocked, the listing was deleted, and the funds were unrecoverable.

Investigating how peer-to-peer marketplaces like OLX operate revealed that platforms struggle with three structural vulnerabilities:
1. **Information Asymmetry:** Buyers must evaluate listings using only a title, a thumbnail, a declared price, and an anonymous seller name.
2. **Cross-City Image Syndication:** Deceptive actors routinely download legitimate product photos from one city (e.g., Mumbai) and publish duplicate listings in distant markets (e.g., Delhi or Jaipur) to harvest advance tokens.
3. **Multimodal Disconnect:** Trust & safety filters often evaluate text, images, and prices in separate, disconnected silos, failing to detect when the text of a listing directly contradicts the physical packaging captured in the photo.

TrustLens was conceived to explore whether a multimodal, graph-based evidence pipeline could automatically cross-corroborate these signals and present human investigators with clear, explainable evidence.

---

# 3. The Reddit Research Foundation (Phases 1 & 2)

Before capturing live marketplace listings, the project grounded its taxonomy in real-world victim experiences by curating and analyzing the **TrustLens Reddit Multimodal Dataset**.

### Dataset Parameters
* **Collection Window:** September 2025 – September 2026.
* **Raw Corpus:** 178 raw Reddit posts and 330 attached media assets gathered from Indian communities (`r/IsThisAScamIndia`, `r/LegalAdviceIndia`, `r/IndianCyberHub`, `r/delhi`, `r/mumbai`, `r/pune`, `r/bangalore`, `r/ps5india`, `r/IndianGaming`).
* **Geographic Filtering:** Excluded 21 non-India posts (20 Pakistani posts, 1 Romanian post), establishing a locked cohort of **157 Indian fraud experience cases** (67 posts with 298 attached media assets; 90 text-only reports).

### Empirical Fraud Vectors Discovered

| Modus Operandi | Raw Cases | Deduplicated | Description / Mechanism |
| :--- | :---: | :---: | :--- |
| **`advance_payment` / `deposit_request`** | 68 | 54 | Seller demands booking token / transport fee before physical meeting |
| **`unrealistic_price`** | 51 | 42 | Item listed 40%–70% below prevailing second-hand market value |
| **`whatsapp_migration`** | 48 | 39 | Communication aggressively pushed off-platform onto WhatsApp |
| **`upi_payment` / `qr_payment`** | 42 | 35 | Reverse-charge QR code scam ("Scan QR to receive funds") |
| **`non_delivery` / `fake_seller`** | 38 | 31 | Seller vanishes immediately upon receiving advance payment |
| **`army_persona` / `cisf_persona`** | 24 | 18 | Seller poses as military officer posted in remote base with fake canteen ID |
| **`fake_invoice` / `canteen_receipt`** | 21 | 16 | Forged Army Canteen or corporate GST invoice sent to build trust |
| **`gate_pass_story` / `fake_courier`** | 19 | 15 | Demands payment for military gate-pass clearance or logistics insurance |

### Product Category Distribution in Victim Reports
Analysis of the 157 Indian cases revealed that victim losses were overwhelmingly concentrated in three high-value consumer electronics verticals:
1. **Smartphones (52 posts):** Dominated by Apple iPhone (iPhone 13, 14, 15 Pro Max) and Samsung S-series.
2. **Laptops (38 posts):** Dominated by Apple MacBook (M1/M2/M3 Air and Pro).
3. **Gaming Consoles (22 posts):** Dominated by Sony PlayStation 5 and DualSense wireless controllers.

### The Bridge: From Reddit to Live OLX Capture
The Reddit discovery phase established the exact hypotheses that dictated the design of the live OLX investigation pipeline:
* **Target Queries:** Directly informed the selection of `iphone`, `macbook`, and `ps5 controller` as the focus of live marketplace captures.
* **Price Delta Thresholds:** Reddit cases showed 40%–70% discounts, inspiring the -35% and -50% comparable median deviation thresholds in Phase B.
* **Text Redirection Regexes:** Reddit cases revealed 39 instances of off-platform WhatsApp migration, leading to the lexical contact extractors in Phase F.
* **Dual-Track Visual Forensics:** User complaints about stolen/reused photos inspired the SHA-256 and DINOv2 visual similarity engines in Phases C and D.
* **Cross-Modal OCR Verification:** Fake invoices and mismatched boxes reported on Reddit directly led to the Tesseract packaging OCR check in Phase E.

---

# 4. Targeted Marketplace Data Acquisition & Ingestion Audit (Phase 3 / Phase A)

### Ingestion Protocol & Tooling
Live marketplace data was captured from OLX India using a purpose-built Chrome browser extension (`capture-olx`) operating in client-side search contexts across major metropolitan markets (Delhi, Mumbai, Bengaluru, Hyderabad, Chennai, Kolkata, Pune, Ahmedabad).

### Raw Ingestion Deduplication
* Total raw JSON export archives collected: **6 files**.
* Deduplication by SHA-256 hash identified **1 exact byte-level duplicate export** (`trustlens_olx_iphone_2026-09-21T17-11-28.json` == `... copy.json`), yielding **5 unique capture batches**.
* Total observation envelopes parsed: **2,980 events**.
* Total unique canonical listing IDs: **2,980 listings** (0 duplicate IDs; 0 multi-capture repeats).

### Authoritative Entity Ledger Funnel

```text
Raw Capture Events: 2,980 (100.0%)
        ↓ [Deduplication & Extraction]
Canonical Marketplace Listings: 2,980 (100.0%)
        ↓ [Search-Card Media Extraction]
Media References: 2,491 (83.59% of listings with image cards)
        ↓ [CDN Asset Deduplication]
Unique Apollo CDN Image IDs: 2,323 (93.26% of media references)
        ↓ [Deterministic Local Downloader]
Downloaded Media Files: 2,282 (98.24% acquisition success)
        ↓ [Integrity & Dimension Validation]
Evaluated Media Assets: 2,280 (99.91% of downloaded; 2 corrupt files excluded)
```

### Search Query Composition
* `iphone`: 2,337 listings (78.42%)
* `macbook`: 393 listings (13.19%)
* `ps5 controller`: 250 listings (8.39%)

### Metadata Availability Realities
* **Listing Titles:** 100% available (2,980 / 2,980).
* **Price Amount:** 100% available (2,980 / 2,980).
* **Location (City/State):** 86.8% available (2,586 / 2,980); 394 listings had unparsed/missing location tags.
* **Listing Descriptions:** 0% available in search cards (uncaptured in search context).
* **Seller Account Identifiers:** 0% available in search cards (uncaptured in search context).
* **Methodological Invariant:** 0 = observed absence; NULL = unobserved/unavailable metadata. Capture limitations are never treated as fraud signals.

---

# 5. Product Taxonomy Normalization & Price Baseline Modeling (Phase B)

Raw marketplace titles are unconstrained, colloquial, and noisy (e.g. *"I phone 13 128 gb mint condition urgent sale"*). Phase B engineered a deterministic rule-based taxonomy normalizer.

### Attribute Normalization
The specification parser extracted structured hardware attributes using regular expressions:
* **Product Domain:** Electronics / Hardware.
* **Product Category:** Smartphone (2,314), Laptop (388), Gaming Accessory (245), Other/Noise (33).
* **Brand:** Apple (2,708), Sony (238), Microsoft (18), Other (16).
* **Model Family:** iPhone 13 (350), iPhone 15 (276), iPhone 14 (248), iPhone 15 Pro Max (189), iPhone 11 (185), MacBook Air (182), DualSense Controller (162), etc.
* **Hardware Specs:** Storage capacity (64GB, 128GB, 256GB, 512GB, 1TB), RAM, Battery Health percentage, Chip (M1, M2, M3, Core i7).

### Accessory Noise Isolation
Search queries suffer from accessory contamination (e.g., a ₹200 silicon phone case appearing in an `iphone` search). TrustLens parsed condition cues and accessory keywords, isolating 33 pure accessory listings. Removing accessory prices prevented artificial downward distortion of device median baselines.

### Comparable-Product Price Baseline Modeling
For every normalized model family with sample size $N \ge 5$, the engine calculated median price baselines and Interquartile Ranges (IQR):
* **iPhone 13 (N=350):** Median ₹36,000 | IQR: ₹11,000 | Min: ₹8,000 | Max: ₹72,000
* **iPhone 15 (N=276):** Median ₹52,000 | IQR: ₹14,000
* **iPhone 14 (N=248):** Median ₹42,000 | IQR: ₹12,000
* **iPhone 15 Pro Max (N=189):** Median ₹88,000 | IQR: ₹25,000
* **MacBook Air (N=182):** Median ₹45,000 | IQR: ₹24,000
* **DualSense Controller (N=162):** Median ₹3,500 | IQR: ₹1,500

### Price Deviation Metrics
* **Extreme Discounting:** 127 listings (4.26%) were priced below 35% of their comparable-model median.
* **Severe Outliers:** 74 listings (2.48%) were priced below 50% of their comparable-model median.
* **Guardrail:** A listing falling $>35\%$ below median is **statistically unusual, NOT proven fraud**. Legitimate factors include severe screen damage, activation locks, urgent relocation sales, or placeholder prices.

---

# 6. Cryptographic & Perceptual Image Fingerprinting (Phase C)

Phase C built the first visual forensic layer over the 2,280 validated media assets.

### Dual Fingerprinting Protocol
1. **Cryptographic Identity (SHA-256):** Computes exact 256-bit cryptographic digest of raw image bytes to identify byte-for-byte identical images uploaded across different listing envelopes without re-encoding.
2. **Perceptual Hashing (pHash, dHash, aHash):** Computes 64-bit DCT perceptual hashes and difference hashes to detect images that underwent recompression, minor resolution scaling, or aspect ratio changes. Clustered via normalized Hamming distance ($d \le 10$).

### Key Empirical Findings
* **Exact Binary Reuse (SHA-256):** Discovered **164 pairwise instances of exact image duplication** across 242 listings.
* **Cross-City Mobility:** **78.0% of identical image pairs spanned different metropolitan cities** (e.g. identical image uploaded in Thane and Mumbai, or Delhi and Jaipur).
* **Perceptual Candidates:** 78 candidate pairs exhibited near-identical perceptual structure ($d \le 10$) despite file-size and compression differences.
* **Finding:** Binary image reuse across geographically distant markets is widespread in consumer electronics classifieds, reflecting either commercial syndication, refurbisher multi-branch marketing, or photo scraping.

---

# 7. Deep Visual Embeddings & Semantic Similarity (Phase D)

While cryptographic and perceptual hashes detect identical or recompressed image binaries, they fail when sellers photograph the same physical object from a slightly different angle, with different background lighting, or with minor perspective tilt.

### Architecture: DINOv2 Foundation Vision Transformer
* **Model:** `dinov2_vits14` (Vision Transformer Small, 14×14 patch size, self-supervised without class supervision).
* **Representation:** 384-dimensional dense L2-normalized visual embedding per image.
* **Index:** Cosine similarity calculation across all $\approx 2.6 \times 10^6$ pairwise image combinations.
* **Candidate Threshold:** Cosine similarity $\ge 0.70$.

### Key Empirical Findings
* **Visual Relationship Candidates:** Identified **9,492 candidate visual relationships** exceeding the 0.70 threshold.
* **Capturing Non-Hash Affinity:** In pairs like Listing `1854413649` & `1852565327`, pHash distance was 18 (unrelated by hash standards), but DINOv2 cosine similarity was **0.884**, successfully linking two photos of an iPhone 14 Pro Max Deep Purple taken in the same studio setup under shifted camera angles.
* **Methodological Distinction:** DINO visual similarity is a **candidate relationship**, not proof of identical physical custody. Many standard retail photos of unboxed phones achieve high DINO similarity due to semantic alignment.

---

# 8. Multimodal Packaging OCR & Cross-Modal Consistency Engine (Phase E)

Deceptive sellers frequently declare an attractive product specification in their listing title while uploading a photograph of a cheaper model or a damaged/locked device. Phase E built an automated cross-modal verification engine.

### Optical Character Recognition Protocol
* **Engine:** Local, offline Tesseract 5.5.2 engine.
* **Preprocessing:** Grayscale conversion, adaptive thresholding, noise removal, and contrast enhancement.
* **Coverage & Yield:** 1,885 of 2,280 images (**82.68% yield**) contained legible text strings.
* **Confidence Distribution:** Mean confidence 38.34, median 36.50 (reflecting unconstrained, mobile-phone marketplace photography).

### The Consistency Validator
Extracted OCR tokens were normalized and matched against declared listing title metadata via deterministic regular expression matching.

### Empirical Discrepancy Findings (68 Candidates)
1. **Packaging Model Mismatch (1 Candidate):**
   * *Subject:* Listing `1856180547` (Media `MED-1856180547-0`).
   * *Listing Claim:* Title asserted *"iPhone 13 128"*.
   * *OCR Observation:* Detected the explicit string **"iPhone 13 Mini"** on the packaging box (OCR confidence: 48.84).
   * *Verification Status:* `UNVERIFIED_CANDIDATE` (requires human review; distinguishes seller error from intentional bait-and-switch).
2. **Demo Unit / Activation Lock Cue (1 Candidate):**
   * *Subject:* Listing `1848124756` (Media `MED-1848124756-0`).
   * *Listing Claim:* Commercial title *"Apple iPhone"*.
   * *OCR Observation:* Detected the uppercase string **"ACTIVATION LOCK"** on the physical device screen (OCR confidence: 76.25).
   * *Verification Status:* `UNVERIFIED_CANDIDATE` (identifies unusable or parts-only device).
3. **Shared-Image Claim Drift (66 Candidates):**
   * Listing pairs sharing identical images (via SHA-256 or DINOv2) while asserting conflicting storage tiers (e.g. 128GB vs 256GB) or model variants.

---

# 9. Text Intelligence & Lexical Linguistics (Phase F)

Phase F extracted deterministic lexical features from listing titles to capture linguistic patterns without resorting to black-box sentiment or subjective "suspicious text" scoring.

### Linguistic Feature Extraction
* **N-Gram Tokenization:** Extracted unigrams, bigrams, and trigrams across normalized titles.
* **TF-IDF Keyword Distinctiveness:** Ranked distinctive terms across product categories (e.g., "sealed", "warranty", "m1", "dualsense", "controller").
* **Deterministic Phrase Categories:**
  * *Condition Phrases:* Found in 1,566 listings (52.6% presence; "brand new", "mint condition", "like new").
  * *Warranty Cues:* Found in 423 listings (14.2%; "under warranty", "months warranty", "apple care").
  * *Urgency Cues:* Found in 212 listings (7.1%; "urgent cash", "immediate sale", "moving out").
  * *Clearance Cues:* Found in 178 listings (6.0%; "clearance sale", "stock available", "wholesale").
  * *Contact-Redirection Language:* Found in 92 listings (3.1%; "WhatsApp only", "call on 98...", embedded phone digits).

### Exact Title Duplication
* **666 listings (22.3%)** exhibited exact byte-for-byte title duplication with at least one other listing in the corpus.
* **Cross-Listing Jaccard Overlap:** 847 pairwise candidate relationships exhibited lexical Jaccard similarity $\ge 0.75$.

---

# 10. Image Authenticity, EXIF/C2PA & Dual AI Detector Consensus (Phase G & G.1)

With the rise of generative AI tools, marketplace platforms must evaluate whether uploaded images are synthetic AI renders or authentic physical photographs.

### Metadata & Provenance Audit (Phase G)
* **EXIF Metadata:** 100% stripped by OLX Apollo CDN during automated ingestion and WebP re-encoding.
* **C2PA Cryptographic Content Credentials:** 0% present. C2PA provenance manifests do not survive standard e-commerce WebP compression pipelines.

### Dual-Detector Synthetic Image Consensus (Phase G.1)
To prevent single-detector bias, Phase G.1 deployed a sequential ensemble of two distinct foundation vision architectures:
* **Detector A:** ViT-Base (Vision Transformer Base, 50M parameters).
* **Detector B:** Swin-Base (Hierarchical Shifted-Window Transformer, 88M parameters).
* **Candidate Threshold:** Minimum score of 0.70 on both detectors required for consensus.

### Empirical Findings Across 2,280 Images

| Consensus Category | Image Count | % Share | Research Interpretation |
| :--- | :---: | :---: | :--- |
| **Agreement Real** | **958** | **42.02%** | Both detectors independently scored $< 0.30$ (classified as real photo) |
| **Borderline Zone** | **757** | **33.20%** | At least one detector scored in ambiguous intermediate range (0.30–0.70) |
| **Detector Disagreement** | **559** | **24.52%** | Swin-Base flagged AI candidate while ViT-Base classified as Real |
| **Mutual AI Candidates** | **6** | **0.26%** | Both detectors independently crossed the 0.70 candidate threshold |

### Investigation of the 6 Mutual AI Candidates
Manual inspection of the 6 mutual candidates (`MED-1835966549-0`, `MED-1842975565-0`, `MED-1849662426-0`, `MED-1855112256-0`, `MED-1855210274-0`, `MED-1856372030-0`) revealed:
* None were photorealistic deceptive deepfakes.
* They consisted of commercial 3D digital product renders, marketing flyers with heavy graphic overlays, and promotional service banners.
* **Critical Finding:** The 559 detector disagreements prove that single-model AI detection on compressed e-commerce images produces unacceptable false positive rates. Dual consensus is mandatory.

---

# 11. Relationship Network Intelligence & Graph Topology (Phase H)

In Phase H, TrustLens moved beyond isolated listing evaluation by projecting all multimodal signals into a heterogeneous entity graph.

### Graph Architecture
* **Total Entity Nodes:** **5,709 nodes** (Listings, Media Assets, Cities, States, Product Families, Distinctive OCR Phrases).
* **Total Relationship Edges:** **21,395 edges**.
* **Observational Forensic Edges:** **12,791 edges** (connecting listings through shared data):
  * DINOv2 Visual Similarity ($\ge 0.70$): 9,492 edges
  * Exact Title Duplication: 2,182 edges
  * Lexical Title Similarity (Jaccard $\ge 0.75$): 847 edges
  * Exact Binary Image Reuse (SHA-256): 164 edges
  * Perceptual Image Candidates (pHash $\le 10$): 78 edges
  * Distinctive Shared OCR Phrases: 28 edges

### Connected Component Analysis
* **Total Connected Components:** **2,133 components**.
* **Non-Singleton Clusters:** **266 components** containing $\ge 2$ listings.
* **Macro-Component Cluster:** The largest component linked **122 listings across 14 cities** via shared marketing templates, images, and text collocations.
* **Mobility Corridors:** 7,446 edges spanned cross-city listing pairs; 6,988 edges spanned cross-state pairs.

### The 213 Multi-Signal Candidate Pairs
Phase H identified exactly **213 listing pairs** connected through $\ge 2$ independent forensic layers:
* **4 Forensic Layers:** **5 pairs** (Image SHA + Exact Title + OCR Banner Phrase + DINO Embedding).
* **3 Forensic Layers:** **63 pairs** (e.g. Image SHA + Exact Title + DINO Embedding).
* **2 Forensic Layers:** **145 pairs** (e.g. Exact Title + DINO Embedding).

---

# 12. Unified Listing-Level Feature Store Consolidation (Phase I)

Phase I consolidated all deterministic outputs from Phases B through H into a single canonical table: `data/olx_processed/unified_features.parquet`.

### Invariant & Integrity Standards
* **Invariant:** **1 row = 1 canonical listing**.
* **Dimensions:** Exactly **2,980 rows $\times$ 137 validated columns**.
* **Column Breakdown:** 63 numeric features, 40 categorical features, 34 binary flags.
* **Completeness:** 0 unmatched joins; 0 duplicate listing IDs.
* **Missingness Semantics:** Strict distinction between observed zero (`0`) and uncaptured data (`NULL`).
* **Zero Target Leakage:** Verified that no human review outcomes, scam labels, or future variables entered the feature store.

---

# 13. Multivariate Statistical Novelty & Isolation Forest Modeling (Phase J)

In Phase J, TrustLens conducted unsupervised statistical novelty modeling to answer:
> *"Which listings are statistically unusual within the observed marketplace dataset under different feature spaces?"*

### Experimental Design
Isolation Forest models (`n_estimators=150`, `random_state=42`, `RobustScaler`) were trained across four primary feature spaces:
1. **`J_PRICE` (7 features):** Price amount, median price ratio, delta from median, percentile, discount flags.
2. **`J_PRICE_TEXT` (28 features):** Price features + token counts, N-gram metrics, condition/warranty/urgency cues, contact-redirection flags.
3. **`J_PRICE_IMAGE` (37 features):** Price features + media coverage, SHA reuse count, pHash count, DINO neighbor count, OCR tokens, AI detector counts.
4. **`J_FULL_MULTIMODAL` (85 features):** Comprehensive cross-modal feature representation.

### Outlier Persistence Across Feature Spaces
At nominal contamination $c=0.05$ (149 outliers per space), the engine evaluated which listings remained anomalous across independent representations:
* **Inliers across all spaces:** **2,574 listings (86.38%)**
* **Outliers in only 1 space:** **270 listings (9.06%)**
* **Persistent in 2 spaces:** **88 listings (2.95%)**
* **Persistent in 3 spaces:** **45 listings (1.51%)**
* **Persistent in ALL 4 spaces:** **3 listings (0.10%)**

### The 3 Persistent Outliers
1. **Listing `1854083889` (Bhuj):** PS5 Pro 2TB console bundle at ₹110,000 appearing within a controller query (extreme bundle price outlier).
2. **Listing `1855231431` (Bengaluru):** PS5 Controller at ₹2,200 with anomalous cross-modal feature distribution.
3. **Listing `1856141038` (Bhiwandi):** "I phone 17 pro" at ₹350 (unreleased model string + placeholder price).

### Contamination Sensitivity Sweep
Evaluating contamination levels across $c \in [0.01, 0.02, 0.05, 0.10]$ demonstrated strict nested retention: the 30 outliers flagged at $c=0.01$ were a strict subset of the 149 outliers at $c=0.05$, confirming model stability.

---

# 14. Final Evidence Synthesis, Dataset Ledger & Review Queue (Phase K)

Phase K executed the final read-only synthesis across all frozen phases:
* **Dataset Ledger:** Documented in [`data/olx_analysis/reports/TRUSTLENS_DATASET_LEDGER.md`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/data/olx_analysis/reports/TRUSTLENS_DATASET_LEDGER.md).
* **Multi-Signal Evidence Table:** 213 candidate pairs exported to [`data/olx_analysis/reports/multi_signal_evidence.parquet`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/data/olx_analysis/reports/multi_signal_evidence.parquet).
* **Research Review Queue:** 213 prioritized items exported to [`data/olx_analysis/reports/research_review_queue.parquet`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/data/olx_analysis/reports/research_review_queue.parquet), deterministically sorted by `evidence_count descending, missingness ascending`.
* **Zero Arbitrary Risk Scores:** Proved that multi-modal layer counting provides actionable prioritization without black-box risk weighting.

---

# 15. Representative Research Case Studies (The 12 In-Depth Investigations)

### Case Study 1: Exact Binary Image Reuse Across Metropolitan Markets
* **Subjects:** Listing `1853431683` (Thane) & Listing `1853844217` (Mumbai)
* **Observed:** Both listings contain media files with identical SHA-256 hashes (`f6c0eb2d8477...`).
* **Derived:** Spatial distance between listing locations is ~25 km; listings published across different capture envelopes.
* **Candidate:** High perceptual hash similarity (pHash distance = 0).
* **Unknown:** Whether listings originate from a single multi-branch merchant or an unrelated copycat seller.
* **Significance:** Demonstrates byte-for-byte image recycling across city boundaries.

### Case Study 2: Deep Visual Similarity (DINOv2) Without Binary Hash Equality
* **Subjects:** Listing `1854413649` & Listing `1852565327` (iPhone 14 Pro Max)
* **Observed:** DINOv2 cosine similarity is 0.884; SHA-256 hashes distinct; pHash distance is 18.
* **Derived:** Both images depict an iPhone 14 Pro Max Deep Purple on a white surface, taken from slightly shifted camera angles.
* **Candidate:** Visual similarity candidate identified by foundation vision model.
* **Unknown:** Whether the same physical handset was photographed in two poses or two distinct handsets were photographed in similar studio environments.
* **Significance:** Highlights why deep representation learning captures semantic visual affinity that hash-based fingerprinting misses.

### Case Study 3: Multimodal Model Mismatch (Box vs. Title Claim)
* **Subjects:** Listing `1856180547` (Media `MED-1856180547-0`)
* **Observed:** Title asserted *"iPhone 13 128"*. Tesseract OCR detected the string *"iPhone 13 Mini"* on the packaging box (confidence 48.84).
* **Derived:** Product category model mismatch flag set to `1`.
* **Candidate:** Deterministic regex model mismatch candidate (`TEXT_IMAGE_MODEL_MISMATCH`).
* **Unknown:** Whether the seller uploaded an incorrect photograph by mistake or is selling an iPhone 13 Mini mislabeled as a standard iPhone 13.
* **Significance:** Demonstrates automated cross-modal extraction catching direct packaging contradictions.

### Case Study 4: Multimodal Activation Lock / Demo Screen Cue
* **Subjects:** Listing `1848124756` (Media `MED-1848124756-0`)
* **Observed:** Title states *"Apple iPhone"*. OCR detected the uppercase string *"ACTIVATION LOCK"* on the display (confidence 76.25).
* **Derived:** Demo / lock cue flag set to `1`.
* **Candidate:** Candidate activation-locked hardware (`TEXT_IMAGE_DEMO_CLUE`).
* **Unknown:** Whether the device is locked to the owner's iCloud account, a store demo unit, or being sold for parts.
* **Significance:** Illustrates automated identification of operational hardware constraints from unconstrained screen text.

### Case Study 5: Shared-Image Claim Drift Across Listings
* **Subjects:** Listing `1853989585` & Listing `1855905757`
* **Observed:** Both listings share deep visual similarity (DINOv2 cosine = 0.912). Listing A advertises 128GB capacity at ₹42,000; Listing B advertises 256GB capacity at ₹48,000.
* **Derived:** Shared-image claim drift candidate (`INC-DRIFT-1853989585-1855905757`).
* **Candidate:** Potential claim divergence across duplicated media.
* **Unknown:** Whether an inventory refurbisher re-used a single photo template for multiple devices of varying storage tiers.
* **Significance:** Proves that shared imagery does not imply identical physical specifications.

### Case Study 6: AI Detector Mutual Agreement Candidate
* **Subjects:** Listing `1842975565` (Media `MED-1842975565-0`, Bengaluru)
* **Observed:** Detector A (ViT-Base) score: 0.975; Detector B (Swin-Base) score: 0.772. Title: *"Iphone 13 pro max for exchange"*.
* **Derived:** Both detectors independently crossed the 0.70 candidate threshold (`AGREEMENT_AI`).
* **Candidate:** AI-generation candidate.
* **Unknown:** Whether the image is a fully synthetic AI generation, a heavy commercial digital render, or an image altered by digital enhancement filters.
* **Significance:** Demonstrates mutual detector agreement on non-standard marketplace imagery while acknowledging the absence of ground-truth provenance.

### Case Study 7: AI Detector Inter-Model Disagreement
* **Subjects:** Listing `1694522732` (Media `MED-1694522732-0`)
* **Observed:** Detector A score: 0.012 (strongly classified as real); Detector B score: 0.954 (strongly classified as AI candidate).
* **Derived:** Classified as `DETECTOR_DISAGREEMENT`.
* **Candidate:** Ambiguous provenance artifact.
* **Unknown:** Which model is empirically correct in the absence of controlled training benchmarks.
* **Significance:** Emphasizes that single-detector AI classification is prone to severe false positives/negatives, validating the two-detector consensus architecture.

### Case Study 8: Severe Price Discount Novelty Without Image/Text Reuse
* **Subjects:** Listing `1856141038` (Bhiwandi)
* **Observed:** Title: *"I phone 17 pro"*; Price: ₹350.
* **Derived:** Price ratio to smartphone median is 0.009 (99.1% below median). Persistent statistical anomaly across all 4 Isolation Forest spaces.
* **Candidate:** Extreme statistical novelty outlier.
* **Unknown:** Whether the listing is an unreleased model spoof, a dummy test entry, a price placeholder for negotiable calls, or a listing for a phone case misclassified as a device.
* **Significance:** Demonstrates how statistical novelty models isolate extreme outliers even when no network reuse exists.

### Case Study 9: Multi-Signal Convergence Across 4 Independent Layers
* **Subjects:** Listing `1853686065` (Nashik; ₹999) & Listing `1854199139` (Mumbai; ₹1,499)
* **Observed:** 
  1. Identical SHA-256 image binary.
  2. High lexical similarity (Titles: *"iPhone And Android Software Service"* vs. *"iPhone / Android Software Service"*).
  3. Shared distinctive OCR phrase detected on image banner.
  4. DINOv2 visual similarity candidate (cosine > 0.95).
* **Derived:** Multi-signal listing pair with 4 independent evidence layers; cross-city mobility spanning Nashik and Mumbai.
* **Candidate:** Syndicated service provider network.
* **Unknown:** Whether a legitimate multi-city repair chain operates these accounts or an affiliate is replicating listings.
* **Significance:** Prime exemplar of multimodal corroboration: image, text, OCR, and embedding signals all converge.

### Case Study 10: High-Value Bundle Novelty (PS5 Pro Outlier)
* **Subjects:** Listing `1854083889` (Bhuj)
* **Observed:** Title: *"PS5 Pro 2TB + 2 Original Controllers Like New"*; Price: ₹110,000.
* **Derived:** Price ratio to gaming accessory median is 36.7 (3,670% above median). Persistent anomaly across all 4 experiments.
* **Candidate:** High-end console bundle outlier.
* **Unknown:** Transaction legitimacy.
* **Significance:** Illustrates that statistical anomalies often reflect legitimate high-value bundles (full console bundle appearing within a controller search query) rather than deceptive entries.

### Case Study 11: Cross-Category Perceptual Image Reuse
* **Subjects:** Listing `1855231431` (Bengaluru) & Listing `1855112256` (Kanpur)
* **Observed:** pHash distance $\le 8$; DINOv2 cosine = 0.842. Both depict PS5 controller packaging.
* **Derived:** Cross-state image reuse linking Karnataka and Uttar Pradesh.
* **Candidate:** Perceptual reuse candidate across non-adjacent markets.
* **Unknown:** Whether imagery was scraped from an e-commerce platform (e.g. Amazon/Flipkart) by two independent sellers.
* **Significance:** Shows that widespread web scraping of manufacturer stock photography creates artificial cross-city network edges.

### Case Study 12: Massive Connected Component Hub
* **Subjects:** Component `COMP-001` (122 listings across 14 cities)
* **Observed:** 122 listings connected via exact title reuse (*"iPhone 13 128GB Mint Condition"*), shared image hashes, and high text similarity.
* **Derived:** Largest connected component in the marketplace graph.
* **Candidate:** Commercial syndication hub or marketing automation script.
* **Unknown:** Whether this represents an authorized commercial refurbisher, an affiliate marketing ring, or automated spam duplication.
* **Significance:** Demonstrates how automated listing tools can populate nationwide classifieds with identical templates, dominating search visibility.

---

# 16. Comprehensive Visual Assets & Figures Catalogue (Figures 01 to 73)

All visual assets generated by the TrustLens pipeline are consolidated in [`all_graphs_and_images/`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/all_graphs_and_images/):

### Core Architecture & Infographic Slides
* `infographics_and_architecture/trustlens_architecture.svg` — High-fidelity vector architecture diagram.
* `infographics_and_architecture/trustlens_architecture_and_results.png` — 1920×1080 executive infographic slide.

### Interactive HTML Dashboards
* `interactive_dashboards/final_research_dashboard.html` — Master Phase K research exploration dashboard.
* `interactive_dashboards/relationship_graph.html` — 5,709-node network visualization.
* `interactive_dashboards/image_reuse_network.html` — Cryptographic SHA-256 reuse graph.
* `interactive_dashboards/text_similarity_network.html` — Lexical text similarity candidate graph.
* `interactive_dashboards/geographic_relationship_map.html` — Cross-city & cross-state mobility corridor map.
* `interactive_dashboards/ai_detector_gallery.html` — Dual-detector AI image consensus gallery.
* `interactive_dashboards/image_forensics_gallery.html` — Metadata, EXIF, and C2PA provenance gallery.
* `interactive_dashboards/multimodal_ocr_gallery.html` — Tesseract OCR text extraction gallery.
* `interactive_dashboards/text_intelligence_gallery.html` — Lexical N-gram & TF-IDF keyword gallery.
* `interactive_dashboards/visual_gallery.html` — DINOv2 visual neighbor gallery.

### Publication Figures (83 PNG Charts)
* **Figures 01–08 (Phase B):** Query shares, brand distribution, comparable price medians, -35% threshold curve, accessory noise filter.
* **Figures 09–11 (Phase C):** pHash Hamming distance distribution, threshold sensitivity curve, top image cluster sizes.
* **Figures 12–19 (Phase D):** DINOv2 cosine distribution, nearest-neighbor decay, pHash vs DINO scatter, cross-city visual matrix.
* **Figures 20–24 (Phase E):** Tesseract OCR yield, confidence bands, character counts, 68 discrepancy categories.
* **Figures 25–35 (Phase F):** Token distributions, condition/warranty cues, unigram/bigram/trigram frequencies, TF-IDF terms, price-band heatmap.
* **Figures 36–42 & fig_* (Phase G/G.1):** Image types, C2PA audit, ViT/Swin score distributions, 559 disagreements, recompression stability.
* **Figures 43–50 (Phase H):** Edge type distribution, component sizes, shared image degrees, cross-city corridors.
* **Figures 51–61 (Phase J):** Novelty distributions across 4 spaces, Jaccard overlap matrix, persistence curve, contamination sensitivity, PCA projection.
* **Figures 62–73 (Phase K):** Population funnel, normalized price violins, multimodal relationships, 213 multi-signal pairs, geographic observation map.

---

# 17. Public Showcase, Career Artifacts & Industry Outreach

All packaging materials are housed in [`showcase/`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/showcase/):
* **Interactive Web Showcase:** [`showcase/demo/index.html`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/showcase/demo/index.html) — 10-screen visual storytelling application.
* **Portfolio Deep Dive:** [`showcase/portfolio/TRUSTLENS_CASE_STUDY.md`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/showcase/portfolio/TRUSTLENS_CASE_STUDY.md) — 2,000-word case study detailing *"What I Refused to Automate"*.
* **System Architecture:** [`showcase/architecture/trustlens_architecture.md`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/showcase/architecture/trustlens_architecture.md).
* **Career Materials:** [`showcase/application/`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/showcase/application/) — Interview answers (`ai_ml_project_story.md`), resume bullets across 3 tracks (`resume_bullets.md`), and LinkedIn story post (`linkedin_project_post.md`).
* **OLX Outreach Suite:** [`showcase/outreach/`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/showcase/outreach/) — LinkedIn notes, DMs, engineering briefs, and meeting one-pagers tailored for OLX engineering and talent acquisition leaders.

---

# 18. Methodological Limitations & Production Roadmap

### Empirical Limitations
1. **Search-Card Ingestion Boundary:** Detailed item descriptions and seller account registration dates were unobserved in public search cards.
2. **Targeted Sample Scope:** Data collection was restricted to three high-value electronics categories (`iphone`, `macbook`, `ps5 controller`).
3. **Absence of Ground Truth:** Observations represent **statistical novelty, cross-listing duplication, and multimodal inconsistencies**, not proven criminal guilt.

### Production Transition Roadmap
If deploying this architecture inside a commercial marketplace like OLX:
1. **Authenticated Ingestion:** Ingest internal seller account IDs, device fingerprints, and KYC status to resolve network clusters into verified commercial merchant entities.
2. **Streaming Event Pipeline:** Replace batch Parquet evaluation with real-time Kafka/Flink streaming, computing hashes and OCR checks at the moment of listing creation.
3. **Investigator Active Learning Feedback:** Connect human reviewer decisions back into calibrated supervised rerankers.
4. **Hardware Serial Verification:** Deploy private OCR models to cross-reference partially masked IMEI and serial numbers against authorized platform databases.

---

> **TrustLens provides evidence organization, multimodal observation, relationship analysis, and statistical novelty detection. It does not independently establish fraud, criminal intent, seller identity, or AI image provenance without appropriate external verification and ground truth.**
