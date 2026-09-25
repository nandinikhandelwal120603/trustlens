# TRUSTLENS — REDDIT MULTIMODAL DATASET INTELLIGENCE REPORT
**Phase 2 Multimodal Case Transformation & Evidence Analysis**

---

## 1. EXECUTIVE SUMMARY & LOCKED DATASET METRICS

This report presents the evidence-grounded multimodal analysis of the raw Reddit research collection for **TrustLens**. The dataset captures user-reported secondhand and firsthand marketplace fraud experiences, payment screenshots, QR codes, chat conversations, and seller listings.

### Locked Dataset Overview
* **Collection Window**: **2025-09-26 → 2026-09-19** (~1 year collection window; *not* a full two-year longitudinal dataset).
* **Total Raw Reddit Posts in Collection**: **178 posts**
* **Total Media Assets in Collection**: **330 assets** (0 download failures; 100% downloaded).
* **Geographic Filtering & Scope Control**:
  * **Excluded Non-India Posts**: **21 posts** (20 Pakistani posts from subreddits like `r/PakGamers`, `r/pakistan`, `r/PakistanAutoHub`, `r/PakistanLawyers`, `r/PakistaniTech`, `r/karachi`; 1 Romanian post `1u0elfw`).
  * **Filtered Indian Case Dataset**: **157 posts**
* **Indian Case Breakdown**:
  * **Posts with Media**: **67 posts** (containing 298 attached media assets)
  * **Posts without Media**: **90 posts** (text-only reports or title-only stubs)
  * **Full Text Stories (with body text)**: **95 posts**
  * **Title-Only Stubs**: **62 posts** (15 of which contain attached media evidence)

---

## 2. RAW VS. DEDUPLICATED CLUSTERING & MEDIA RECOVERY

### The Fareed / Honda City Crosspost Cluster
A prominent structural finding is the existence of heavy cross-posting across Indian subreddits (`r/IsThisAScamIndia`, `r/LegalAdviceIndia`, `r/IndianCyberHub`, `r/ps5india`).

* **Raw Post Count in Cluster**: **11 crossposts**
* **Raw Media Assets Referenced in Cluster**: **98 raw media references**
* **Unique Media Asset Count (SHA-256 verified)**: **18 unique SHA-256 files**

> **Methodological Principle**: TrustLens preserves all 178 raw Reddit post records and 330 raw media records to maintain full auditability. Pattern frequency statistics are evaluated on **deduplicated stories** so that a single 11× cross-posted story does not artificially distort marketplace risk rates.

---

## 3. SUBREDDIT & PRODUCT CATEGORY DISTRIBUTION

### Indian Subreddit Breakdown (157 Indian Posts)
| Subreddit | Raw Post Count | Percentage |
| :--- | :--- | :--- |
| `r/IsThisAScamIndia` | 30 | 19.1% |
| `r/LegalAdviceIndia` | 18 | 11.5% |
| `r/IndianCyberHub` | 5 | 3.2% |
| `r/pune` | 5 | 3.2% |
| `r/ps5india` | 6 | 3.8% |
| `r/IndianGaming` | 4 | 2.5% |
| `r/ScamSupport` | 3 | 1.9% |
| `r/mumbai` | 3 | 1.9% |
| `r/delhi` | 3 | 1.9% |
| `r/bangalore` | 3 | 1.9% |
| Other Indian Subreddits | 77 | 49.0% |

### Product Category Distribution (Indian Cases)
| Category | Raw Post Count | Key Brands / Models Observed |
| :--- | :--- | :--- |
| **Smartphone** | 52 | Apple iPhone 15/17 Pro Max, Google Pixel, Samsung S-series |
| **Laptop** | 38 | Apple MacBook M1/M2/M3, ASUS ROG/TUF, Lenovo ThinkPad |
| **Gaming Console** | 22 | Sony PlayStation 5, PlayStation 4, Xbox Series X |
| **Car / Vehicle** | 18 | Honda City, Mahindra Thar, Maruti Swift, Royal Enfield Bullet |
| **Camera** | 12 | Sony Alpha, Canon EOS, Vintage DigiCams |
| **Rental / Property** | 8 | 1BHK / 2BHK rental apartments in Bangalore/Pune |
| **Electronics / Other** | 7 | AirPods Pro, Smartwatches, PC Components |

---

## 4. RECURRING FRAUD MECHANISMS & TAXONOMY FREQUENCIES

Analysis of the 157 Indian post cases reveals clear recurring fraud vectors:

| Fraud Pattern | Raw Case Count | Deduplicated Count | Description / Modus Operandi |
| :--- | :--- | :--- | :--- |
| `advance_payment` / `deposit_request` | 68 | 54 | Seller demands booking token/advance before meeting or shipping |
| `army_persona` / `cisf_persona` | 24 | 18 | Seller claims to be military officer posted in remote location |
| `upi_payment` / `qr_payment` | 42 | 35 | QR code sent under pretext of 'receiving' money or paying deposit |
| `fake_invoice` / `canteen_receipt` | 21 | 16 | Fabricated Army Canteen or corporate GST invoice sent to build trust |
| `gate_pass_story` / `fake_courier` | 19 | 15 | Fake logistics transport / military gate-pass fee requested |
| `unrealistic_price` | 51 | 42 | Item listed at 40%-70% below prevailing market value |
| `whatsapp_migration` | 48 | 39 | Communication quickly redirected off OLX onto WhatsApp |
| `non_delivery` / `fake_seller` | 38 | 31 | Seller disappears immediately upon receiving initial payment |

---

## 5. CANDIDATE DISCOVERED PATTERNS

In addition to established taxonomy items, four candidate patterns emerged from the evidence:

1. **`defence_store_receipt_scam`**: Use of fake 'Army Canteen / Defence Store' invoices containing forged official stamps to justify low prices and demand advance transport fees.
2. **`macbook_m1_m2_suspiciously_cheap`**: Listings offering M1/M2 MacBooks for ₹25,000–₹32,000 using stolen corporate asset photos or 'Samsung India Electronics' clearance claims.
3. **`fake_tech_company_warehouse_clearance`**: Impersonation of legitimate corporate entities (e.g. *Innologic Electronics Pvt Ltd*) offering liquidation stock on OLX.
4. **`qr_reverse_charge_receive_money_trap`**: Scammers sending 'Pay' QR codes to sellers listing items, convincing them that scanning the QR will credit funds into their account.

---

## 6. RECURRING FRAUD JOURNEYS

```text
JOURNEY 1: Defence Officer Relocation & Canteen Gate-Pass Trap
Listing (Thar/iPhone at ~50% price)
   ↓
Contact on OLX → Immediate WhatsApp Migration
   ↓
Trust Building: Military ID / Army Canteen Receipt Shared
   ↓
Payment Request: "Pay ₹2,000 Gate-Pass / Transport Fee"
   ↓
Additional Fee Demand: "Courier clearance stuck; pay ₹5,000 security deposit"
   ↓
Victim Realizes Scam / Seller Disappears
```

```text
JOURNEY 2: QR Code Reverse-Charge Receive Money Trap
Listing Created by Legitimate Seller
   ↓
Scammer Contacts Seller Posing as Eager Buyer
   ↓
Scammer Offers Advance Payment via UPI / QR Code
   ↓
Scammer Sends QR Code with Text "Scan to Receive ₹5,000"
   ↓
Victim Scans QR & Enters UPI PIN → Money Debited from Victim
   ↓
Scammer Claims Error & Sends 2nd QR to "Refund" → Double Debit
```

---

## 7. OBSERVABLE MARKETPLACE SIGNALS

TrustLens bridges Reddit research into observable marketplace signals that can be inspected directly on live listings:

1. **Price Delta Anomaly**: Listing price >35% below category median.
2. **Description Pattern Match**: Text containing relocation excuses ("army transfer", "urgent relocation", "canteen delivery").
3. **Contact Redirection**: Description or chat insisting on immediate WhatsApp contact.
4. **Image Perceptual Similarity**: Photo matching previously flagged stolen product images or generic web assets.
5. **Entity Claim Anomaly**: Claims of corporate liquidation stock or official army canteen dispatch on individual C2C accounts.

---

## 8. INVESTIGATION HYPOTHESES

* **`INV-001`**: **Army / Defence Relocation & Gate-Pass Scam**
  * *Target Categories*: Car, Bike, Laptop
  * *Search Queries*: `"Army officer urgent sale"`, `"Thar army transfer"`, `"Canteen delivery car"`
* **`INV-002`**: **High-End Tech Warehouse Clearance & Booking Token Trap**
  * *Target Categories*: Smartphone, Laptop, Gaming Console
  * *Search Queries*: `"iPhone 17 cheap OLX"`, `"PS5 15k urgent"`, `"MacBook M2 30k warehouse"`

---

## 9. CRITICAL EVIDENCE & RECONCILIATION RULE

All records strictly enforce the **Critical Evidence Rule**:
* **Reported Claim**: What the Reddit author states (e.g., *"Seller sent me a genuine Army ID card"*).
* **Visual Observation**: What is actually visible in attached screenshots (e.g., *Image displays an ID-like document with military branding*).
* **Verified Fact**: Status remains **Unverified** unless corroborated by independent ground truth.

---

## 10. HUMAN REVIEW QUEUE & PRIVACY COMPLIANCE

* **Human Review Queue**: **38 cases** flagged for manual review due to image-only stubs, candidate pattern evaluation, low-quality metadata, or sensitive document visual content.
* **Privacy Compliance**: All telephone numbers, UPI handles, full personal names, and document IDs have been redacted or hashed in analytical outputs.

---

## 11. NEXT STEPS & LIMITATIONS

### Dataset Limitations
1. **Selection Bias**: Reddit reports represent self-selected incidents where users suspected or experienced fraud.
2. **Unverified Claims**: Statements reflect author assertions rather than legally adjudicated findings.
3. **Temporal Constraint**: Dataset spans 2025-09-26 to 2026-09-19.

### Next Step in TrustLens Pipeline
Use the generated **Marketplace Signal Library** and **Investigation Hypotheses** to design targeted, non-intrusive marketplace observational research for the next phase.

---
*Report generated by TrustLens Multimodal Evidence Processor on 2026-09-20.*
