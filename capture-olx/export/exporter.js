/**
 * TrustLens OLX Exporter
 * Generates and downloads standard JSON export from IndexedDB.
 */

class OLXExporter {
  /**
   * Export all captures from IndexedDB into a single JSON file.
   * @returns {Promise<{ filename: string, captures_count: number, listings_count: number }>}
   */
  static async exportToJSON() {
    if (typeof captureDB === "undefined") {
      throw new Error("IndexedDB capture database not available.");
    }

    const captures = await captureDB.getAllCaptures();
    if (!captures || captures.length === 0) {
      throw new Error("No captured records found in storage to export.");
    }

    // Deduplicate listings across capture envelopes
    const seenListingIds = new Set();
    const deduplicatedCaptures = [];

    for (const cap of captures) {
      const uniqueListingsInCap = [];
      for (const item of (cap.listings || [])) {
        const id = item.listing_id || item.source_url;
        if (id && !seenListingIds.has(id)) {
          seenListingIds.add(id);
          uniqueListingsInCap.push(item);
        }
      }

      if (uniqueListingsInCap.length > 0) {
        deduplicatedCaptures.push({
          ...cap,
          listings: uniqueListingsInCap,
          capture_context: {
            ...cap.capture_context,
            total_rendered_cards: uniqueListingsInCap.length,
          },
        });
      }
    }

    const payload = typeof createExportPayload === "function"
      ? createExportPayload(deduplicatedCaptures)
      : {
          schema_version: "1.0",
          source: "olx.in",
          exported_at: new Date().toISOString(),
          captures_count: deduplicatedCaptures.length,
          captures: deduplicatedCaptures,
        };

    // Generate descriptive filename using research search query or item title
    let querySlug = "";
    for (const cap of deduplicatedCaptures) {
      if (cap.capture_context && cap.capture_context.search_query) {
        querySlug = cap.capture_context.search_query
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, "_")
          .replace(/^_+|_+$/g, "");
        if (querySlug) break;
      }
      if (cap.listings && cap.listings[0]) {
        const itemTitle = cap.listings[0].normalized?.title || cap.listings[0].raw?.title || "";
        if (itemTitle) {
          querySlug = itemTitle
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "_")
            .slice(0, 30)
            .replace(/^_+|_+$/g, "");
          if (querySlug) break;
        }
      }
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
    const filename = querySlug
      ? `trustlens_olx_${querySlug}_${timestamp}.json`
      : `trustlens_olx_captures_${timestamp}.json`;

    const jsonString = JSON.stringify(payload, null, 2);
    const dataUrl = "data:application/json;charset=utf-8," + encodeURIComponent(jsonString);

    // Primary: Native Chrome extension downloads API
    let downloadInitiated = false;

    if (typeof chrome !== "undefined" && chrome.downloads && typeof chrome.downloads.download === "function") {
      try {
        await new Promise((resolve, reject) => {
          chrome.downloads.download(
            {
              url: dataUrl,
              filename: filename,
              saveAs: false,
            },
            (downloadId) => {
              if (chrome.runtime.lastError || !downloadId) {
                reject(new Error(chrome.runtime.lastError?.message || "Chrome download failed"));
              } else {
                resolve(downloadId);
              }
            }
          );
        });
        downloadInitiated = true;
      } catch (chromeErr) {
        console.warn("[TrustLens] chrome.downloads failed, trying anchor fallback:", chromeErr);
      }
    }

    // Fallback: Standard browser DOM anchor download
    if (!downloadInitiated) {
      try {
        const blob = new Blob([jsonString], { type: "application/json;charset=utf-8" });
        const blobUrl = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = blobUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        setTimeout(() => URL.revokeObjectURL(blobUrl), 30000);
        downloadInitiated = true;
      } catch (domErr) {
        console.error("[TrustLens] Anchor download failed:", domErr);
        throw new Error("Unable to trigger file download. Please verify browser permissions.");
      }
    }

    const totalListings = deduplicatedCaptures.reduce((acc, c) => acc + (c.listings ? c.listings.length : 0), 0);

    return {
      filename,
      captures_count: deduplicatedCaptures.length,
      listings_count: totalListings,
    };
  }

  /**
   * Clear all captured records after export confirmation.
   * @returns {Promise<boolean>}
   */
  static async clearCaptures() {
    if (typeof captureDB === "undefined") {
      throw new Error("IndexedDB capture database not available.");
    }
    return await captureDB.clearAll();
  }
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { OLXExporter };
}
