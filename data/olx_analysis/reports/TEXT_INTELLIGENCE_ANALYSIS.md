# TrustLens — Text Normalization, Lexical Linguistics & Language-Pattern Report (Phase F)
## Deterministic Marketplace Corpus Lexical Intelligence

- **Generated At:** 2026-09-24T05:44:17.083596
- **Analysis Method:** Deterministic N-grams, Controlled Lexicons, Pure TF-IDF & Jaccard Overlap
- **Status:** COMPLETED & VERIFIED (Phase F)

---

## 1. Population & Text Availability Hierarchy

| Processing Stage | Entity Count | Percentage / Rate | Methodological Context |
| :--- | :---: | :---: | :--- |
| **Total Canonical Listings** | **2,980** | **100.0%** | Total deduplicated marketplace listings. |
| **Title Text Available** | **2,980** | **100.00%** | Non-null product listing titles from search cards. |
| **Description Text Available** | **0** | **0.00%** | Descriptions absent due to search-page capture methodology. |
| **Combined Usable Text** | **2,980** | **100.00%** | Listings with at least one non-empty text field for linguistic analysis. |

> **Methodological Note on Missing Descriptions:**
> All 2,980 listings in the current OLX corpus were captured directly from search-result cards (which display title, price, location, and thumbnail image, but omit full body descriptions). The text intelligence layer operates strictly on verified visible title text without hallucinating or imputing missing description content.

---

## 2. Corpus Lexical & Token Statistics

- **Total Corpus Tokens:** **20,293** (Mean: 6.81 tokens/listing, Median: 6)
- **Unique Lexical Vocabulary:** **1,637** unique word tokens
- **Extracted N-Gram Phrases ($df \ge 2$):** **3,947** total phrases
  - **Unigrams ($n=1$):** 737
  - **Bigrams ($n=2$):** 1,622
  - **Trigrams ($n=3$):** 1,588

---

## 3. Controlled Marketplace Lexicon Prevalences

| Lexical Category | Matching Listings | Corpus Prevalence (%) | Category Definition & Sample Keywords |
| :--- | :---: | :---: | :--- |
| **Warranty & Authenticity** | **628** | **21.07%** | `original`, `warranty`, `bill`, `invoice`, `sealed`, `gst`, `box pack` |
| **Condition Lexicon** | **684** | **22.95%** | `new`, `used`, `like new`, `mint`, `flawless`, `clean`, `refurbished` |
| **Transaction & Payment** | **86** | **2.89%** | `price`, `cash`, `fixed`, `negotiable`, `best price`, `exchange`, `emi` |
| **Urgency & Relocation** | **61** | **2.05%** | `urgent`, `immediate`, `today`, `urgently`, `relocation`, `need gone` |
| **Contact Redirection** | **357** | **11.98%** | `call`, `whatsapp`, `contact`, `message`, `dm`, `number` |
| **Clearance & Commercial** | **17** | **0.57%** | `shop`, `store`, `wholesale`, `dealer`, `stock`, `clearance` |
| **Company Claims** | **2** | **0.07%** | `company`, `official`, `corporate`, `office` |
| **Delivery & Logistics** | **8** | **0.27%** | `delivery`, `courier`, `transport`, `shipping`, `all india` |
| **Explicit Relocation** | **0** | **0.00%** | `relocation`, `shifting`, `moving`, `transfer`, `leaving` |

---

## 4. Text Reuse & Boilerplate Overlap Candidates (Status: UNVERIFIED)

| Candidate Type | Pairwise Candidate Count | Methodological Meaning |
| :--- | :---: | :--- |
| **`EXACT_TITLE_REUSE`** | **2,096** | Pairs of distinct listings sharing identical normalized title strings ($s = 1.0000$). |
| **`HIGH_TEXT_OVERLAP`** | **933** | Pairs of listings sharing $\ge 80\%$ Jaccard token overlap across distinct titles. |
| **Total Text Reuse Pairs** | **3,029** | **Observational candidate pairs for review (does not prove same seller or fraud).** |

---

## 5. Observed Script & Language Composition

- **Latin / English Script:** **2,977** listings (99.90%)
- **Mixed / Special Symbol Scripts:** **0** listings (0.00%)
- **Devanagari Script:** **1** listings (0.03%)

---

## 6. Analytical Parquet Artifacts

1. **`data/olx_processed/text_features.parquet`**: Listing-level text metadata and lexical category indicator columns (2,980 rows).
2. **`data/olx_processed/text_phrases.parquet`**: Corpus n-gram vocabulary with document/term frequencies (3,947 rows).
3. **`data/olx_processed/text_similarity_candidates.parquet`**: Pairwise text reuse candidate relationships (3,029 rows).
4. **`data/olx_analysis/reports/text_intelligence_gallery.html`**: Interactive gallery with privacy-redacted text previews.
