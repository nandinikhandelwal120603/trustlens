# TRUSTLENS — PHASE 3: MARKETPLACE INVESTIGATION MATRIX
## Empirical Research Matrix for Targeted OLX Acquisition

- **Version:** 1.0.0
- **Date:** 2026-09-21
- **Status:** APPROVED FOR EXECUTION
- **Source of Truth:** Phase 2 Reddit Multimodal Fraud Dataset (157 Indian Marketplace Fraud Reports)
- **Scope:** Defines *what* product classes, investigation suites, target queries, and baseline queries will be captured from OLX India using the researcher-controlled `capture-olx` extension and ingested into the TrustLens Media Intelligence Layer.

---

## 1. Executive Summary & Research Framework

The TrustLens **Marketplace Media Intelligence Layer** and **`capture-olx` Extension** provide an audited, idempotent, and deterministic pipeline for capturing, indexing, fingerprinting, and clustering marketplace listings, images, and text.

Before capturing new marketplace data, this document establishes a **strict research matrix** derived from the empirical findings of Phase 2 (157 Reddit Indian marketplace fraud cases).

```
┌────────────────────────────────────────────────────────┐
│     PHASE 2 REDDIT FRAUD INTELLIGENCE (157 CASES)      │
│  • Smartphones (52)    • Laptops (38)   • Gaming (22)  │
│  • Vehicles (18)       • Cameras (12)   • Rental (8)   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│        INVESTIGATION SUITES & RESEARCH HYPOTHESES      │
│  • INV-001: Defence / Army Relocation & Gate-Pass     │
│  • INV-002: High-End Tech Clearance & Booking Token   │
│  • INV-003: QR Reverse-Charge / Token Trap             │
│  • INV-004: Vehicle Remote Delivery & Transport Fee   │
│  • BASELINE: Neutral Market Benchmark                 │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│        TARGETED OLX SEARCH QUERIES & BASELINES         │
│  Targeted Query (Hypothesis)  ↔  Baseline Query (Norm) │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│    CONTROLLED BROWSER CAPTURE & MEDIA INTELLIGENCE     │
│  • capture-olx Extension  • Local Media Fingerprints   │
│  • Perceptual Clusters    • Deterministic Text Reuse   │
└────────────────────────────────────────────────────────┘
```

### Core Methodological Principles

1. **Observational Research, Not Fraud Scoring**: This layer discovers, indexes, and measures observable marketplace patterns (text claims, price differentials, image reuse, off-platform migration). It does **NOT** generate fraud scores, scam probabilities, or seller rankings.
2. **Empirically Grounded**: Only product classes and narratives substantiated by the Phase 2 Reddit corpus are included.
3. **Paired Baseline Methodology**: Every targeted search query is paired with a neutral baseline query in the same category to measure signal prevalence and false-positive rates accurately.
4. **Data Immutability**: All raw capture JSON artifacts remain permanently immutable in local storage.

---

## 2. Investigation Suites Structure

| Suite ID | Suite Name | Primary Focus / Journey Narrative | Target Categories | Key Reddit Mechanisms |
| :--- | :--- | :--- | :--- | :--- |
| **`INV-001`** | **Defence / Relocation Persona & Gate-Pass** | Sellers claiming Indian Army / CISF officer relocation, posting at remote cantonments/airports, offering steep discounts, and demanding advance gate-pass or courier fees. | Vehicles, Smartphones, Laptops | `army_persona`, `cisf_persona`, `advance_payment`, `gate_pass`, `fake_canteen_receipt` |
| **`INV-002`** | **High-End Tech Clearance & Warehouse Stock** | Listings offering premium electronics at 40–70% below market value under the pretext of warehouse stock liquidation, corporate office closing, or bulk clearance. Demands booking token or advance. | Smartphones, Laptops, Desktops, Gaming, Cameras | `unrealistic_price`, `warehouse_clearance`, `whatsapp_migration`, `advance_payment`, `fake_invoice` |
| **`INV-003`** | **QR Reverse-Charge / Token Trap Interaction** | Listings targeting sellers/buyers with fake QR codes ("scan to receive advance money") or immediate off-platform contact demands via WhatsApp/phone. | Smartphones, Gaming Consoles, Cameras, Other Electronics | `qr_payment`, `upi_payment`, `whatsapp_migration`, `booking_token` |
| **`INV-004`** | **Vehicle Remote Delivery & Transport Escrow** | High-value cars, 4x4s, and motorcycles listed at discounted prices with claims that the vehicle is in a distant military cantonment or state border, requiring transport/escrow deposit. | Cars, Motorcycles, Scooters | `remote_posting`, `transport_fee`, `delivery_deposit`, `advance_payment` |
| **`BASELINE`** | **Neutral Marketplace Benchmark** | Organic, unprompted category searches to establish normal market median prices, standard descriptive vocabulary, and organic image reuse baselines. | All Categories | `neutral_market_norm` |

---

## 3. Product Class Evaluation Matrix

### 3.1. Smartphones

| Field | Details |
| :--- | :--- |
| **Product Class** | **Smartphones** |
| **Specific Products to Search** | • **Apple iPhone:** iPhone 13, 14, 15, 15 Pro, 15 Pro Max, 16 Pro<br>• **Samsung Flagships:** Galaxy S23 Ultra, S24 Ultra, Z Fold 5<br>• **Google Pixel:** Pixel 7 Pro, Pixel 8 Pro, Pixel 9 Pro<br>• **OnePlus:** OnePlus 11, 12 |
| **Reddit-Derived Pattern(s)** | • Reddit Case Count: **52 cases** (Rank 1)<br>• Reused boxed/sealed stock photos<br>• Army officer posted in cantonment selling gifted iPhone<br>• Office/shop closing clearance sale<br>• "WhatsApp only" contact with advance token demand |
| **Investigation Hypothesis** | Listings claiming steep discounts on recent iPhone/Samsung flagships under "urgent transfer" or "company bulk stock" will exhibit high cross-listing text reuse, off-platform WhatsApp migration tokens, and image reuse across different accounts. |
| **OLX Target Queries** | `"iPhone cheap"`, `"iPhone urgent sale"`, `"iPhone warehouse clearance"`, `"iPhone company clearance"`, `"iPhone army transfer"`, `"iPhone 15 Pro urgent"`, `"Samsung S24 Ultra cheap"`, `"Pixel 8 Pro urgent sale"` |
| **Baseline Queries** | `"iPhone 15"`, `"iPhone 14 Pro"`, `"iPhone 13 128gb"`, `"Samsung Galaxy S23 Ultra"`, `"Google Pixel 8"` |
| **Observable Marketplace Signals** | `unusually_low_price` (>35% discount), `army_persona`, `whatsapp_migration`, `warehouse_clearance`, `same_title`, `exact_image_reuse` |
| **Why Class is Relevant** | Highest volume category in empirical Reddit dataset; highest liquidity and consumer search frequency in secondary markets. |
| **Priority for Initial Capture** | **TIER 1 (Immediate / Ongoing Pilot Expansion)** |
| **Notes / Limitations** | Common titles like *"iPhone 15 Pro"* occur organically across legitimate sellers; text reuse must be evaluated alongside phone numbers, pricing, and image clusters. |

---

### 3.2. Laptops

| Field | Details |
| :--- | :--- |
| **Product Class** | **Laptops** |
| **Specific Products to Search** | • **Apple MacBook Air:** M1 (2020), M2 (2022), M3 (2024)<br>• **Apple MacBook Pro:** 14"/16" M1 Pro/Max, M2 Pro, M3 Pro<br>• **Gaming Laptops:** Asus ROG Zephyrus/Strix, Lenovo Legion 5/7, Acer Predator Helios, Dell Alienware, HP Omen |
| **Reddit-Derived Pattern(s)** | • Reddit Case Count: **38 cases** (Rank 2)<br>• "IT company closing / startup liquidation" narrative<br>• "Bought from Army CSD canteen / duty free" claim with fake GST/canteen bill<br>• Low price (₹25,000–₹40,000 for M1/M2 MacBooks vs ₹55,000–₹95,000 market)<br>• Token deposit requested for courier dispatch |
| **Investigation Hypothesis** | Corporate liquidation and defence claims on MacBooks and premium gaming laptops correlate with off-platform contact redirection, identical description templates across multiple cities, and unverified invoice claims. |
| **OLX Target Queries** | `"MacBook cheap"`, `"MacBook Air clearance"`, `"MacBook Pro urgent sale"`, `"MacBook warehouse"`, `"MacBook company clearance"`, `"MacBook M1 cheap"`, `"MacBook M2 urgent"`, `"gaming laptop cheap"`, `"gaming laptop clearance"`, `"Asus ROG urgent sale"`, `"laptop army transfer"` |
| **Baseline Queries** | `"MacBook Air M1"`, `"MacBook Air M2"`, `"MacBook Pro M2"`, `"MacBook Pro 14"`, `"Lenovo Legion 5"`, `"Asus ROG Strix"`, `"Dell XPS 15"` |
| **Observable Marketplace Signals** | `unusually_low_price`, `warehouse_clearance`, `invoice_claim`, `advance_payment`, `whatsapp_migration`, `perceptual_image_match` |
| **Why Class is Relevant** | Second highest category in Reddit dataset; high unit value (₹50k–₹1.5L) makes it a prime target for advance payment and token demands. |
| **Priority for Initial Capture** | **TIER 1 (Immediate - First Wave Tomorrow)** |
| **Notes / Limitations** | Differentiate genuine corporate IT asset liquidators (refurbishers with physical shops) from remote individual listings requiring advance deposits. |

---

### 3.3. Apple Desktops & High-End PC Hardware

| Field | Details |
| :--- | :--- |
| **Product Class** | **Apple Desktops & PC Hardware** |
| **Specific Products to Search** | • **Apple Mac Mini:** Mac Mini M1, Mac Mini M2, Mac Mini M2 Pro<br>• **Apple Mac Studio / iMac:** M1 iMac 24", Mac Studio M1/M2<br>• **High-End PC / GPU:** RTX 3080, RTX 4070/4080/4090, Custom Gaming Desktops |
| **Reddit-Derived Pattern(s)** | • Reddit Case Count: **4 cases**<br>• Graphic card / PC build scams (full payment taken for high-end GPU, parcel sent with dummy weight or not sent)<br>• Mac Mini listed at ₹15,000–₹22,000 (market: ₹35,000–₹50,000)<br>• "Urgent relocation from Bangalore/Hyderabad" |
| **Investigation Hypothesis** | Desktop computing hardware with compact form factors (Mac Mini, standalone GPUs) will show geographic relocation claims and requests for full or partial courier advance payments due to non-local buyer appeal. |
| **OLX Target Queries** | `"Mac Mini cheap"`, `"Mac Mini M1 urgent"`, `"Mac Mini clearance"`, `"Mac Mini M2 cheap"`, `"iMac M1 urgent sale"`, `"RTX 4080 cheap"`, `"RTX 3080 urgent sale"`, `"gaming PC full setup cheap"` |
| **Baseline Queries** | `"Mac Mini M1"`, `"Mac Mini M2"`, `"Apple iMac 24"`, `"RTX 3080 graphic card"`, `"RTX 4070"`, `"custom gaming pc"` |
| **Observable Marketplace Signals** | `unusually_low_price`, `advance_payment`, `whatsapp_migration`, `same_title`, `exact_image_reuse` |
| **Why Class is Relevant** | Mac Mini M1/M2 has become a major target in Indian tech communities due to high demand among developers and students seeking entry-level Apple silicon. |
| **Priority for Initial Capture** | **TIER 2 (High - Capture alongside Laptops)** |
| **Notes / Limitations** | Older Intel Mac Minis (2012, 2014, 2018) legitimately trade at ₹10,000–₹20,000; benchmark model matching must distinguish Intel vs Apple Silicon (M1/M2). |

---

### 3.4. Gaming Consoles

| Field | Details |
| :--- | :--- |
| **Product Class** | **Gaming Consoles** |
| **Specific Products to Search** | • **Sony PlayStation 5:** PS5 Disc Edition, PS5 Digital, PS5 Slim<br>• **Sony PlayStation 4:** PS4 Slim, PS4 Pro (1TB, jailbroken/firmware 9.00)<br>• **Microsoft Xbox:** Xbox Series X, Xbox Series S<br>• **Nintendo:** Nintendo Switch OLED (where supported) |
| **Reddit-Derived Pattern(s)** | • Reddit Case Count: **22 cases** (Rank 3)<br>• PS5 listed at ₹18,000–₹25,000 (market: ₹38,000–₹45,000)<br>• "Son went abroad / gift from uncle / bought for exams but selling"<br>• Fake Flipkart/Amazon invoice provided as proof<br>• Demand for ₹1,000–₹3,000 "shipping/courier insurance" |
| **Investigation Hypothesis** | PS5 and PS4 Pro listings with prices >40% below retail will frequently use recycled unboxing/shelf photos and direct users to phone/WhatsApp for "immediate token confirmation." |
| **OLX Target Queries** | `"PS5 cheap"`, `"PS5 urgent sale"`, `"PS5 clearance"`, `"PS5 warehouse"`, `"PS5 disc edition cheap"`, `"PS5 slim urgent"`, `"PS4 Pro cheap"`, `"PS4 jailbreak urgent"`, `"Xbox Series X cheap"`, `"Xbox Series S urgent sale"` |
| **Baseline Queries** | `"PS5 console"`, `"PlayStation 5 disc edition"`, `"PS5 slim"`, `"PS4 Pro 1TB"`, `"Xbox Series X"`, `"Xbox Series S console"` |
| **Observable Marketplace Signals** | `unusually_low_price`, `invoice_claim`, `advance_payment`, `whatsapp_migration`, `exact_image_reuse`, `perceptual_image_match` |
| **Why Class is Relevant** | Third most frequent category in Reddit dataset; high youth demographic target with high susceptibility to token deposit demands. |
| **Priority for Initial Capture** | **TIER 1 (Immediate - First Wave Tomorrow)** |
| **Notes / Limitations** | PS4 base models trade legitimately around ₹12,000–₹16,000. Price benchmarks must distinguish PS4 FAT vs PS4 Pro vs PS5 Disc/Digital. |

---

### 3.5. Cameras & Optical Equipment

| Field | Details |
| :--- | :--- |
| **Product Class** | **Cameras & Optical Equipment** |
| **Specific Products to Search** | • **Mirrorless:** Sony Alpha A7 III, A7 IV, Sony A6400, A6700, Fujifilm X-T4/X-T5<br>• **DSLR:** Canon EOS 200D II, 1500D, 5D Mark IV, 80D, Nikon D750, D850<br>• **Lenses / Action:** Sony G-Master lenses, Canon EF/RF lenses, GoPro Hero 11/12/13, DJI Osmo Action |
| **Reddit-Derived Pattern(s)** | • Reddit Case Count: **12 cases** (Rank 5)<br>• Professional wedding/studio photography gear listed at amateur prices<br>• "Studio shut down / owner moving to UAE/Canada"<br>• Serial numbers concealed or stolen catalog photos used<br>• Advance demanded for doorstep trial or courier delivery |
| **Investigation Hypothesis** | High-end mirrorless cameras (Sony A7 series) listed with lenses at deep discounts exhibit repetitive descriptions regarding studio liquidation and require advance shipping tokens. |
| **OLX Target Queries** | `"Sony A7 cheap"`, `"Sony A7 III urgent sale"`, `"Sony A6400 cheap"`, `"Canon 200D urgent sale"`, `"Canon 5D cheap"`, `"DSLR camera clearance"`, `"mirrorless camera urgent"`, `"camera studio clearance"`, `"GoPro Hero urgent sale"` |
| **Baseline Queries** | `"Sony A7 III"`, `"Sony Alpha A7 IV"`, `"Sony A6400 camera"`, `"Canon EOS 200D"`, `"Canon 5D Mark IV"`, `"Nikon D750"`, `"GoPro Hero 12"` |
| **Observable Marketplace Signals** | `unusually_low_price`, `warehouse_clearance`, `advance_payment`, `whatsapp_migration`, `exact_image_reuse` |
| **Why Class is Relevant** | Substantial presence in Reddit corpus (12 cases); high individual item value (₹40,000–₹2,00,000) and highly specialized product specifications. |
| **Priority for Initial Capture** | **TIER 2 (High - Capture after Laptops & Consoles)** |
| **Notes / Limitations** | Entry-level DSLRs (Canon 1500D, Nikon D3200) have low natural market prices (₹15,000–₹22,000). Specific model-level price benchmarks are required. |

---

### 3.6. Vehicles (Cars & Two-Wheelers)

| Field | Details |
| :--- | :--- |
| **Product Class** | **Vehicles (Cars, Motorcycles, Scooters)** |
| **Specific Products to Search** | • **4x4 / SUVs:** Mahindra Thar, Mahindra Scorpio, Hyundai Creta, Tata Harrier<br>• **Sedans / Hatchbacks:** Honda City, Maruti Suzuki Swift, Hyundai i20<br>• **Motorcycles:** Royal Enfield Classic 350, Bullet 350, Himalayan, KTM Duke 200/390, Yamaha R15<br>• **Scooters:** Honda Activa 6G, TVS Jupiter |
| **Reddit-Derived Pattern(s)** | • Reddit Case Count: **18 cases** (Rank 4)<br>• **Archetypal Army Relocation / CISF Persona (FJ-001):** "Army Subedar / Officer transferred to Assam/Leh/Kashmir; car stationed at Military Cantonment or Airport cargo"<br>• Delivery via "Army Transport / Canteen Cargo Service"<br>• Demands for "Gate Pass ₹2,500", "NOC Deposit ₹5,000", "Transport Insurance ₹10,000" before physical vehicle inspection |
| **Investigation Hypothesis** | Vehicle listings featuring explicit military/cisf transfer narratives and prices 50–70% below bluebook value will display cross-state phone numbers, template descriptions, and demand gate-pass/transport fees. |
| **OLX Target Queries** | `"army transfer car"`, `"army officer car urgent sale"`, `"cisf car transfer"`, `"canteen car"`, `"defence canteen car"`, `"Thar army transfer"`, `"Mahindra Thar urgent sale"`, `"army transfer bike"`, `"Royal Enfield army transfer"`, `"Bullet army transfer"`, `"urgent army sale bike"`, `"gate pass car"`, `"transport fee car"` |
| **Baseline Queries** | `"Mahindra Thar 4x4"`, `"Honda City ivtec"`, `"Maruti Swift VXi"`, `"Royal Enfield Classic 350"`, `"Royal Enfield Bullet 350"`, `"KTM Duke 390"`, `"Honda Activa 6G"` |
| **Observable Marketplace Signals** | `army_persona`, `unusually_low_price`, `advance_payment` (gate-pass/transport), `whatsapp_migration`, `same_title`, `exact_image_reuse` |
| **Why Class is Relevant** | Vehicles represent the highest financial loss category in the Reddit dataset and embody the complete multi-step gate-pass fraud journey. |
| **Priority for Initial Capture** | **TIER 1 (Immediate - First Wave Tomorrow)** |
| **Notes / Limitations** | Vehicle listings on OLX often contain RTO registration data and multi-photo sets. Cluster analysis will determine if the same car photos are posted across different Indian cities. |

---

### 3.7. Rental / Property

| Field | Details |
| :--- | :--- |
| **Product Class** | **Rental & Residential Property** |
| **Specific Products to Search** | • **1BHK / 2BHK Furnished Apartments:** Bangalore (Koramangala, Indiranagar, HSR), Mumbai (Bandra, Andheri), Gurgaon (Cyber City, Sector 48), Pune (Hinjewadi, Viman Nagar)<br>• **Studio Rooms / PG:** Single occupancy luxury studio |
| **Reddit-Derived Pattern(s)** | • Reddit Case Count: **8 cases** (Rank 6)<br>• "Owner is CISF / Airport Authority / Army officer posted at remote base"<br>• Key is with building security or Society gatekeeper<br>• "Gate pass / visiting token of ₹2,000–₹4,000 required to generate visitor QR code before building guard allows flat viewing" |
| **Investigation Hypothesis** | Premium rental apartments advertised significantly below locality median rents will claim out-of-station owner identity and require advance gate-pass/security registration fees before physical keys are shown. |
| **OLX Target Queries** | `"1BHK army transfer rent"`, `"flat gate pass rent"`, `"urgent rent furnished flat"`, `"flat deposit low rent"`, `"house rent army officer"` |
| **Baseline Queries** | `"1BHK furnished rent Koramangala"`, `"2BHK rent HSR Layout"`, `"1BHK rent Gurgaon"`, `"2BHK rent Andheri West"`, `"studio apartment rent Pune"` |
| **Observable Marketplace Signals** | `army_persona`, `advance_payment` (gate pass / visit token), `unusually_low_price`, `whatsapp_migration` |
| **Why Class is Relevant** | Explicitly documented in 8 Reddit cases as a growing urban advance-fee mechanism targeting relocating professionals. |
| **Priority for Initial Capture** | **TIER 3 (Secondary Phase)** |
| **Notes / Limitations** | Rental listings on OLX have distinct geographic clustering by city locality; baseline comparison requires locality-specific rental pricing indices. |

---

### 3.8. Other High-Value Electronics

| Field | Details |
| :--- | :--- |
| **Product Class** | **Other Electronics (Tablets, Wearables, Audio)** |
| **Specific Products to Search** | • **Apple iPad:** iPad Air M1/M2, iPad Pro 11"/12.9", iPad 10th Gen<br>• **Apple Watch:** Apple Watch Ultra, Ultra 2, Series 8/9<br>• **Audio:** Apple AirPods Pro 2, AirPods Max, Sony WH-1000XM5<br>• **Drones / Action:** DJI Mini 3/4 Pro |
| **Reddit-Derived Pattern(s)** | • Reddit Case Count: **7 cases** (Rank 7)<br>• Counterfeit/clone products sold as "sealed original with GST invoice"<br>• "Gift item / company raffle prize never opened"<br>• Listed at 50% retail price; seller insists on courier delivery or upfront token |
| **Investigation Hypothesis** | Sealed audio accessories and Apple Watches listed at deep discounts with claims of "unwanted gift / company raffle" show high text reuse across metropolitan regions and unverified GST invoice assertions. |
| **OLX Target Queries** | `"iPad Pro cheap"`, `"iPad Pro urgent sale"`, `"Apple Watch Ultra cheap"`, `"Apple Watch Ultra urgent"`, `"AirPods Max cheap"`, `"AirPods Pro sealed urgent"`, `"DJI drone cheap"`, `"DJI Mini urgent sale"` |
| **Baseline Queries** | `"Apple iPad Air M1"`, `"Apple iPad Pro 11"`, `"Apple Watch Ultra 2"`, `"AirPods Pro 2nd generation"`, `"Sony WH-1000XM5"`, `"DJI Mini 3 Pro"` |
| **Observable Marketplace Signals** | `unusually_low_price`, `invoice_claim`, `warehouse_clearance`, `whatsapp_migration`, `same_title` |
| **Why Class is Relevant** | Completes the consumer electronics ecosystem identified in the Reddit dataset; frequent vehicle for fake invoice claims. |
| **Priority for Initial Capture** | **TIER 2 (High - Capture alongside Smartphones)** |
| **Notes / Limitations** | First-party and third-party replicas (clones) are common; physical hardware inspection is impossible via OLX DOM; research focus remains on listing claims, text reuse, and advance token requirements. |

---

## 4. Master Search Query Reference: Target vs. Baseline

To ensure disciplined scientific execution, every targeted discovery query has a corresponding baseline query:

```
┌───────────────────────────────────────┐         ┌───────────────────────────────────────┐
│        TARGET SEARCH QUERIES          │         │        BASELINE SEARCH QUERIES        │
│  (Hypothesis-Driven Discovery)       │         │  (Neutral Market Distribution)        │
├───────────────────────────────────────┤         ├───────────────────────────────────────┤
│ • MacBook Air clearance               │  <--- > │ • MacBook Air M1                      │
│ • PS5 urgent sale                     │  <--- > │ • PS5 console                         │
│ • Thar army transfer                  │  <--- > │ • Mahindra Thar 4x4                   │
│ • Bullet army transfer                │  <--- > │ • Royal Enfield Classic 350           │
│ • Sony A7 III urgent sale             │  <--- > │ • Sony A7 III                         │
│ • Mac Mini M1 cheap                   │  <--- > │ • Mac Mini M1                         │
│ • iPhone warehouse clearance          │  <--- > │ • iPhone 15                           │
└───────────────────────────────────────┘         └───────────────────────────────────────┘
```

### Comprehensive Query Mapping Table

| Investigation ID | Category | Target Query (Discovery) | Baseline Query (Control) | Primary Hypothesis / Justification |
| :--- | :--- | :--- | :--- | :--- |
| **`INV-002`** | Laptops | `"MacBook cheap"` | `"MacBook Air M1"` | Warehouse/clearance narrative price anomaly |
| **`INV-002`** | Laptops | `"MacBook Air clearance"` | `"MacBook Air M2"` | Corporate liquidation claim |
| **`INV-002`** | Laptops | `"MacBook Pro urgent sale"` | `"MacBook Pro M2"` | Urgent relocation discount |
| **`INV-002`** | Laptops | `"gaming laptop cheap"` | `"Lenovo Legion 5"` | Deep discount on high-end gaming hardware |
| **`INV-002`** | Gaming | `"PS5 cheap"` | `"PS5 console"` | Advance shipping token requirement |
| **`INV-002`** | Gaming | `"PS5 urgent sale"` | `"PlayStation 5 disc edition"` | Fake invoice and rapid liquidation claim |
| **`INV-002`** | Gaming | `"PS4 Pro cheap"` | `"PS4 Pro 1TB"` | Below-market console pricing |
| **`INV-001`** | Vehicles | `"Thar army transfer"` | `"Mahindra Thar 4x4"` | Military relocation gate-pass trap (FJ-001) |
| **`INV-001`** | Vehicles | `"army transfer car"` | `"Honda City ivtec"` | Transport fee / canteen delivery narrative |
| **`INV-001`** | Vehicles | `"Bullet army transfer"` | `"Royal Enfield Classic 350"` | Defence canteen motorcycle relocation |
| **`INV-001`** | Vehicles | `"army transfer bike"` | `"KTM Duke 390"` | Gate-pass deposit request |
| **`INV-002`** | Cameras | `"Sony A7 cheap"` | `"Sony A7 III"` | Studio liquidation / stolen media |
| **`INV-002`** | Cameras | `"Canon 200D urgent sale"` | `"Canon EOS 200D"` | Advance token for courier trial |
| **`INV-002`** | Desktops | `"Mac Mini cheap"` | `"Mac Mini M1"` | Entry Apple silicon discount anomaly |
| **`INV-002`** | Desktops | `"Mac Mini M1 urgent"` | `"Mac Mini M2"` | Urgent seller relocation narrative |
| **`INV-002`** | Other | `"Apple Watch Ultra cheap"` | `"Apple Watch Ultra 2"` | Gift/clearance claim with fake bill |
| **`INV-002`** | Other | `"iPad Pro cheap"` | `"Apple iPad Pro 11"` | Advance deposit demand |

---

## 5. Observable Marketplace Signals Definition

The TrustLens investigation framework strictly detects **observable signals** without making automated fraud inferences:

```
                                  LISTING TEXT & MEDIA
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               ▼                            ▼                            ▼
      [PRICE ANOMALY]              [PERSONA & CLAIMS]           [MEDIA & TEXT REUSE]
 • unusually_low_price        • army_persona               • exact_image_reuse (SHA-256)
   (>35% discount below         (military/CISF claim)      • perceptual_image_match
    category median)          • warehouse_clearance          (pHash/dHash/aHash ≤ 10)
                              • invoice_claim              • same_title (Unicode NFKC)
                              • advance_payment            • similar_description
                                (token / gate pass)          (Jaccard overlap ≥ 0.70)
                              • whatsapp_migration
                                (off-platform contact)
```

| Signal Identifier | Detection Logic | Confidence Level | Neutral Investigation Interpretation |
| :--- | :--- | :--- | :--- |
| **`unusually_low_price`** | Numerical price is ≥35% below established model median benchmark | High | Price is statistically anomalous for the stated product tier. |
| **`army_persona`** | Regex matches `army`, `cisf`, `defence`, `military`, `posted at`, `cantonment` | High | Seller asserts military identity in listing copy (unverified). |
| **`advance_payment`** | Text demands `advance`, `booking token`, `gate pass`, `delivery charge first` | High | Transaction requires buyer payment prior to physical goods inspection. |
| **`whatsapp_migration`** | Directs communication to WhatsApp / phone number regex `\b[6-9]\d{9}\b` | High | Seller attempts to shift transaction conversation off-platform. |
| **`warehouse_clearance`** | Text asserts `warehouse clearance`, `company clearance`, `office closing` | Medium | Seller asserts corporate liquidation context (unverified). |
| **`invoice_claim`** | Text asserts `gst bill`, `original bill`, `canteen receipt`, `defence receipt` | Medium | Listing claims verifiable purchase documentation exists. |
| **`exact_image_reuse`** | Identical SHA-256 hash across distinct listing IDs or seller IDs | Deterministic | Exact image asset binary is shared between multiple listings. |
| **`perceptual_image_match`**| pHash / dHash / aHash Hamming distance ≤ configured threshold (10) | Statistical | Image visual features are perceptually similar (crop/recompress). |
| **`same_title`** | Normalized Unicode NFKC title match across distinct listings | Deterministic | Multiple listings share identical title phrasing. |
| **`similar_description`** | Token Jaccard similarity ≥ 0.70 across listing descriptions | Statistical | Multiple listings share substantial description copy. |

---

## 6. Capture Strategy & Execution Plan

### 6.1. Workflow Architecture

```text
1. RESEARCHER BROWSER (Chrome + capture-olx extension)
   ├── Navigate to OLX India search URL (Target or Baseline query)
   ├── Scroll to render target result cards (100–240 cards)
   ├── Open extension popup → Click "Capture Listings"
   └── Export JSON → trustlens_olx_<query>_<timestamp>.json

2. TRUSTLENS INGESTION & MEDIA INTELLIGENCE
   ├── CLI Ingest: trustlens marketplace ingest --file <export_json>
   ├── Database: SQLite (trustlens.db)
   ├── Fingerprinting: SHA-256, pHash, dHash, aHash for available media
   ├── Deduplication: Deterministic text reuse & exact image clustering
   └── Provenance: Preserves capture context, search queries, and timestamps
```

### 6.2. Execution Roadmap & Priority Tiers

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             EXECUTION ROADMAP                                    │
├────────────────────────────────┬───────────────────────────────┬─────────────────┤
│ TIER 1: IMMEDIATE PRIORITY     │ TIER 2: SECONDARY TECH        │ TIER 3: URBAN   │
│ (First Wave Captures Tomorrow) │ (Wave Two Captures)           │ (Wave Three)    │
├────────────────────────────────┼───────────────────────────────┼─────────────────┤
│ 1. Laptops (MacBook Air/Pro)   │ 1. Apple Desktops (Mac Mini)  │ 1. Rentals/PGs  │
│ 2. Gaming (PS5, PS4 Pro)       │ 2. Android Flagships (S24/Pix)│ 2. Audio/Watch  │
│ 3. Vehicles (Thar, Bullet)     │ 3. Gaming Laptops (ROG/Legion)│ 3. Drones       │
│ 4. Cameras (Sony A7, Canon)    │ 4. Studio Cameras & Lenses    │                 │
└────────────────────────────────┴───────────────────────────────┴─────────────────┘
```

#### Tier 1 Target Plan (Day 1 — Tomorrow)
1. **Laptops Suite (`INV-002` + `BASELINE`)**:
   - `MacBook Air clearance` vs `MacBook Air M1`
   - `MacBook Pro urgent sale` vs `MacBook Pro M2`
   - Target result: ~200–400 listings across targeted and baseline queries.
2. **Gaming Consoles Suite (`INV-002` + `BASELINE`)**:
   - `PS5 cheap` & `PS5 urgent sale` vs `PS5 console`
   - `PS4 Pro cheap` vs `PS4 Pro 1TB`
   - Target result: ~200–300 listings.
3. **Vehicles Suite (`INV-001` + `BASELINE`)**:
   - `Thar army transfer` vs `Mahindra Thar 4x4`
   - `Bullet army transfer` vs `Royal Enfield Classic 350`
   - Target result: ~200–300 listings.
4. **Cameras Suite (`INV-002` + `BASELINE`)**:
   - `Sony A7 cheap` vs `Sony A7 III`
   - `Canon 200D urgent sale` vs `Canon EOS 200D`
   - Target result: ~150–250 listings.

---

## 7. Compliance, Ethics & Researcher Safety

1. **No Automated Scraping / No Crawlers**: All collection is strictly conducted via human researcher navigation in the browser using the `capture-olx` extension.
2. **No Seller Interaction / No Deception**: TrustLens does not message sellers, engage in undercover chats, or negotiate prices. All data captured is publicly exposed on standard marketplace web pages.
3. **Privacy by Design**: Personal phone numbers and contact handles are normalized and stored safely; no raw personal identities are published.
4. **No Premature Accusation**: Terms like "scammer," "fraudster," or "confirmed fraud" are strictly prohibited in the codebase and output schemas. All observations remain `candidate_match`, `unverified`, or `investigation_signal`.
5. **Raw Artifact Immutability**: All original JSON files exported from the browser extension are stored as immutable records in `data/raw/` or `data/olx_pilot/`.

---
*Document produced as part of the TrustLens Marketplace Media Intelligence Layer expansion.*
