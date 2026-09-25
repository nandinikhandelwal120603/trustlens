/**
 * TrustLens OLX Collector - Popup Controller
 */

document.addEventListener("DOMContentLoaded", async () => {
  const statusSearch = document.getElementById("status-search");
  const statusListing = document.getElementById("status-listing");
  const statusUnsupported = document.getElementById("status-unsupported");

  const queryName = document.getElementById("query-name");
  const cardsCount = document.getElementById("cards-count");
  const listingIdEl = document.getElementById("listing-id");

  const btnCapture = document.getElementById("btn-capture");
  const btnCaptureText = document.getElementById("btn-capture-text");
  const captureTip = document.getElementById("capture-tip");
  const feedbackMsg = document.getElementById("feedback-msg");

  const autoLoadCard = document.getElementById("auto-load-card");
  const autoLoadBadge = document.getElementById("auto-load-badge");
  const btnAutoLoad = document.getElementById("btn-auto-load");
  const btnAutoLoadText = document.getElementById("btn-auto-load-text");
  const autoLoadMetrics = document.getElementById("auto-load-metrics");
  const autoIteration = document.getElementById("auto-iteration");
  const autoCollected = document.getElementById("auto-collected");
  const autoCountdown = document.getElementById("auto-countdown");

  const sessionCount = document.getElementById("session-count");
  const envelopesCount = document.getElementById("envelopes-count");
  const btnExport = document.getElementById("btn-export");
  const btnClear = document.getElementById("btn-clear");

  let activeTab = null;
  let detectedPageType = "unsupported";
  let isAutoLoading = false;
  let autoStatusPollInterval = null;

  /**
   * Update storage stats from IndexedDB.
   */
  async function refreshStats() {
    try {
      const stats = await captureDB.getStats();
      sessionCount.textContent = `${stats.listings_count} ${stats.listings_count === 1 ? "listing" : "listings"}`;
      envelopesCount.textContent = `${stats.captures_count} ${stats.captures_count === 1 ? "capture batch" : "capture batches"} saved`;

      btnExport.disabled = stats.captures_count === 0;
      btnClear.disabled = stats.captures_count === 0;
    } catch (e) {
      console.error("Error fetching stats:", e);
    }
  }

  /**
   * Show feedback message banner.
   */
  function showFeedback(text, type = "success") {
    feedbackMsg.textContent = text;
    feedbackMsg.className = `feedback-toast ${type}`;
    feedbackMsg.classList.remove("hidden");
    setTimeout(() => {
      feedbackMsg.classList.add("hidden");
    }, 4000);
  }

  /**
   * Update Auto-Load UI state.
   */
  function updateAutoLoadUI(active, state = null) {
    isAutoLoading = active;
    if (active) {
      autoLoadBadge.textContent = "RUNNING (5s)";
      autoLoadBadge.className = "badge-active";
      btnAutoLoad.className = "btn-auto-stop";
      btnAutoLoadText.textContent = "⏹ Stop Auto-Load";
      autoLoadMetrics.classList.remove("hidden");

      if (state) {
        autoIteration.textContent = state.iteration || "1";
        autoCollected.textContent = state.totalListingsCollected || "0";
        autoCountdown.textContent = `${state.countdownSeconds || 5}s`;
      }
    } else {
      autoLoadBadge.textContent = "IDLE";
      autoLoadBadge.className = "badge-idle";
      btnAutoLoad.className = "btn-auto-start";
      btnAutoLoadText.textContent = "▶ Start Auto-Load (5s)";
      if (state && state.totalListingsCollected > 0) {
        autoCollected.textContent = state.totalListingsCollected;
      } else {
        autoLoadMetrics.classList.add("hidden");
      }
    }
  }

  /**
   * Poll active tab for continuous auto-load status.
   */
  function startStatusPolling() {
    if (autoStatusPollInterval) clearInterval(autoStatusPollInterval);

    autoStatusPollInterval = setInterval(() => {
      if (!activeTab || detectedPageType !== "search") return;

      chrome.tabs.sendMessage(activeTab.id, { action: "GET_AUTO_LOAD_STATUS" }, (response) => {
        if (chrome.runtime.lastError || !response || !response.autoLoadState) return;

        const state = response.autoLoadState;
        updateAutoLoadUI(state.isRunning, state);
        if (state.totalListingsCollected > 0) {
          refreshStats();
        }
      });
    }, 1000);
  }

  /**
   * Ensure content scripts are injected into active tab.
   */
  async function ensureScriptsInjected(tabId) {
    try {
      if (typeof chrome !== "undefined" && chrome.scripting && chrome.scripting.executeScript) {
        await chrome.scripting.executeScript({
          target: { tabId },
          files: [
            "schemas/listing-schema.js",
            "content/detector.js",
            "content/media-extractor.js",
            "content/normalizer.js",
            "content/search-capture.js",
            "content/listing-capture.js",
            "content/auto-loader.js",
            "content/content-main.js",
          ],
        });
      }
    } catch (e) {
      console.warn("Script injection note:", e);
    }
  }

  // Initial stats load
  await refreshStats();

  // Query active tab and detect page
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    activeTab = tab;

    if (!tab || !tab.url) {
      showUnsupportedState();
      return;
    }

    if (!tab.url.includes("olx.in")) {
      showUnsupportedState();
      return;
    }

    // Attempt detection
    chrome.tabs.sendMessage(tab.id, { action: "DETECT_PAGE" }, async (response) => {
      if (chrome.runtime.lastError || !response) {
        // Scripts might not be loaded yet, inject and retry
        await ensureScriptsInjected(tab.id);
        chrome.tabs.sendMessage(tab.id, { action: "DETECT_PAGE" }, (retryResponse) => {
          if (chrome.runtime.lastError || !retryResponse) {
            tryFallbackTabUrlDetection(tab.url);
          } else {
            handleDetectionResponse(retryResponse);
          }
        });
        return;
      }

      handleDetectionResponse(response);
    });
  } catch (err) {
    console.error("Error communicating with tab:", err);
    showUnsupportedState();
  }

  /**
   * Handle content script detection response.
   */
  function handleDetectionResponse(response) {
    detectedPageType = response.pageType;

    if (detectedPageType === "search") {
      statusSearch.classList.remove("hidden");
      statusListing.classList.add("hidden");
      statusUnsupported.classList.add("hidden");

      queryName.textContent = response.searchQuery || "(All Category Items)";
      cardsCount.textContent = response.cardCount || "0";

      btnCapture.disabled = false;
      btnCaptureText.textContent = `Capture Now (${response.cardCount || 0} cards)`;
      captureTip.classList.remove("hidden");
      autoLoadCard.classList.remove("hidden");

      // Query auto-load status
      chrome.tabs.sendMessage(activeTab.id, { action: "GET_AUTO_LOAD_STATUS" }, (statusResp) => {
        if (statusResp && statusResp.autoLoadState) {
          updateAutoLoadUI(statusResp.autoLoadState.isRunning, statusResp.autoLoadState);
        }
      });
      startStatusPolling();
    } else if (detectedPageType === "listing") {
      statusListing.classList.remove("hidden");
      statusSearch.classList.add("hidden");
      statusUnsupported.classList.add("hidden");

      listingIdEl.textContent = response.listingId || "Detected";

      btnCapture.disabled = false;
      btnCaptureText.textContent = "Capture Listing";
      captureTip.classList.add("hidden");
      autoLoadCard.classList.add("hidden");
    } else {
      showUnsupportedState();
    }
  }

  /**
   * Fallback detector based on tab URL alone.
   */
  function tryFallbackTabUrlDetection(url) {
    if (!url.includes("olx.in")) {
      showUnsupportedState();
      return;
    }

    if (url.includes("/item/") || url.includes("iid-")) {
      detectedPageType = "listing";
      statusListing.classList.remove("hidden");
      statusSearch.classList.add("hidden");
      statusUnsupported.classList.add("hidden");
      btnCapture.disabled = false;
      btnCaptureText.textContent = "Capture Listing";
      autoLoadCard.classList.add("hidden");
    } else {
      detectedPageType = "search";
      statusSearch.classList.remove("hidden");
      statusListing.classList.add("hidden");
      statusUnsupported.classList.add("hidden");
      btnCapture.disabled = false;
      btnCaptureText.textContent = "Capture Search Page";
      captureTip.classList.remove("hidden");
      autoLoadCard.classList.remove("hidden");
      startStatusPolling();
    }
  }

  /**
   * Display unsupported UI state.
   */
  function showUnsupportedState() {
    detectedPageType = "unsupported";
    statusUnsupported.classList.remove("hidden");
    statusSearch.classList.add("hidden");
    statusListing.classList.add("hidden");
    btnCapture.disabled = true;
    btnCaptureText.textContent = "Capture Unavailable";
    captureTip.classList.add("hidden");
    autoLoadCard.classList.add("hidden");
  }

  /**
   * Manual Capture Button Click Handler
   */
  btnCapture.addEventListener("click", async () => {
    if (!activeTab || detectedPageType === "unsupported") return;

    btnCapture.disabled = true;
    btnCaptureText.textContent = "Capturing...";

    chrome.tabs.sendMessage(activeTab.id, { action: "CAPTURE_PAGE" }, async (response) => {
      btnCapture.disabled = false;

      if (chrome.runtime.lastError || !response) {
        showFeedback("Capture failed: Content script not responding. Try refreshing the OLX page.", "error");
        btnCaptureText.textContent = detectedPageType === "search" ? "Capture Now" : "Capture Listing";
        return;
      }

      if (response.status === "success" && response.captureEnvelope) {
        try {
          await captureDB.saveCapture(response.captureEnvelope);
          const count = response.listingsCaptured || response.captureEnvelope.listings.length;
          showFeedback(`Successfully captured ${count} ${count === 1 ? "listing" : "listings"}! ✓`, "success");
          await refreshStats();
        } catch (storageErr) {
          console.error("Storage error:", storageErr);
          showFeedback(`Storage error: ${storageErr.message}`, "error");
        }
      } else {
        showFeedback(`Error: ${response.message || "Failed to capture."}`, "error");
      }

      btnCaptureText.textContent = detectedPageType === "search" ? "Capture Now" : "Capture Listing";
    });
  });

  /**
   * Auto-Load Button Click Handler
   */
  btnAutoLoad.addEventListener("click", () => {
    if (!activeTab || detectedPageType !== "search") return;

    if (!isAutoLoading) {
      // Start Auto-Load
      chrome.tabs.sendMessage(activeTab.id, { action: "START_AUTO_LOAD", intervalSeconds: 5 }, (response) => {
        if (chrome.runtime.lastError || !response || response.status !== "ok") {
          showFeedback("Failed to start auto-loader. Try refreshing the page.", "error");
        } else {
          updateAutoLoadUI(true, response.autoLoadState);
          showFeedback("Auto-loader started! Clicks 'Load More' every 5s. 🚀", "success");
        }
      });
    } else {
      // Stop Auto-Load
      chrome.tabs.sendMessage(activeTab.id, { action: "STOP_AUTO_LOAD" }, (response) => {
        updateAutoLoadUI(false, response?.autoLoadState);
        showFeedback("Auto-loader stopped.", "success");
        refreshStats();
      });
    }
  });

  /**
   * Export JSON Button Click Handler
   */
  btnExport.addEventListener("click", async () => {
    try {
      btnExport.disabled = true;
      const result = await OLXExporter.exportToJSON();
      showFeedback(`Exported ${result.listings_count} listings to ${result.filename}`, "success");
    } catch (err) {
      showFeedback(err.message || "Export failed.", "error");
    } finally {
      btnExport.disabled = false;
      await refreshStats();
    }
  });

  /**
   * Clear Captures Button Click Handler
   */
  btnClear.addEventListener("click", async () => {
    const confirmClear = confirm("Are you sure you want to clear all locally captured listings?");
    if (confirmClear) {
      await OLXExporter.clearCaptures();
      await refreshStats();
      showFeedback("Storage cleared successfully.", "success");
    }
  });
});
