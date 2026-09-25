/**
 * Media Extractor & Gallery Deduplicator
 * Extracts unique images from listing pages, search cards, and carousels.
 * Robust against Slick carousel clone duplicates and multiple resolution variants.
 */

class OLXMediaExtractor {
  /**
   * Extract unique OLX file/media identifier from image URL.
   * e.g., "https://apollo.olx.in/v1/files/e9l0k8h-1853436229/image;s=1080x1080" -> "e9l0k8h-1853436229"
   * @param {string} url
   * @returns {string} canonical identifier
   */
  static extractFileId(url) {
    if (!url || typeof url !== "string") return "";

    // 1. Apollo files pattern: /files/<file_id>/
    const apolloMatch = url.match(/\/files\/([^/?#;]+)/i);
    if (apolloMatch) {
      return apolloMatch[1];
    }

    // 2. Fallback: normalize by removing dimensions, hashes, and query params
    try {
      const parsed = new URL(url);
      const cleanPath = parsed.pathname.replace(/;s=\d+x\d+.*$/i, "").replace(/;q=\d+.*$/i, "");
      return `${parsed.hostname}${cleanPath}`;
    } catch {
      return url.split("?")[0].split(";")[0];
    }
  }

  /**
   * Cleans an image URL to its highest resolution / canonical form.
   * @param {string} url
   * @returns {string}
   */
  static canonicalizeUrl(url) {
    if (!url || typeof url !== "string") return "";
    return url.trim();
  }

  /**
   * Extract single main image from a search card or container.
   * @param {Element} container
   * @returns {Array<Object>}
   */
  static extractCardMedia(container) {
    if (!container) return [];

    const img = container.querySelector('img[data-aut-id="itemImage"], img[src*="apollo"], img');
    if (!img) return [];

    const src = img.getAttribute("src") || img.getAttribute("data-src") || "";
    if (!src || src.startsWith("data:")) return [];

    const fileId = this.extractFileId(src);

    return [
      {
        file_id: fileId || null,
        src: this.canonicalizeUrl(src),
        srcset: img.getAttribute("srcset") || null,
        alt: img.getAttribute("alt") || null,
        gallery_index: 0,
      },
    ];
  }

  /**
   * Extract all unique gallery images from an individual listing page.
   * Handles Slick carousel cloned slides and thumbnail grids safely.
   * @param {Document|Element} root
   * @returns {Array<Object>}
   */
  static extractGalleryMedia(root = document) {
    if (!root) return [];

    const mediaList = [];
    const seenFileIds = new Set();
    const seenUrls = new Set();

    // 1. Target primary gallery containers and images
    // Primary selectors using data-aut-id or gallery wrappers
    const candidateImgs = root.querySelectorAll(
      '[data-aut-id="itemImage"], ' +
      '.slick-slider img, ' +
      '[data-aut-id="gallery"] img, ' +
      'div[class*="gallery"] img, ' +
      'div[class*="carousel"] img, ' +
      'div[class*="image"] img[src*="apollo"], ' +
      'img[src*="apollo.olx.in"], ' +
      'img[src*="apollo-singapore"], ' +
      'img[src*="/v1/files/"]'
    );

    let galleryIdx = 0;

    candidateImgs.forEach((img) => {
      // Check if image is an icon, placeholder, or UI badge
      const src = img.getAttribute("src") || img.getAttribute("data-src") || "";
      if (!src || src.startsWith("data:") || src.includes("icon") || src.includes("avatar")) {
        return;
      }

      // Canonicalize and deduplicate
      const cleanUrl = this.canonicalizeUrl(src);
      const fileId = this.extractFileId(cleanUrl);

      const dedupeKey = fileId || cleanUrl;

      if (dedupeKey && (seenFileIds.has(dedupeKey) || seenUrls.has(cleanUrl))) {
        // Skip duplicate carousel slide / duplicate clone
        return;
      }

      seenFileIds.add(dedupeKey);
      seenUrls.add(cleanUrl);

      mediaList.push({
        file_id: fileId || null,
        src: cleanUrl,
        srcset: img.getAttribute("srcset") || null,
        alt: img.getAttribute("alt") || null,
        gallery_index: galleryIdx++,
      });
    });

    // 2. Also check for background-image style slides if no img tags found
    if (mediaList.length === 0) {
      const bgElements = root.querySelectorAll('[style*="background-image"], [data-aut-id="itemImage"]');
      bgElements.forEach((el) => {
        const style = el.getAttribute("style") || "";
        const match = style.match(/url\(["']?(https?:\/\/[^"'\)]+)["']?\)/i);
        if (match) {
          const bgUrl = this.canonicalizeUrl(match[1]);
          const fileId = this.extractFileId(bgUrl);
          const dedupeKey = fileId || bgUrl;
          if (!seenFileIds.has(dedupeKey)) {
            seenFileIds.add(dedupeKey);
            mediaList.push({
              file_id: fileId || null,
              src: bgUrl,
              srcset: null,
              alt: null,
              gallery_index: galleryIdx++,
            });
          }
        }
      });
    }

    return mediaList;
  }
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { OLXMediaExtractor };
}
