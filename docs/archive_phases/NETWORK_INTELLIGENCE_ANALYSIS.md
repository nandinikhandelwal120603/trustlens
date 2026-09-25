# TrustLens Phase H: Relationship & Network Intelligence Analysis

## Master Multimodal Relationship Graph & Forensic Network Report

- **Investigation Phase:** Phase H (Relationship & Network Intelligence)
- **Status:** COMPLETED & VERIFIED
- **Date:** 2026-09-24
- **Scope:** 2,980 Canonical Marketplace Listings | 2,491 Media Assets | 5,709 Entity Nodes | 21,395 Relationship Edges

---

## 1. Objective

Phase H establishes an explicit, deterministic, and explainable **Relationship Graph** connecting independently observed marketplace forensic attributes from Phases A through G.1. Rather than treating listings as isolated observations, Phase H enables investigators to examine repeated binary assets, perceptual image reuse, visual similarities, exact title duplicates, high lexical overlap, shared OCR phrases, and cross-jurisdictional mobility within a unified, traceable graph topology.

### Absolute Scientific Guardrails
- **No Risk / Fraud Scoring:** This system computes structural network properties and evidence counts. It does **NOT** compute `scam_score`, `fraud_score`, `seller_risk_score`, or automated probabilities.
- **No Seller Accusations / Common Identity Inference:** Listings sharing images, text, or locations are **NOT** presumed to belong to the same physical seller or coordinated ring. Commercial retailers, multi-branch refurbishers, and common syndication scripts frequently replicate assets legitimately.
- **Evidence Traceability:** Every edge in the graph points to a verifiable artifact in Phase A, B, C, D, E, or F.

---

## 2. Input Datasets (Frozen Phases A–G.1)

All input tables were loaded strictly read-only:
1. `data/olx_processed/listings.parquet` (2,980 rows): Canonical listing identifiers, titles, prices, raw locations, and timestamps.
2. `data/olx_processed/normalized_listings.parquet` (2,980 rows): Normalized product brand, category, family, and model.
3. `data/olx_processed/fingerprints.parquet` (2,491 rows): SHA-256 binary digests, pHash, dHash, and aHash perceptual hashes.
4. `data/olx_processed/image_relationships.parquet` (242 rows): Phase C binary exact reuse (82 pairs) and perceptual pHash similarity (160 pairs).
5. `data/olx_processed/deep_visual_relationships.parquet` (9,492 rows): Phase D DINOv2 ViT-B/14 cosine similarity candidates ($\ge 0.70$).
6. `data/trustlens/marketplace/text_similarity_candidates.parquet` (3,029 rows): Phase F exact title duplicates (2,096) and high lexical overlap candidates (933 at Jaccard $\ge 0.75$).
7. `data/olx_processed/image_ocr.parquet` (2,280 rows): Phase E normalized OCR text strings.
8. `data/olx_processed/multimodal_inconsistencies.parquet` (68 rows): Phase E cross-modal inconsistencies (66 shared-image claim drifts).
9. `data/olx_processed/image_authenticity.parquet` (2,280 rows): Phase G provenance metadata (EXIF/C2PA).
10. `data/olx_processed/ai_detector_results.parquet` (2,280 rows): Phase G.1 dual-detector AI image classification.

---

## 3. Entity Model

A deterministic NetworkX heterogeneous graph was constructed with 5,709 stable entity nodes across 6 entity types:

| Node Type | Entity Count | ID Format Pattern | Description |
| :--- | :---: | :--- | :--- |
| **`LISTING`** | 2,980 | `listing:<listing_id>` | Individual marketplace listing observation |
| **`MEDIA`** | 2,491 | `media:<media_id>` | Downloaded and validated image asset |
| **`PRODUCT`** | 60 | `product:<normalized_model>` | Normalized hardware model (e.g. `product:iphone_13`) |
| **`PRODUCT_FAMILY`**| 7 | `family:<normalized_family>` | Broad product line (e.g. `family:iphone`) |
| **`CITY`** | 153 | `city:<normalized_city>` | Normalized metropolitan jurisdiction |
| **`STATE`** | 18 | `state:<normalized_state>` | State administrative jurisdiction |
| **Total Nodes** | **5,709** | — | — |

*Note: In strict accordance with the project guidelines, no seller or account nodes were constructed because seller identity tokens do not exist in the source capture data.*

---

## 4. Controlled Edge Taxonomy

Edges are strictly categorized into structural containment edges and observed forensic relationship candidates:

| Edge Relationship Type | Count | Edge Category | Evidence Source | Threshold / Criteria |
| :--- | :---: | :--- | :--- | :--- |
| `MEDIA_VISUAL_SIMILARITY_CANDIDATE` | 9,492 | Deep Visual | Phase D (DINOv2) | Cosine similarity $\ge 0.70$ |
| `LISTING_IN_CITY` | 2,980 | Containment | Phase A Geography | Administrative match |
| `LISTING_HAS_PRODUCT` | 2,980 | Containment | Phase B Taxonomy | Deterministic model match |
| `LISTING_HAS_MEDIA` | 2,491 | Containment | Phase A Media Index | Media gallery membership |
| `LISTING_TEXT_EXACT_REUSE` | 2,182 | Text Reuse | Phase F Text | Exact normalized title match |
| `LISTING_TEXT_SIMILARITY_CANDIDATE` | 847 | Text Similarity | Phase F Text | Token Jaccard similarity $\ge 0.75$ |
| `MEDIA_EXACT_REUSE` | 164 | Image Reuse | Phase C Fingerprints | SHA-256 equality |
| `CITY_IN_STATE` | 153 | Containment | Phase A Geography | Administrative hierarchy |
| `MEDIA_PERCEPTUAL_REUSE_CANDIDATE` | 78 | Image Reuse | Phase C Fingerprints | pHash hamming distance $\le 10$ |
| `LISTING_SHARED_OCR_PHRASE` | 28 | Multimodal OCR | Phase E OCR | Distinctive shared n-gram $\ge 12$ chars |
| **Total Edges** | **21,395** | — | — | — |

---

## 5. Image Relationships (Exact vs. Perceptual vs. Visual Candidates)

Forensic signals across media assets are strictly separated by physical certainty:
- **`MEDIA_EXACT_REUSE` (164 directed edges / 82 unique pairs):** Exact binary asset reuse established by SHA-256 bit-level equality.
- **`MEDIA_PERCEPTUAL_REUSE_CANDIDATE` (78 directed edges / 39 unique pairs):** Perceptually near-identical images identified via perceptual hashing (pHash distance $\le 10$), capturing recompressed, cropped, or slightly color-shifted uploads.
- **`MEDIA_VISUAL_SIMILARITY_CANDIDATE` (9,492 directed edges):** Deep feature similarity identified via DINOv2 ViT-B/14 embeddings at cosine similarity $\ge 0.70$. Crucially, visual similarity candidates represent visual composition (e.g. angle, box packaging, device pose) and are **never** conflated with binary reuse or common provenance.

---

## 6. Text Relationships

Lexical analysis from Phase F provides two distinct relationship categories:
1. **Exact Title Reuse (2,182 edges):** Multiple listings sharing character-identical normalized title strings (e.g., standard promotional templates like *"iPhone 13 128GB 100% Battery Health All Working"*).
2. **High Lexical Overlap (847 edges):** Listing pairs exhibiting pairwise token Jaccard similarity $\ge 0.75$, capturing minor variations in boilerplate ad copy while preserving title intent.

---

## 7. OCR Relationships & Privacy Redaction

Distinctive OCR phrases extracted from Phase E Tesseract normalized strings yielded **28 pairwise shared OCR phrase links** across listings.
- **Privacy Protection:** All OCR phrase edges use normalized, privacy-redacted n-grams (e.g., repeated shop warranty banners, device spec stickers, and store receipts). Personal phone numbers and financial tokens were redacted using SHA-256 hashes (`ocr_entity_hash`) and never stored in plain text.

---

## 8. Product Relationships

Product containment edges tie listings to 60 distinct normalized models and 7 product families:
- Intra-product relationships (`product_a == product_b`): 11,563 observational edges.
- Cross-product family relationships (`cross_product == True`): 1,228 observational edges. Cross-product edges occur when sellers reuse generic marketing templates (e.g. *"Brand new sealed box with warranty"*) across both iPhone 13 and iPhone 14 listings.

---

## 9. Geographic Relationships & Corridors

The graph captures observed spatial mobility across metropolitan centers:
- **Total Cross-City Relationships:** 7,446 edges.
- **Total Cross-State Relationships:** 6,988 edges.
- **Top Observed Inter-City Corridors:**
  1. **Bengaluru $\leftrightarrow$ Delhi:** 2,238 edges (predominantly visual similarity and syndicated text).
  2. **Bengaluru $\leftrightarrow$ Mumbai:** 265 edges.
  3. **Delhi $\leftrightarrow$ Mumbai:** 206 edges.
  4. **Bengaluru $\leftrightarrow$ Thane:** 90 edges.
  5. **Delhi $\leftrightarrow$ Pune:** 88 edges.
  6. **Delhi $\leftrightarrow$ Thane:** 80 edges.
  7. **Bengaluru $\leftrightarrow$ Pune:** 62 edges.

*Note: Cross-city relationships reflect regional commercial supply chains, dealer cross-posting, and standardized manufacturer collateral, not evidence of cross-border scam operations.*

---

## 10. Connected Components & Overconnection Prevention

A central architectural requirement of Phase H is preventing **transitive graph collapse**.
- **The Pitfall of Naive Clustering:** If generic visual similarity candidates (DINO $\ge 0.70$) are included unconditionally in listing-to-listing connectivity, 1,756 listings collapse into a single giant component simply because stock photos of rectangular smartphones on white backgrounds cluster densely.
- **The Deterministic Solution:** Connected components in `relationship_components.parquet` are formed strictly from **direct observational reuse** (`MEDIA_EXACT_REUSE`, `MEDIA_PERCEPTUAL_REUSE_CANDIDATE`, `LISTING_TEXT_EXACT_REUSE`, `LISTING_TEXT_SIMILARITY_CANDIDATE`, `LISTING_SHARED_OCR_PHRASE`). Visual similarity candidates are preserved as independent edge attributes.

### Component Statistics (Direct Observational Reuse Graph):
- **Total Components:** 2,133
- **Singleton Components (isolated listings):** 1,867 (62.65%)
- **Non-Singleton Components:** 266 (37.35% of listings participate in $\ge 1$ relationship)
- **Largest Component:** 122 listings (a syndicated title and exact image reuse cluster)
- **Top 5 Component Sizes:** 122, 32, 24, 21, 21 listings.

---

## 11. Multi-Signal Relationships

Rather than relying on a single modality, multi-signal candidate pairs identify listings connected through **$\ge 2$ independent forensic layers**:
- **Total Multi-Signal Candidate Pairs:** 213 pairs
- **Breakdown by Evidence Layer Count:**
  - **4 Evidence Layers:** 5 pairs (e.g. Exact Image Reuse + Exact Title Reuse + Shared OCR Phrase + DINO Visual Similarity)
  - **3 Evidence Layers:** 63 pairs
  - **2 Evidence Layers:** 145 pairs

*Guardrail: The evidence count is an integer count of observed modalities. It is NOT weighted into an arbitrary risk score.*

---

## 12. Summary Metrics Table

| Metric Category | Parameter | Value |
| :--- | :--- | :---: |
| **Catalog Population** | Canonical Listings Evaluated | 2,980 |
| | Validated Local Media Assets | 2,491 |
| **Graph Topology** | Total Entity Nodes | 5,709 |
| | Total Relationship & Containment Edges | 21,395 |
| | Observational Relationship Edges | 12,791 |
| | Total Connected Components | 2,133 |
| | Non-Singleton Components | 266 |
| | Maximum Component Size | 122 listings |
| **Media Forensics** | Exact Binary Image Reuse (SHA-256) | 164 |
| | Perceptual Image Candidates (pHash $\le 10$) | 78 |
| | Deep Visual Similarity Candidates (DINO $\ge 0.70$) | 9,492 |
| **Text & OCR** | Exact Title Reuse | 2,182 |
| | High Lexical Overlap Candidates (Jaccard $\ge 0.75$) | 847 |
| | Distinctive Shared OCR Phrases | 28 |
| **Mobility Corridors** | Cross-City Observational Edges | 7,446 |
| | Cross-State Observational Edges | 6,988 |
| | Cross-Product Family Edges | 1,228 |
| **Multi-Modal Signals** | Candidate Pairs with $\ge 2$ Independent Signals | 213 |

---

## 13. Publication Figures

The following 8 publication-quality forensic figures were generated in `data/olx_analysis/reports/figures/`:
1. `43_relationship_type_distribution.png`: Frequency breakdown of all 10 edge types.
2. `44_connected_component_size_distribution.png`: Heavy-tailed log distribution of non-singleton components.
3. `45_image_reuse_distribution.png`: Comparative count of Exact SHA-256 vs. pHash vs. DINO candidates.
4. `46_text_similarity_distribution.png`: Pairwise Jaccard similarity score distribution.
5. `47_cross_city_relationships.png`: Top observed metropolitan relationship corridors.
6. `48_cross_state_relationships.png`: Top observed interstate relationship corridors.
7. `49_component_product_distribution.png`: Product family diversity across connected components.
8. `50_component_geography_distribution.png`: Geographic span (Single City vs. 2–3 Cities vs. 4+ Cities) per component.

---

## 14. Interactive HTML Dashboards

Four self-contained interactive dashboards were created:
1. [`image_reuse_network.html`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/image_reuse_network.html): Filterable media reuse table and perceptual network explorer answering all 8 forensic questions.
2. [`text_similarity_network.html`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/text_similarity_network.html): Side-by-side title comparison and distinctive OCR phrase inspector.
3. [`geographic_relationship_map.html`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/geographic_relationship_map.html): Inter-city corridor volume rankings and jurisdiction matrix.
4. [`relationship_graph.html`](file:///Users/nandinikhandelwal/Desktop/Codes/trustlens/relationship_graph.html): Master interactive Vis.js graph explorer with component selection, listing search, and evidence inspector.

---

## 15. Reproducibility & Integrity

- **Execution Command:** `.venv/bin/python scripts/run_network_intelligence.py`
- **Elapsed Runtime:** ~1.3 seconds
- **Test Suite:** `pytest tests/marketplace/test_network_intelligence.py` (10 passed in 0.89s)
- **Full Suite Status:** 97 passed, 1 skipped across the complete TrustLens repository.
- **Phase A–G.1 Immutability:** No frozen Parquet files from previous phases were modified.
