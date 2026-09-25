"""Data normalization engine for TrustLens marketplace listings.

Normalizes prices, currency symbols, condition vernacular, category taxonomy,
and text strings while preserving all raw source inputs.
"""

import re
import unicodedata
from typing import Any, Optional, Tuple

from trustlens.config.categories import ELECTRONICS_TAXONOMY, SUBCATEGORY_ALIASES
from trustlens.models.common import ItemCondition


class Normalizer:
    """Core normalizer for marketplace data fields."""

    # ------------------------------------------------------------------
    # Price and Currency Normalization
    # ------------------------------------------------------------------

    CURRENCY_SYMBOLS: dict[str, str] = {
        "₹": "INR",
        "rs.": "INR",
        "rs": "INR",
        "inr": "INR",
        "$": "USD",
        "usd": "USD",
        "€": "EUR",
        "eur": "EUR",
        "£": "GBP",
        "gbp": "GBP",
    }

    @classmethod
    def normalize_price(
        cls, raw_val: Any, raw_currency: Optional[str] = None
    ) -> Tuple[Optional[float], Optional[float], Optional[str], Optional[str]]:
        """Parse raw price string or number into (raw_num, normalized_price, raw_curr, norm_curr).

        Handles:
        - "₹45,000" -> (45000.0, 45000.0, "₹", "INR")
        - "45k"     -> (45000.0, 45000.0, None, "INR")
        - "Rs. 45000" -> (45000.0, 45000.0, "Rs.", "INR")
        - "1.5 Lakh" -> (150000.0, 150000.0, None, "INR")
        - 45000     -> (45000.0, 45000.0, None, "INR")
        """
        if raw_val is None or raw_val == "":
            return (None, None, raw_currency, "INR")

        if isinstance(raw_val, (int, float)):
            num = float(raw_val)
            norm_curr = cls.normalize_currency(raw_currency) or "INR"
            return (num, num, raw_currency, norm_curr)

        text = str(raw_val).strip()

        # Detect currency from string if not explicitly given
        detected_curr = raw_currency
        for sym in cls.CURRENCY_SYMBOLS:
            pattern = rf"\b{re.escape(sym)}\b" if len(sym) > 1 else re.escape(sym)
            if re.search(pattern, text, re.IGNORECASE):
                if not detected_curr:
                    detected_curr = sym
                break

        norm_curr = cls.normalize_currency(detected_curr) or "INR"

        # Clean string for numeric parsing
        cleaned = text.lower()
        for sym in cls.CURRENCY_SYMBOLS.keys():
            cleaned = cleaned.replace(sym, "")

        cleaned = cleaned.replace(",", "").strip()

        # Handle 'k' multiplier (e.g. 45k -> 45000)
        k_match = re.search(r"(\d+(?:\.\d+)?)\s*k\b", cleaned)
        if k_match:
            val = float(k_match.group(1)) * 1000.0
            return (val, val, detected_curr, norm_curr)

        # Handle 'lakh' / 'lac' multiplier (e.g. 1.5 lakh -> 150000)
        lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs)\b", cleaned)
        if lakh_match:
            val = float(lakh_match.group(1)) * 100000.0
            return (val, val, detected_curr, norm_curr)

        # Handle regular numeric extraction
        num_match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
        if num_match:
            try:
                val = float(num_match.group(1))
                return (val, val, detected_curr, norm_curr)
            except ValueError:
                pass

        return (None, None, detected_curr, norm_curr)

    @classmethod
    def normalize_currency(cls, curr: Optional[str]) -> Optional[str]:
        """Map currency symbol or abbreviation to ISO 4217 code."""
        if not curr:
            return "INR"
        cleaned = curr.strip().lower()
        return cls.CURRENCY_SYMBOLS.get(cleaned, cleaned.upper())

    # ------------------------------------------------------------------
    # Condition Normalization
    # ------------------------------------------------------------------

    @classmethod
    def normalize_condition(cls, raw_cond: Optional[str]) -> ItemCondition:
        """Map messy condition text to ItemCondition enum."""
        if not raw_cond or not str(raw_cond).strip():
            return ItemCondition.UNKNOWN

        cond = str(raw_cond).strip().lower()

        # Exact enum name matches
        for member in ItemCondition:
            if cond == member.value:
                return member

        # NEW patterns
        if any(
            w in cond
            for w in ["brand new", "seal pack", "sealed", "unopened", "unused", "box pack"]
        ):
            return ItemCondition.NEW

        # LIKE_NEW patterns
        if any(
            w in cond
            for w in [
                "like new",
                "mint",
                "flawless",
                "open box",
                "box opened",
                "barely used",
                "almost new",
                "10/10",
                "9.5/10",
                "as new",
            ]
        ):
            return ItemCondition.LIKE_NEW

        # GOOD patterns
        if any(
            w in cond
            for w in [
                "good",
                "working",
                "fine",
                "clean",
                "minor scratches",
                "gently used",
                "8/10",
                "9/10",
                "used",
            ]
        ):
            return ItemCondition.GOOD

        # FAIR patterns
        if any(
            w in cond
            for w in ["fair", "average", "scratched", "heavy use", "wear", "7/10", "functional"]
        ):
            return ItemCondition.FAIR

        # POOR patterns
        if any(
            w in cond
            for w in [
                "poor",
                "broken",
                "cracked",
                "damaged",
                "faulty",
                "for parts",
                "repair",
                "not working",
                "dead",
            ]
        ):
            return ItemCondition.POOR

        return ItemCondition.UNKNOWN

    # ------------------------------------------------------------------
    # Category and Subcategory Normalization
    # ------------------------------------------------------------------

    @classmethod
    def normalize_category(
        cls,
        raw_category: Optional[str],
        raw_subcategory: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Tuple[str, Optional[str]]:
        """Normalize category and subcategory against the Electronics Taxonomy.

        Returns (canonical_category, canonical_subcategory).
        """
        cat_input = (raw_category or "").strip()
        sub_input = (raw_subcategory or "").strip()
        title_input = (title or "").lower()

        # 1. Exact canonical category match
        if cat_input in ELECTRONICS_TAXONOMY:
            canonical_cat = cat_input
            # Check subcategory
            sub_matches = ELECTRONICS_TAXONOMY[canonical_cat]["subcategories"]
            for sub in sub_matches:
                if sub.lower() == sub_input.lower():
                    return (canonical_cat, sub)
            # Try subcategory from title
            for sub in sub_matches:
                if sub.lower() in title_input:
                    return (canonical_cat, sub)
            return (canonical_cat, sub_input or None)

        # 2. Check subcategory aliases against sub_input or title
        for alias, (c_cat, c_sub) in SUBCATEGORY_ALIASES.items():
            if sub_input and alias == sub_input.lower():
                return (c_cat, c_sub)
            if cat_input and alias == cat_input.lower():
                return (c_cat, c_sub)

        # 3. Check category aliases in taxonomy
        cat_lower = cat_input.lower()
        for canon_cat, data in ELECTRONICS_TAXONOMY.items():
            if cat_lower in [a.lower() for a in data.get("aliases", [])]:
                # Found category, now find subcategory from subcategories or aliases
                for sub in data["subcategories"]:
                    if sub.lower() in (sub_input.lower() + " " + title_input):
                        return (canon_cat, sub)
                # Check subcategory aliases against title
                for alias, (c_cat, c_sub) in SUBCATEGORY_ALIASES.items():
                    if c_cat == canon_cat and re.search(rf"\b{re.escape(alias)}\b", title_input):
                        return (canon_cat, c_sub)
                return (canon_cat, sub_input or None)

        # 4. Infer from title if category is generic or unknown
        for alias, (c_cat, c_sub) in SUBCATEGORY_ALIASES.items():
            if re.search(rf"\b{re.escape(alias)}\b", title_input):
                return (c_cat, c_sub)

        # Default fallback: preserve raw or 'Electronics'
        return (cat_input or "Electronics", sub_input or None)

    # ------------------------------------------------------------------
    # Text Sanitization
    # ------------------------------------------------------------------

    @classmethod
    def normalize_text(cls, text: Optional[str]) -> Optional[str]:
        """Normalize whitespace, remove invisible unicode, strip edges without altering meaning."""
        if not text:
            return None

        # Normalize unicode (NFKC)
        normalized = unicodedata.normalize("NFKC", text)

        # Preserve paragraph breaks (\n\n) while collapsing single newlines/tabs into single space
        paragraphs = re.split(r"\n\s*\n+", normalized)
        cleaned_paras = []
        for para in paragraphs:
            cleaned_para = re.sub(r"\s+", " ", para).strip()
            if cleaned_para:
                cleaned_paras.append(cleaned_para)

        return "\n\n".join(cleaned_paras) if cleaned_paras else None

    # ------------------------------------------------------------------
    # Location Parsing
    # ------------------------------------------------------------------

    @classmethod
    def parse_location(cls, location_raw: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """Split a comma-separated location into city and state if identifiable."""
        if not location_raw:
            return (None, None)

        parts = [p.strip() for p in location_raw.split(",") if p.strip()]
        if len(parts) >= 3:
            return (parts[-2], parts[-1])
        elif len(parts) == 2:
            return (parts[0], parts[1])
        elif len(parts) == 1:
            return (parts[0], None)
        return (None, None)
