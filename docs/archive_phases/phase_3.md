# TRUSTLENS — PHASE 3

# TARGETED OLX MARKETPLACE ACQUISITION

## Reddit Intelligence → Targeted OLX Collection

You are working on the existing TrustLens project:

```text
/Users/nandinikhandelwal/Desktop/Codes/trustlens/
```

---

# 0. MOST IMPORTANT OBJECTIVE

We have completed the Reddit multimodal research phase.

**DO NOT start by broadly scraping OLX.**

The Reddit research has already told us **which marketplace fraud mechanisms and product/category combinations are worth investigating.**

Phase 3 must therefore perform:

```text
REDDIT FRAUD INTELLIGENCE
        ↓
TARGETED SEARCH HYPOTHESES
        ↓
OLX DISCOVERY
        ↓
LISTING COLLECTION
        ↓
SELLER / PRODUCT / PRICE / DESCRIPTION COLLECTION
        ↓
IMAGE + MEDIA COLLECTION
        ↓
LOCAL OLX DATASET
        ↓
READY FOR TRUSTLENS INVESTIGATION
```

The goal is to determine whether the fraud journeys and observable signals discovered from Reddit can actually be found and investigated in the live OLX marketplace environment.

---

# 1. SOURCE OF TRUTH — REDDIT PHASE 2

The Reddit multimodal analysis produced the following intelligence.

## Dataset

* 178 raw Reddit posts
* 157 India-context posts
* 330 raw media assets
* 247 unique SHA-256 media files
* collection window: 2025-09-26 → 2026-09-19

The Reddit dataset is a **research signal layer**, not proof that any specific OLX seller is fraudulent.

---

# 2. KEY PRODUCT CATEGORIES FROM REDDIT

The Indian Reddit cases showed the following product/category distribution:

| Category            | Raw Cases |
| ------------------- | --------: |
| Smartphone          |        52 |
| Laptop              |        38 |
| Gaming Console      |        22 |
| Car / Vehicle       |        18 |
| Camera              |        12 |
| Rental / Property   |         8 |
| Electronics / Other |         7 |

The first OLX pilot should therefore NOT search everything.

Prioritize the categories that appear repeatedly in the Reddit evidence.

---

# 3. PRIORITY FRAUD MECHANISMS

The Reddit research identified recurring mechanisms:

### 1. Advance / Deposit Payment

* advance payment
* booking token
* deposit request
* payment before meeting/shipping

### 2. Army / CISF Persona

* army officer claims
* CISF claims
* relocation/transfer stories
* remote posting explanations

### 3. UPI / QR Payment

* QR payment
* UPI payment
* “scan to receive money”
* payment/refund QR narratives

### 4. Fake Invoice / Canteen Receipt

* army canteen receipt
* defence store receipt
* corporate invoice
* GST invoice claims

### 5. Gate Pass / Courier Story

* gate-pass fee
* courier fee
* transport fee
* delivery/security deposit

### 6. Unrealistic Pricing

* unusually cheap high-value products
* urgent sale
* clearance/warehouse claims

### 7. WhatsApp Migration

* immediate move from OLX to WhatsApp
* phone number emphasis
* off-platform communication

### 8. Non-delivery / Fake Seller

* advance payment followed by disappearance
* fake seller identity
* delivery never completed

These are **investigation hypotheses**, not automatic OLX classifications.

---

# 4. TWO PRIMARY INVESTIGATION JOURNEYS

The first OLX collection should focus primarily on these two journeys.

---

## JOURNEY 1

# DEFENCE / ARMY RELOCATION + GATE-PASS JOURNEY

Reddit-derived sequence:

```text
Cheap listing
      ↓
OLX contact
      ↓
WhatsApp migration
      ↓
Army / military identity claim
      ↓
Army canteen / defence receipt
      ↓
Transport / gate-pass story
      ↓
Advance payment
      ↓
Additional courier/security fee
```

The purpose of Phase 3 is NOT to search for “scams.”

The purpose is to see whether OLX currently contains listings exhibiting the **observable components of this journey**.

---

# 5. JOURNEY 1 — TARGET CATEGORIES

Prioritize:

### Primary

* Cars
* Bikes

### Secondary

* iPhones
* Laptops

The Reddit report specifically identified:

```text
Car / Vehicle
Smartphone
Laptop
```

as relevant categories.

---

# 6. JOURNEY 1 — TARGETED SEARCH QUERIES

Use the Reddit-derived search hypotheses as starting points.

Examples:

```text
"army officer urgent sale"
"army transfer"
"army transfer urgent sale"
"army posted"
"army relocation"
"army canteen"
"army canteen delivery"
"canteen car"
"defence canteen"
"defence store"
"cisf transfer"
"cisf officer"
"gate pass"
"transport fee"
"urgent army sale"
```

Also search combinations where OLX search allows them:

```text
Thar army transfer
car army transfer
bike army transfer
iPhone army transfer
laptop army transfer
```

DO NOT assume every query exists on OLX.

Record which queries produced results and which did not.

---

# 7. JOURNEY 2

# HIGH-END TECH + WAREHOUSE CLEARANCE + BOOKING TOKEN

Reddit-derived sequence:

```text
High-value electronics
        ↓
Unusually low price
        ↓
Warehouse / company clearance claim
        ↓
Corporate/business identity claim
        ↓
Invoice / receipt claim
        ↓
WhatsApp migration
        ↓
Booking token / advance
```

Again:

These are hypotheses to investigate.

Do NOT label a matching OLX listing fraudulent.

---

# 8. JOURNEY 2 — TARGET CATEGORIES

Prioritize:

### Smartphones

Especially:

* iPhone
* Google Pixel
* Samsung flagship

### Laptops

Especially:

* MacBook
* premium gaming laptops

### Gaming

Especially:

* PS5
* Xbox
* high-value gaming hardware

These correspond directly to the Reddit product distribution and candidate patterns.

---

# 9. JOURNEY 2 — TARGETED SEARCH QUERIES

Use targeted searches such as:

```text
iPhone cheap
iPhone urgent sale
iPhone warehouse
iPhone company clearance
iPhone liquidation
iPhone bulk sale

MacBook cheap
MacBook urgent sale
MacBook warehouse
MacBook company clearance
MacBook liquidation

PS5 cheap
PS5 urgent sale
PS5 warehouse
PS5 clearance

gaming laptop cheap
gaming laptop urgent sale
gaming laptop clearance
```

Also use Reddit-derived candidate-pattern language where relevant:

```text
warehouse clearance
company clearance
corporate liquidation
stock clearance
bulk stock
company closing
office closing
```

Do not assume that every phrase indicates fraud.

They are discovery terms.

---

# 10. THIRD TARGET — QR / UPI JOURNEY

The Reddit research also identified:

# QR REVERSE-CHARGE / RECEIVE-MONEY TRAP

Sequence:

```text
Legitimate seller
       ↓
Scammer contacts seller
       ↓
Claims to send advance
       ↓
Sends QR
       ↓
"Scan to receive ₹X"
       ↓
Victim scans / enters UPI PIN
       ↓
Money debited
```

This journey is different because the OLX listing itself may look completely normal.

Therefore:

## DO NOT SEARCH ONLY FOR “QR SCAM.”

Instead collect ordinary OLX seller listings in relevant electronics categories so that the later investigation system can study the **seller-side interaction pattern** if the researcher explicitly captures subsequent communication.

Phase 3 itself should only collect what is publicly available on OLX.

Do NOT scrape:

* private chats
* WhatsApp
* Telegram
* phone conversations

The QR journey becomes a later investigation workflow.

---

# 11. WHAT WE ARE ACTUALLY COLLECTING

For every discovered OLX listing, collect:

## Listing

```text
listing_id
source_listing_id
listing_url
title
description
price
currency
category
subcategory
condition
location
posted_at
updated_at
```

## Product

```text
brand
model
variant
storage
RAM
year
condition
color
other public attributes
```

## Seller / Vendor

```text
seller_id if publicly exposed
display_name
profile_url
seller location
account age if publicly displayed
listing count if publicly displayed
seller type if explicitly displayed
verification badge if explicitly displayed
```

## Contact / claim information

Preserve the raw description and publicly visible information containing phrases such as:

```text
WhatsApp
call
phone
urgent
army
CISF
transfer
relocation
canteen
warehouse
clearance
company
invoice
GST
receipt
advance
token
deposit
courier
delivery
transport
gate pass
```

BUT:

Do not classify them as fraud during acquisition.

---

# 12. PRODUCT + SELLER + LISTING ARE ALL REQUIRED

Do not create a collector that only downloads listing cards.

We need the **full listing page**.

The desired acquisition is:

```text
SEARCH RESULT
     ↓
LISTING URL
     ↓
FULL LISTING PAGE
     ├── product
     ├── title
     ├── description
     ├── price
     ├── location
     ├── seller
     ├── seller profile
     ├── listing metadata
     └── images
```

If seller information is available through a public seller/profile page, collect the relevant public information.

Do not collect unrelated seller information.

---

# 13. MEDIA IS FIRST CLASS

For every listing:

```text
listing
  ↓
all available public listing images
  ↓
download
  ↓
SHA-256
  ↓
dimensions
  ↓
local file
```

Preserve every image.

Do not select only the “best” image.

Do not discard duplicates.

Duplicates themselves may become useful later.

---

# 14. IMAGE TYPES WE WANT TO PRESERVE

Do not classify deeply yet, but preserve images that may later contain:

* product photos
* invoice screenshots
* receipts
* military/identity-looking documents
* business documents
* packaging
* serial numbers
* product labels
* screenshots
* WhatsApp screenshots if publicly included in the listing
* payment-related screenshots if publicly included
* seller-provided promotional material

The image itself is evidence.

Do not infer authenticity.

---

# 15. CRAWL4AI + BROWSER EXTENSION ARCHITECTURE

Build BOTH components.

## Browser extension

Used for:

* researcher-controlled discovery
* collecting current search results
* collecting a selected listing
* sending URLs to the local backend
* manual fallback when automated collection fails

## Crawl4AI

Used for:

* controlled public-page retrieval
* structured extraction
* listing-page parsing
* image URL extraction
* seller/profile extraction where publicly accessible

Architecture:

```text
                 RESEARCHER
                     │
                     ▼
              OLX IN BROWSER
                     │
            ┌────────┴────────┐
            │                 │
            ▼                 ▼
       Search Page        Listing Page
            │                 │
            └────────┬────────┘
                     ▼
             TRUSTLENS EXTENSION
                     │
                     ▼
              LOCAL FASTAPI
                     │
                     ▼
                 CRAWL4AI
                     │
                     ▼
              OLX PUBLIC PAGE
                     │
                     ▼
              STRUCTURED DATA
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Listing     Seller      Media
          │          │          │
          └──────────┼──────────┘
                     ▼
              OLX PILOT DATASET
```

---

# 16. IMPORTANT — CONTROLLED TARGETING

Do NOT build:

```text
crawl all OLX
crawl every category
crawl every city
crawl every listing
```

Instead implement a **Targeted Investigation Search Configuration**.

Example:

```json
{
  "investigation_id": "INV-001",
  "journey": "defence_relocation_gate_pass",
  "categories": [
    "cars",
    "bikes",
    "laptops",
    "smartphones"
  ],
  "queries": [
    "army transfer",
    "army urgent sale",
    "army canteen",
    "gate pass",
    "cisf transfer"
  ],
  "max_results_per_query": 20
}
```

And:

```json
{
  "investigation_id": "INV-002",
  "journey": "high_end_tech_clearance_token",
  "categories": [
    "smartphones",
    "laptops",
    "gaming consoles"
  ],
  "queries": [
    "iPhone cheap",
    "iPhone clearance",
    "MacBook cheap",
    "MacBook warehouse",
    "PS5 cheap",
    "PS5 clearance"
  ],
  "max_results_per_query": 20
}
```

This configuration drives collection.

---

# 17. DO NOT PRE-FILTER TOO AGGRESSIVELY

This is important.

We want to test the Reddit hypotheses against OLX.

Therefore collect:

### Query-matching listings

AND, where practical:

### Baseline listings

For example:

```text
INV-002

Targeted:
"MacBook warehouse"
"MacBook clearance"
"MacBook cheap"

Baseline:
"MacBook Air"
"MacBook Pro"
```

The baseline allows us to later compare:

```text
ordinary marketplace listings
vs.
hypothesis-targeted listings
```

Do not collect only the weirdest listings.

---

# 18. COLLECTION SIZE

For the first pilot:

## Target approximately 100–150 OLX listings

across the targeted investigation configurations.

Suggested distribution:

```text
INV-001:
30–50 listings

INV-002:
40–60 listings

QR / baseline electronics:
20–40 listings
```

These are targets, not requirements.

If a query produces fewer results, record the actual count.

---

# 19. COLLECTION RUNS

Every targeted investigation run must have:

```text
run_id
investigation_id
query
category
search_url
collection_method
start_time
end_time
discovered_count
collected_count
failed_count
duplicate_count
```

Example:

```text
OLX-RUN-20260920-001

INV-002
Query: "MacBook warehouse"
Category: laptops

Discovered: 18
Collected: 16
Failed: 2
Duplicates: 3
```

---

# 20. RAW DATA MUST REMAIN IMMUTABLE

Store:

```text
raw/
```

separately from:

```text
normalized/
```

Never overwrite the raw source representation.

We need auditability.

---

# 21. MEDIA MANIFEST

Create:

```text
media_manifest.jsonl
```

with:

```json
{
  "media_id": "MEDIA-OLX-00001",
  "listing_id": "OLX-00001",
  "source_url": "...",
  "local_path": "...",
  "sha256": "...",
  "width": 1080,
  "height": 1350,
  "mime_type": "image/jpeg",
  "file_size_bytes": 123456,
  "download_status": "success"
}
```

Also create:

```text
duplicate_media_groups.json
```

using exact SHA-256 matches.

---

# 22. DATA PROVENANCE

Every record must tell us:

```text
where
when
how
```

Example:

```json
{
  "collection_metadata": {
    "source": "olx",
    "collection_method": "crawl4ai",
    "discovered_via": "browser_extension",
    "run_id": "OLX-RUN-...",
    "collected_at": "...",
    "collector_version": "..."
  }
}
```

Possible methods:

```text
browser_extension
crawl4ai
researcher_assisted
```

---

# 23. RESEARCHER-ASSISTED FALLBACK

If Crawl4AI cannot retrieve a permitted public listing page, do NOT try to bypass OLX protections.

The extension should support:

```text
[Capture Current Listing]
```

which can send the researcher-visible listing data to the local backend.

This keeps the acquisition pipeline usable without evasive scraping.

---

# 24. EXTENSION UI

The extension should understand the current context.

If researcher is on an OLX search page:

```text
TRUSTLENS OLX COLLECTOR

Investigation:
[INV-002 ▼]

Detected listings:
23

Query:
MacBook warehouse

[Collect 23 Listings]
[Collect Selected]
```

If researcher is on an individual listing:

```text
TRUSTLENS

Listing detected

Apple MacBook Pro
₹32,000

Seller:
...

Images:
7

[Collect Listing]
```

Show collection state:

```text
Queued
Collecting
Collected
Failed
Duplicate
```

Do NOT show risk/scam labels.

---

# 25. TARGETED INVESTIGATION SELECTOR

The extension should allow:

```text
Investigation:

○ INV-001
  Defence / Army Relocation

○ INV-002
  High-End Tech Clearance

○ BASELINE
  Ordinary Electronics
```

This simply attaches the appropriate investigation metadata to the collected records.

It does NOT classify the listing.

---

# 26. NO AUTOMATIC ACCUSATIONS

Absolutely do NOT generate:

```text
SCAM
FRAUD
FRAUDSTER
SCAMMER
90% RISK
HIGH RISK SELLER
```

during acquisition.

At this phase the system says only:

```text
Collected
Observed
Unavailable
```

Any later interpretation belongs to the investigation layer.

---

# 27. PRIVACY

Collect only information necessary for marketplace investigation.

Do not intentionally collect:

* private messages
* personal account data hidden behind access controls
* unrelated profile information
* precise private addresses
* government IDs unless they are publicly included as part of a listing image and are necessary for later evidence review

If sensitive information appears in public listing media:

* preserve raw evidence only as necessary
* minimize derived copies
* redact in analytical exports later
* never expose unnecessary PII in logs

---

# 28. NO WHATSAPP / TELEGRAM SCRAPING

The Reddit research identified WhatsApp migration as an important fraud mechanism.

But Phase 3 MUST NOT scrape:

* WhatsApp
* Telegram
* SMS
* private OLX messages
* phone calls

We only collect:

> what is publicly observable on OLX.

For example, if an OLX description says:

```text
"WhatsApp me for details"
```

preserve that raw description.

Do not follow the contact into WhatsApp.

---

# 29. NO REVERSE IMAGE SEARCH YET

Do NOT implement:

* Google Lens
* TinEye
* reverse image search
* image embeddings
* external image matching

Exact SHA-256 duplicate detection is enough for Phase 3.

---

# 30. NO LLM ANALYSIS YET

Do not send every OLX listing to an LLM during acquisition.

The collector's job is:

```text
GET THE DATA
```

not:

```text
INTERPRET THE DATA
```

The later TrustLens investigation phase will analyze the collected dataset.

---

# 31. DATA STRUCTURE

Create at minimum:

```text
olx_listings.jsonl
olx_sellers.jsonl
olx_media_manifest.jsonl
olx_collection_runs.jsonl
olx_failures.jsonl
```

Each listing should have:

```json
{
  "listing_id": "OLX-000001",
  "source": "olx",
  "investigation_id": "INV-002",

  "listing": {},
  "product": {},
  "seller": {},

  "media": [],

  "collection_metadata": {}
}
```

---

# 32. IMPORTANT — PRESERVE SEARCH CONTEXT

Every listing must remember:

```text
investigation_id
query
category
search_url
discovery_timestamp
```

This matters because later we need to answer:

> Why was this listing collected?

Example:

```json
{
  "discovery_context": {
    "investigation_id": "INV-002",
    "query": "MacBook warehouse",
    "search_url": "...",
    "discovered_at": "..."
  }
}
```

---

# 33. BASELINE VS TARGETED

Add:

```text
collection_type
```

with:

```text
targeted
baseline
```

Example:

```json
{
  "collection_type": "targeted"
}
```

versus:

```json
{
  "collection_type": "baseline"
}
```

This is important for later comparison.

---

# 34. CITY / GEOGRAPHIC VARIATION

Do not restrict the pilot to one city unless OLX search behavior forces it.

Capture the publicly displayed location.

Try to get geographic diversity where the targeted queries naturally produce it.

Do NOT infer location.

Do NOT collect exact addresses.

---

# 35. CATEGORIES TO PRIORITIZE

Priority order from the Reddit evidence:

## Tier 1

```text
Smartphones
Laptops
Cars / Vehicles
Gaming Consoles
```

## Tier 2

```text
Cameras
Electronics / PC components
Bikes
```

Do NOT spend the pilot on rental/property yet.

The first objective is validating the strongest marketplace acquisition hypotheses.

---

# 36. INITIAL PILOT CONFIGURATION

Implement these configs:

## INV-001

```yaml
name: Defence / Army Relocation & Gate-Pass
categories:
  - cars
  - bikes
  - smartphones
  - laptops

target_queries:
  - army officer urgent sale
  - army transfer
  - army relocation
  - army canteen
  - defence canteen
  - cisf transfer
  - cisf officer
  - gate pass
  - transport fee

baseline_queries:
  - used car
  - used bike
  - used iphone
  - used laptop
```

## INV-002

```yaml
name: High-End Tech Clearance & Booking Token
categories:
  - smartphones
  - laptops
  - gaming consoles

target_queries:
  - iphone cheap
  - iphone clearance
  - iphone warehouse
  - iphone company clearance
  - macbook cheap
  - macbook clearance
  - macbook warehouse
  - macbook company clearance
  - ps5 cheap
  - ps5 clearance
  - gaming laptop cheap

baseline_queries:
  - iphone
  - macbook
  - ps5
  - gaming laptop
```

Do not assume these exact search strings are optimal.

Make them configurable so the researcher can modify them.

---

# 37. PHASE 3 CLI

Support something conceptually like:

```bash
trustlens olx discover \
  --investigation INV-002 \
  --query "MacBook warehouse" \
  --limit 20
```

Then:

```bash
trustlens olx collect \
  --run-id OLX-RUN-...
```

Or, if the existing architecture supports it cleanly:

```bash
trustlens olx run \
  --investigation INV-002
```

Also:

```bash
trustlens olx status <RUN_ID>
```

and:

```bash
trustlens olx export <RUN_ID>
```

Use the existing TrustLens CLI conventions.

---

# 38. TESTING

Write tests for:

* search-result discovery
* listing URL normalization
* listing parser
* product parser
* seller parser
* price parser
* description preservation
* media extraction
* media download
* SHA-256
* duplicate detection
* investigation metadata
* targeted vs baseline labeling
* collection runs
* failure handling
* researcher-assisted capture
* extension/backend communication

Use local fixtures.

Do NOT make tests dependent on live OLX.

---

# 39. DOCUMENTATION

Create:

```text
PHASE_3_OLX_TARGETED_ACQUISITION.md
```

Document:

1. Why the OLX phase is targeted
2. Reddit → investigation hypothesis mapping
3. INV-001
4. INV-002
5. baseline collection
6. extension
7. Crawl4AI
8. local API
9. dataset schema
10. media handling
11. provenance
12. privacy
13. compliance constraints
14. how to run the pilot
15. known limitations

---

# 40. DO NOT BUILD THE NEXT PHASE

Do NOT implement yet:

```text
fraud scoring
risk scoring
LLM investigation
RAG
vector database
embeddings
reverse image search
agentic investigation
business verification engine
GST verification engine
OCR reasoning
marketplace risk ranking
seller ranking
browser extension investigation UI
```

Those come after we have real OLX data.

---

# 41. SUCCESS CRITERIA

Phase 3 Prompt 1 is successful when we can:

```text
Choose INV-001 or INV-002
        ↓
Run targeted OLX searches
        ↓
Discover relevant listings
        ↓
Collect listing pages
        ↓
Collect product information
        ↓
Collect publicly visible seller information
        ↓
Collect descriptions
        ↓
Collect prices + locations
        ↓
Download listing images
        ↓
Hash + deduplicate media
        ↓
Preserve provenance
        ↓
Export a reproducible OLX dataset
```

We should be able to say:

> “These are the actual OLX listings we found while testing the Reddit-derived fraud hypotheses.”

That is the output.

---

# 42. FIRST REAL EXPERIMENT

After implementation, DO NOT automatically launch a huge crawl.

First run:

## INV-002 — High-End Tech Clearance

Use:

```text
MacBook warehouse
MacBook clearance
iPhone clearance
iPhone cheap
PS5 clearance
PS5 cheap
```

plus their baseline queries.

Collect approximately:

```text
30–50 targeted listings
+
20–30 baseline listings
```

Then inspect the dataset.

After that, we decide whether INV-001 should be collected next.

---

# 43. FINAL REPORT TO ME

When implementation is finished, report:

### 1. Repository changes

### 2. Extension architecture

### 3. Crawl4AI architecture

### 4. Local API

### 5. Investigation configuration system

### 6. INV-001 configuration

### 7. INV-002 configuration

### 8. Dataset schema

### 9. Media schema

### 10. Provenance

### 11. CLI commands

### 12. Test results

### 13. Exact command for the first real OLX run

### 14. Limitations

Do NOT claim that TrustLens can detect fraud yet.

The correct statement is:

> **Phase 3 acquires targeted, reproducible OLX marketplace evidence based on fraud mechanisms discovered during the Reddit research phase.**

---

# FINAL PRINCIPLE

The Reddit phase answered:

> **“What fraud journeys are people reporting in the Indian marketplace ecosystem?”**

Phase 3 must now answer:

> **“Can we find the marketplace-side evidence corresponding to those journeys on OLX?”**

Therefore:

```text
NOT:
Scrape all OLX.

NOT:
Search random products.

NOT:
Build a scam detector.

YES:
Take the strongest Reddit-derived fraud journeys.

        ↓

Turn them into targeted OLX search hypotheses.

        ↓

Find real listings.

        ↓

Collect the complete listing/vendor/product/media context.

        ↓

Preserve everything needed for investigation.

        ↓

Only then build the TrustLens investigation layer.
```

Build **Phase 3 Prompt 1 — targeted OLX marketplace acquisition only**.
