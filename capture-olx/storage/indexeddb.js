/**
 * IndexedDB Storage Layer for TrustLens OLX Capture Extension
 * Stores high-volume capture payloads without hitting chrome.storage.local limits.
 */

const DB_NAME = "TrustLensOLXCaptureDB";
const DB_VERSION = 1;
const STORE_CAPTURES = "captures";

class CaptureDatabase {
  constructor() {
    this._db = null;
    this._initPromise = null;
  }

  /**
   * Initializes or returns the open IndexedDB connection.
   */
  async getDB() {
    if (this._db) return this._db;
    if (this._initPromise) return this._initPromise;

    this._initPromise = new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(STORE_CAPTURES)) {
          const store = db.createObjectStore(STORE_CAPTURES, { keyPath: "capture_id" });
          store.createIndex("captured_at", "captured_at", { unique: false });
          store.createIndex("page_type", "page_type", { unique: false });
          store.createIndex("source_url", "source_url", { unique: false });
        }
      };

      request.onsuccess = (event) => {
        this._db = event.target.result;
        resolve(this._db);
      };

      request.onerror = (event) => {
        console.error("TrustLens IndexedDB open error:", event.target.error);
        reject(event.target.error);
      };
    });

    return this._initPromise;
  }

  /**
   * Saves a capture envelope to IndexedDB.
   * @param {Object} captureRecord
   * @returns {Promise<string>} capture_id
   */
  async saveCapture(captureRecord) {
    const db = await this.getDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORE_CAPTURES], "readwrite");
      const store = transaction.objectStore(STORE_CAPTURES);
      const request = store.put(captureRecord);

      request.onsuccess = () => {
        this._syncCaptureCount().catch(console.warn);
        resolve(captureRecord.capture_id);
      };

      request.onerror = (event) => {
        console.error("Error saving capture to IndexedDB:", event.target.error);
        reject(event.target.error);
      };
    });
  }

  /**
   * Retrieves all capture records sorted by captured_at descending.
   * @returns {Promise<Array<Object>>}
   */
  async getAllCaptures() {
    const db = await this.getDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORE_CAPTURES], "readonly");
      const store = transaction.objectStore(STORE_CAPTURES);
      const request = store.getAll();

      request.onsuccess = (event) => {
        const captures = event.target.result || [];
        captures.sort((a, b) => new Date(b.captured_at) - new Date(a.captured_at));
        resolve(captures);
      };

      request.onerror = (event) => {
        console.error("Error retrieving captures from IndexedDB:", event.target.error);
        reject(event.target.error);
      };
    });
  }

  /**
   * Returns total count of captured envelopes and total listings across envelopes.
   * @returns {Promise<{captures_count: number, listings_count: number}>}
   */
  async getStats() {
    const captures = await this.getAllCaptures();
    const captures_count = captures.length;
    const listings_count = captures.reduce((acc, c) => acc + (c.listings ? c.listings.length : 0), 0);
    return { captures_count, listings_count };
  }

  /**
   * Clears all captures from IndexedDB.
   * @returns {Promise<boolean>}
   */
  async clearAll() {
    const db = await this.getDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORE_CAPTURES], "readwrite");
      const store = transaction.objectStore(STORE_CAPTURES);
      const request = store.clear();

      request.onsuccess = () => {
        this._syncCaptureCount(0, 0).catch(console.warn);
        resolve(true);
      };

      request.onerror = (event) => {
        console.error("Error clearing IndexedDB:", event.target.error);
        reject(event.target.error);
      };
    });
  }

  /**
   * Synchronizes counts with chrome.storage.local for lightweight UI badge display.
   */
  async _syncCaptureCount(capturesCount = null, listingsCount = null) {
    try {
      if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
        if (capturesCount === null || listingsCount === null) {
          const stats = await this.getStats();
          capturesCount = stats.captures_count;
          listingsCount = stats.listings_count;
        }
        await chrome.storage.local.set({
          trustlens_captures_count: capturesCount,
          trustlens_listings_count: listingsCount,
          trustlens_last_updated: new Date().toISOString(),
        });
      }
    } catch (e) {
      // Non-fatal if chrome.storage is not accessible
    }
  }
}

// Global instance for browser execution
const captureDB = new CaptureDatabase();

if (typeof module !== "undefined" && module.exports) {
  module.exports = { CaptureDatabase, captureDB };
}
