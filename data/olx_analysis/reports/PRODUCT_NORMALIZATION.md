# TrustLens — Product Normalization Report (Phase B)
## Deterministic Entity & Specification Classification for OLX Marketplace Corpus

- **Generated At:** 2026-09-21T18:59:34.907778
- **Total Canonical Listings:** 2,980
- **Artifact:** `data/olx_processed/normalized_listings.parquet`

---

## 1. Overall Product Recognition Breakdown

| Entity Classification | Count | % Share | Research Meaning |
| :--- | :---: | :---: | :--- |
| **Primary Devices (`device`)** | **2,864** | **96.11%** | Actual smartphone, laptop, or gaming console hardware. |
| **Accessories & Parts (`accessory/case/part`)** | **116** | **3.89%** | Cases, covers, chargers, cables, screen protectors, dummy boxes, and replacement parts. |

---

## 2. Query Match Classification (Contamination Analysis)

Why search queries cannot be used as ground-truth product labels:

| Query Match Status | Count | % Share | Description |
| :--- | :---: | :---: | :--- |
| **`direct_match`** | **2,365** | **79.36%** | Listing directly represents the target hardware family. |
| **`related_accessory`** | **85** | **2.85%** | Listing represents an accessory or case for the searched product. |
| **`different_product`** | **16** | **0.54%** | Listing represents an entirely different brand/product in the search feed. |
| **`ambiguous`** | **235** | **7.89%** | Title lacks specific model tokens (e.g. "phone available best price"). |
| **`unknown`** | **279** | **9.36%** | Unclassified listing text. |

---

## 3. Product Category & Brand Hierarchy

### Categories
| Category | Count | % Share |
| :--- | :---: | :---: |
| **Smartphone** | 1,986 | 66.64% |
| **Laptop** | 380 | 12.75% |
| **Unknown** | 279 | 9.36% |
| **Gaming Accessory** | 240 | 8.05% |
| **Accessory** | 85 | 2.85% |
| **Gaming Console** | 10 | 0.34% |

### Top Brands
| Brand | Count | % Share |
| :--- | :---: | :---: |
| **Apple** | 2,210 | 74.16% |
| **Unknown** | 279 | 9.36% |
| **Sony** | 250 | 8.39% |
| **Generic / Other** | 236 | 7.92% |
| **Samsung** | 5 | 0.17% |
