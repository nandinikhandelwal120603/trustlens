# TrustLens — Unified Visual & Graphical Asset Catalogue

A complete, structured inventory of all publication figures, architecture diagrams, infographics, and interactive dashboards generated throughout the TrustLens research pipeline.

---

## 1. Directory Structure

```text
all_graphs_and_images/
│
├── infographics_and_architecture/
│   ├── trustlens_architecture.svg                 <- High-fidelity vector architecture diagram
│   └── trustlens_architecture_and_results.png     <- 1920x1080 executive infographic slide
│
├── interactive_dashboards/
│   ├── final_research_dashboard.html              <- Master Phase K research exploration dashboard
│   ├── relationship_graph.html                    <- 5,709-node network visualization
│   ├── image_reuse_network.html                   <- Cryptographic SHA-256 reuse graph
│   ├── text_similarity_network.html               <- Lexical text similarity candidate graph
│   ├── geographic_relationship_map.html           <- Cross-city & cross-state mobility corridor map
│   ├── ai_detector_gallery.html                   <- Dual-detector AI image consensus gallery
│   ├── image_forensics_gallery.html               <- Metadata, EXIF, and C2PA provenance gallery
│   ├── multimodal_ocr_gallery.html                <- Tesseract OCR text extraction gallery
│   ├── text_intelligence_gallery.html             <- Lexical N-gram & TF-IDF keyword gallery
│   └── visual_gallery.html                        <- DINOv2 visual neighbor gallery
│
└── publication_figures/                           <- 83 Publication-grade PNG charts (Figures 01 to 73 + extra)
```

---

## 2. Interactive Dashboards Catalogue

| Dashboard File | Core Focus | Key Analytical Value |
| :--- | :--- | :--- |
| [`final_research_dashboard.html`](interactive_dashboards/final_research_dashboard.html) | Master Executive Overview | Unified dashboard spanning all 11 phases with tabbed navigation and metrics |
| [`relationship_graph.html`](interactive_dashboards/relationship_graph.html) | Network Intelligence (Phase H) | Interactive 5,709-node entity graph with 21,395 edges across 2,133 components |
| [`image_reuse_network.html`](interactive_dashboards/image_reuse_network.html) | Image Reuse Clusters (Phase C) | Visualizes the 164 exact duplicate image pairs across Indian metropolitan markets |
| [`text_similarity_network.html`](interactive_dashboards/text_similarity_network.html) | Linguistic Similarity (Phase F) | High lexical overlap candidate pairs (Jaccard similarity $\ge 0.75$) |
| [`geographic_relationship_map.html`](interactive_dashboards/geographic_relationship_map.html) | Geographic Corridors (Phase H) | Interactive map of 7,446 cross-city and 6,988 cross-state observational edges |
| [`ai_detector_gallery.html`](interactive_dashboards/ai_detector_gallery.html) | Synthetic Image Evaluation (G.1) | Dual-detector consensus gallery (ViT-Base vs Swin-Base across 2,280 images) |
| [`multimodal_ocr_gallery.html`](interactive_dashboards/multimodal_ocr_gallery.html) | OCR Claim Checks (Phase E) | 68 candidate packaging-vs-title inconsistencies extracted by Tesseract |
| [`visual_gallery.html`](interactive_dashboards/visual_gallery.html) | Deep Vision Embeddings (Phase D) | 384-dimensional DINOv2 nearest neighbor clusters across angles and lighting |
| [`text_intelligence_gallery.html`](interactive_dashboards/text_intelligence_gallery.html) | Lexical Intelligence (Phase F) | N-gram frequencies, TF-IDF distinctiveness, and contact-redirection cues |
| [`image_forensics_gallery.html`](interactive_dashboards/image_forensics_gallery.html) | Image Authenticity (Phase G) | EXIF, C2PA, and compression artifact inspections |

---

## 3. Publication Figures Roadmap (Figures 01 to 73)

### Phase B — Product Normalization & Price Intelligence
* `01_search_query_composition.png` — Search query distribution (`iphone` 78.4%, `macbook` 13.2%, `ps5 controller` 8.4%).
* `02_product_category_distribution.png` — Category taxonomy breakdown across smartphone, laptop, accessory.
* `03_brand_distribution.png` — Brand composition across Apple, Sony, Samsung, etc.
* `04_top_normalized_models.png` — Top normalized models (iPhone 13, iPhone 15, iPhone 14, MacBook Air, DualSense).
* `05_price_distribution_by_major_group.png` — Price boxplots across major hardware categories.
* `06_price_distribution_comparable_models.png` — Price dispersion within normalized hardware families.
* `07_price_delta_threshold_analysis.png` — Evaluation of the -35% and -50% price discount thresholds.
* `08_query_contamination_accessory_noise.png` — Isolation of ₹100–₹500 accessories from device medians.

### Phase C — Cryptographic & Perceptual Image Fingerprinting
* `09_hamming_distance_distribution.png` — Distribution of normalized pHash Hamming distances ($d \le 10$).
* `10_threshold_sensitivity_curve.png` — Perceptual hash threshold sensitivity analysis.
* `11_top_image_cluster_sizes.png` — Cluster size distribution for exact SHA-256 and pHash image reuse.

### Phase D — Deep Visual Embeddings (DINOv2)
* `12_dino_similarity_distribution.png` — Cosine similarity distribution across 384-d dense embeddings.
* `13_nn_rank_similarity_decay.png` — Nearest neighbor similarity decay curves.
* `14_exact_vs_perceptual_dino_validation.png` — Cross-validation between SHA-256, pHash, and DINOv2.
* `15_dino_threshold_sensitivity_curve.png` — Sensitivity sweep for cosine threshold $\ge 0.70$.
* `16_cross_listing_visual_similarity_breakdown.png` — Visual similarity pairs across different listings.
* `17_cross_city_visual_relationships_matrix.png` — Visual similarity matrix linking major metropolitan markets.
* `18_phash_vs_dino_scatter_disagreement.png` — Scatter plot contrasting pHash distance against DINO cosine similarity.
* `19_visual_candidates_price_spread_distribution.png` — Price dispersion between visually similar listings.

### Phase E — Multimodal OCR & Packaging Claim Consistency
* `20_ocr_status_distribution.png` — OCR yield across 2,280 assets (82.7% text-positive, 17.3% no text).
* `21_ocr_confidence_distribution.png` — Confidence score distribution for Tesseract extractions.
* `22_ocr_length_distribution.png` — Character and token count distributions for extracted text.
* `23_inconsistency_categories.png` — Breakdown of the 68 inconsistencies (66 drift, 1 model mismatch, 1 demo lock).
* `24_preprocessing_variant_selection.png` — Evaluation of image binarization and thresholding variants.

### Phase F — Text Intelligence & Lexical Patterns
* `25_text_availability.png` — Title availability across canonical listings (100% available).
* `26_token_count_distribution.png` — Token and character length distributions across listing titles.
* `27_lexical_categories_distribution.png` — Condition, warranty, urgency, and clearance cue frequencies.
* `28_top_unigrams.png` — Highest frequency unigram tokens.
* `29_top_bigrams.png` — Highest frequency bigram collocations.
* `30_top_trigrams.png` — Highest frequency trigram phrases.
* `31_tfidf_distinctive_terms.png` — Distinctive vocabulary terms ranked by TF-IDF across categories.
* `32_lexical_frequency_by_group.png` — Vocabulary frequency conditioned on product family.
* `33_text_reuse_distribution.png` — Distribution of exact title duplication (666 listings with shared titles).
* `34_script_distribution.png` — Latin, Devanagari, and alphanumeric script analysis.
* `35_price_band_lexicon_heatmap.png` — Cross-tabulation of lexical cues across price quartiles.

### Phase G & G.1 — Image Authenticity & Dual AI Image Detection
* `36_image_type_distribution.png` — Image classification (Photos, Screenshots, Text-Heavy, Document-Like).
* `37_c2pa_presence.png` — C2PA cryptographic provenance inspection (0% present in OLX WebP conversions).
* `38_exif_metadata_presence.png` — EXIF metadata stripping audit by OLX Apollo CDN.
* `39_detector_score_distribution.png` — Score distribution for ViT-Base and Swin-Base detectors.
* `40_detector_status_distribution.png` — Classification status distribution across the cohort.
* `41_detector_agreement.png` — 4-quadrant agreement breakdown (958 real, 6 AI, 559 disagreement, 757 borderline).
* `42_status_by_image_type.png` — AI candidate rate conditioned on image type.
* `fig_detector_agreement_matrix.png` — Confusion/agreement matrix between ViT and Swin.
* `fig_detector_correlation_scatter.png` — Scatter plot showing inter-model correlation.
* `fig_score_stability_recompression.png` — Robustness evaluation against JPEG/WebP recompression.

### Phase H — Relationship Network Intelligence
* `43_relationship_type_distribution.png` — Breakdown of the 21,395 graph edges.
* `44_connected_component_size_distribution.png` — Cluster size distribution across 2,133 components.
* `45_image_reuse_distribution.png` — Network degree distribution for shared image nodes.
* `46_text_similarity_distribution.png` — Distribution of lexical title edges.
* `47_cross_city_relationships.png` — 7,446 cross-city edges connecting metropolitan regions.
* `48_cross_state_relationships.png` — 6,988 cross-state edges connecting Indian states.
* `49_component_product_distribution.png` — Product composition within multi-listing components.
* `50_component_geography_distribution.png` — Geographic dispersion of clusters.

### Phase J — Multivariate Statistical Novelty Modeling
* `51_price_anomaly_distribution.png` — Score distribution for `J_PRICE` Isolation Forest.
* `52_price_text_anomaly_distribution.png` — Score distribution for `J_PRICE_TEXT`.
* `53_price_image_anomaly_distribution.png` — Score distribution for `J_PRICE_IMAGE`.
* `54_full_multimodal_anomaly_distribution.png` — Score distribution for `J_FULL_MULTIMODAL`.
* `55_anomaly_counts_across_experiments.png` — Nominal 5% anomaly counts (149 outliers per experiment).
* `56_experiment_overlap_jaccard_matrix.png` — Jaccard similarity matrix across the 4 feature spaces.
* `57_anomaly_persistence_distribution.png` — Persistence: 2,574 (0 exps), 270 (1 exp), 88 (2), 45 (3), 3 (all 4).
* `58_contamination_sensitivity.png` — Contamination sensitivity across $c \in [0.01, 0.02, 0.05, 0.10]$.
* `59_pca_feature_space_visualization.png` — 2D PCA projection of the 85-feature multimodal space.
* `60_anomaly_frequency_by_product.png` — Anomaly rates across normalized product models with explicit denominators.
* `61_anomaly_frequency_by_geography.png` — Anomaly rates across Indian cities with explicit denominators.

### Phase K — Final Synthesis & Public Showcase
* `62_dataset_population_funnel.png` — Authoritative population funnel: 2,980 events $\rightarrow$ 2,280 images.
* `63_product_category_composition.png` — Query and normalized product family shares.
* `64_price_distribution_by_normalized_product.png` — Comparable-model price distributions with median lines.
* `65_text_reuse_landscape.png` — Exact title reuse and lexical cue presence.
* `66_image_reuse_landscape.png` — Exact SHA-256 reuse vs. pHash vs. DINOv2 visual similarity.
* `67_multimodal_evidence_relationships.png` — Tesseract OCR yield and 68 discrepancy categories.
* `68_ai_detector_agreement_disagreement.png` — Two-detector raw score agreement landscape and consensus zones.
* `69_network_relationship_overview.png` — Heterogeneous graph edge composition across 5,709 nodes.
* `70_statistical_anomaly_experiment_overlap.png` — Nominal novelty counts across 4 Isolation Forest spaces.
* `71_anomaly_persistence.png` — Multi-space persistence distribution.
* `72_multi_signal_evidence_distribution.png` — Multi-signal pair breakdown across 2, 3, and 4 evidence layers (213 total).
* `73_geographic_observation_map.png` — Observed listings and anomaly rates across Indian metropolitan hubs.
