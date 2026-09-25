/**
 * Normalizer utility for TrustLens OLX captures.
 * Converts raw observed DOM strings into clean structured data while preserving originals.
 */

class OLXNormalizer {
  /**
   * Parse raw price text into numeric amount and currency.
   * Examples:
   *  "₹ 58,000" -> { amount: 58000, currency: "INR" }
   *  "Rs. 25,999" -> { amount: 25999, currency: "INR" }
   *  "Free" -> { amount: 0, currency: "INR" }
   * @param {string|null} rawPrice
   * @returns {{ amount: number|null, currency: string }}
   */
  static normalizePrice(rawPrice) {
    if (!rawPrice || typeof rawPrice !== "string") {
      return { amount: null, currency: "INR" };
    }

    const trimmed = rawPrice.trim();
    if (trimmed.toLowerCase() === "free") {
      return { amount: 0, currency: "INR" };
    }

    // Determine currency
    let currency = "INR";
    if (trimmed.includes("$")) currency = "USD";
    else if (trimmed.includes("€")) currency = "EUR";
    else if (trimmed.includes("£")) currency = "GBP";

    // Extract digits and optional decimals
    const digitsMatch = trimmed.replace(/,/g, "").match(/(\d+(?:\.\d+)?)/);
    if (digitsMatch) {
      const parsedAmount = parseFloat(digitsMatch[1]);
      return {
        amount: isNaN(parsedAmount) ? null : parsedAmount,
        currency,
      };
    }

    return { amount: null, currency };
  }

  /**
   * Clean text by collapsing excessive whitespace.
   * @param {string|null} text
   * @returns {string|null}
   */
  static cleanText(text) {
    if (!text || typeof text !== "string") return null;
    const cleaned = text.replace(/\s+/g, " ").trim();
    return cleaned.length > 0 ? cleaned : null;
  }

  /**
   * Cleans and splits description into paragraphs while preserving original line structure.
   * @param {string|Element} rawDescription
   * @returns {{ text: string, paragraphs: Array<string> }}
   */
  static normalizeDescription(rawDescription) {
    if (!rawDescription) {
      return { text: "", paragraphs: [] };
    }

    if (typeof rawDescription === "string") {
      const paragraphs = rawDescription
        .split(/\r?\n+/)
        .map((p) => p.trim())
        .filter((p) => p.length > 0);
      return {
        text: rawDescription.trim(),
        paragraphs,
      };
    }

    // If passed a DOM element (e.g. [data-aut-id="itemDescriptionContent"])
    if (typeof rawDescription === "object" && rawDescription.querySelectorAll) {
      const pElements = rawDescription.querySelectorAll("p, span, div");
      let paragraphs = [];

      if (pElements.length > 0) {
        pElements.forEach((el) => {
          // only take direct or leaf text elements to avoid nested duplication
          if (el.children.length === 0) {
            const t = el.textContent?.trim();
            if (t) paragraphs.push(t);
          }
        });
      }

      if (paragraphs.length === 0) {
        const rawText = rawDescription.innerText || rawDescription.textContent || "";
        paragraphs = rawText
          .split(/\r?\n+/)
          .map((p) => p.trim())
          .filter((p) => p.length > 0);
      }

      const fullText = paragraphs.join("\n").trim() || rawDescription.textContent?.trim() || "";
      return {
        text: fullText,
        paragraphs,
      };
    }

    return { text: "", paragraphs: [] };
  }
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { OLXNormalizer };
}
