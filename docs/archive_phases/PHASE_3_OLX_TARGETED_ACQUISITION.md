# TRUSTLENS — PHASE 3: TARGETED OLX MARKETPLACE ACQUISITION & INVESTIGATION

## 1. Executive Summary

Phase 3 transitions TrustLens from retrospective Reddit fraud research to **targeted empirical evidence acquisition on OLX**. 

Instead of broad, unfocused web scraping, TrustLens uses the empirical findings from Phase 2 (157 Indian fraud cases, 330 media assets, 21 canonical patterns) to construct **targeted investigation hypotheses**.

```text
REDDIT FRAUD INTELLIGENCE
        ↓
TARGETED SEARCH HYPOTHESES (INV-001, INV-002, BASELINE)
        ↓
CONTROLLED OLX DISCOVERY
        ↓
STRUCTURED LISTING & PAGE INGESTION
        ├── Product Attributes (Brand, Model, Specs, Condition)
        ├── Seller Public Profile (Badges, Age, Type)
        ├── Pricing & Geographic Location
        └── Description & Contact Claims
        ↓
MEDIA DOWNLOAD & SHA-256 DEDUPLICATION
        ↓
LOCAL REPRODUCIBLE DATASET (data/olx_pilot/)
        ↓
OBSERVABLE SIGNAL DETECTION & EVIDENCE PROVENANCE
```

---

## 2. Reddit Intelligence → Investigation Suites

| Investigation ID | Focus Area | Target Categories | Target Search Queries | Baseline Comparative Queries |
| :--- | :--- | :--- | :--- | :--- |
| **`INV-001`** | **Defence / Army Relocation & Gate-Pass** | Cars, Bikes, Smartphones, Laptops | `"army officer urgent sale"`, `"army transfer"`, `"cisf transfer"`, `"army canteen"`, `"gate pass"`, `"transport fee"` | `"used car"`, `"used bike"`, `"used laptop"`, `"used iphone"` |
| **`INV-002`** | **High-End Tech Clearance & Booking Token** | Smartphones, Laptops, Gaming Consoles, Cameras | `"iphone cheap"`, `"iphone clearance"`, `"macbook cheap"`, `"macbook warehouse"`, `"ps5 cheap"`, `"ps5 clearance"`, `"gaming laptop cheap"` | `"iphone 15"`, `"macbook pro"`, `"ps5"`, `"gaming laptop"` |
| **`BASELINE`** | **Neutral Marketplace Baseline** | All Key Electronics | Standard model queries | Standard model queries |

---

## 3. Architecture & Acquisition Channels

### 3.1. Dual Acquisition Architecture
1. **Automated Search & Ingest**: Controlled search discovery via Crawl4AI / HTTP client fetching public listings without bypassing platform protections.
2. **Researcher-Assisted Fallback**: Manual capture via browser extension or saved HTML ingestion (`trustlens olx ingest --html ...`), ensuring complete usability regardless of anti-bot protections.

### 3.2. Local Ingestion API Daemon (`trustlens olx serve`)
A lightweight daemon running at `http://127.0.0.1:8765` accepting JSON payloads from the TrustLens browser extension:
* `POST /`: Accepts `{ "url": "...", "html": "...", "investigation_id": "INV-002", "collection_type": "targeted" }`.

---

## 4. Local Pilot Dataset Layout (`data/olx_pilot/`)

```text
data/olx_pilot/
├── raw/                              # Immutable raw HTML files by run
│   └── OLX-RUN-20260920-001/
│       └── OLX-000001.html
├── normalized/                       # Structured JSONL records
│   ├── olx_listings.jsonl
│   └── olx_sellers.jsonl
├── media/                            # Downloaded listing images
│   ├── MEDIA-OLX-000001-001.webp
│   ├── olx_media_manifest.jsonl
│   └── duplicate_media_groups.json
├── investigations/                   # Full investigation JSON instances
│   └── INV-OLX-000001.json
├── reports/                          # Human-readable markdown reports
│   └── INV-OLX-000001.md
├── olx_collection_runs.jsonl         # Run metadata & statistics
└── olx_failures.jsonl                # Failure audit log
```

---

## 5. Observable Signal Library

Every detected signal links directly to concrete, verifiable evidence records (`EVID-xxxx`):
1. **`unusually_low_price`**: Listing price $\ge 35\%$ below model median benchmark.
2. **`army_persona`**: Mentions military / defense / CISF identity or remote base relocation.
3. **`advance_payment`**: Demands booking token, advance deposit, or gate-pass fee before inspection.
4. **`whatsapp_migration`**: Requests buyer communicate off-platform via WhatsApp or phone call.
5. **`warehouse_clearance`**: Claims corporate liquidation, office closing, or bulk clearance.
6. **`invoice_claim`**: Claims availability of official GST invoice or defense canteen receipt.
7. **`urgent_sale`**: Creates urgency by claiming immediate departure or distress sale.

---

## 6. How to Run Phase 3 Commands

### 6.1. Inspect Investigation Suites
```bash
trustlens olx suites
```

### 6.2. Run Full Targeted Investigation Suite (`INV-002`)
```bash
trustlens olx run --investigation INV-002 --max-results 5
```

### 6.3. Discover Listings for a Specific Query
```bash
trustlens olx discover --investigation INV-002 --query "MacBook warehouse" --limit 10
```

### 6.4. Ingest Single Listing from URL or Saved HTML
```bash
# Live URL ingestion
trustlens olx ingest --url "https://www.olx.in/item/..." --investigation INV-002

# Researcher-assisted HTML ingestion
trustlens olx ingest --html path/to/saved_listing.html --investigation INV-001
```

### 6.5. Inspect Status & View Human-Readable Report
```bash
# Check repository statistics
trustlens olx status

# View investigation report
trustlens olx report INV-OLX-000001
```

### 6.6. Start Ingestion Server for Browser Extension
```bash
trustlens olx serve --port 8765
```

---

## 7. Compliance & Privacy Guarantees

* **No Mass / Evasive Scraping**: Adheres strictly to lawful retrieval; falls back gracefully to researcher-assisted capture when rate-limited.
* **No Speculative Profiling**: Captures only publicly visible listing attributes; no private chat or communication scraping.
* **Strict Evidence Separation**: Distinguishes *Observed*, *Reported*, and *Verified* attributes.
* **No Automated Accusations**: TrustLens does not generate numeric "scam scores" or label sellers as fraudulent during acquisition.
