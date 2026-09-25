# TrustLens — Final Marketplace Findings (Phase K)
## Evidence Synthesis, Multi-Signal Analysis & Forensic Intelligence

**Pipeline Phase:** Phase K (Final Synthesis)  
**Corpus Evaluated:** 2,980 Canonical OLX Listings | 2,280 Processed Media Assets  
**Document Status:** FINAL AUTHORITATIVE SYNTHESIS  

---

## 1. Executive Summary

TrustLens is an evidence-based marketplace fraud intelligence research system designed to empirically examine how deceptive patterns, visual and textual reuse, multimodal inconsistencies, and statistical novelty manifest within online classified listings. 

Over a multi-phase investigation spanning Phases A through K, the pipeline established:
1. **Dataset Population:** Evaluated 2,980 canonical OLX listings across 3 core consumer hardware queries (`iphone`, `macbook`, `ps5 controller`) with 2,491 media references and 2,280 fully processed, validated local image assets.
2. **Deterministic Fingerprinting & Similarity:** Identified 164 pairwise instances of exact binary image reuse (SHA-256), 78 perceptual similarity candidates (pHash $\le 10$), and 9,492 deep visual similarity relationships (DINOv2 cosine $\ge 0.70$).
3. **Multimodal Discrepancies:** OCR processing across 2,280 assets uncovered 68 candidate inconsistencies, including 66 instances of shared-image claim drift, 1 explicit model mismatch (listing title claiming iPhone 13 while screen displayed iPhone 13 Mini), and 1 activation lock/demo unit screen cue.
4. **Synthetic Image Candidates:** Evaluated all 2,280 images across two independent vision transformers (ViT-Base and Swin-Base). Identified 6 mutual AI-generation candidates, 958 mutual real agreements, and 559 detector disagreements.
5. **Relationship Network:** Constructed a 5,709-node entity graph with 21,395 edges, identifying 213 multi-signal candidate pairs corroborated across $\ge 2$ independent forensic layers (including 5 pairs with 4 independent evidence layers).
6. **Statistical Novelty:** Evaluated listings across 4 distinct Isolation Forest feature spaces (Price, Price+Text, Price+Image, Full Multimodal). Found 3 listings persistently anomalous across all 4 spaces.

---

## 2. Dataset & Collection Scope

| Dimension | Measured Value | Definitive Analytical Interpretation |
| :--- | :---: | :--- |
| **Canonical Listings** | **2,980** | Distinct OLX listing cards collected across 5 deduplicated capture batches. |
| **Search Queries** | **3** | `iphone` (78.42%), `macbook` (13.19%), `ps5 controller` (8.39%). |
| **Media References** | **2,491** | Listing search cards containing thumbnail image URLs. |
| **Unique Apollo Assets** | **2,323** | Unique image file IDs hosted on OLX's Apollo CDN infrastructure. |
| **Downloaded Image Files** | **2,282** | Local image files downloaded (98.24% acquisition success). |
| **Evaluated Media Assets** | **2,280** | Valid image binaries evaluated through pHash, DINOv2, OCR, and AI detectors. |
| **Feature Store Schema** | **137 columns** | Listing-level features (63 numeric, 40 categorical, 34 binary). |

---

## 3. Marketplace Composition

* **Query Concentration:** The dataset is heavily concentrated in smartphones (78.4% iPhone), reflecting targeted high-value consumer electronics queries. Findings reflect this sample and cannot be generalized to general classified categories (e.g., real estate or automobiles).
* **Geographic Distribution:** Dominated by Tier-1 metropolitan markets: Delhi (939 listings; 31.5%), Mumbai (412 listings; 13.8%), Bengaluru (305 listings; 10.2%), Hyderabad (184 listings; 6.2%), and Chennai (142 listings; 4.8%).
* **Missingness Realities:** Descriptions and persistent seller profile IDs were unobserved in the search-card capture layer. All text intelligence is derived from listing titles.

---

## 4. Product & Price Findings

* **Severe Price Dispersion:** Significant dispersion was observed within identical product models. For example, iPhone 13 listings ranged from ₹8,000 to ₹72,000 (median ₹38,500).
* **Extreme Discounting:** 127 listings (4.26%) were priced below 35% of their comparable-product median.
* **Accessory vs. Device Noise:** Query contamination was observed where accessories (cases, screen guards, boxes) priced at ₹100–₹500 shared search results with full devices. The product normalizer successfully classified 33 listings as pure accessories.

---

## 5. Text & Language Intelligence

* **Exact Title Duplication:** 666 listings (22.3%) exhibited exact title duplication with at least one other listing in the dataset.
* **Lexical Markers:** Condition claims ("mint condition", "sealed pack", "like new") were observed in 52.6% of listings. Warranty claims were present in 14.2% of titles.
* **Contact Redirection:** 92 listings (3.1%) contained direct external redirection cues (e.g., "WhatsApp", "call on", phone digits embedded in titles).

---

## 6. Image & Media Forensics

* **Exact Image Duplication (SHA-256):** 164 pairwise instances of exact binary image reuse were detected across 242 listings. 78.0% of these pairs spanned different cities, demonstrating cross-market media reuse.
* **Perceptual Similarity (pHash $\le 10$):** 78 candidate pairs exhibited near-identical perceptual structure despite recompression or minor dimensional resizing.
* **Deep Visual Similarity (DINOv2):** 9,492 pairwise relationships exceeded cosine similarity 0.70. While capturing genuine visual affinity (e.g. phones photographed on tables), DINO similarity frequently connects different listings of the same model photographed under standard retail angles.

---

## 7. OCR & Multimodal Inconsistencies

* **OCR Yield:** 1,885 of 2,280 images (82.7%) yielded legible text strings under local Tesseract OCR (mean confidence 38.34).
* **Claim Mismatches:**
  * **Model Mismatch:** 1 instance (`INC-MOD-1856180547-MED-1856180547-0`) where listing claimed iPhone 13, but OCR detected "iPhone 13 Mini" on the device box.
  * **Demo/Lock Screen:** 1 instance (`INC-DEMO-1848124756-MED-1848124756-0`) where commercial listing displayed an "ACTIVATION LOCK" screen.
  * **Shared-Image Claim Drift:** 66 instances where listings sharing identical images asserted differing storage capacities, models, or pricing.

---

## 8. Image Authenticity & AI Detection Findings

* **Two-Detector Consensus:** Tested all 2,280 images with ViT-Base (Detector A) and Swin-Base (Detector B).
* **Consensus Real:** 958 images (42.0%) evaluated as real by both detectors.
* **Mutual AI Candidates:** 6 images (0.26%) independently crossed the 0.70 threshold on both detectors. Manual audit revealed these were predominantly synthetic product renders, text-heavy flyers, or graphic promotional overlays rather than photorealistic deepfakes.
* **Detector Disagreement:** 559 images (24.5%) caused disagreement (Detector B flagged as AI candidate while Detector A scored as real). Single-detector evaluation is fundamentally unreliable.
* **Unexecuted Cloud Escalation:** The 1,316 borderline/disagreement images remained an unexecuted escalation queue; no external cloud inference was performed.

---

## 9. Relationship & Network Topology

* **Network Graph:** 5,709 entity nodes and 21,395 relationship edges form 2,133 connected components.
* **Clustering & Syndication:** 266 non-singleton components exist. The largest component links 122 listings across 14 cities via shared templates, images, and text.
* **Alternative Hypotheses:** Large clusters are consistent with merchant syndication, refurbisher multi-branch operations, or commercial marketing templates—not necessarily coordinated malicious fraud.

---

## 10. Statistical Anomaly Findings (Phase J)

* **Isolation Forest Novelty:** Evaluated across 4 spaces (Price: 7 features; Price+Text: 28 features; Price+Image: 37 features; Full Multimodal: 85 features) at nominal contamination $c=0.05$ (149 outliers per space).
* **Novelty Persistence:**
  * Inliers in all spaces: 2,574 listings (86.38%).
  * Outlier in 1 space only: 270 listings (9.06%).
  * Persistent in 2 spaces: 88 listings (2.95%).
  * Persistent in 3 spaces: 45 listings (1.51%).
  * **Persistent in all 4 spaces:** **3 listings (0.10%)**.
* **Interpretation:** High anomaly scores indicate multivariate statistical distance from the sample median; they do not establish fraud or seller malice.

---

## 11. Multi-Signal Evidence Convergence

* **213 Multi-Signal Pairs:** Exactly 213 listing pairs are connected through $\ge 2$ independent forensic layers:
  * 4 layers: 5 pairs
  * 3 layers: 63 pairs
  * 2 layers: 145 pairs
* **Dominant Combinations:**
  * Exact Image + Exact Title + DINO Similarity (48 pairs)
  * Exact Title + DINO Similarity (46 pairs)
  * pHash Perceptual + DINO Similarity (41 pairs)
  * Exact Image + DINO Similarity (29 pairs)
  * Shared OCR Phrase + Exact Image + Text Similarity + DINO (5 pairs)

---

## 12. Geographic Observations

* **Top Markets:** Delhi (48 anomalies / 939 listings; 5.11%), Mumbai (22 anomalies / 412 listings; 5.34%), Bengaluru (16 anomalies / 305 listings; 5.25%).
* **Proportionality:** Anomaly rates remain remarkably consistent (5.1%–5.4%) across all major cities, demonstrating that statistical novelty is uniformly distributed and not concentrated in a single geographic hub.
* **Mobility Corridors:** 7,446 observational edges span cross-city listing pairs, reflecting extensive cross-market duplication.

---

## 13. Research Limitations

1. **Targeted Query Bias:** Sample consists of electronics queries (`iphone`, `macbook`, `ps5 controller`).
2. **Missing Metadata:** Seller identifiers and descriptions were unavailable in search cards.
3. **Unsupervised Anomaly Modeling:** Contamination settings define the nominal outlier fraction; no ground truth fraud labels exist.
4. **AI Detector Calibration:** Synthetic image models lack localized marketplace calibration.
5. **No Seller Linkage:** Shared media or text does not definitively prove common seller ownership.

---

## 14. What TrustLens Can and Cannot Establish

| Forensic Dimension | TrustLens Capability | Definitive Scientific Boundary |
| :--- | :---: | :--- |
| **Price Anomaly** | **CAN ESTABLISH** | Identifies empirical deviation from median; **CANNOT** prove seller malice or scam intent. |
| **Binary Image Reuse** | **CAN ESTABLISH** | Measures SHA-256 byte equality; **CANNOT** prove image theft or unauthorized use. |
| **Perceptual Image Reuse** | **CAN ESTABLISH** | Identifies candidate image recompression; **CANNOT** establish seller coordination. |
| **Deep Visual Similarity**| **CAN ESTABLISH** | Identifies semantic visual alignment; **CANNOT** prove identical physical device. |
| **Exact Title Reuse** | **CAN ESTABLISH** | Measures string equality; **CANNOT** determine if author is single or multiple entities. |
| **OCR Text Extraction** | **CAN ESTABLISH** | Reads visible text on boxes/screens; **CANNOT** guarantee physical ownership. |
| **Claim Inconsistencies** | **CAN ESTABLISH** | Identifies text-vs-image contradictions; **CANNOT** distinguish error from deceit. |
| **AI Detector Signals** | **CAN ESTABLISH** | Identifies candidate model activations; **CANNOT** confirm generative AI creation. |
| **Seller Identity** | **CANNOT ESTABLISH** | Persistent seller profile data is unobserved in search captures. |
| **Fraud Determination** | **CANNOT ESTABLISH** | No ground-truth fraud outcomes or transaction logs exist in the corpus. |

---

## 15. Recommended Next Research Steps

1. **Longitudinal Capture:** Ingest continuous time-series data to track listing lifecycles.
2. **Seller Profile Ingestion:** Ingest authorized seller metadata to establish genuine seller graphs.
3. **Ground-Truth Fraud Benchmarks:** Partner with verified platforms to evaluate detector precision.
4. **Hardware Verification:** Incorporate IMEI / serial-number verification mechanisms.
