/**
 * OLX Individual Listing Page Extractor
 * Extracts detailed listing attributes, description, media gallery, and observable UI.
 */

class OLXListingCapture {
  /**
   * Generically extract key/value attributes from itemParams container.
   * Matches both data-aut-id key/value patterns and structured param children.
   * @param {Document|Element} root
   * @returns {Object} Key-value attribute dictionary
   */
  static extractAttributes(root = document) {
    const attributes = {};
    const paramsContainer = root.querySelector('[data-aut-id="itemParams"]');

    if (paramsContainer) {
      // 1. Look for explicit key_* and value_* data-aut-id pairs
      const keyElements = paramsContainer.querySelectorAll('[data-aut-id^="key_"]');
      if (keyElements.length > 0) {
        keyElements.forEach((keyEl) => {
          const keyAttr = keyEl.getAttribute("data-aut-id") || "";
          const suffix = keyAttr.replace(/^key_/, "");
          const keyName = keyEl.textContent?.trim() || suffix;

          // Find corresponding value element
          let valEl = paramsContainer.querySelector(`[data-aut-id="value_${suffix}"]`);
          if (!valEl) {
            // Check next sibling
            valEl = keyEl.nextElementSibling;
          }

          if (valEl) {
            const valText = valEl.textContent?.trim() || "";
            if (keyName && valText) {
              attributes[keyName] = valText;
            }
          }
        });
      }

      // 2. Generic param children (e.g. <div><span>Brand</span><span>Apple</span></div>)
      if (Object.keys(attributes).length === 0) {
        const paramItems = paramsContainer.children;
        for (let i = 0; i < paramItems.length; i++) {
          const item = paramItems[i];
          const spans = item.querySelectorAll("span, div, p");
          if (spans.length >= 2) {
            const k = spans[0].textContent?.trim();
            const v = spans[1].textContent?.trim();
            if (k && v && k !== v) {
              attributes[k] = v;
            }
          } else {
            const text = item.textContent?.trim();
            if (text && text.includes(":")) {
              const [k, ...rest] = text.split(":");
              attributes[k.trim()] = rest.join(":").trim();
            }
          }
        }
      }
    }

    return attributes;
  }

  /**
   * Extract observable badges and seller contact actions from listing page.
   * @param {Document} doc
   * @returns {{ badges: Object, contact_actions: Object }}
   */
  static extractObservableUI(doc = document) {
    const pageText = doc.body?.innerText || doc.body?.textContent || "";

    const isFeatured = Boolean(
      doc.querySelector('[data-aut-id="itemFeatured"], [aria-label*="featured" i]') ||
      pageText.includes("FEATURED")
    );

    const isVerified = Boolean(
      doc.querySelector('[data-aut-id="verified"], [aria-label*="verified" i]')
    );

    const isElite = Boolean(
      doc.querySelector('[data-aut-id="elite"]') ||
      pageText.includes("ELITE")
    );

    // Observable seller contact actions
    const hasChat = Boolean(
      doc.querySelector('button[data-aut-id="btnChat"], button[class*="chat" i], [aria-label*="chat" i]')
    );

    const hasCall = Boolean(
      doc.querySelector('button[data-aut-id="btnCall"], button[class*="call" i], [aria-label*="call" i], button[data-aut-id="btnShowNumber"]')
    );

    const hasFav = Boolean(
      doc.querySelector('[data-aut-id="btnFavorite"], [aria-label*="favorite" i], [aria-label*="favourite" i]')
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
   * Extract observable seller information when present in the DOM.
   * @param {Document} doc
   * @returns {Object}
   */
  static extractSeller(doc = document) {
    let displayName = null;
    let accountAge = null;
    let profileUrl = null;
    let profileLocation = null;

    // 1. Seller display name via [data-aut-id="userTitle"]
    const userTitleEl = doc.querySelector('[data-aut-id="userTitle"], [data-aut-id="seller-name"], [class*="userTitle" i]');
    if (userTitleEl) {
      const clone = userTitleEl.cloneNode(true);
      const postedByEl = clone.querySelector('span');
      if (postedByEl && postedByEl.textContent.toLowerCase().includes("posted by")) {
        postedByEl.remove();
      }
      displayName = clone.textContent?.trim() || null;
      if (displayName) {
        displayName = displayName.replace(/^Posted by\s*/i, "").trim();
      }
    }

    // 2. Member since / account age via [data-aut-id="memberSince"]
    const memberSinceEl = doc.querySelector('[data-aut-id="memberSince"], [class*="memberSince" i]');
    if (memberSinceEl) {
      const fullText = memberSinceEl.textContent?.trim() || "";
      accountAge = fullText.replace(/^Member since\s*/i, "").trim() || fullText;
    }

    // 3. Profile URL
    const profileLink = doc.querySelector('a[href*="/profile/"], [data-aut-id="userProfile"], [data-aut-id="userTitle"] a');
    if (profileLink) {
      profileUrl = profileLink.getAttribute("href") || null;
    }

    return {
      display_name: displayName || null,
      profile_url: profileUrl || null,
      seller_type: null,
      account_age: accountAge || null,
      profile_location: profileLocation || null,
    };
  }

  /**
   * Captures an individual listing page.
   * @param {Document} doc
   * @param {string} pageUrl
   * @returns {Object} Complete capture envelope with single listing
   */
  static captureListingPage(doc = document, pageUrl = window.location.href) {
    const listingId = (typeof OLXDetector !== "undefined" ? OLXDetector.extractListingId(pageUrl) : null) || "";
    const categoryId = typeof OLXDetector !== "undefined" ? OLXDetector.extractCategoryId(pageUrl) : null;

    // 1. Core text elements via data-aut-id
    const titleEl = doc.querySelector('[data-aut-id="itemTitle"], [data-aut-id="item-title"], h1[data-aut-id="itemTitle"], h1');
    const priceEl = doc.querySelector('[data-aut-id="itemPrice"], [data-aut-id="item-price"]');
    const locationEl = doc.querySelector('[data-aut-id="item-location"], [data-aut-id="itemLocation"]');
    const dateEl = doc.querySelector('[data-aut-id="itemDate"], [data-aut-id="item-date"]');
    const descEl = doc.querySelector('[data-aut-id="itemDescriptionContent"], [data-aut-id="itemDescription"]');

    const rawTitle = titleEl ? titleEl.textContent.trim() : null;
    const rawPrice = priceEl ? priceEl.textContent.trim() : null;
    const rawLocation = locationEl ? locationEl.textContent.trim() : null;
    const rawDate = dateEl ? dateEl.textContent.trim() : null;
    const rawDescText = descEl ? descEl.textContent.trim() : "";

    // 2. Normalization
    const normalizedTitle = typeof OLXNormalizer !== "undefined"
      ? OLXNormalizer.cleanText(rawTitle)
      : rawTitle;

    const normalizedPrice = typeof OLXNormalizer !== "undefined"
      ? OLXNormalizer.normalizePrice(rawPrice)
      : { amount: null, currency: "INR" };

    const normalizedLocation = typeof OLXNormalizer !== "undefined"
      ? OLXNormalizer.cleanText(rawLocation)
      : rawLocation;

    const description = typeof OLXNormalizer !== "undefined"
      ? OLXNormalizer.normalizeDescription(descEl || rawDescText)
      : { text: rawDescText, paragraphs: rawDescText.split("\n").filter(Boolean) };

    // 3. Media gallery extraction
    const media = typeof OLXMediaExtractor !== "undefined"
      ? OLXMediaExtractor.extractGalleryMedia(doc)
      : [];

    // 4. Generic attributes
    const attributes = this.extractAttributes(doc);

    // 5. Observable UI & Badges
    const { badges, contact_actions } = this.extractObservableUI(doc);

    // 6. Observable seller model
    const seller = this.extractSeller(doc);

    const listingRecord = {
      listing_id: String(listingId),
      source_url: pageUrl,
      raw: {
        title: rawTitle,
        price: rawPrice,
        location: rawLocation,
        date: rawDate,
        description: rawDescText,
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
      attributes,
      description,
      seller,
    };

    const captureContext = {
      search_query: null,
      category_id: categoryId,
      total_rendered_cards: 1,
    };

    if (typeof createCaptureEnvelope === "function") {
      return createCaptureEnvelope({
        page_type: "listing",
        source_url: pageUrl,
        capture_context: captureContext,
        listings: [listingRecord],
      });
    }

    return {
      capture_id: `cap-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`,
      captured_at: new Date().toISOString(),
      page_type: "listing",
      source_url: pageUrl,
      capture_context: captureContext,
      listings: [listingRecord],
    };
  }
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { OLXListingCapture };
}
