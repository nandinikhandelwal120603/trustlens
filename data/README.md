# TrustLens Data Directory & Privacy Policy

This directory contains ingested and processed marketplace data across different lifecycle stages.

## Directory Structure

```text
data/
├── raw/          # Raw, untouched payloads (source.json, HTML, images)
├── normalized/   # Cleaned, standardized JSONL and Parquet files
├── processed/    # Future multimodal features (OCR text, visual hashes, embeddings)
└── labels/       # Ground-truth fraud/risk annotations
```

## Data Governance & Privacy Rules

1. **NO Personal Identifiable Information (PII) in Git**:
   - `data/raw/`, `data/normalized/`, `data/processed/`, and `data/labels/` are strictly excluded in `.gitignore`.
   - Never commit raw scraped dumps, customer telephone numbers, or email addresses.
2. **Deterministic Salting**:
   - Phone numbers and emails are never logged in plain text.
   - When stored for deduplication, they are transformed using salted `HMAC-SHA256` (`HASH_SALT` in `.env`).
3. **Synthetic Data**:
   - Only synthetic and mock data located in `examples/` may be committed to version control.
   - Synthetic listings must be explicitly flagged with `"is_synthetic": true`.
4. **Permitted Sources**:
   - Only data from user submissions with consent, permitted research datasets, or authorized marketplace API endpoints may be processed.
