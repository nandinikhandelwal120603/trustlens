# TrustLens: Multimodal Marketplace Fraud Intelligence

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Tests: 124 passed](https://img.shields.io/badge/tests-124%20passed-brightgreen.svg)](tests/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Complete Research Dataset](https://img.shields.io/badge/Full%20Data-trustlens--full-purple.svg)](https://github.com/nandinikhandelwal120603/trustlens-full)

> **An evidence-based multimodal research system investigating deceptive patterns, cross-market image reuse, multimodal contradictions, and statistical novelty in online classifieds (OLX India).**

---

## 🌟 Quick Links & Navigation

* 📖 **[Super Master Document](TRUSTLENS_SUPER_MASTER_DOCUMENT.md)** — Complete 18-section end-to-end chronicle (Reddit foundation to Phase K).
* 📑 **[Final Research Report](FINAL_TRUSTLENS_RESEARCH_REPORT.md)** — Authoritative evidence synthesis & methodology.
* 📊 **[Empirical Marketplace Findings](MARKETPLACE_FINDINGS.md)** — Verified observations, dispersion metrics & guardrails.
* 💻 **[Phase-Wise Code Structure (`phases_code/`)](phases_code/README.md)** — Self-contained directories (Phases 00–11) with runners and guides.
* 🕷️ **Scrapers & Acquisition Tools**:
  * **[OLX Chrome Extension (`capture-olx/`)](capture-olx/README.md)** — Manifest V3 client-side listing & search feed extractor.
  * **[Reddit Complaint Scraper (`scripts/scrape_reddit_complaints.py`)](scripts/scrape_reddit_complaints.py)** — Public subreddit scam report collector.
* 📈 **[Visual Assets Catalogue (`all_graphs_and_images/`)](all_graphs_and_images/VISUAL_CATALOGUE.md)** — 83 publication figures + 10 interactive dashboards.
* 🚀 **[Interactive Showcase & Demo (`showcase/`)](showcase/README.md)** — 10-screen visual storytelling web app.
* 💾 **[Full Research Vault (`trustlens-full`)](https://github.com/nandinikhandelwal120603/trustlens-full)** — Complete 120MB raw multimodal dataset (2,280 image assets, 178 Reddit complaint posts, raw Parquet feature stores).

---

## 1. Core Research Philosophy

TrustLens is an **evidence-based marketplace fraud intelligence system**. It explicitly rejects black-box "scam scores" and subjective fraud probabilities. Instead, it operates on a rigorous **Evidence Hierarchy**:

* **OBSERVED:** Directly visible, byte-verifiable data (e.g. identical SHA-256 image hashes, exact title string equality).
* **DERIVED:** Deterministically calculated from observations (e.g. price z-score, distance from category median).
* **CANDIDATE:** Model-identified hypotheses requiring human triage (e.g. DINOv2 cosine similarity $\ge 0.70$, OCR packaging text mismatches).
* **UNVERIFIED / UNKNOWN:** Factors unobserved in public search captures (e.g. seller legal identity, criminal intent, transaction outcome).

> **Scientific Guardrail:** An anomaly is **NOT** a scam. High statistical novelty and cross-city media reuse represent candidate investigation triggers for marketplace trust teams, not automated accusations.

---

## 2. Key Empirical Findings (At a Glance)

Evaluated across **2,980 canonical OLX India listings** across 3 targeted consumer hardware queries (`iphone`, `macbook`, `ps5 controller`):

* 🖼️ **78.0% Cross-City Image Mobility:** 164 pairwise instances of byte-for-byte identical image reuse (SHA-256); nearly 4 out of 5 spanned different cities and states (e.g. Delhi to Bengaluru, Thane to Mumbai).
* 🔤 **22.35% Exact Title Duplication:** 666 listings used verbatim, repeated title templates; 52.6% contained aggressive condition claims (*"mint condition"*, *"sealed pack"*).
* 📞 **3.09% Out-of-Band Redirection:** 92 listings embedded phone numbers or WhatsApp strings in titles to divert buyers off-platform.
* 📦 **Multimodal Packaging Contradictions:** Local OCR extracted text from 82.68% of images, discovering:
  * 1 direct **model mismatch** (title claimed *"iPhone 13 128"*, while packaging box OCR confirmed *"iPhone 13 Mini"*).
  * 1 **activation lock screen** (*"ACTIVATION LOCK"* visible on display).
  * 66 instances of **shared-image claim drift** (divergent storage/pricing on identical photos).
* 🤖 **The Single AI Detector Fallacy:** Evaluated across dual Vision Transformers (ViT-Base and Swin-Base). While 958 images agreed real (42.0%) and only 6 were mutual AI candidates (0.26%; graphic flyers, not deepfakes), **559 images caused detector disagreement (24.5%)**, proving single AI detectors produce unacceptable false-positive rates on classified imagery.
* 🌐 **5,709-Node Entity Graph:** 21,395 relationship edges formed 2,133 components. The largest component (`COMP-001`) linked **122 listings across 14 cities** via shared templates, images, and text.
* 🎯 **213 Multi-Signal Corroborated Pairs:** Exactly 213 listing pairs were corroborated across $\ge 2$ independent forensic layers (with 5 pairs corroborated across 4 distinct layers).

---

## 3. Architecture & Pipeline Overview

```text
[ Reddit Scam Foundation ] ──▶ [ Targeted OLX Data Capture ]
   (178 Posts, 330 Media)          (2,980 Canonical Listings)
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               MULTIMODAL FORENSIC ENGINE                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  Phase B: Product Normalization & Price Baseline Modeling (81 Canonical Categories)   │
│  Phase C: Cryptographic (SHA-256) & Perceptual Image Fingerprinting (pHash/dHash)     │
│  Phase D: Deep Visual Embeddings & Semantic Similarity (DINOv2 ViT-B/14)               │
│  Phase E: Multimodal Packaging OCR & Cross-Modal Consistency Engine (Tesseract)       │
│  Phase F: Text Intelligence, Lexical Linguistics & Urgency Extraction                 │
│  Phase G/G.1: Image Authenticity, Dual AI Consensus & Spectral FFT Analysis            │
│  Phase H: Relationship Network Intelligence & Graph Topology (NetworkX)                │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              EVIDENCE SYNTHESIS & MODELING                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  Phase I: Unified Multimodal Feature Store (2,980 Rows × 137 Validated Columns)       │
│  Phase J: Multivariate Statistical Novelty Modeling (Isolation Forests across 4 spaces)│
│  Phase K: Multi-Signal Evidence Synthesis & Prioritized Investigator Review Queue     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Phase-Wise Code Navigation

All source code has been structured phase-by-phase inside [`phases_code/`](phases_code/README.md) for effortless browsing:

| Phase Directory | Focus Area | Key Modules |
| :--- | :--- | :--- |
| **[`00_reddit_research_foundation/`](phases_code/00_reddit_research_foundation/)** | Problem Foundation | `reddit_scraper.py`, `full_processor.py`, `media_packager.py`, `validator.py` |
| **[`01_phase_a_data_ingestion_audit/`](phases_code/01_phase_a_data_ingestion_audit/)** | Ingestion & Quality | `data_audit.py`, `ingest.py`, `schemas.py` |
| **[`02_phase_b_product_price_intelligence/`](phases_code/02_phase_b_product_price_intelligence/)** | Price Baselines | `price_analysis.py`, `normalizer.py`, `taxonomy.py` |
| **[`03_phase_c_image_fingerprinting/`](phases_code/03_phase_c_image_fingerprinting/)** | Media Hashing | `image_fingerprints.py`, `hasher.py` |
| **[`04_phase_d_dino_visual_embeddings/`](phases_code/04_phase_d_dino_visual_embeddings/)** | Deep Vision | `visual_embeddings.py`, `dinov2_extractor.py` |
| **[`05_phase_e_multimodal_ocr/`](phases_code/05_phase_e_multimodal_ocr/)** | Packaging OCR | `multimodal_ocr.py`, `ocr_engine.py` |
| **[`06_phase_f_text_intelligence/`](phases_code/06_phase_f_text_intelligence/)** | Lexical NLP | `text_intelligence.py`, `linguistics.py` |
| **[`07_phase_g_g1_ai_image_detection/`](phases_code/07_phase_g_g1_ai_image_detection/)** | AI Forensics | `ai_image_detector.py`, `consensus_engine.py` |
| **[`08_phase_h_relationship_network/`](phases_code/08_phase_h_relationship_network/)** | Entity Graph | `relationship_network.py`, `graph_builder.py` |
| **[`09_phase_i_unified_feature_store/`](phases_code/09_phase_i_unified_feature_store/)** | Feature Store | `feature_store.py`, `schema_validator.py` |
| **[`10_phase_j_statistical_anomaly_detection/`](phases_code/10_phase_j_statistical_anomaly_detection/)** | Novelty Modeling | `anomaly_detection.py`, `isolation_forest.py` |
| **[`11_phase_k_final_evidence_synthesis/`](phases_code/11_phase_k_final_evidence_synthesis/)** | Evidence Synthesis | `final_synthesis.py`, `review_queue.py` |

---

## 5. Getting Started

### Prerequisites
* Python 3.11+
* Tesseract OCR (`brew install tesseract` on macOS / `apt install tesseract-ocr` on Linux)

### Installation
```bash
# Clone the repository
git clone https://github.com/nandinikhandelwal120603/trustlens.git
cd trustlens

# Create virtual environment & install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Running the Scrapers

#### 1. Reddit Scam Complaint Scraper
```bash
# Scrape live public fraud reports from Indian subreddits
python scripts/scrape_reddit_complaints.py --query "olx scam" --limit-per-sub 25 --output data/scraped_complaints.json
```

#### 2. OLX Marketplace Capture Extension
1. Open Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** (top-right).
3. Click **Load unpacked** and select the [`capture-olx`](capture-olx/) folder.
4. Browse OLX India, click the extension icon, and click **Capture**.
5. See [`capture-olx/README.md`](capture-olx/README.md) for full instructions.

### Running Tests
```bash
# Execute the complete test suite (124 tests)
pytest tests/
```

### Launching the Showcase Web App
```bash
open showcase/demo/index.html
```

---

## 6. Repository Scope & Full Data Link

To keep this repository clean, lightweight (~23 MB), and easy for recruiters and open-source contributors to navigate, the 2,280 downloaded raw listing images and large raw crawl archives are maintained in a dedicated research dataset repository:

👉 **[https://github.com/nandinikhandelwal120603/trustlens-full](https://github.com/nandinikhandelwal120603/trustlens-full)**

---

## 7. License

Distributed under the Apache 2.0 License. See [`LICENSE`](LICENSE) for details.
