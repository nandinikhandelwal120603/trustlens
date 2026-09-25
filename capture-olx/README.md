# TrustLens OLX Collector (`capture-olx`)

A researcher-controlled Chrome Extension (Manifest V3) for capturing publicly visible OLX India search feeds and individual listing pages for the TrustLens marketplace research pipeline.

---

## 1. What This Is

The **TrustLens OLX Collector** is a strictly client-side data acquisition tool. It operates under direct researcher control:
* You browse OLX manually in your regular browser session.
* When you find a search results feed or individual listing page, click the extension icon and click **Capture**.
* The extension extracts the structured data from the visible DOM using semantic `data-aut-id` selectors.
* Data is stored locally in your browser's IndexedDB and can be exported as a clean, standardized JSON dataset.

---

## 2. Installation Instructions

1. Open Google Chrome (or any Chromium browser).
2. Navigate to `chrome://extensions/`.
3. In the top-right corner, enable **Developer mode**.
4. Click **Load unpacked** in the top-left corner.
5. Select the `capture-olx` folder from this repository:
   ```text
   /path/to/trustlens/capture-olx
   ```
6. The **TrustLens OLX Collector** icon will appear in your Chrome toolbar. Pin it for quick access.

---

## 3. How to Use

### A. Capturing an OLX Search Results Page
1. Navigate to an OLX search or category page (e.g., `https://www.olx.in/en-in/mobile-phones_c1453/q-iphone-15-pro`).
2. *(Optional)* Scroll down manually if you wish to load additional listing cards into the page DOM.
3. Click the **TrustLens** extension icon in your toolbar.
4. The popup will indicate: `✓ OLX search page detected` and display the count of visible cards.
5. Click **[ Capture Search Page (X cards) ]**.
6. The listings are immediately extracted, normalized, and saved to local IndexedDB.

### B. Capturing an Individual Listing Page
1. Click into any listing page (e.g., `https://www.olx.in/en-in/item/iphone-15-pro-iid-1853436229`).
2. Click the **TrustLens** extension icon.
3. The popup will indicate: `✓ OLX listing page detected` and display the listing ID.
4. Click **[ Capture Listing ]**.
5. The listing title, price, description paragraphs, generic attributes (`itemParams`), unique gallery media (with Slick clone deduplication), and observable badges are saved.

### C. Exporting Captured Data
1. Open the popup at any time.
2. View your session stats (e.g., `18 listings across 3 capture batches`).
3. Click **[ Download JSON ]** to save `trustlens_olx_captures_YYYYMMDD_HHMMSS.json` to your computer.
4. Click **[ Clear ]** whenever you want to reset your local IndexedDB storage.

---

## 4. Scope Limitations & Research Ethics

To maintain strict research integrity, privacy standards, and platform compliance:

* **No Autonomous Crawling**: The extension does NOT crawl pages automatically, navigate to links in the background, or loop through paginations unattended.
* **No Continuous Monitoring**: It only captures when the researcher explicitly clicks the Capture button.
* **No Seller Contact**: It NEVER clicks "Chat", "Call", or "Show Number" buttons, sends messages, or initiates communication.
* **No CAPTCHA / Anti-Bot Bypass**: It relies entirely on standard researcher browser interactions without bypassing security controls.
* **No In-Browser Scam Scoring or Fraud Classification**: It does not assign risk scores, accuse sellers, or make fraud judgments. It is purely a data acquisition layer.
* **No Remote Uploads**: Captured records are stored exclusively on your local machine in IndexedDB and exported directly to your filesystem.

---

## 5. Project Structure

```text
capture-olx/
├── manifest.json                  # Chrome Extension Manifest V3 configuration
├── icons/                         # 16px, 48px, 128px PNG extension icons
├── popup/
│   ├── popup.html                 # Researcher UI (Status, Capture Button, Stats, Export)
│   ├── popup.js                   # Popup controller & tab messaging
│   └── popup.css                  # Dark-mode styling
├── content/
│   ├── detector.js                # OLX page type detection (search vs listing)
│   ├── media-extractor.js         # Unique gallery extraction & Slick clone deduplication
│   ├── normalizer.js              # Price, text, and paragraph normalization
│   ├── search-capture.js          # Search results feed card extractor
│   ├── listing-capture.js         # Listing page details, attributes, and description extractor
│   └── content-main.js            # Content script entrypoint & message dispatcher
├── background/
│   └── service-worker.js          # Extension lifecycle and badge counter
├── schemas/
│   └── listing-schema.js          # Standard JSON schema definition & builders
├── storage/
│   └── indexeddb.js               # Robust IndexedDB storage manager
├── export/
│   └── exporter.js                # Standard JSON export generator and downloader
├── tests/
│   ├── fixtures/
│   │   ├── search_page.html       # Realistic search DOM fixture with data-aut-id cards
│   │   ├── listing_page.html      # Realistic listing DOM fixture with carousel clones
│   │   └── non_olx.html           # Non-OLX control page fixture
│   └── test_extractors.js         # Automated test suite using JSDOM
├── COMPATIBILITY.md               # Field mappings to TrustLens Python models
├── package.json                   # Test dependencies
└── README.md                      # Documentation
```

---

## 6. Running Tests

Run the automated DOM extraction and deduplication test suite:

```bash
cd capture-olx
npm test
```
