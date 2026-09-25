# Phase 10 / Phase J — Multivariate Statistical Novelty Modeling

## 1. Objectives
Unsupervised Isolation Forest novelty modeling across 4 distinct feature spaces to isolate multivariate outliers without fraud ground truth.

## 2. Included Python Modules
* `anomaly_detection.py` — Isolation Forest engine, contamination sensitivity, PCA projection, and persistence analysis.
* `run_anomaly_analysis.py` — Executable runner script.

## 3. Key Results
* Evaluated 4 primary spaces at nominal contamination c=0.05 (149 outliers per space): Price, Price+Text, Price+Image, Full Multimodal.
* Persistence Analysis:
  * Inliers in all spaces: 2,574 listings (86.38%).
  * Flagged in 1 space: 270 listings (9.06%).
  * Persistent in 2 spaces: 88 listings (2.95%).
  * Persistent in 3 spaces: 45 listings (1.51%).
  * Persistent in ALL 4 spaces: 3 listings (0.10%).
* Guardrail: Anomaly score = statistical multivariate novelty, NOT fraud probability or guilt.
