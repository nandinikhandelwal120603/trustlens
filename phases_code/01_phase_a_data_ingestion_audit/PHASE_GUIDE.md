# Phase 01 / Phase A — Marketplace Data Ingestion & Audit

## 1. Objectives & Invariant
Ingest raw search cards collected via Chrome extension across 3 core queries (iphone, macbook, ps5 controller). Enforce the invariant: 1 row = 1 canonical listing.

## 2. Included Python Modules
* `ingestion.py` — Ingestion pipeline parsing raw capture envelopes.
* `audit_engine.py` — Comprehensive data-quality audit engine.
* `media_downloader.py` — Local media acquisition engine.
* `models.py` — Core Pydantic marketplace data models.
* `run_marketplace_audit.py` — Executable runner script.

## 3. Authoritative Ledger Metrics
* 2,980 Canonical Listings (100% deduplicated, 0 duplicate IDs).
* 2,491 Media references (83.59% media availability).
* 2,323 Unique Apollo CDN image assets.
* 2,282 Downloaded image files (98.24% success rate).
* 2,280 Validated media cohort (2 corrupt files excluded).
