# Phase 00 — Reddit Research & Problem Foundation

## 1. Objectives & Research Scope
Analyzed 178 raw user-reported fraud cases and 330 media assets from Indian subreddits (r/IsThisAScamIndia, r/LegalAdviceIndia, etc.) to establish real-world victim experiences and ground the empirical fraud taxonomy.

## 2. Included Python Modules
* `reddit_scraper.py` — Standalone Reddit public complaint search crawler.
* `full_processor.py` — End-to-end dataset transformation, geographic filtering, and pattern taxonomy mapping.
* `media_packager.py` — Media downloader and case-mapped dataset packager.
* `validator.py` — Integrity validation for media assets and post metadata.

## 3. Key Findings & Modus Operandi Discovered
* 68 cases of advance payment / deposit demands.
* 51 cases of unrealistic below-market pricing (40%–70% below median).
* 48 cases of WhatsApp off-platform contact migration.
* 42 cases of reverse-charge UPI / QR code payment traps.
* 24 cases of Army / CISF officer persona impersonation with fake canteen invoices.
