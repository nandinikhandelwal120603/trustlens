# Phase 04 / Phase D — DINOv2 Deep Visual Similarity

## 1. Objectives
Extract 384-dimensional dense visual representations using foundation vision transformer (dinov2_vits14) to capture semantic visual affinity invariant to camera angles and lighting.

## 2. Included Python Modules
* `visual_embeddings.py` — DINOv2 inference engine and PyTorch batching pipeline.
* `similarity.py` — Cosine similarity calculation and nearest-neighbor search.
* `run_visual_embeddings.py` — Executable runner script.

## 3. Key Results
* Extracted dense embeddings across all 2,280 media assets.
* 9,492 candidate visual relationships identified (cosine similarity >= 0.70).
* Successfully captured pose/lighting variations where cryptographic and perceptual hashes failed.
