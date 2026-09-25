# TRUSTLENS — PHASE 3

## OLX Investigation Pilot

You are working on the existing TrustLens project.

### IMPORTANT CONTEXT

TrustLens is an evidence-first marketplace fraud intelligence system.

The project started from real Reddit marketplace-fraud reports. We have already completed the Reddit research and multimodal processing pipeline.

The Reddit research produced:

* 178 collected Reddit posts
* 157 India-context cases
* 143 deduplicated India-context stories
* 330 downloaded media assets
* 247 unique SHA-256 media files
* 330 visual evidence records
* 21 established fraud patterns
* 3 candidate patterns
* 2 fraud journeys
* 2 investigation hypotheses

The Reddit corpus is NOT the final product.

It is being used to identify recurring fraud journeys and investigation signals that we can now test against real marketplace listings.

We are now moving to:

# PHASE 3 — LIVE OLX INVESTIGATION PILOT

The purpose of this phase is to answer:

> Can TrustLens take a real OLX listing and systematically gather, structure, analyze, and explain marketplace trust signals using observable evidence?

We are NOT building the complete production system yet.

We are NOT building a large-scale OLX scraper.

We are NOT assigning "scam probabilities."

We are NOT accusing sellers.

We are building a controlled investigation prototype.

---

# 1. CORE PRINCIPLE

TrustLens must NEVER behave like:

> "AI thinks this seller is 94% scam."

Instead it should behave like:

> "This listing contains several observable signals that require verification. Here is the evidence supporting each observation, what was not verified, and what should be checked next."

Every important conclusion must be traceable to evidence.

Use these distinctions everywhere:

### OBSERVED

Directly visible in the collected listing/profile/image/page.

Example:

```text
The listing displays a price of ₹45,000.
```

### REPORTED

Claim made by the seller/listing.

Example:

```text
Seller claims the MacBook is unused.
```

### VERIFIED

A claim supported by an independent source or reliable verification step.

Example:

```text
The GSTIN format and registered business name correspond to an external registry result.
```

### CONTRADICTED

Independent evidence conflicts with the claim.

Example:

```text
Listing claims a Mumbai business, while the independently retrieved business information points elsewhere.
```

### UNKNOWN

We could not establish the fact.

Example:

```text
Seller ownership of the claimed business could not be established.
```

NEVER convert UNKNOWN into a negative conclusion.

---

# 2. CURRENT REPOSITORY

Assume the existing TrustLens repository is:

```text
/Users/nandinikhandelwal/Desktop/Codes/trustlens/
```

Do NOT create a new TrustLens repository.

Inspect the existing repository before making changes.

Understand the existing:

* Python package structure
* CLI
* schemas/models
* tests
* configuration
* existing Reddit research integration
* logging
* data directories
* coding conventions

The Reddit research repo is separate and must remain separate.

Do not merge the Reddit collector into the TrustLens core.

---

# 3. EXISTING REDDIT-DERIVED INVESTIGATION HYPOTHESES

Use the existing Reddit research outputs as the starting point.

The most relevant hypothesis for this pilot is:

## INVESTIGATION HYPOTHESIS — CHEAP HIGH-END ELECTRONICS

Recurring signals observed in the Reddit research include combinations of:

* unusually low prices
* advance/token/deposit requests
* off-platform communication
* WhatsApp migration
* fake or questionable business identity claims
* questionable invoices
* courier/delivery narratives
* identity inconsistencies
* product/company mismatch

These are NOT proof of fraud.

They are investigation signals.

The pilot should test whether these signals can be observed and independently investigated on real OLX listings.

---

# 4. PILOT CATEGORY

Start with:

## ELECTRONICS

Prioritize:

1. iPhone
2. MacBook
3. PlayStation
4. Gaming laptop
5. Camera
6. GPU
7. Other high-value electronics

Do NOT attempt every OLX category.

The pilot should deliberately target listings where investigation signals can reasonably be observed.

---

# 5. PILOT SIZE

Target:

## 10–20 OLX listings

Do NOT build a crawler for thousands of listings.

The goal is experimentation and architecture validation.

The investigator should support manually supplied listing URLs and/or a small controlled collection workflow.

Example:

```bash
trustlens olx investigate --url "<OLX_LISTING_URL>"
```

Potential batch mode:

```bash
trustlens olx investigate-batch --input pilot_urls.txt
```

Only implement batch mode if it naturally fits the existing architecture.

Do not over-engineer this.

---

# 6. OLX ACCESS / COMPLIANCE

This project must use only lawful and authorized access methods.

Do NOT:

* bypass CAPTCHA
* bypass bot protections
* evade rate limits
* rotate identities to avoid restrictions
* scrape private information
* scrape private messages
* perform browser-wide surveillance
* access private seller information
* bypass login/access controls
* use stealth scraping techniques
* create fake accounts
* automate actions that OLX prohibits

If automated retrieval is blocked, the system must support a researcher-assisted workflow where the user explicitly provides the listing URL and/or exported/saved page evidence.

The architecture should make this possible.

Do not solve access restrictions with evasive techniques.

---

# 7. INVESTIGATION WORKFLOW

Implement this conceptual pipeline:

```text
OLX Listing URL
       ↓
Listing Collection
       ↓
Listing Normalization
       ↓
Media Collection
       ↓
Seller Information
       ↓
Claim Extraction
       ↓
Marketplace Signal Detection
       ↓
Evidence Collection
       ↓
Independent Verification
       ↓
Contradiction / Corroboration Analysis
       ↓
Investigation Report
```

The important distinction is:

## COLLECTION ≠ ANALYSIS ≠ VERIFICATION

Do not collapse them.

---

# 8. LISTING SCHEMA

Create a structured listing record.

Suggested structure:

```json
{
  "investigation_id": "OLX-0001",
  "source": "olx",
  "listing_url": "...",
  "source_listing_id": null,
  "collected_at": "...",

  "title": "...",
  "description": "...",
  "category": "...",
  "subcategory": "...",

  "brand": null,
  "model": null,
  "condition": null,

  "price": null,
  "currency": "INR",

  "location": null,

  "posted_at": null,
  "updated_at": null,

  "seller": {
    "display_name": null,
    "seller_type": null,
    "account_age": null,
    "listing_count": null,
    "location": null,
    "verification_status": null
  },

  "contact_signals": [],

  "claims": [],

  "media": [],

  "collection_metadata": {}
}
```

Do not invent fields from information that was not observed.

Use null / unknown where necessary.

---

# 9. CLAIM EXTRACTION

Extract claims made by the listing/seller.

Examples:

```text
"Brand new"
"Imported from USA"
"Only used for 2 months"
"Urgent sale"
"Company closing"
"Warehouse clearance"
"Original bill available"
"GST bill available"
"Army officer"
"Moving abroad"
"Need advance payment"
"Delivery available"
"WhatsApp only"
```

Each claim should preserve its source.

Example:

```json
{
  "claim_id": "CLAIM-001",
  "claim_text": "Original bill available",
  "source": "listing_description",
  "status": "reported"
}
```

Do not convert a seller claim into a fact.

---

# 10. MEDIA COLLECTION

Media is a first-class part of TrustLens.

For every collected listing image:

```json
{
  "media_id": "MEDIA-OLX-0001-001",
  "investigation_id": "OLX-0001",
  "source_url": "...",
  "local_path": "...",
  "media_type": "image",
  "sha256": "...",
  "width": null,
  "height": null,
  "mime_type": "...",
  "file_size_bytes": null,
  "collection_timestamp": "...",
  "analysis_status": "pending"
}
```

Preserve:

* original file
* SHA-256
* dimensions
* MIME type
* source URL if available
* collection timestamp

Do not overwrite originals.

---

# 11. IMAGE ANALYSIS

Do NOT build advanced computer vision yet.

For this pilot, image analysis should focus on evidence extraction.

Possible visual types:

```text
product_photo
listing_screenshot
invoice
receipt
identity_document
chat_screenshot
payment_screenshot
business_document
shipping_document
contact_card
unknown
```

Extract only observable information.

Example:

```json
{
  "media_id": "...",
  "visual_type": ["invoice"],
  "visible_text": "...",
  "visible_amounts": ["₹45,000"],
  "visible_dates": [],
  "visible_platforms": [],
  "visible_product_info": ["MacBook Pro"],
  "visible_seller_info": [],
  "visible_payment_info": [],
  "visible_claims": [],
  "pii_present": true,
  "pii_types": ["phone_number"],
  "analysis_confidence": "medium",
  "notable_uncertainty": "Invoice authenticity cannot be established from visual inspection alone."
}
```

If OCR is already available in the project, reuse it.

If not, do NOT spend the phase building a massive OCR architecture.

A clean interface is enough.

---

# 12. MARKETPLACE SIGNAL LIBRARY

Create a reusable signal definition system.

Initial signals:

### Pricing

```text
unusually_low_price
price_claim_mismatch
```

### Communication

```text
off_platform_communication
whatsapp_migration
phone_contact_emphasis
```

### Payment

```text
advance_payment
deposit_request
token_payment
qr_payment
upi_payment
payment_before_inspection
```

### Identity

```text
fake_identity_claim
identity_inconsistency
business_identity_claim
business_identity_mismatch
```

### Documentation

```text
invoice_claim
invoice_inconsistency
receipt_claim
document_inconsistency
```

### Logistics

```text
courier_story
delivery_fee
gate_pass_story
relocation_story
```

### Product

```text
product_claim_mismatch
model_inconsistency
condition_claim_mismatch
```

### Other

```text
urgent_sale
unrealistic_price
duplicate_or_reused_media
```

Do not automatically mark these as fraud.

Each signal must have:

```text
signal_id
name
description
evidence_required
detection_method
status
```

---

# 13. SIGNAL RECORD

Every detected signal must point to evidence.

Example:

```json
{
  "signal_id": "SIG-0001",
  "investigation_id": "OLX-0001",
  "signal_type": "advance_payment",
  "status": "observed",
  "description": "Listing description asks buyer to pay a token amount before viewing the product.",
  "evidence_ids": [
    "EVID-0004"
  ],
  "confidence": "high"
}
```

Possible statuses:

```text
observed
reported
verified
contradicted
unknown
```

Do NOT create a numeric scam score.

---

# 14. EVIDENCE MODEL

Create an evidence record:

```json
{
  "evidence_id": "EVID-0001",
  "investigation_id": "OLX-0001",

  "source_type": "olx_listing",

  "source_reference": "...",

  "description": "...",

  "evidence_text": "...",

  "related_media_id": null,

  "claim_or_observation": "...",

  "relationship_to_claim": "supports",

  "verification_status": "unverified",

  "collected_at": "..."
}
```

Supported relationships:

```text
supports
contradicts
contextualizes
does_not_verify
```

Important:

A screenshot showing an invoice is evidence that the invoice image exists.

It is NOT automatically evidence that the invoice is genuine.

---

# 15. INDEPENDENT VERIFICATION

This is where the OLX investigation becomes more than scraping.

For claims that can reasonably be checked independently, create verification tasks.

Examples:

### Business claim

Seller:

> "ABC Electronics Pvt Ltd"

Investigation:

* Search publicly available business information.
* Compare business name.
* Compare location.
* Compare website/domain if claimed.
* Compare publicly available contact information where appropriate.

Output:

```text
seller_claim
external_observation
verification_status
```

Possible:

```text
corroborated
contradicted
inconclusive
not_found
not_checked
```

Do NOT claim legal/business fraud simply because something was not found.

---

# 16. PRICE COMPARISON

For high-value products, allow a contextual price comparison.

The purpose is NOT:

> "Cheap = scam."

Instead:

```text
Listing price: ₹45,000

Comparable observed listings:
₹72,000
₹75,000
₹69,000
₹78,000

Observation:
The target listing is substantially below the observed comparison range.

Interpretation:
Price discrepancy warrants additional verification.
```

Store the comparison evidence.

Do not manufacture market prices.

---

# 17. DUPLICATE / REUSED MEDIA

For the pilot, implement basic:

```text
SHA-256 exact duplicate detection
```

If feasible, also create an interface for future perceptual hashing.

Do NOT implement reverse image search yet.

If two collected OLX listings contain byte-identical images:

```text
duplicate_media_detected = true
```

But do not automatically conclude:

```text
same seller
scam
stolen image
```

Instead:

> "The same image was observed across these listings."

That is the evidence.

---

# 18. SELLER MODEL

Capture only publicly observable seller information.

Example:

```json
{
  "seller_id": "SELLER-OLX-001",
  "display_name": "...",
  "location": "...",
  "account_age": null,
  "listing_count": null,
  "verification_badges": [],
  "seller_type": null,
  "business_claim": null
}
```

Do not build a person-profiling system.

Do not collect unrelated personal information.

Do not infer identity beyond what is explicitly observable.

---

# 19. INVESTIGATION REPORT

Every pilot investigation should produce a human-readable report.

Example structure:

```text
TRUSTLENS INVESTIGATION
=======================

Investigation ID:
OLX-0001

Listing:
MacBook Pro M4 — ₹45,000

Source:
OLX

COLLECTED INFORMATION
---------------------
Price:
Location:
Category:
Seller:
Listing age:

SELLER/LISTING CLAIMS
---------------------
• "Brand new"
• "Original invoice available"
• "WhatsApp for details"

OBSERVED SIGNALS
----------------
1. Unusually low observed price
   Evidence: EVID-0003

2. Off-platform communication
   Evidence: EVID-0005

3. Invoice claim
   Evidence: EVID-0007

INDEPENDENT CHECKS
------------------
Business identity:
Inconclusive

Invoice:
Not independently verified

Price comparison:
Observed below comparison range

MEDIA OBSERVATIONS
------------------
• Product photo
• Invoice image
• WhatsApp screenshot

IMPORTANT UNCERTAINTIES
-----------------------
• Seller ownership of claimed business not established.
• Invoice authenticity not established.
• Product ownership not independently verified.

NEXT VERIFICATION STEPS
-----------------------
• Verify product serial number during physical inspection.
• Verify invoice independently.
• Avoid advance payment before inspection.
• Confirm seller/business identity through independent sources.

OVERALL STATUS
--------------
Multiple observable signals require verification.

This report does NOT establish that the seller is fraudulent.
```

Do NOT generate:

```text
SCAM SCORE: 94%
HIGH RISK SELLER
FRAUDSTER
SCAMMER
```

---

# 20. INVESTIGATION JSON

Every investigation must be reproducible from structured data.

Create something like:

```json
{
  "investigation_id": "OLX-0001",

  "source": "olx",

  "listing": {},

  "seller": {},

  "claims": [],

  "media": [],

  "media_analysis": [],

  "signals": [],

  "evidence": [],

  "verification_checks": [],

  "comparisons": [],

  "uncertainties": [],

  "next_steps": [],

  "human_review_status": "unreviewed",

  "created_at": "...",

  "updated_at": "..."
}
```

---

# 21. FILE STRUCTURE

Keep the implementation clean.

Suggested:

```text
trustlens/
│
├── src/
│   └── trustlens/
│       ├── olx/
│       │   ├── collector.py
│       │   ├── models.py
│       │   ├── media.py
│       │   ├── claims.py
│       │   ├── signals.py
│       │   ├── evidence.py
│       │   ├── verification.py
│       │   ├── investigation.py
│       │   └── report.py
│       │
│       └── ...
│
├── data/
│   └── olx_pilot/
│       ├── investigations/
│       ├── media/
│       ├── evidence/
│       └── reports/
│
└── tests/
    └── olx/
```

Adapt this to the EXISTING repository architecture rather than blindly creating this exact structure.

---

# 22. CLI

Add a minimal CLI.

At minimum:

```bash
trustlens olx investigate --url "<URL>"
```

And ideally:

```bash
trustlens olx inspect <investigation_id>
```

and:

```bash
trustlens olx report <investigation_id>
```

If batch mode is straightforward:

```bash
trustlens olx investigate-batch --input pilot_urls.txt
```

Do not build unnecessary commands.

---

# 23. RESEARCHER-ASSISTED FALLBACK

This is important.

If direct automated OLX collection cannot reliably access a page, support:

```bash
trustlens olx ingest --html <saved_page>
```

or another simple researcher-assisted input.

The investigator should not depend entirely on automated scraping.

The architecture should allow:

```text
URL
OR
saved HTML
OR
structured researcher-provided listing data
```

while preserving provenance.

---

# 24. SCREENSHOTS

For the pilot, preserve page evidence where possible.

Store:

```text
screenshots/
    OLX-0001/
        listing.png
        seller.png
        description.png
```

Screenshots should be linked to evidence records.

Do not treat screenshots as independently verified facts.

---

# 25. PRIVACY

Apply privacy minimization.

Do not unnecessarily store:

* personal phone numbers
* personal email addresses
* home addresses
* government IDs
* bank details
* UPI IDs

If sensitive information appears in evidence:

* preserve the minimum necessary evidence for the investigation
* redact it in derived reports where possible
* keep raw evidence isolated
* never expose PII in logs

Do not publish seller PII.

---

# 26. HUMAN REVIEW

Every investigation begins:

```text
human_review_status = unreviewed
```

Provide a mechanism to mark:

```text
reviewed
corrected
rejected
```

The reviewer must be able to inspect:

```text
listing
claims
signals
media
evidence
verification
uncertainties
```

---

# 27. TESTING

Write tests BEFORE declaring the phase complete.

Minimum tests:

### Collection

* valid listing input
* malformed URL
* inaccessible listing
* researcher-assisted input

### Claims

* extracts seller claims
* preserves claim source
* does not convert claims into verified facts

### Signals

* signal requires evidence
* unknown information remains unknown
* title alone cannot generate unsupported signals

### Evidence

* every signal references evidence
* evidence retains provenance
* visual evidence does not imply authenticity

### Media

* SHA-256 generated
* duplicate images detected
* media linked to investigation

### Verification

* corroborated
* contradicted
* inconclusive
* not_checked

### Privacy

* PII does not leak into logs
* derived report redacts sensitive values where required

### Report

* report generated
* evidence references resolve
* uncertainties displayed

Target:

```text
ALL TESTS PASS
```

---

# 28. VERY IMPORTANT — DO NOT REPEAT THE REDDIT DATA-CLEANING PROJECT

Do NOT spend this phase doing:

* more Reddit taxonomy cleanup
* more Reddit scraping
* RAG
* vector databases
* LangChain
* LangGraph
* autonomous agents
* fraud probability models
* scam scoring
* reverse image search
* AI image detection
* large-scale CV
* production dashboard
* browser extension
* OLX-wide crawler
* cloud deployment
* monetization

Those belong to later phases.

We need to test the actual investigation loop first.

---

# 29. PILOT EXPERIMENT

Once the implementation is ready, help prepare a controlled experiment with approximately:

## 10–20 OLX listings

Try to include a mixture of:

* unusually cheap electronics
* normal-priced electronics
* listings with WhatsApp/off-platform language
* listings without such language
* listings with business claims
* listings with invoice/receipt claims
* listings with multiple product images
* listings with sparse descriptions

Do NOT cherry-pick only suspicious-looking listings.

We need enough variation to determine whether the investigation framework is actually useful.

Record:

```text
investigation_id
listing_url
category
price
signals_found
evidence_count
verification_checks
uncertainties
human_review
```

---

# 30. SUCCESS CRITERIA

Phase 3 succeeds if we can take a real OLX listing and answer:

### 1. What does the listing claim?

### 2. What can TrustLens directly observe?

### 3. Which signals are actually present?

### 4. What evidence supports each signal?

### 5. What can be independently verified?

### 6. What contradicts the seller/listing claims?

### 7. What remains unknown?

### 8. What should a human verify next?

If we can do this reliably for 10–20 listings, Phase 3 is successful.

The objective is NOT to prove that TrustLens can identify scammers.

The objective is to prove that TrustLens can perform a reproducible, evidence-backed marketplace investigation.

---

# 31. IMPLEMENTATION PROCESS

Follow this order:

## STEP 1 — Inspect

Inspect the existing TrustLens repository.

Do not modify anything yet.

Report:

* architecture
* existing reusable modules
* CLI
* test setup
* relevant existing schemas
* where OLX functionality should fit

## STEP 2 — Design

Create a concise:

```text
PHASE_3_OLX_INVESTIGATION_DESIGN.md
```

with the proposed architecture.

## STEP 3 — Implement core schemas

Implement:

* investigation
* listing
* seller
* claims
* media
* signals
* evidence
* verification

## STEP 4 — Implement controlled collection

Support URL-based or researcher-assisted collection.

## STEP 5 — Implement evidence/media handling

## STEP 6 — Implement signal detection

## STEP 7 — Implement verification framework

## STEP 8 — Implement report generation

## STEP 9 — Add tests

## STEP 10 — Run the pilot

Do not jump straight into a huge implementation.

---

# 32. DEVELOPMENT RULE

Prefer simple, explicit Python over clever abstractions.

Use the existing project dependencies where possible.

Do not introduce a large dependency just to solve a small problem.

Keep modules testable.

Keep collection separate from analysis.

Keep analysis separate from verification.

Keep raw evidence separate from derived outputs.

---

# 33. FINAL OUTPUTS

When complete, produce:

```text
PHASE_3_OLX_INVESTIGATION_DESIGN.md

OLX investigation schemas

OLX collection module

Media handling

Signal library

Evidence model

Verification framework

Investigation report generator

CLI commands

Tests

Pilot documentation
```

And create:

```text
data/olx_pilot/
```

for the actual pilot investigations.

---

# 34. FINAL REPORT TO ME

When you finish implementation, do NOT just say "done."

Report:

### Repository changes

What files were created/modified.

### Architecture

How the OLX investigator works.

### Commands

Exact commands to run it.

### Data model

Important schemas.

### Evidence model

How evidence is linked to observations.

### Verification

What can be independently checked.

### Privacy

What is stored/redacted.

### Tests

Exact test count and result.

### Pilot readiness

What is ready.

### Remaining limitations

Be explicit.

### DO NOT

Claim that the system detects scams.

The correct statement is:

> TrustLens performs evidence-backed marketplace investigations and surfaces observable signals, verification results, contradictions, and uncertainties.

---

# FINAL PRIORITY

The priority hierarchy is:

```text
1. Real OLX investigation
2. Evidence provenance
3. Media + text together
4. Independent verification
5. Reproducibility
6. Human review
7. Small pilot
8. Automation later
```

Do NOT optimize for scale yet.

Do NOT optimize for model sophistication yet.

Do NOT build an "AI scam detector."

Build the smallest credible version of:

> "Give TrustLens a marketplace listing. Show me what is observable, what is claimed, what can be verified, what conflicts, and what I should check next."

Start by inspecting the existing repository and produce the Phase 3 design before making substantial code changes.
