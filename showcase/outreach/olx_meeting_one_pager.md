# TrustLens — Evidence-First AI for Marketplace Trust
### Executive Research Brief & Meeting One-Pager

**Researcher / Engineer:** Nandini Khandelwal  
**Focus:** Multimodal Fraud Intelligence • Computer Vision • Graph Analytics • Feature Stores  
**Location:** Delhi, India  

---

### 1. The Problem
Peer-to-peer marketplaces suffer from information asymmetry. Traditional automated anti-fraud approaches rely heavily on single-signal heuristics (like price drops) or ungrounded "scam probability" scores (e.g. "95% Scam"). Without post-transaction ground truth, black-box scores trigger high false positives, lack explainability, and fail to empower trust & safety investigators.

---

### 2. What I Built
**TrustLens** is an independent, end-to-end research prototype designed to investigate marketplace listings using **multimodal evidence triangulation**. Across 2,980 canonical OLX listings and 2,280 validated images, TrustLens extracts independent forensic signals across Price, Text, Image Hashes, DINOv2 Vision Embeddings, and Tesseract Packaging OCR, projecting them into a heterogeneous relationship network and an unsupervised novelty engine.

---

### 3. How It Works
1. **Taxonomy & Price Modeling:** Standardizes hardware models and computes median price deviations against comparable products (isolating listings priced >35% below median).
2. **Dual-Track Visual Forensics:** Uses exact SHA-256 hashes to find byte-level duplicate images across listings, alongside 384-d DINOv2 vision embeddings to detect visual similarity across angles.
3. **Cross-Modal Packaging OCR:** Extracts packaging text strings using OCR, flagging discrepancies where declared title claims contradict visible box labels.
4. **Dual-Transformer AI Consensus:** Combines ViT-Base and Swin-Base detectors, requiring dual agreement to avoid single-detector false alarms.
5. **Relationship Graph & Feature Store:** Unifies 137 features into a canonical feature store and constructs a 5,709-node network to detect cross-city syndication.
6. **Novelty Modeling:** Employs Isolation Forest across 4 feature spaces to isolate persistent statistical novelties without arbitrary risk weighting.

---

### 4. Key Empirical Results
* **Dataset Scope:** 2,980 canonical listings, 2,280 evaluated media files, 137 validated features.
* **Exact Image Duplicates:** 164 pairwise instances of exact image reuse (**78% cross-city**).
* **Deep Visual Similarity:** 9,492 candidate pairs identified via DINOv2 embeddings (cosine $\ge 0.70$).
* **Multimodal Discrepancies:** 68 candidate contradictions (66 shared-image claim drifts, 1 box model mismatch, 1 demo lock screen).
* **AI Detector Limits:** Discovered **559 single-detector disagreements (24.5%)**, proving single models cannot be relied upon in classifieds.
* **Network Topology:** 5,709 nodes, 21,395 edges. Largest component linked 122 listings across 14 cities.
* **Multi-Signal Candidates:** **213 listing pairs** corroborated across $\ge 2$ independent forensic layers (including 5 pairs cross-verified across 4 layers).
* **Automated Tests:** 124 passed, 1 skipped (0 regressions).

---

### 5. Example Investigation
* **Listing A:** *"iPhone And Android Software Service"* in Nashik (₹999).
* **Listing B:** *"iPhone / Android Software Service"* in Mumbai (₹1,499).
* **TrustLens Triangulation:** Identical SHA-256 image binary + Jaccard text similarity > 0.85 + shared OCR banner text + DINOv2 cosine > 0.95.
* **Outcome:** Surfaces an explainable 4-layer syndication corridor without making reckless automated accusations.

---

### 6. What a Production Deployment Would Require
* **Authenticated Account Linking:** Internal seller IDs to resolve network clusters into verified commercial merchants vs. abuse rings.
* **Real-Time Streaming:** Kafka/Flink pipeline computing hashes and OCR checks at the moment of listing creation.
* **Investigator Active Learning:** Connecting human reviewer decisions back into calibrated supervised models.

---

### 7. Potential Contribution Areas
I would love to explore opportunities where I can apply this multimodal, evidence-first approach:
* **Applied AI / Machine Learning Engineering**
* **Trust & Safety Intelligence Systems**
* **Multimodal Search & Computer Vision**
* **Fraud Investigation & Policy Tooling**
* **ML Systems & Feature Store Architecture**
* **AI-Assisted Marketplace Operations**

---
*GitHub: [Project Repository] • LinkedIn: [Profile Link] • Email: [Contact Email]*
