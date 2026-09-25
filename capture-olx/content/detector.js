/**
 * OLX Page Type & Metadata Detector
 * Identifies page context, category, query, and listing identifiers.
 */

class OLXDetector {
  /**
   * Check if a URL or hostname belongs to OLX.
   * @param {string} url
   * @returns {boolean}
   */
  static isOLX(url = window.location.href) {
    try {
      const parsed = new URL(url);
      return parsed.hostname.includes("olx.in") || parsed.hostname.includes("olx.");
    } catch {
      return false;
    }
  }

  /**
   * Extract category ID from OLX URL structure.
   * Example: https://www.olx.in/en-in/mobile-phones_c1453/q-iphone-15-pro -> "1453"
   * @param {string} url
   * @returns {string|null}
   */
  static extractCategoryId(url = window.location.href) {
    // 1. URL pattern e.g. _c1453 or /c1453/
    const catMatch = url.match(/_c(\d+)/i) || url.match(/\/c(\d+)/i) || url.match(/[?&]categoryId=(\d+)/i);
    if (catMatch) {
      return catMatch[1];
    }

    // 2. Check DOM data-aut-category-id attribute on items
    if (typeof document !== "undefined") {
      const catElem = document.querySelector("[data-aut-category-id]");
      if (catElem) {
        const id = catElem.getAttribute("data-aut-category-id");
        if (id) return id;
      }
    }

    return null;
  }

  /**
   * Extract search query from OLX URL.
   * Example: /q-iphone-15-pro -> "iphone 15 pro"
   * @param {string} url
   * @returns {string|null}
   */
  static extractSearchQuery(url = window.location.href) {
    try {
      const parsed = new URL(url);

      // 1. Path slug: /q-iphone-15-pro or /q-apple-watch
      const qPathMatch = parsed.pathname.match(/\/q-([^/?#]+)/i);
      if (qPathMatch) {
        return decodeURIComponent(qPathMatch[1].replace(/-/g, " ")).trim();
      }

      // 2. Query param: ?query=... or ?q=...
      const queryParam = parsed.searchParams.get("query") || parsed.searchParams.get("q");
      if (queryParam) {
        return queryParam.trim();
      }

      // 3. Fallback: search input element in DOM if visible
      if (typeof document !== "undefined") {
        const searchInput = document.querySelector('input[data-aut-id="searchBox"], input[type="search"]');
        if (searchInput && searchInput.value) {
          return searchInput.value.trim();
        }
      }
    } catch {
      // ignore
    }
    return null;
  }

  /**
   * Extract numeric listing ID from URL.
   * Examples:
   *  - https://www.olx.in/en-in/item/iphone-15-pro-iid-1853436229 -> "1853436229"
   *  - https://www.olx.in/item/1853436229 -> "1853436229"
   * @param {string} url
   * @returns {string|null}
   */
  static extractListingId(url = window.location.href) {
    const iidMatch = url.match(/iid-(\d+)/i);
    if (iidMatch) return iidMatch[1];

    const itemDigitsMatch = url.match(/\/item\/[^/?#]*?(\d{7,})/i) || url.match(/\/ad\/[^/?#]*?(\d{7,})/i);
    if (itemDigitsMatch) return itemDigitsMatch[1];

    const trailingDigitsMatch = url.match(/\/(\d{8,})(?:[/?#]|$)/);
    if (trailingDigitsMatch) return trailingDigitsMatch[1];

    return null;
  }

  /**
   * Detect current page type.
   * @param {Document} doc
   * @param {string} url
   * @returns {"search" | "listing" | "unsupported"}
   */
  static detectPageType(doc = (typeof document !== "undefined" ? document : null), url = (typeof window !== "undefined" ? window.location.href : "")) {
    if (!this.isOLX(url)) {
      return "unsupported";
    }

    // 1. Check if it's an individual listing
    const listingIdFromUrl = this.extractListingId(url);
    const hasListingMarkers = doc && (
      Boolean(doc.querySelector('[data-aut-id="itemDescriptionContent"]')) ||
      Boolean(doc.querySelector('[data-aut-id="itemParams"]')) ||
      Boolean(doc.querySelector('[data-aut-id="itemPrice"]'))
    );

    if (url.includes("/item/") || (listingIdFromUrl && hasListingMarkers)) {
      return "listing";
    }

    // 2. Check if it's a search page
    const hasSearchList = doc && (
      Boolean(doc.querySelector('[data-aut-id="itemsList1"]')) ||
      Boolean(doc.querySelector('[data-aut-id^="itemBox"]')) ||
      Boolean(doc.querySelector('ul[data-aut-id*="itemsList"]'))
    );

    const isSearchUrl = url.includes("/q-") || url.includes("_c") || url.includes("?query=") || url.includes("?q=");

    if (hasSearchList || isSearchUrl) {
      return "search";
    }

    // 3. Fallback check on general DOM
    if (hasListingMarkers) return "listing";
    if (hasSearchList) return "search";

    return "unsupported";
  }

  /**
   * Count currently rendered listing cards in the search page DOM.
   * @param {Document} doc
   * @returns {number}
   */
  static countRenderedSearchCards(doc = (typeof document !== "undefined" ? document : null)) {
    if (!doc) return 0;
    const cards = doc.querySelectorAll('[data-aut-id^="itemBox"], li[data-aut-id="itemBox3"], [data-aut-id="itemsList1"] > li');
    return cards.length;
  }
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { OLXDetector };
}
