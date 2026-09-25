# Phase 06 / Phase F — Text Intelligence & Lexical Linguistics

## 1. Objectives
Deterministic lexical intelligence across listing titles without black-box sentiment or fraud scores.

## 2. Included Python Modules
* `text_intelligence.py` — N-gram tokenization, TF-IDF distinctiveness, and phrase matching.
* `text_normalizer.py` — Text cleaning and normalization.
* `pii_redactor.py` — Redaction of sensitive phone digits and identifiers.
* `run_text_intelligence.py` — Executable runner script.

## 3. Key Results
* 666 listings (22.3%) exhibited exact title duplication with other listings.
* Identified 92 instances of contact-redirection cues ('WhatsApp only', embedded phone numbers).
* Mapped condition cues (52.6%) and warranty cues (14.2%) across all 2,980 listings.
