# TrustLens — Phase-by-Phase Codebase Navigation Directory

Welcome to the **Phase-Wise Code Directory** of TrustLens. This directory organizes every Python module, runner script, and analytical subsystem directly by pipeline phase, making it effortless to inspect, navigate, and execute any specific phase of the research without digging through markdown files.

---

## 🗺️ Master Pipeline Phase Roadmap

```text
phases_code/
│
├── 00_reddit_research_foundation/             <- Reddit research corpus (178 posts, 330 media, taxonomy)
│   ├── full_processor.py
│   ├── media_packager.py
│   ├── validator.py
│   └── PHASE_GUIDE.md
│
├── 01_phase_a_data_ingestion_audit/           <- Search-card ingestion, deduplication, 2,980 listings
│   ├── ingestion.py
│   ├── audit_engine.py
│   ├── media_downloader.py
│   ├── models.py
│   ├── run_marketplace_audit.py
│   └── PHASE_GUIDE.md
│
├── 02_phase_b_product_price_intelligence/     <- Taxonomy normalization, spec parser, median baselines
│   ├── product_normalizer.py
│   ├── product_rules.py
│   ├── product_taxonomy.py
│   ├── specification_parser.py
│   ├── condition_parser.py
│   ├── price_analysis.py
│   ├── run_price_analysis.py
│   └── PHASE_GUIDE.md
│
├── 03_phase_c_image_fingerprinting/           <- SHA-256 binary hash, pHash/dHash, 164 duplicate pairs
│   ├── image_fingerprinting.py
│   ├── media_fingerprint.py
│   ├── cluster.py
│   ├── run_image_fingerprints.py
│   └── PHASE_GUIDE.md
│
├── 04_phase_d_dino_visual_embeddings/         <- 384-d DINOv2 vision transformer, 9,492 visual pairs
│   ├── visual_embeddings.py
│   ├── similarity.py
│   ├── run_visual_embeddings.py
│   └── PHASE_GUIDE.md
│
├── 05_phase_e_multimodal_ocr/                 <- Tesseract 5.5 OCR packaging verification, 68 discrepancies
│   ├── multimodal_ocr.py
│   ├── run_multimodal_ocr.py
│   └── PHASE_GUIDE.md
│
├── 06_phase_f_text_intelligence/              <- N-grams, TF-IDF terms, WhatsApp redirection regexes
│   ├── text_intelligence.py
│   ├── text_normalizer.py
│   ├── pii_redactor.py
│   ├── run_text_intelligence.py
│   └── PHASE_GUIDE.md
│
├── 07_phase_g_g1_ai_image_detection/          <- EXIF/C2PA audit, dual ViT-Base & Swin-Base consensus
│   ├── image_authenticity.py
│   ├── ai_image_detector.py
│   ├── run_image_authenticity.py
│   ├── run_ai_detector_pilot.py
│   └── PHASE_GUIDE.md
│
├── 08_phase_h_relationship_network/           <- 5,709-node heterogeneous graph, 213 multi-signal pairs
│   ├── network_intelligence.py
│   ├── network_dashboards.py
│   ├── run_network_intelligence.py
│   └── PHASE_GUIDE.md
│
├── 09_phase_i_unified_feature_store/          <- Canonical 137-column listing-level feature store
│   ├── feature_store.py
│   ├── run_feature_store.py
│   └── PHASE_GUIDE.md
│
├── 10_phase_j_statistical_anomaly_detection/  <- Isolation Forest across 4 spaces, persistence analysis
│   ├── anomaly_detection.py
│   ├── run_anomaly_analysis.py
│   └── PHASE_GUIDE.md
│
└── 11_phase_k_final_evidence_synthesis/       <- Dataset ledger, review queue, executive infographic
    ├── final_synthesis.py
    ├── run_final_synthesis.py
    ├── generate_executive_graphic.py
    └── PHASE_GUIDE.md
```

---

## ⚡ Quick Execution Guide

Every phase directory includes an executable runner script. To run any phase independently:

```bash
# Phase A (Ingestion & Audit)
python phases_code/01_phase_a_data_ingestion_audit/run_marketplace_audit.py

# Phase B (Product & Price Intelligence)
python phases_code/02_phase_b_product_price_intelligence/run_price_analysis.py

# Phase C (Image Fingerprints)
python phases_code/03_phase_c_image_fingerprinting/run_image_fingerprints.py

# Phase D (DINOv2 Visual Similarity)
python phases_code/04_phase_d_dino_visual_embeddings/run_visual_embeddings.py

# Phase E (Multimodal OCR)
python phases_code/05_phase_e_multimodal_ocr/run_multimodal_ocr.py

# Phase F (Text Intelligence)
python phases_code/06_phase_f_text_intelligence/run_text_intelligence.py

# Phase G / G.1 (AI Image Detection)
python phases_code/07_phase_g_g1_ai_image_detection/run_image_authenticity.py

# Phase H (Relationship Network)
python phases_code/08_phase_h_relationship_network/run_network_intelligence.py

# Phase I (Feature Store)
python phases_code/09_phase_i_unified_feature_store/run_feature_store.py

# Phase J (Isolation Forest Novelty)
python phases_code/10_phase_j_statistical_anomaly_detection/run_anomaly_analysis.py

# Phase K (Final Evidence Synthesis)
python phases_code/11_phase_k_final_evidence_synthesis/run_final_synthesis.py
```

---

## 📊 Summary of Phase Deliverables

| Phase Folder | Primary Function | Key Output Parquet / Artifact |
| :--- | :--- | :--- |
| `00_reddit_research_foundation` | Reddit incident analysis | `dataset_intelligence_report.md` |
| `01_phase_a_data_ingestion_audit` | Deduplicated ingestion | `listings.parquet`, `media.parquet` |
| `02_phase_b_product_price_intelligence` | Normalization & pricing | `normalized_listings.parquet` |
| `03_phase_c_image_fingerprinting` | Cryptographic/pHash hashing | `fingerprints.parquet`, `image_relationships.parquet` |
| `04_phase_d_dino_visual_embeddings` | 384-d vision embeddings | `image_embeddings.parquet`, `deep_visual_relationships.parquet` |
| `05_phase_e_multimodal_ocr` | Packaging OCR checks | `image_ocr.parquet`, `multimodal_inconsistencies.parquet` |
| `06_phase_f_text_intelligence` | Lexical linguistics | `text_features.parquet`, `text_phrases.parquet` |
| `07_phase_g_g1_ai_image_detection` | Dual-detector ensemble | `ai_detector_results.parquet`, `image_authenticity.parquet` |
| `08_phase_h_relationship_network` | Graph topology engine | `relationship_edges.parquet`, `relationship_components.parquet` |
| `09_phase_i_unified_feature_store` | 137-col feature store | `unified_features.parquet` |
| `10_phase_j_statistical_anomaly_detection` | Novelty modeling | `anomaly_results.parquet`, `anomaly_persistence.parquet` |
| `11_phase_k_final_evidence_synthesis` | Evidence synthesis | `multi_signal_evidence.parquet`, `research_review_queue.parquet` |
