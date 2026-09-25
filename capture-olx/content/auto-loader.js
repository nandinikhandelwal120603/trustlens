/**
 * TrustLens OLX Capture - Auto-Loader & Continuous Collector
 * Automatically clicks "Load More" on OLX search pages every 5 seconds,
 * extracts all rendered listing cards, and saves them to local storage.
 */

class OLXAutoLoader {
  constructor() {
    this.isRunning = false;
    this.intervalMs = 5000;
    this.timerId = null;
    this.countdownTimerId = null;
    this.countdownSeconds = 5;
    this.iteration = 0;
    this.totalListingsCollected = 0;
    this.consecutiveNoButtons = 0;
    this.hudElement = null;
    this.statusListeners = [];
  }

  /**
   * Find the OLX "Load More" button in DOM using multiple robust selectors.
   * @param {Document} doc
   * @returns {Element|null}
   */
  static findLoadMoreButton(doc = (typeof document !== "undefined" ? document : null)) {
    if (!doc) return null;

    // 1. Primary data-aut-id attribute
    const primaryBtn = doc.querySelector(
      'button[data-aut-id="btnLoadMore"], ' +
      'button[data-aut-id*="loadMore" i], ' +
      'button[data-aut-id*="load-more" i], ' +
      'div[data-aut-id="btnLoadMore"]'
    );
    if (primaryBtn && typeof primaryBtn.click === "function") {
      return primaryBtn;
    }

    // 2. Button or link containing text "load more"
    const allButtons = doc.querySelectorAll('button, a[role="button"], div[role="button"]');
    for (const btn of allButtons) {
      const text = (btn.textContent || "").trim().toLowerCase();
      if (text.includes("load more") || text.includes("load_more") || text === "more") {
        return btn;
      }
    }

    // 3. Class-based fallback
    const classBtn = doc.querySelector('[class*="loadMore" i], [class*="load-more" i]');
    if (classBtn && typeof classBtn.click === "function") {
      return classBtn;
    }

    return null;
  }

  /**
   * Start auto-loading every intervalSeconds (default: 5s).
   * @param {number} intervalSeconds
   * @returns {boolean}
   */
  start(intervalSeconds = 5) {
    if (this.isRunning) return false;

    this.isRunning = true;
    this.intervalMs = Math.max(2, intervalSeconds) * 1000;
    this.countdownSeconds = Math.round(this.intervalMs / 1000);
    this.iteration = 0;
    this.consecutiveNoButtons = 0;

    console.log(`[TrustLens] Auto-loader started (${intervalSeconds}s interval).`);
    this._mountHUD();
    this._notifyStatus("Auto-collector started...");

    // Execute first tick immediately
    this._executeTick();

    // Start interval
    this.timerId = setInterval(() => {
      this._executeTick();
    }, this.intervalMs);

    // Start countdown ticker for UI
    this._startCountdownTicker();

    return true;
  }

  /**
   * Stop auto-loading and perform final capture.
   */
  stop(reason = "Researcher stopped auto-collector") {
    if (!this.isRunning) return;

    this.isRunning = false;
    if (this.timerId) {
      clearInterval(this.timerId);
      this.timerId = null;
    }
    if (this.countdownTimerId) {
      clearInterval(this.countdownTimerId);
      this.countdownTimerId = null;
    }

    console.log(`[TrustLens] Auto-loader stopped: ${reason}`);
    this._notifyStatus(`Stopped: ${reason}`);

    // Perform final extraction to ensure all rendered cards are saved
    this._captureAndSave(true);

    if (this.hudElement) {
      this._updateHUD(0, `Auto-Collector Stopped • ${this.totalListingsCollected} listings total`);
      setTimeout(() => {
        if (!this.isRunning) {
          this._unmountHUD();
        }
      }, 5000);
    }
  }

  /**
   * Current status query.
   */
  getStatus() {
    return {
      isRunning: this.isRunning,
      iteration: this.iteration,
      totalListingsCollected: this.totalListingsCollected,
      intervalSeconds: Math.round(this.intervalMs / 1000),
      countdownSeconds: this.countdownSeconds,
    };
  }

  /**
   * Register a callback listener for status updates.
   */
  addStatusListener(fn) {
    if (typeof fn === "function") {
      this.statusListeners.push(fn);
    }
  }

  /**
   * Internal single tick execution.
   */
  async _executeTick() {
    if (!this.isRunning || typeof document === "undefined") return;

    this.iteration += 1;
    this.countdownSeconds = Math.round(this.intervalMs / 1000);

    // 1. Scroll smoothly towards bottom to bring load more button and lazy images into view
    try {
      if (typeof window !== "undefined") {
        window.scrollTo({
          top: document.body.scrollHeight - 600,
          behavior: "smooth",
        });
      }
    } catch (e) {
      // ignore
    }

    // 2. Find and click Load More button
    const loadBtn = OLXAutoLoader.findLoadMoreButton(document);

    if (loadBtn) {
      this.consecutiveNoButtons = 0;
      try {
        loadBtn.scrollIntoView({ behavior: "smooth", block: "center" });
        loadBtn.click();
        this._updateHUD(this.countdownSeconds, `Clicked "Load More" (Batch #${this.iteration})`);
        this._notifyStatus(`Batch #${this.iteration}: Clicked Load More`);
      } catch (err) {
        console.warn("[TrustLens] Click error:", err);
      }
    } else {
      this.consecutiveNoButtons += 1;
      this._updateHUD(this.countdownSeconds, `Scrolling... (No Load More button visible #${this.consecutiveNoButtons})`);

      // If no button found 4 times in a row, all listings might be loaded
      if (this.consecutiveNoButtons >= 4) {
        this.stop("All available listings loaded from OLX");
        return;
      }
    }

    // 3. Wait 1.5 seconds for network / DOM update, then capture
    setTimeout(() => {
      if (this.isRunning) {
        this._captureAndSave(false);
      }
    }, 1500);
  }

  /**
   * Capture search page and dispatch to extension storage.
   */
  _captureAndSave(isFinal = false) {
    if (typeof document === "undefined") return;

    try {
      if (typeof OLXSearchCapture === "undefined") {
        console.warn("[TrustLens] OLXSearchCapture not available.");
        return;
      }

      const captureEnvelope = OLXSearchCapture.captureSearchPage(document, window.location.href);
      if (!captureEnvelope || !captureEnvelope.listings) return;

      const count = captureEnvelope.listings.length;
      this.totalListingsCollected = count;

      // Send to background / extension IndexedDB
      if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.sendMessage) {
        chrome.runtime.sendMessage(
          {
            action: "SAVE_CAPTURE",
            captureEnvelope,
            isAutoCollect: true,
            iteration: this.iteration,
          },
          (response) => {
            if (chrome.runtime.lastError) {
              // Service worker might be sleeping or popup handles it
            }
          }
        );
      }

      const statusMsg = `Saved ${count} listings (Batch #${this.iteration}${isFinal ? " - Final" : ""})`;
      this._updateHUD(this.countdownSeconds, statusMsg);
      this._notifyStatus(statusMsg);
    } catch (err) {
      console.error("[TrustLens] Auto-collect capture error:", err);
    }
  }

  /**
   * Start 1-second countdown ticker for UI feedback.
   */
  _startCountdownTicker() {
    if (this.countdownTimerId) clearInterval(this.countdownTimerId);

    this.countdownTimerId = setInterval(() => {
      if (!this.isRunning) {
        clearInterval(this.countdownTimerId);
        return;
      }
      if (this.countdownSeconds > 0) {
        this.countdownSeconds -= 1;
      }
      this._updateHUD(
        this.countdownSeconds,
        `Active • ${this.totalListingsCollected} listings collected (Batch #${this.iteration})`
      );
    }, 1000);
  }

  /**
   * Notify external listeners.
   */
  _notifyStatus(message) {
    const status = { ...this.getStatus(), message };
    for (const fn of this.statusListeners) {
      try {
        fn(status);
      } catch (e) {
        // ignore
      }
    }
  }

  /**
   * Mount floating on-page HUD pill.
   */
  _mountHUD() {
    if (typeof document === "undefined") return;
    if (document.getElementById("trustlens-autoloader-hud")) return;

    const hud = document.createElement("div");
    hud.id = "trustlens-autoloader-hud";
    hud.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 9999999;
      background: rgba(15, 23, 42, 0.92);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(59, 130, 246, 0.4);
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 0 15px rgba(59, 130, 246, 0.2);
      border-radius: 12px;
      padding: 12px 16px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #f8fafc;
      font-size: 13px;
      display: flex;
      align-items: center;
      gap: 14px;
      animation: trustlensSlideIn 0.3s ease-out;
    `;

    hud.innerHTML = `
      <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 18px; filter: drop-shadow(0 0 4px #3b82f6);">🛡️</span>
        <div>
          <div style="font-weight: 700; font-size: 12px; letter-spacing: 0.5px; color: #60a5fa;">TRUSTLENS AUTO-COLLECTOR</div>
          <div id="tl-hud-text" style="font-size: 12px; color: #cbd5e1; margin-top: 2px;">Starting auto-loader (5s)...</div>
        </div>
      </div>
      <div id="tl-hud-countdown" style="
        background: rgba(59, 130, 246, 0.2);
        border: 1px solid rgba(96, 165, 250, 0.4);
        color: #93c5fd;
        font-weight: 700;
        font-size: 12px;
        padding: 4px 8px;
        border-radius: 6px;
        min-width: 28px;
        text-align: center;
      ">5s</div>
      <button id="tl-hud-stop-btn" style="
        background: #ef4444;
        color: #ffffff;
        border: none;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 12px;
        cursor: pointer;
        transition: background 0.2s;
      ">⏹ Stop</button>
    `;

    document.body.appendChild(hud);
    this.hudElement = hud;

    const stopBtn = hud.querySelector("#tl-hud-stop-btn");
    if (stopBtn) {
      stopBtn.addEventListener("click", () => this.stop("Stopped by user via on-page HUD"));
      stopBtn.addEventListener("mouseenter", () => (stopBtn.style.background = "#dc2626"));
      stopBtn.addEventListener("mouseleave", () => (stopBtn.style.background = "#ef4444"));
    }
  }

  /**
   * Update HUD pill contents.
   */
  _updateHUD(countdownSecs, text) {
    if (!this.hudElement) return;

    const textEl = this.hudElement.querySelector("#tl-hud-text");
    const countEl = this.hudElement.querySelector("#tl-hud-countdown");

    if (textEl && text) textEl.textContent = text;
    if (countEl) {
      countEl.textContent = `${countdownSecs}s`;
      countEl.style.color = countdownSecs <= 1 ? "#34d399" : "#93c5fd";
    }
  }

  /**
   * Unmount HUD pill from DOM.
   */
  _unmountHUD() {
    if (this.hudElement && this.hudElement.parentNode) {
      this.hudElement.parentNode.removeChild(this.hudElement);
      this.hudElement = null;
    }
  }
}

// Global instance for browser execution
const olxAutoLoader = new OLXAutoLoader();

if (typeof module !== "undefined" && module.exports) {
  module.exports = { OLXAutoLoader, olxAutoLoader };
}
