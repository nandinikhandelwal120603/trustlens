/**
 * OLX Search Page Card Extractor
 * Extracts all currently rendered listing cards using semantic data-aut-id selectors.
 */

class OLXSearchCapture {
  /**
   * Extract listing ID from card anchor href or attributes.
   * @param {Element} cardElement
   * @returns {string|null}
   */
  static extractListingIdFromCard(cardElement) {
    if (!cardElement) return null;

    // 1. Check data-aut-id or data-id attributes
    const dataId = cardElement.getAttribute("data-id") || cardElement.getAttribute("data-aut-id");
    if (dataId && /^\d+$/.test(dataId)) return dataId;

    // 2. Check anchor href
    const anchor = cardElement.querySelector('a[href*="iid-"], a[href*="/item/"], a[href*="/ad/"], a');
    if (anchor) {
      const href = anchor.getAttribute("href") || "";
      const match = href.match(/iid-(\d+)/i) || href.match(/\/item\/[^/?#]*?(\d{7,})/i) || href.match(/\/(\d{8,})(?:[/?#]|$)/);
      if (match) return match[1];
    }

    return null;
  }

  /**
   * Extract source URL from card anchor.
   * @param {Element} cardElement
   * @param {string} baseUrl
   * @returns {string}
   */
  static extractListingUrlFromCard(cardElement, baseUrl = "https://www.olx.in") {
    if (!cardElement) return "";
    const anchor = cardElement.querySelector('a[href*="iid-"], a[href*="/item/"], a[href*="/ad/"], a');
    if (!anchor) return "";

    const href = anchor.getAttribute("href") || "";
    if (!href) return "";

    try {
      if (href.startsWith("http")) return href;
      return new URL(href, baseUrl).href;
    } catch {
      return href;
    }
  }

  /**
   * Extract observable UI indicators for a search card.
   * @param {Element} cardElement
   * @returns {Object}
   */
  static extractCardObservableUI(cardElement) {
    if (!cardElement) {
      return {
        badges: { featured: false, verified: false, elite: false },
        contact_actions: { chat_available: false, call_available: false, favourite_available: false },
      };
    }

    const cardText = cardElement.innerText || cardElement.textContent || "";
    const isFeatured = Boolean(
      cardElement.querySelector('[data-aut-id="itemFeatured"], [aria-label*="featured" i], [class*="featured" i]') ||
      cardText.includes("FEATURED")
    );

    const isVerified = Boolean(
      cardElement.querySelector('[data-aut-id="verified"], [aria-label*="verified" i], [class*="verified" i]')
    );

    const isElite = Boolean(
      cardElement.querySelector('[data-aut-id="elite"], [class*="elite" i]') ||
      cardText.includes("ELITE")
    );

    const hasChat = Boolean(
      cardElement.querySelector('button[data-aut-id="btnChat"], [aria-label*="chat" i], button[class*="chat" i]')
    );

    const hasCall = Boolean(
      cardElement.querySelector('button[data-aut-id="btnCall"], [aria-label*="call" i], button[class*="call" i]')
    );

    const hasFav = Boolean(
      cardElement.querySelector('[data-aut-id="btnFavorite"], [aria-label*="favorite" i], [aria-label*="favourite" i], button[class*="favorite" i]')
    );

    return {
      badges: {
        featured: isFeatured,
        verified: isVerified,
        elite: isElite,
      },
      contact_actions: {
        chat_available: hasChat,
        call_available: hasCall,
        favourite_available: hasFav,
      },
    };
  }

  /**
   * Extract a single listing card.
   * @param {Element} cardElement
   * @param {string} baseUrl
   * @returns {Object|null}
   */
  static extractCard(cardElement, baseUrl = "https://www.olx.in") {
    if (!cardElement) return null;

    // Primary data-aut-id selectors
    const titleEl = cardElement.querySelector('[data-aut-id="itemTitle"], [data-aut-id="item-title"], h2, [class*="title" i], [class*="itemTitle" i]');
    const priceEl = cardElement.querySelector('[data-aut-id="itemPrice"], [data-aut-id="item-price"], [class*="price" i]');
    const locationEl = cardElement.querySelector('[data-aut-id="item-location"], [data-aut-id="itemLocation"], [data-aut-id="itemDetailsLocation"], [class*="location" i]');
    const dateEl = cardElement.querySelector('[data-aut-id="itemDate"], [data-aut-id="item-date"], [data-aut-id="itemDetailsDate"], [class*="date" i]');
    const imgEl = cardElement.querySelector('img[alt], img[data-aut-id="itemImage"]');

    let rawTitle = titleEl ? (titleEl.getAttribute("title") || titleEl.textContent || "").trim() : null;
    const rawPrice = priceEl ? priceEl.textContent.trim() : null;
    const rawLocation = locationEl ? locationEl.textContent.trim() : null;
    const rawDate = dateEl ? dateEl.textContent.trim() : null;

    // If title was grabbed from a wrapper containing price/location or FEATURED, prefer clean img alt
    const imgAlt = imgEl ? (imgEl.getAttribute("alt") || "").trim() : "";
    if (imgAlt && imgAlt.length > 0) {
      if (!rawTitle || (rawPrice && rawTitle.includes(rawPrice)) || (rawLocation && rawTitle.includes(rawLocation)) || rawTitle.startsWith("FEATURED") || rawTitle.includes("₹")) {
        rawTitle = imgAlt;
      }
    }

    // Clean any remaining concatenated prefixes or HTML entities
    if (rawTitle) {
      rawTitle = rawTitle.replace(/^FEATURED\s*/i, "").replace(/&ndash;/g, "–").replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;/g, "'").trim();
      if (rawPrice && rawTitle.startsWith(rawPrice)) {
        rawTitle = rawTitle.slice(rawPrice.length).trim();
      }
      if (rawLocation && rawTitle.endsWith(rawLocation)) {
        rawTitle = rawTitle.slice(0, -rawLocation.length).trim();
      }
      if (rawDate && rawTitle.endsWith(rawDate)) {
        rawTitle = rawTitle.slice(0, -rawDate.length).trim();
      }
    }

    const listingId = this.extractListingIdFromCard(cardElement);
    const listingUrl = this.extractListingUrlFromCard(cardElement, baseUrl);

    // Fallback if no valid listing card elements detected
    if (!rawTitle && !rawPrice && !listingId && !listingUrl) {
      return null;
    }

    const { badges, contact_actions } = this.extractCardObservableUI(cardElement);
    const media = typeof OLXMediaExtractor !== "undefined"
      ? OLXMediaExtractor.extractCardMedia(cardElement)
      : [];

    const normalizedPrice = typeof OLXNormalizer !== "undefined"
      ? OLXNormalizer.normalizePrice(rawPrice)
      : { amount: null, currency: "INR" };

    const normalizedTitle = typeof OLXNormalizer !== "undefined"
      ? OLXNormalizer.cleanText(rawTitle)
      : rawTitle;

    const normalizedLocation = typeof OLXNormalizer !== "undefined"
      ? OLXNormalizer.cleanText(rawLocation)
      : rawLocation;

    return {
      listing_id: listingId || "",
      source_url: listingUrl || "",
      raw: {
        title: rawTitle,
        price: rawPrice,
        location: rawLocation,
        date: rawDate,
        description: null,
      },
      normalized: {
        title: normalizedTitle,
        price: normalizedPrice,
        location: normalizedLocation,
        posted_text: rawDate,
      },
      badges,
      contact_actions,
      media,
      attributes: {},
      description: { text: "", paragraphs: [] },
      seller: {
        display_name: null,
        profile_url: null,
        seller_type: null,
        account_age: null,
        profile_location: null,
      },
    };
  }

  /**
   * Extracts all currently rendered cards on the search page.
   * @param {Document} doc
   * @param {string} pageUrl
   * @returns {Object} Capture envelope
   */
  static captureSearchPage(doc = document, pageUrl = window.location.href) {
    const baseUrl = pageUrl.startsWith("http") ? pageUrl : "https://www.olx.in";

    // Primary container & card selectors
    const cardElements = doc.querySelectorAll(
      'ul[data-aut-id="itemsList1"] > li, ' +
      'li[data-aut-id="itemBox3"], ' +
      'li[data-aut-id^="itemBox"], ' +
      '[data-aut-id^="itemBox"], ' +
      'li[data-aut-category-id]'
    );

    const listings = [];
    const seenIds = new Set();
    const seenUrls = new Set();

    cardElements.forEach((el) => {
      const cardData = this.extractCard(el, baseUrl);
      if (!cardData) return;

      const dedupeKey = cardData.listing_id || cardData.source_url;
      if (!dedupeKey) return;

      if (cardData.listing_id && seenIds.has(cardData.listing_id)) return;
      if (cardData.source_url && seenUrls.has(cardData.source_url)) return;

      if (cardData.listing_id) seenIds.add(cardData.listing_id);
      if (cardData.source_url) seenUrls.add(cardData.source_url);

      listings.push(cardData);
    });

    const searchQuery = typeof OLXDetector !== "undefined"
      ? OLXDetector.extractSearchQuery(pageUrl)
      : null;

    const categoryId = typeof OLXDetector !== "undefined"
      ? OLXDetector.extractCategoryId(pageUrl)
      : null;

    const captureContext = {
      search_query: searchQuery,
      category_id: categoryId,
      total_rendered_cards: listings.length,
    };

    if (typeof createCaptureEnvelope === "function") {
      return createCaptureEnvelope({
        page_type: "search",
        source_url: pageUrl,
        capture_context: captureContext,
        listings,
      });
    }

    return {
      capture_id: `cap-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`,
      captured_at: new Date().toISOString(),
      page_type: "search",
      source_url: pageUrl,
      capture_context: captureContext,
      listings,
    };
  }
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { OLXSearchCapture };
}
