/**
 * TrustLens OLX Capture - Content Script Bridge
 * Listens for capture commands from popup, extracts data, and returns capture payload.
 */

(() => {
  // Prevent multiple injections
  if (window.__TRUSTLENS_CAPTURE_INITIALIZED__) return;
  window.__TRUSTLENS_CAPTURE_INITIALIZED__ = true;

  console.log("[TrustLens] OLX capture content script loaded.");

  /**
   * Handle incoming messages from popup or background service worker.
   */
  if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.onMessage) {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      const { action } = request;

      if (action === "PING") {
        sendResponse({ status: "ok" });
        return true;
      }

      if (action === "DETECT_PAGE") {
        try {
          const pageType = OLXDetector.detectPageType(document, window.location.href);
          const cardCount = pageType === "search" ? OLXDetector.countRenderedSearchCards(document) : (pageType === "listing" ? 1 : 0);
          const searchQuery = pageType === "search" ? OLXDetector.extractSearchQuery(window.location.href) : null;
          const listingId = pageType === "listing" ? OLXDetector.extractListingId(window.location.href) : null;

          sendResponse({
            status: "ok",
            pageType,
            url: window.location.href,
            cardCount,
            searchQuery,
            listingId,
          });
        } catch (err) {
          sendResponse({
            status: "error",
            message: err.message,
          });
        }
        return true;
      }

      if (action === "CAPTURE_PAGE") {
        try {
          const pageType = OLXDetector.detectPageType(document, window.location.href);

          let captureEnvelope = null;

          if (pageType === "search") {
            captureEnvelope = OLXSearchCapture.captureSearchPage(document, window.location.href);
          } else if (pageType === "listing") {
            captureEnvelope = OLXListingCapture.captureListingPage(document, window.location.href);
          } else {
            sendResponse({
              status: "error",
              message: "Unsupported page. Please navigate to an OLX search or listing page.",
            });
            return true;
          }

          sendResponse({
            status: "success",
            captureEnvelope,
            pageType: captureEnvelope.page_type,
            listingsCaptured: captureEnvelope.listings ? captureEnvelope.listings.length : 0,
          });
        } catch (err) {
          console.error("[TrustLens] Extraction error:", err);
          sendResponse({
            status: "error",
            message: err.message || "Failed to extract listing data.",
          });
        }
        return true;
      }

      if (action === "START_AUTO_LOAD") {
        try {
          if (typeof olxAutoLoader === "undefined") {
            sendResponse({ status: "error", message: "AutoLoader module not loaded." });
            return true;
          }
          const interval = request.intervalSeconds || 5;
          const started = olxAutoLoader.start(interval);
          sendResponse({
            status: "ok",
            started,
            autoLoadState: olxAutoLoader.getStatus(),
          });
        } catch (err) {
          sendResponse({ status: "error", message: err.message });
        }
        return true;
      }

      if (action === "STOP_AUTO_LOAD") {
        try {
          if (typeof olxAutoLoader !== "undefined") {
            olxAutoLoader.stop("Stopped by user via popup");
          }
          sendResponse({
            status: "ok",
            autoLoadState: typeof olxAutoLoader !== "undefined" ? olxAutoLoader.getStatus() : null,
          });
        } catch (err) {
          sendResponse({ status: "error", message: err.message });
        }
        return true;
      }

      if (action === "GET_AUTO_LOAD_STATUS") {
        try {
          const autoLoadState = typeof olxAutoLoader !== "undefined" ? olxAutoLoader.getStatus() : null;
          sendResponse({
            status: "ok",
            autoLoadState,
          });
        } catch (err) {
          sendResponse({ status: "error", message: err.message });
        }
        return true;
      }
    });
  }
})();
