# TrustLens — Media Fingerprinting & Perceptual Mapping Report (Phase C)
## Multi-Level Deterministic Hashing & Perceptual Distance Sensitivity

- **Generated At:** 2026-09-24T04:33:39.976342
- **Total Media Records:** 2,491
- **Unique Apollo Assets:** 2,323
- **Status:** COMPLETED & VERIFIED (Phase C)

---

## 1. Image Acquisition & Fingerprint Coverage

| Pipeline Stage | Asset Count | % Coverage | Notes |
| :--- | :---: | :---: | :--- |
| **Total Media References** | **2,491** | 100.0% | Recorded across 2,980 listings. |
| **Unique Apollo File IDs** | **2,323** | 100.0% | Unique image assets in capture set. |
| **Download Succeeded** | **2,282** | **98.24%** | Local WebP bytes acquired in `data/olx_media/`. |
| **Fingerprints Available** | **2,280** | **91.53%** | SHA-256, pHash, dHash, aHash calculated. |
| **Unique SHA-256 Binaries** | **2,220** | — | Distinct binary signatures. |

---

## 2. Level 1: Exact Binary Image Reuse (`EXACT_FILE_REUSE`)

- **Exact Duplicate Groups:** **47** distinct groups
- **Exact Cross-Listing Reuse Relationships:** **82** pairwise edges
- **Interpretation:** Deterministic proof that identical image file bytes are shared across multiple distinct listings.

---

## 3. Level 2: Perceptual Hash Distance Sensitivity (`PERCEPTUAL_SIMILARITY_CANDIDATE`)

Evaluating candidate threshold sensitivity across all unique image pairs:

| Hamming Threshold | Candidate Pairs | Sensitivity Tier | Visual Match Interpretation |
| :--- | :---: | :---: | :--- |
| **$d \le 4$** | **121** | High Precision | Near-identical crop or minor compression re-encoding. |
| **$d \le 6$** | **126** | Strong Candidate | Minor angle / lighting variation of same subject. |
| **$d \le 8$** | **139** | Moderate Candidate | Re-framed or filtered candidate matches. |
| **$d \le 10$ (Standard Threshold)** | **160** | **Candidate Filter** | **Standard perceptual similarity threshold** (Status: `UNVERIFIED`). |
| **$d \le 12$** | **242** | Broad | Includes generic stock backgrounds. |
| **$d \le 15$** | **570** | Loose | High false-positive rate across uniform studio shots. |

---

## 4. Multi-Level Image Clusters

- **Total Connected Clusters ($N \ge 2$ Listings):** **87**
- **Cross-City Spanning Clusters:** **20**

| Cluster ID | Unique Listings | Media Count | Membership Type | Cities Represented | Price Range (INR) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`IMG-CLUST-0001`** | 15 | 15 | `perceptual_only` | Bengaluru, Delhi | ₹19,000 → ₹90,000 |
| **`IMG-CLUST-0002`** | 3 | 3 | `perceptual_only` | Delhi | ₹5,500 → ₹5,500 |
| **`IMG-CLUST-0003`** | 2 | 2 | `perceptual_only` | Bengaluru, Delhi | ₹68,700 → ₹150,000 |
| **`IMG-CLUST-0004`** | 2 | 2 | `perceptual_only` | Unknown | ₹129,300 → ₹138,500 |
| **`IMG-CLUST-0005`** | 2 | 2 | `perceptual_only` | Unknown | ₹146,800 → ₹147,000 |
| **`IMG-CLUST-0006`** | 2 | 2 | `perceptual_only` | Unknown | ₹22,999 → ₹27,999 |
| **`IMG-CLUST-0007`** | 2 | 2 | `perceptual_only` | Unknown | ₹89,999 → ₹131,999 |
| **`IMG-CLUST-0008`** | 2 | 2 | `perceptual_only` | Unknown | ₹116,999 → ₹116,999 |
| **`IMG-CLUST-0009`** | 2 | 2 | `perceptual_only` | Delhi | ₹28,000 → ₹28,000 |
| **`IMG-CLUST-0010`** | 2 | 2 | `perceptual_only` | Unknown | ₹79,999 → ₹131,999 |
| **`IMG-CLUST-0011`** | 3 | 3 | `perceptual_only` | Unknown | ₹59,990 → ₹59,999 |
| **`IMG-CLUST-0012`** | 2 | 2 | `perceptual_only` | Solapur | ₹1,500 → ₹77,990 |
| **`IMG-CLUST-0013`** | 2 | 2 | `perceptual_only` | Unknown | ₹45,999 → ₹84,990 |
| **`IMG-CLUST-0014`** | 3 | 3 | `perceptual_only` | Unknown | ₹32,999 → ₹32,999 |
| **`IMG-CLUST-0015`** | 2 | 2 | `perceptual_only` | Delhi, Noida | ₹349 → ₹84,000 |

---

## 5. Analytical Parquet Artifacts

1. **`data/olx_processed/fingerprints.parquet`**: Multi-hash table (SHA-256, pHash, dHash, aHash, width, height, size).
2. **`data/olx_processed/image_relationships.parquet`**: All `242` exact and perceptual pairwise evidence links.
3. **`data/olx_processed/image_clusters.parquet`**: Connected image clusters with cross-city spans and price spreads.
