# Phase 02 / Phase B — Product Taxonomy & Price Intelligence

## 1. Objectives
Deterministic regex-based taxonomy normalization and comparable-model price benchmarking.

## 2. Included Python Modules
* `product_normalizer.py` — Normalizes titles into structured attributes (Brand, Model, Generation, Storage, RAM).
* `product_rules.py` & `product_taxonomy.py` — Deterministic taxonomy rules.
* `specification_parser.py` & `condition_parser.py` — Extracts storage, battery health, and condition cues.
* `price_analysis.py` — Price median baseline modeling and outlier threshold evaluation (< -35%, < -50%).
* `run_price_analysis.py` — Executable runner script.

## 3. Key Results
* Cleaned 2,980 listings into normalized models (e.g. 350 iPhone 13; median ₹38,500).
* Isolated 33 pure accessory listings (e.g. ₹200 phone cases) to prevent artificial price deflation.
* Evaluated -35% outlier threshold, capturing ~10–14% of the market tail without drowning human reviewers.
