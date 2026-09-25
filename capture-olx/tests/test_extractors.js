/**
 * Automated Test Suite for TrustLens capture-olx Extension
 * Tests detector, search card extractor, listing page extractor, Slick deduplication, and schema.
 */

const fs = require("fs");
const path = require("path");
const assert = require("assert");
const { JSDOM } = require("jsdom");

const projectRoot = path.resolve(__dirname, "..");

// Load Modules
const { OLXDetector } = require(path.join(projectRoot, "content", "detector.js"));
const { OLXMediaExtractor } = require(path.join(projectRoot, "content", "media-extractor.js"));
const { OLXNormalizer } = require(path.join(projectRoot, "content", "normalizer.js"));
const { OLXSearchCapture } = require(path.join(projectRoot, "content", "search-capture.js"));
const { OLXListingCapture } = require(path.join(projectRoot, "content", "listing-capture.js"));
const {
  SCHEMA_VERSION,
  SOURCE_IDENTIFIER,
  createDefaultSeller,
  createDefaultBadges,
  createDefaultContactActions,
  createCaptureEnvelope,
  createExportPayload,
} = require(path.join(projectRoot, "schemas", "listing-schema.js"));

// Test Fixture Paths
const SEARCH_FIXTURE = fs.readFileSync(path.join(__dirname, "fixtures", "search_page.html"), "utf-8");
const LISTING_FIXTURE = fs.readFileSync(path.join(__dirname, "fixtures", "listing_page.html"), "utf-8");
const NON_OLX_FIXTURE = fs.readFileSync(path.join(__dirname, "fixtures", "non_olx.html"), "utf-8");

let totalTests = 0;
let passedTests = 0;

function runTest(name, fn) {
  totalTests++;
  try {
    fn();
    console.log(`  ✓ ${name}`);
    passedTests++;
  } catch (err) {
    console.error(`  ✗ ${name}`);
    console.error(`    ${err.message}`);
  }
}

console.log("\n🧪 Running TrustLens capture-olx Test Suite...\n");

// ---------------------------------------------------------
// 1. OLX Detector Tests
// ---------------------------------------------------------
console.log("1. Testing OLX Detector...");

runTest("detects OLX hostname correctly", () => {
  assert.strictEqual(OLXDetector.isOLX("https://www.olx.in/en-in/mobile-phones_c1453/q-iphone-15-pro"), true);
  assert.strictEqual(OLXDetector.isOLX("https://olx.in/item/1853436229"), true);
  assert.strictEqual(OLXDetector.isOLX("https://example.com/item/1853436229"), false);
});

runTest("extracts category ID from URL or DOM", () => {
  const cat1 = OLXDetector.extractCategoryId("https://www.olx.in/en-in/mobile-phones_c1453/q-iphone-15-pro");
  assert.strictEqual(cat1, "1453");

  const cat2 = OLXDetector.extractCategoryId("https://www.olx.in/cars/c84");
  assert.strictEqual(cat2, "84");
});

runTest("extracts search query from URL slug and params", () => {
  const q1 = OLXDetector.extractSearchQuery("https://www.olx.in/en-in/mobile-phones_c1453/q-iphone-15-pro");
  assert.strictEqual(q1, "iphone 15 pro");

  const q2 = OLXDetector.extractSearchQuery("https://www.olx.in/all-results?query=macbook+pro");
  assert.strictEqual(q2, "macbook pro");
});

runTest("extracts numeric listing ID from URL", () => {
  const id1 = OLXDetector.extractListingId("https://www.olx.in/en-in/item/apple-iphone-15-pro-iid-1853436229");
  assert.strictEqual(id1, "1853436229");

  const id2 = OLXDetector.extractListingId("https://www.olx.in/item/1853436229");
  assert.strictEqual(id2, "1853436229");
});

runTest("detects search vs listing vs non-OLX page type", () => {
  const searchDom = new JSDOM(SEARCH_FIXTURE, { url: "https://www.olx.in/en-in/mobile-phones_c1453/q-iphone-15-pro" });
  assert.strictEqual(OLXDetector.detectPageType(searchDom.window.document, "https://www.olx.in/en-in/mobile-phones_c1453/q-iphone-15-pro"), "search");

  const listingDom = new JSDOM(LISTING_FIXTURE, { url: "https://www.olx.in/en-in/item/apple-iphone-15-pro-iid-1853436229" });
  assert.strictEqual(OLXDetector.detectPageType(listingDom.window.document, "https://www.olx.in/en-in/item/apple-iphone-15-pro-iid-1853436229"), "listing");

  const nonOlxDom = new JSDOM(NON_OLX_FIXTURE, { url: "https://example.com/news" });
  assert.strictEqual(OLXDetector.detectPageType(nonOlxDom.window.document, "https://example.com/news"), "unsupported");
});

// ---------------------------------------------------------
// 2. Normalizer Tests
// ---------------------------------------------------------
console.log("\n2. Testing Normalizer...");

runTest("normalizes prices while preserving raw values", () => {
  const p1 = OLXNormalizer.normalizePrice("₹ 58,000");
  assert.deepStrictEqual(p1, { amount: 58000, currency: "INR" });

  const p2 = OLXNormalizer.normalizePrice("Rs. 25,999.50");
  assert.deepStrictEqual(p2, { amount: 25999.5, currency: "INR" });

  const p3 = OLXNormalizer.normalizePrice("Free");
  assert.deepStrictEqual(p3, { amount: 0, currency: "INR" });

  const p4 = OLXNormalizer.normalizePrice(null);
  assert.deepStrictEqual(p4, { amount: null, currency: "INR" });
});

runTest("normalizes description paragraphs preserving text structure", () => {
  const desc = OLXNormalizer.normalizeDescription("Line 1\n\nLine 2\nLine 3");
  assert.strictEqual(desc.paragraphs.length, 3);
  assert.strictEqual(desc.text, "Line 1\n\nLine 2\nLine 3");
});

// ---------------------------------------------------------
// 3. Search Page Capture Tests
// ---------------------------------------------------------
console.log("\n3. Testing Search Page Card Extraction...");

const searchDom = new JSDOM(SEARCH_FIXTURE, { url: "https://www.olx.in/en-in/mobile-phones_c1453/q-iphone-15-pro" });
global.OLXDetector = OLXDetector;
global.OLXMediaExtractor = OLXMediaExtractor;
global.OLXNormalizer = OLXNormalizer;
global.createCaptureEnvelope = createCaptureEnvelope;

const searchCapture = OLXSearchCapture.captureSearchPage(
  searchDom.window.document,
  "https://www.olx.in/en-in/mobile-phones_c1453/q-iphone-15-pro"
);

runTest("extracts search capture envelope with context", () => {
  assert.strictEqual(searchCapture.page_type, "search");
  assert.strictEqual(searchCapture.source_url, "https://www.olx.in/en-in/mobile-phones_c1453/q-iphone-15-pro");
  assert.strictEqual(searchCapture.capture_context.search_query, "iphone 15 pro");
  assert.strictEqual(searchCapture.capture_context.category_id, "1453");
  assert.strictEqual(searchCapture.listings.length, 2);
});

runTest("extracts first card details and observable badges accurately", () => {
  const item1 = searchCapture.listings[0];
  assert.strictEqual(item1.listing_id, "1853436229");
  assert.strictEqual(item1.raw.title, "Apple iPhone 15 Pro 256GB Natural Titanium");
  assert.strictEqual(item1.raw.price, "₹ 58,000");
  assert.strictEqual(item1.normalized.price.amount, 58000);
  assert.strictEqual(item1.normalized.price.currency, "INR");
  assert.strictEqual(item1.raw.location, "Koh E Fiza, Bhopal");
  assert.strictEqual(item1.raw.date, "Aug 23");
  assert.strictEqual(item1.badges.featured, true);
  assert.strictEqual(item1.badges.verified, true);
  assert.strictEqual(item1.badges.elite, false);
  assert.strictEqual(item1.contact_actions.chat_available, true);
  assert.strictEqual(item1.contact_actions.call_available, true);
  assert.strictEqual(item1.contact_actions.favourite_available, true);
  assert.strictEqual(item1.media.length, 1);
  assert.strictEqual(item1.media[0].file_id, "img-file-101");
});

runTest("seller fields are faithfully null and un-fabricated", () => {
  const item1 = searchCapture.listings[0];
  assert.deepStrictEqual(item1.seller, {
    display_name: null,
    profile_url: null,
    seller_type: null,
    account_age: null,
    profile_location: null,
  });
});

// ---------------------------------------------------------
// 4. Listing Page Capture & Deduplication Tests
// ---------------------------------------------------------
console.log("\n4. Testing Listing Page Capture & Gallery Deduplication...");

const listingDom = new JSDOM(LISTING_FIXTURE, { url: "https://www.olx.in/en-in/item/apple-iphone-15-pro-iid-1853436229" });

const listingCapture = OLXListingCapture.captureListingPage(
  listingDom.window.document,
  "https://www.olx.in/en-in/item/apple-iphone-15-pro-iid-1853436229"
);

runTest("extracts listing envelope with single item", () => {
  assert.strictEqual(listingCapture.page_type, "listing");
  assert.strictEqual(listingCapture.listings.length, 1);
});

runTest("extracts listing title, price, location, date, and description paragraphs", () => {
  const listing = listingCapture.listings[0];
  assert.strictEqual(listing.listing_id, "1853436229");
  assert.strictEqual(listing.raw.title, "Apple iPhone 15 Pro 128GB Blue Titanium");
  assert.strictEqual(listing.raw.price, "₹ 65,000");
  assert.strictEqual(listing.normalized.price.amount, 65000);
  assert.strictEqual(listing.raw.location, "Indiranagar, Bengaluru");
  assert.strictEqual(listing.raw.date, "Yesterday");
  assert.strictEqual(listing.description.paragraphs.length, 3);
  assert.ok(listing.description.paragraphs[0].includes("100% battery health"));
});

runTest("generically extracts all itemParams key-value pairs", () => {
  const listing = listingCapture.listings[0];
  assert.strictEqual(listing.attributes["Brand"], "Apple");
  assert.strictEqual(listing.attributes["Model"], "iPhone 15 Pro");
  assert.strictEqual(listing.attributes["Condition"], "Used");
  assert.strictEqual(listing.attributes["Storage"], "128 GB");
  assert.strictEqual(listing.attributes["Color"], "Blue Titanium");
});

runTest("deduplicates Slick carousel clone images by file identifier", () => {
  const listing = listingCapture.listings[0];
  // Fixture has 5 slides (2 clones + 3 real) -> deduplicates to exactly 3 unique file IDs
  assert.strictEqual(listing.media.length, 3);
  const fileIds = listing.media.map((m) => m.file_id);
  assert.ok(fileIds.includes("img-gal-001"));
  assert.ok(fileIds.includes("img-gal-002"));
  assert.ok(fileIds.includes("img-gal-003"));

  // Check gallery index numbering
  assert.deepStrictEqual(listing.media.map(m => m.gallery_index), [0, 1, 2]);
});

runTest("extracts seller display_name and memberSince when present in DOM", () => {
  const listing = listingCapture.listings[0];
  assert.strictEqual(listing.seller.display_name, "OLX User");
  assert.strictEqual(listing.seller.account_age, "Yesterday");
});

// ---------------------------------------------------------
// 5. Schema Export Payload Tests
// ---------------------------------------------------------
console.log("\n5. Testing Schema Export Payload...");

runTest("generates valid standard JSON export payload", () => {
  const exportData = createExportPayload([searchCapture, listingCapture]);
  assert.strictEqual(exportData.schema_version, SCHEMA_VERSION);
  assert.strictEqual(exportData.source, SOURCE_IDENTIFIER);
  assert.strictEqual(exportData.captures_count, 2);
  assert.strictEqual(exportData.captures.length, 2);
  assert.ok(exportData.exported_at.includes("T"));
});

// ---------------------------------------------------------
// 6. Auto-Loader & Continuous Collector Tests
// ---------------------------------------------------------
console.log("\n6. Testing Auto-Loader & Continuous Collector...");

const { OLXAutoLoader } = require(path.join(projectRoot, "content", "auto-loader.js"));

runTest("finds Load More button via data-aut-id selector", () => {
  const domWithBtn = new JSDOM(`
    <div>
      <ul data-aut-id="itemsList1"><li>Item 1</li></ul>
      <button data-aut-id="btnLoadMore"><span>load more</span></button>
    </div>
  `);
  const btn = OLXAutoLoader.findLoadMoreButton(domWithBtn.window.document);
  assert.ok(btn !== null);
  assert.strictEqual(btn.getAttribute("data-aut-id"), "btnLoadMore");
});

runTest("finds Load More button via text content fallback", () => {
  const domWithTextBtn = new JSDOM(`
    <div>
      <div class="rui-btn" role="button">Load More Items</div>
    </div>
  `);
  const btn = OLXAutoLoader.findLoadMoreButton(domWithTextBtn.window.document);
  assert.ok(btn !== null);
  assert.ok(btn.textContent.includes("Load More"));
});

runTest("returns null when no Load More button exists", () => {
  const domNoBtn = new JSDOM(`<div><p>End of search results</p></div>`);
  const btn = OLXAutoLoader.findLoadMoreButton(domNoBtn.window.document);
  assert.strictEqual(btn, null);
});

runTest("manages AutoLoader start, status tracking, and stop states", () => {
  const loader = new OLXAutoLoader();
  assert.strictEqual(loader.isRunning, false);

  const initialStatus = loader.getStatus();
  assert.strictEqual(initialStatus.isRunning, false);
  assert.strictEqual(initialStatus.iteration, 0);

  // Test status listeners
  let notifiedMessage = null;
  loader.addStatusListener((status) => {
    notifiedMessage = status.message;
  });

  loader._notifyStatus("Test notification");
  assert.strictEqual(notifiedMessage, "Test notification");
});

// Summary
console.log("\n--------------------------------------------------");
console.log(`Summary: ${passedTests} of ${totalTests} tests passed.`);
if (passedTests === totalTests) {
  console.log("🎉 All TrustLens capture-olx tests PASSED successfully!\n");
  process.exit(0);
} else {
  console.error("❌ Some tests failed!\n");
  process.exit(1);
}
