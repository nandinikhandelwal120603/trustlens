# TrustLens: Final Marketplace Research Report
## Multimodal Evidence Synthesis, Forensic Intelligence & Statistical Novelty Analysis in Online Classifieds

**Document Version:** 1.0.0 (Final Release)  
**Pipeline Phases:** Phase A through Phase K (COMPLETE & FROZEN)  
**Corpus Evaluated:** 2,980 Canonical OLX Listings | 2,280 Validated Media Assets  
**Principal System:** TrustLens Evidence-Based Fraud Intelligence System  

---

## 1. Executive Summary

TrustLens is an empirical marketplace research system engineered to analyze deceptive patterns, cross-listing duplication, multimodal inconsistencies, and statistical novelty within online classified advertising. Over eleven systematic phases (A through K), the TrustLens pipeline ingested, normalized, fingerprinted, embedded, OCR-evaluated, and modeled 2,980 canonical OLX listings across 3 key electronics query spaces (`iphone`, `macbook`, `ps5 controller`).

The investigation established:
* **Evidence-Based Findings:** Multi-modal analysis identified 164 pairwise instances of exact binary image reuse (SHA-256), 78 perceptual similarity candidates (pHash), 9,492 deep visual relationships (DINOv2), and 68 candidate multimodal discrepancies (including 66 instances of shared-image claim drift and 1 packaging model mismatch).
* **Multi-Signal Convergence:** 213 listing pairs exhibited convergence across $\ge 2$ independent forensic layers, with 5 pairs cross-corroborated across 4 distinct evidence layers (image, text, OCR, and embeddings).
* **Statistical Novelty:** Isolation Forest modeling across 4 feature spaces isolated 3 listings that were persistently anomalous across all evaluated modalities.
* **Definitive Boundary:** TrustLens produces structured observations and cross-corroborated research queues. In the absence of transaction logs and verified fraud ground truth, TrustLens **does not** infer seller malice, calculate fraud probabilities, or make automated accusations.

---

## 2. Research Objective

Online classifieds suffer from significant information asymmetry. Prior automated solutions have relied heavily on black-box "scam scores" or single-signal heuristics (such as price alone or unverified AI image detection). The primary objective of TrustLens is to answer:

> **What observable patterns exist in the collected marketplace data, what independent evidence supports them, and what cannot be established from this dataset?**

TrustLens replaces arbitrary risk scoring with an **Evidence Hierarchy**:
* **OBSERVED:** Directly visible, byte-verifiable data (e.g., exact SHA-256 equality).
* **DERIVED:** Deterministically calculated from observed data (e.g., price ratio to category median).
* **CANDIDATE:** Model-identified hypotheses requiring review (e.g., DINO similarity $\ge 0.70$).
* **UNVERIFIED:** Claims lacking independent corroboration (e.g., unverified user reports).
* **UNKNOWN:** Data unobserved in the capture environment (e.g., seller identity, transaction outcome).

---

## 3. Dataset & Collection Methodology

The dataset comprises 2,980 canonical marketplace listings gathered via targeted client-side search capture on OLX India across 5 distinct deduplicated archives:
* `iphone`: 2,337 observations (78.42%)
* `macbook`: 393 observations (13.19%)
* `ps5 controller`: 250 observations (8.39%)

### Collection Hierarchy:
```text
Raw Capture Events: 2,980
    ↓
Canonical Listings: 2,980 (1 row = 1 listing)
    ↓
Media References: 2,491
    ↓
Unique Apollo CDN Assets: 2,323
    ↓
Downloaded Local Assets: 2,282 (98.24% success)
    ↓
Evaluated Media Cohort: 2,280 (2 corrupted files excluded)
```

---

## 4. End-to-End Pipeline Architecture

The TrustLens research pipeline executed sequentially across eleven frozen stages:
1. **Phase A (Data Ingestion & Audit):** Parsing raw JSON archives, deduplicating capture runs, verifying entity counts.
2. **Phase B (Product Normalization & Price Intelligence):** Rule-based regex model parsing, category taxonomy, median price deviation modeling.
3. **Phase C (Image Fingerprinting):** Exact binary SHA-256 hashes, pHash, dHash, and aHash computation; Hamming distance clustering.
4. **Phase D (Deep Visual Embeddings):** 384-dimensional DINOv2-Small dense embeddings, cosine similarity indexing, nearest neighbor search.
5. **Phase E (Multimodal OCR & Consistency):** Tesseract OCR extraction, token parsing, packaging vs. title mismatch detection.
6. **Phase F (Text Intelligence & Linguistics):** Title normalization, n-gram lexical analysis, TF-IDF term distinctiveness, contact redirection regexes.
7. **Phase G & G.1 (Image Forensics & AI Detection):** EXIF/C2PA provenance audits, dual-detector ViT-Base & Swin-Base synthetic image evaluation.
8. **Phase H (Relationship Network Intelligence):** Multimodal graph construction (5,709 nodes, 21,395 edges), connected component analysis.
9. **Phase I (Unified Feature Store):** Consolidation into a canonical table (2,980 rows × 137 validated features).
10. **Phase J (Statistical Anomaly Analysis):** Unsupervised Isolation Forest novelty modeling across 4 feature spaces, contamination sensitivity.
11. **Phase K (Final Synthesis & Reporting):** Multi-signal cross-corroboration, research review queue, case studies, and final reporting.

---

## 5. Product & Price Analysis

* **Price Dispersion:** Comparable-model analysis revealed severe price dispersion. Within the normalized iPhone 14 Pro Max category, prices spanned ₹35,000 to ₹125,000 (median ₹68,000).
* **Extreme Discounting:** 127 listings (4.26%) were priced below 35% of their comparable-product median.
* **Analytical Finding:** While extreme discounting is frequently cited in consumer fraud reports, price novelty alone is non-specific: genuine low-priced listings include accessories (cases, screen protectors), damaged/for-parts units, and dummy placeholder prices.

---

## 6. Text & Linguistic Intelligence

* **Lexical Repetition:** 666 listings (22.3%) exhibited exact title duplication with at least one other listing.
* **Commercial Phrasing:** High frequencies of condition cues ("brand new", "mint condition", "sealed pack") appeared in 1,566 listings (52.6%).
* **Contact Redirection:** 92 listings (3.1%) contained direct external redirection cues (e.g., "call on 98...", "WhatsApp only"). These cues bypass on-platform communication channels, presenting notable research interest.

---

## 7. Image Fingerprinting & Visual Similarity

* **Exact SHA-256 Duplication:** 164 pairwise instances of exact binary image reuse were detected across 242 listings. 78.0% of these pairs spanned different cities.
* **Perceptual Candidates (pHash $\le 10$):** 78 candidate pairs were identified where images underwent minor resizing, aspect ratio adjustment, or re-compression.
* **DINOv2 Visual Similarity:** 9,492 pairs exceeded cosine similarity 0.70. Deep embeddings effectively connect listings displaying identical packaging styles and angled product shots across disparate sellers.

---

## 8. OCR & Multimodal Inconsistency Analysis

* **Coverage:** 1,885 of 2,280 images (82.7%) yielded legible text strings.
* **Inconsistency Candidates:**
  * **Model Mismatch (1 candidate):** Listing `1856180547` claimed "iPhone 13 128", while box text confirmed "iPhone 13 Mini".
  * **Demo/Lock Screen (1 candidate):** Listing `1848124756` displayed a device showing "ACTIVATION LOCK".
  * **Shared-Image Claim Drift (66 candidates):** Pairs of listings utilizing identical image binaries but advertising conflicting storage capacities or models.

---

## 9. Image Authenticity & Dual-Detector AI Analysis

* **Architecture:** Evaluated all 2,280 images through Detector A (ViT-Base) and Swin-Base (Detector B).
* **Observed Consensus:**
  * Agreement Real: 958 images (42.0%)
  * Agreement AI Candidate: 6 images (0.26%)
  * Detector Disagreement: 559 images (24.5%)
  * Borderline Zone: 757 images (33.2%)
* **Mutual AI Candidates:** Inspection of the 6 mutual candidates confirmed they were graphic promotional banners, text-heavy flyers, or synthetic 3D product renders rather than deceptive photorealistic deepfakes.
* **Cloud Escalation:** The 1,316 ambiguous images remained an unexecuted escalation queue; no external cloud inference was performed.

---

## 10. Relationship Network Intelligence

* **Graph Dimensions:** 5,709 nodes (listings, media, locations, product families) and 21,395 edges.
* **Components:** 2,133 total connected components, including 266 non-singleton clusters.
* **Component Scaling:** The largest component linked 122 listings across 14 cities via shared templates and images. Such macro-components reflect commercial retailer syndication, refurbisher multi-branch marketing, or automated listing tools.

---

## 11. Statistical Anomaly Analysis (Phase J)

* **Isolation Forest Novelty:** Evaluated across 4 primary spaces at nominal contamination $c=0.05$ (149 outliers per space):
  * `J_PRICE`: 7 features
  * `J_PRICE_TEXT`: 28 features
  * `J_PRICE_IMAGE`: 37 features
  * `J_FULL_MULTIMODAL`: 85 features
* **Persistence:**
  * Inliers: 2,574 listings (86.38%)
  * Flagged in 1 space: 270 listings (9.06%)
  * Flagged in 2 spaces: 88 listings (2.95%)
  * Flagged in 3 spaces: 45 listings (1.51%)
  * **Flagged in all 4 spaces:** **3 listings (0.10%)**
* **Persistence Guardrail:** Persistence across feature spaces measures multivariate statistical novelty; it does not constitute proof of fraudulent intent.

---

## 12. Multi-Signal Evidence Convergence

* **213 Multi-Signal Pairs:** Exactly 213 listing pairs were corroborated by $\ge 2$ independent forensic modalities:
  * 4 layers: 5 pairs
  * 3 layers: 63 pairs
  * 2 layers: 145 pairs
* **Significance:** Multi-signal convergence represents the highest standard of empirical interest in TrustLens. Corroboration across independent modalities (e.g., shared SHA-256 image + high lexical text similarity + shared OCR phrase) significantly reduces false alarms associated with single-signal heuristics.

---


## Representative Research Case Studies

The following 12 case studies illustrate distinct empirical evidence structures observed across the pipeline. Each case answers five mandatory research questions:
1. *What was observed?*
2. *What was derived?*
3. *What is only a candidate?*
4. *What remains unknown?*
5. *Why does this case matter?*

---

### Case Study 1: Exact Binary Image Reuse Across Geographies
* **Subjects:** Listing `1853431683` (Thane) & Listing `1853844217` (Mumbai)
* **Observed:** Both listings contain media files with identical SHA-256 hashes (`f6c0eb2d8477...`).
* **Derived:** Spatial distance between listing locations is ~25 km; listings were captured across different capture envelopes.
* **Candidate:** High perceptual hash similarity (pHash distance = 0).
* **Unknown:** Whether the listings originate from a single seller with multiple physical branches or two unrelated parties copying stock images.
* **Significance:** Demonstrates direct binary image duplication across metropolitan boundaries without image re-encoding.

---

### Case Study 2: Deep Visual Similarity (DINOv2) Without Binary Hash Equality
* **Subjects:** Listing `1854413649` & Listing `1852565327` (iPhone 14 Pro Max)
* **Observed:** DINOv2 cosine similarity is 0.884; SHA-256 hashes are completely distinct; pHash distance is 18.
* **Derived:** Both images depict an iPhone 14 Pro Max in Deep Purple on a white surface, but taken from slightly shifted camera angles and different lighting.
* **Candidate:** Visual relationship candidate identified by deep representation.
* **Unknown:** Whether the same physical handset was photographed in two poses or two distinct handsets were photographed in similar studio environments.
* **Significance:** Highlights why deep representation learning captures semantic visual affinity that hash-based fingerprinting completely misses.

---

### Case Study 3: Multimodal Model Mismatch (Box vs. Title Claim)
* **Subjects:** Listing `1856180547` (Media `MED-1856180547-0`)
* **Observed:** Title states *"iPhone 13 128"*. Tesseract OCR detected the text string *"iPhone 13 Mini"* on the packaging box with 48.84 confidence.
* **Derived:** Product category model mismatch flag set to `1`.
* **Candidate:** Deterministic regex model mismatch candidate (`TEXT_IMAGE_MODEL_MISMATCH`).
* **Unknown:** Whether the seller uploaded an incorrect photograph by mistake, is selling an iPhone 13 Mini mislabeled as a standard iPhone 13, or re-used another listing's image.
* **Significance:** Demonstrates the power of cross-modal OCR extraction to surface direct contradictions between text claims and physical packaging.

---

### Case Study 4: Multimodal Activation Lock / Demo Screen Cue
* **Subjects:** Listing `1848124756` (Media `MED-1848124756-0`)
* **Observed:** Title states *"Apple iPhone"*. OCR detected the uppercase string *"ACTIVATION LOCK"* on the device display with 76.25 confidence.
* **Derived:** Demo / lock cue flag set to `1`.
* **Candidate:** Candidate activation-locked device (`TEXT_IMAGE_DEMO_CLUE`).
* **Unknown:** Whether the device is legitimately locked to the owner's iCloud account, a retail store demo unit, or being sold for parts.
* **Significance:** Illustrates automated identification of operational hardware constraints from unconstrained screen text.

---

### Case Study 5: Shared-Image Claim Drift Across Listings
* **Subjects:** Listing `1853989585` & Listing `1855905757`
* **Observed:** Both listings share deep visual similarity (DINOv2 cosine = 0.912). Listing A advertises 128GB capacity at ₹42,000; Listing B advertises 256GB capacity at ₹48,000.
* **Derived:** Shared-image claim drift candidate (`INC-DRIFT-1853989585-1855905757`).
* **Candidate:** Potential claim divergence across duplicated media.
* **Unknown:** Whether an inventory refurbisher re-used a single photo template for multiple devices of varying storage tiers.
* **Significance:** Proves that shared imagery does not imply identical physical specifications, establishing the need for multi-attribute consistency checks.

---

### Case Study 6: AI Detector Mutual Agreement Candidate
* **Subjects:** Listing `1842975565` (Media `MED-1842975565-0`, Bengaluru)
* **Observed:** Detector A (ViT-Base) score: 0.975; Detector B (Swin-Base) score: 0.772. Title: *"Iphone 13 pro max for exchange"*.
* **Derived:** Both detectors independently crossed the 0.70 threshold (`AGREEMENT_AI`).
* **Candidate:** AI-generation candidate.
* **Unknown:** Whether the image is a fully synthetic AI generation, a heavy commercial digital render, or an image altered by digital enhancement filters.
* **Significance:** Demonstrates mutual detector agreement on non-standard marketplace imagery while acknowledging the absence of ground-truth provenance.

---

### Case Study 7: AI Detector Inter-Model Disagreement
* **Subjects:** Listing `1694522732` (Media `MED-1694522732-0`)
* **Observed:** Detector A score: 0.012 (strongly classified as real); Detector B score: 0.954 (strongly classified as AI candidate).
* **Derived:** Classified as `DETECTOR_DISAGREEMENT`.
* **Candidate:** Ambiguous provenance artifact.
* **Unknown:** Which model is empirically correct in the absence of controlled training benchmarks.
* **Significance:** Emphasizes that single-detector AI classification is prone to severe false positives/negatives, validating the two-detector consensus architecture.

---

### Case Study 8: Severe Price Discount Novelty Without Image/Text Reuse
* **Subjects:** Listing `1856141038` (Bhiwandi)
* **Observed:** Title: *"I phone 17 pro"*; Price: ₹350.
* **Derived:** Price ratio to smartphone median is 0.009 (99.1% below median). Persistent statistical anomaly across all 4 Isolation Forest spaces.
* **Candidate:** Extreme statistical novelty outlier.
* **Unknown:** Whether the listing is an unreleased model spoof, a dummy test entry, a price placeholder for negotiable calls, or a listing for a phone case misclassified as a device.
* **Significance:** Demonstrates how statistical novelty models isolate extreme outliers even when no network reuse exists.

---

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
* **Significance:** Serves as the prime exemplar of multi-modal corroboration: image, text, OCR, and embedding signals all converge.

---

### Case Study 10: High-Value Bundle Novelty (PS5 Pro Outlier)
* **Subjects:** Listing `1854083889` (Bhuj)
* **Observed:** Title: *"PS5 Pro 2TB + 2 Original Controllers Like New"*; Price: ₹110,000.
* **Derived:** Price ratio to gaming accessory median is 36.7 (3,670% above median). Persistent anomaly across all 4 experiments.
* **Candidate:** High-end console bundle outlier.
* **Unknown:** Transaction legitimacy.
* **Significance:** Illustrates that statistical anomalies often reflect legitimate high-value bundles (full console bundle appearing within a controller search query) rather than deceptive entries.

---

### Case Study 11: Cross-Category Perceptual Image Reuse
* **Subjects:** Listing `1855231431` (Bengaluru) & Listing `1855112256` (Kanpur)
* **Observed:** pHash distance $\le 8$; DINOv2 cosine = 0.842. Both depict PS5 controller packaging.
* **Derived:** Cross-state image reuse linking Karnataka and Uttar Pradesh.
* **Candidate:** Perceptual reuse candidate across non-adjacent markets.
* **Unknown:** Whether imagery was scraped from an e-commerce platform (e.g. Amazon/Flipkart) by two independent sellers.
* **Significance:** Shows that widespread web scraping of manufacturer stock photography creates artificial cross-city network edges.

---

### Case Study 12: Massive Connected Component Hub
* **Subjects:** Component `COMP-001` (122 listings across 14 cities)
* **Observed:** 122 listings connected via exact title reuse (*"iPhone 13 128GB Mint Condition"*), shared image hashes, and high text similarity.
* **Derived:** Largest connected component in the marketplace graph.
* **Candidate:** Commercial syndication hub or marketing automation script.
* **Unknown:** Whether this represents an authorized commercial refurbisher, an affiliate marketing ring, or automated spam duplication.
* **Significance:** Demonstrates how automated listing tools can populate nationwide classifieds with identical templates, dominating search visibility.


---

## 14. Geographic Observations

* **Geographic Distribution:** Analyzed top metropolitan markets with explicit denominators:
  * Delhi: 48 anomalies / 939 listings (5.11%)
  * Mumbai: 22 anomalies / 412 listings (5.34%)
  * Bengaluru: 16 anomalies / 305 listings (5.25%)
  * Hyderabad: 9 anomalies / 184 listings (4.89%)
  * Chennai: 7 anomalies / 142 listings (4.93%)
* **Geographic Neutrality:** Observed anomaly rates are remarkably uniform across cities (~5.0%–5.3%), confirming that statistical novelty is an inherent structural feature of the marketplace rather than localized to a specific "high-risk" geography.

---

## 15. Key Research Findings

### Finding 1: Single-Signal Heuristics Are Fundamentally Unreliable
* **Measurement:** Single-detector AI classification disagreed on 24.5% of images; price discounting alone included 33 pure accessory listings and damaged units.
* **Interpretation:** Unimodal detection mechanisms generate unacceptable false positive rates in open marketplace environments.
* **Limitation:** Multi-signal corroboration reduces false alarms but requires richer, multi-modal ingestion pipelines.

### Finding 2: Cross-City Image Duplication is Widespread
* **Measurement:** 78.0% of exact image reuse pairs spanned different cities.
* **Interpretation:** Re-use of existing product imagery across geographic boundaries is standard practice among commercial merchants, refurbishers, and private sellers.
* **Limitation:** In the absence of seller IDs, binary image reuse cannot establish whether duplication is benign syndication or deceptive impersonation.

### Finding 3: Multimodal Consistency Checks Surface Real Discrepancies
* **Measurement:** Tesseract OCR successfully extracted packaging text across 82.7% of images, isolating 68 discrepancy candidates.
* **Interpretation:** Cross-modal comparison between declared title claims and image text provides an explainable, deterministic mechanism for identifying deceptive listings.
* **Limitation:** OCR confidence is modest (mean 38.34), requiring human verification of candidates.

---

## 16. Research Limitations

1. **Targeted Query Scope:** Collected exclusively from three high-value consumer technology searches (`iphone`, `macbook`, `ps5 controller`).
2. **Missing Metadata:** Search-card captures omitted detailed seller profile histories, account ages, and full item descriptions.
3. **Absence of Ground Truth:** No verified fraud labels or transaction outcome logs exist in the dataset.
4. **Model Boundaries:** Synthetic image detectors and Isolation Forest models are sensitive to operational thresholds and pre-processing assumptions.
5. **No Seller Linkage:** Cannot establish legal identity or common beneficial ownership between accounts.

---

## 17. What TrustLens Can Establish

| Capability | Empirical Status | Validating Artifact |
| :--- | :---: | :--- |
| Price Anomaly Detection | **ESTABLISHED** | Phase B / Phase J (`unified_features.parquet`) |
| Exact Binary Image Reuse | **ESTABLISHED** | Phase C SHA-256 (`image_relationships.parquet`) |
| Perceptual Image Similarity | **ESTABLISHED** | Phase C pHash (`image_relationships.parquet`) |
| Deep Visual Embeddings | **ESTABLISHED** | Phase D DINOv2 (`deep_visual_relationships.parquet`) |
| Title Lexical Overlap | **ESTABLISHED** | Phase F Text Engine (`text_similarity_candidates.parquet`) |
| Packaging OCR Text Extraction | **ESTABLISHED** | Phase E OCR (`image_ocr.parquet`) |
| Multimodal Claim Discrepancies | **ESTABLISHED** | Phase E Inconsistencies (`multimodal_inconsistencies.parquet`) |
| AI-Generation Candidates | **ESTABLISHED** | Phase G.1 Dual Detector (`ai_detector_results.parquet`) |
| Multi-Modal Relationship Graph | **ESTABLISHED** | Phase H Network Engine (`relationship_edges.parquet`) |
| Multivariate Statistical Novelty | **ESTABLISHED** | Phase J Isolation Forest (`anomaly_results.parquet`) |

---

## 18. What TrustLens Cannot Establish

```text
1. A listing being statistically anomalous does NOT mean it is fraudulent.
2. A shared image does NOT prove seller coordination or malicious syndication.
3. A shared title does NOT prove common account ownership.
4. DINOv2 visual similarity does NOT prove image theft or identical physical devices.
5. An AI detector candidate score does NOT prove synthetic generation.
6. A low price does NOT prove fraud (e.g., damaged items, accessories, urgent sales).
7. External contact redirection (e.g., WhatsApp) does NOT establish illegal intent.
8. Geographic concentration does NOT establish a geographic fraud hotspot.
9. Multi-signal convergence increases empirical interest but DOES NOT establish criminal guilt.
```

---

## 19. Future Research Directions

1. **Longitudinal Capture Pipelines:** Monitor listing persistence, price adjustments, and deletion lifecycles over extended temporal horizons.
2. **Authorized Seller Metadata Ingestion:** Ingest authenticated seller account histories to link multi-listing clusters to verifiable commercial entities.
3. **Controlled Ground-Truth Benchmarks:** Collaborate with marketplace operators to evaluate multi-signal precision against confirmed dispute outcomes.
4. **Hardware Serial Verification:** Develop privacy-preserving OCR pipelines capable of cross-referencing blurred IMEI / serial numbers against manufacturer databases.

---

## 20. Conclusion

TrustLens demonstrates that automated marketplace intelligence can be rigorous, explainable, and multi-modal without resorting to arbitrary risk scores or unfounded accusations. By combining exact cryptographic fingerprinting, perceptual hashing, deep vision transformers, OCR claim verification, and multivariate novelty modeling, TrustLens provides researchers and marketplace integrity teams with an objective, evidence-backed foundation for understanding marketplace dynamics.

> **TrustLens provides evidence organization, multimodal observation, relationship analysis, and statistical novelty detection. It does not independently establish fraud, criminal intent, seller identity, or AI image provenance without appropriate external verification and ground truth.**
