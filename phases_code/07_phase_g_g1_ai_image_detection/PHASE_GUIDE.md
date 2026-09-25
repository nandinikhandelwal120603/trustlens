# Phase 07 / Phase G & G.1 — Image Forensics & Dual AI Detection

## 1. Objectives
Audit EXIF/C2PA metadata provenance and benchmark generative AI synthetic image signals using two independent vision transformers.

## 2. Included Python Modules
* `image_authenticity.py` — EXIF metadata and C2PA inspection engine.
* `ai_image_detector.py` — Dual-detector consensus engine (ViT-Base & Swin-Base).
* `run_image_authenticity.py` & `run_ai_detector_pilot.py` — Executable runners.

## 3. Key Results
* C2PA / EXIF: 100% stripped by OLX Apollo CDN during WebP conversion.
* Dual-Detector Consensus (2,280 images):
  * 958 Mutual Real agreements.
  * 6 Mutual AI Candidates (commercial 3D renders / promotional flyers).
  * 559 Detector Disagreements (24.5% rate - Swin flagged AI while ViT scored Real).
  * Proves single-detector AI classification on compressed e-commerce photos is unreliable.
