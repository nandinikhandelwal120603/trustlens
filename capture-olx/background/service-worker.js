/**
 * TrustLens OLX Capture - Background Service Worker (Manifest V3)
 * Coordinates extension badge, storage sync, and lifecycle.
 */

try {
  importScripts("../schemas/listing-schema.js", "../storage/indexeddb.js");
} catch (e) {
  console.warn("[TrustLens] importScripts error in service worker:", e);
}

// Initialize state
chrome.runtime.onInstalled.addListener(() => {
  console.log("[TrustLens] Background service worker installed.");
  updateBadge();
});

// Update badge when local storage changes
chrome.storage.onChanged.addListener((changes, areaName) => {
  if (areaName === "local" && (changes.trustlens_listings_count || changes.trustlens_captures_count)) {
    updateBadge();
  }
});

// Handle messages from content scripts or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "SAVE_CAPTURE") {
    (async () => {
      try {
        if (typeof captureDB !== "undefined" && request.captureEnvelope) {
          const captureId = await captureDB.saveCapture(request.captureEnvelope);
          await updateBadge();
          sendResponse({ status: "success", captureId });
        } else {
          sendResponse({ status: "error", message: "IndexedDB not initialized in worker" });
        }
      } catch (err) {
        console.error("[TrustLens] Background save error:", err);
        sendResponse({ status: "error", message: err.message });
      }
    })();
    return true;
  }

  if (request.action === "UPDATE_BADGE") {
    updateBadge().then(() => sendResponse({ status: "ok" }));
    return true;
  }
});

/**
 * Updates extension action badge with current captured listing count.
 */
async function updateBadge() {
  try {
    const data = await chrome.storage.local.get(["trustlens_listings_count", "trustlens_captures_count"]);
    const count = data.trustlens_listings_count || 0;
    if (count > 0) {
      await chrome.action.setBadgeText({ text: String(count) });
      await chrome.action.setBadgeBackgroundColor({ color: "#10b981" }); // Emerald green
    } else {
      await chrome.action.setBadgeText({ text: "" });
    }
  } catch (err) {
    // Non-fatal
  }
}
