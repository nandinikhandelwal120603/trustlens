/**
 * TrustLens OLX Capture Schema v1.0
 * Standard data definitions and validator for researcher captures.
 */

const SCHEMA_VERSION = "1.0";
const SOURCE_IDENTIFIER = "olx.in";

/**
 * Creates an empty/default seller object with nulls for unobservable fields.
 */
function createDefaultSeller() {
  return {
    display_name: null,
    profile_url: null,
    seller_type: null,
    account_age: null,
    profile_location: null,
  };
}

/**
 * Creates default badges object.
 */
function createDefaultBadges(overrides = {}) {
  return {
    featured: false,
    verified: false,
    elite: false,
    ...overrides,
  };
}

/**
 * Creates default contact actions object.
 */
function createDefaultContactActions(overrides = {}) {
  return {
    chat_available: false,
    call_available: false,
    ...overrides,
  };
}

/**
 * Creates a standard listing item schema object.
 */
function createListingRecord({
  listing_id = "",
  source_url = "",
  raw = {},
  normalized = {},
  badges = {},
  contact_actions = {},
  media = [],
  attributes = {},
  description = { text: "", paragraphs: [] },
  seller = null,
} = {}) {
  return {
    listing_id: String(listing_id || ""),
    source_url: String(source_url || ""),
    raw: {
      title: raw.title ?? null,
      price: raw.price ?? null,
      location: raw.location ?? null,
      date: raw.date ?? null,
      description: raw.description ?? null,
    },
    normalized: {
      title: normalized.title ?? raw.title ?? null,
      price: normalized.price ?? { amount: null, currency: "INR" },
      location: normalized.location ?? raw.location ?? null,
      posted_text: normalized.posted_text ?? raw.date ?? null,
    },
    badges: createDefaultBadges(badges),
    contact_actions: createDefaultContactActions(contact_actions),
    media: Array.isArray(media) ? media : [],
    attributes: typeof attributes === "object" && attributes !== null ? attributes : {},
    description: {
      text: description?.text ?? "",
      paragraphs: Array.isArray(description?.paragraphs) ? description.paragraphs : [],
    },
    seller: seller ? { ...createDefaultSeller(), ...seller } : createDefaultSeller(),
  };
}

/**
 * Creates a standard capture envelope.
 */
function createCaptureEnvelope({
  capture_id = null,
  page_type = "unknown",
  source_url = "",
  capture_context = {},
  listings = [],
} = {}) {
  const now = new Date().toISOString();
  return {
    capture_id: capture_id || `cap-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`,
    captured_at: now,
    page_type: String(page_type),
    source_url: String(source_url),
    capture_context: {
      search_query: capture_context.search_query ?? null,
      category_id: capture_context.category_id ?? null,
      total_rendered_cards: capture_context.total_rendered_cards ?? listings.length,
      ...capture_context,
    },
    listings: Array.isArray(listings) ? listings : [],
  };
}

/**
 * Creates a full export payload for multiple captures.
 */
function createExportPayload(captures = []) {
  return {
    schema_version: SCHEMA_VERSION,
    source: SOURCE_IDENTIFIER,
    exported_at: new Date().toISOString(),
    captures_count: captures.length,
    captures: Array.isArray(captures) ? captures : [],
  };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    SCHEMA_VERSION,
    SOURCE_IDENTIFIER,
    createDefaultSeller,
    createDefaultBadges,
    createDefaultContactActions,
    createListingRecord,
    createCaptureEnvelope,
    createExportPayload,
  };
}
