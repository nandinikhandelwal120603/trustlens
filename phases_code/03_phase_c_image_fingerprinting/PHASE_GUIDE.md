# Phase 03 / Phase C — Cryptographic & Perceptual Image Fingerprinting

## 1. Objectives
Dual-level visual fingerprinting using exact cryptographic hashes and perceptual Hamming distance clustering.

## 2. Included Python Modules
* `image_fingerprinting.py` — Computes SHA-256, pHash, dHash, and aHash fingerprints.
* `media_fingerprint.py` — Image fingerprint data models.
* `cluster.py` — Hamming distance clustering engine (threshold d <= 10).
* `run_image_fingerprints.py` — Executable runner script.

## 3. Key Results
* 164 pairwise instances of exact binary image reuse (SHA-256) across 242 listings.
* 78.0% of identical image pairs spanned different metropolitan cities (cross-market syndication).
* 78 candidate perceptual similarity pairs (pHash).
