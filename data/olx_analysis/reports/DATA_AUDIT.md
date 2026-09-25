# TrustLens — Marketplace Data Audit (Phase A)
## Empirical Ingestion & Data-Quality Report for OLX Marketplace Captures

- **Generated At:** 2026-09-21T18:38:46.157142
- **Source Vault:** `data/olx_raw/`
- **Analytical Tables:** `data/olx_processed/`
- **Status:** COMPLETED (Phase A)

---

## 1. Core Dataset Entities & Dimensions

In strict adherence to methodology, we rigorously separate **observation events** (each recorded listing instance per capture run) from **unique canonical listings** and **unique media assets**:

| Dimension | Count | Note / Description |
| :--- | :---: | :--- |
| **Total Raw JSON Files** | **6** | Total export files in `olx output/` |
| **Unique Raw JSON Files** | **5** | Unique capture archives (deduplicated by SHA-256) |
| **Duplicate Raw Files** | **1** | Exact byte-for-byte duplicate exports |
| **Total Capture Batches** | **5** | Capture envelopes parsed across unique files |
| **Total Observations (`observation_count`)** | **2,980** | Total listing observation events across all captures |
| **Unique Canonical Listings (`unique_listing_count`)** | **2,980** | Distinct listing IDs / URLs in corpus |
| **Repeat Observation Instances** | **0** | Multi-capture observations of the same listing |
| **Unique Apollo Media Assets (`unique_media_count`)** | **2,323** | Unique Apollo file IDs (`2,491` total media references) |

### Raw File Deduplication
Found **1** exact duplicate raw file(s):
- `trustlens_olx_iphone_2026-09-21T17-11-28.json` (identical SHA-256 to `trustlens_olx_iphone_2026-09-21T17-11-28 copy.json`)

---

## 2. Product Class & Search Query Breakdown

| Search Query | Total Observations | % Share | Category ID |
| :--- | :---: | :---: | :---: |
| `iphone` | 2,337 | 78.42% |
| `macbook` | 393 | 13.19% |
| `ps5 controller` | 250 | 8.39% |

---

## 3. Data Completeness & Missing-Rate Metrics

| Field / Attribute | Missing Count | Missing % | Available % | Research Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **Listing Title** | 0 | **0.0%** | 100.00% | Full title text successfully extracted across all cards. |
| **Numeric Price** | 1 | **0.03%** | 99.97% | Highly complete price normalization; exactly 1 listing unpriced. |
| **Geographic Location** | 579 | **19.43%** | 80.57% | 579 cards omitted locality in feed; 2,401 cards contain full locality. |
| **Image Media** | 489 | **16.41%** | 83.59% | 2,491 listings have rendered Apollo image URLs; 489 lazy-loaded. |
| **Description Text** | 2980 | **100.00%** | 0.00% | Expected limitation: Search feeds render snippets only; full text requires listing page. |
| **Seller Profile Name** | 2980 | **100.00%** | 0.00% | Expected limitation: OLX search cards omit seller metadata; requires listing page. |

---

## 4. UI Indicators & Marketplace Badges

| Badge Type | Listings with Badge | Badge % |
| :--- | :---: | :---: |
| **`featured`** (Promoted Listings) | **371** | **12.45%** |
| **`verified`** (Verified Seller Badge) | **0** | **0.0%** |
| **`elite`** (Elite Dealer Badge) | **0** | **0.0%** |

---

## 5. Geographic Coverage & Confidence

Locations are resolved into a hierarchical representation (`location_raw`, `city`, `state`, `country`, `geography_confidence`, `geography_source`):

- **High Confidence** (Matched verified city/state index): **2,280 listings (76.5%)**
- **Medium Confidence** (Parsed trailing locality token): **121 listings (4.1%)**
- **Unknown Location** (Unspecified in card): **579 listings (19.4%)**

### Top States by Listing Density

| State | Listing Count | % Share |
| :--- | :---: | :---: |
| **Karnataka** | 943 | 31.64% |
| **Delhi** | 939 | 31.51% |
| **Maharashtra** | 286 | 9.6% |
| **Tamil Nadu** | 23 | 0.77% |
| **Uttar Pradesh** | 18 | 0.6% |
| **Telangana** | 14 | 0.47% |
| **Haryana** | 14 | 0.47% |
| **Punjab** | 9 | 0.3% |
| **West Bengal** | 8 | 0.27% |
| **Gujarat** | 6 | 0.2% |
| **Madhya Pradesh** | 5 | 0.17% |
| **Kerala** | 5 | 0.17% |

### Top Metropolitan Cities

| City | Listing Count | % Share |
| :--- | :---: | :---: |
| **Bengaluru** | 943 | 31.64% |
| **Delhi** | 939 | 31.51% |
| **Mumbai** | 127 | 4.26% |
| **Pune** | 41 | 1.38% |
| **Thane** | 34 | 1.14% |
| **Navi Mumbai** | 20 | 0.67% |
| **Nagpur** | 20 | 0.67% |
| **Chennai** | 18 | 0.6% |
| **Aurangabad** | 16 | 0.54% |
| **Hyderabad** | 14 | 0.47% |
| **Nashik** | 13 | 0.44% |
| **Gurgaon** | 8 | 0.27% |
| **Bhiwandi** | 6 | 0.2% |
| **Maharashtra** | 6 | 0.2% |
| **Kolkata** | 6 | 0.2% |

---

## 6. Price Distribution Overview

- **Sample Size (Priced Listings):** 2,979
- **Price Range:** ₹150 → ₹650,000
- **Median Price:** **₹37,999**
- **Mean Price:** ₹48,341

---

## 7. Analytical Parquet Artifacts

The analytical vault is structured for high-performance vectorized operations:

1. **`data/olx_processed/observations.parquet`**: Contains all `2,980` individual observation events with capture timestamps, search queries, and raw/normalized fields.
2. **`data/olx_processed/listings.parquet`**: Contains `2,980` unique canonical listings with temporal observation spans (`first_seen_at`, `last_seen_at`, `observation_count`).
3. **`data/olx_processed/media.parquet`**: Contains all `2,491` media asset records with Apollo file IDs and image URLs.
