"""
TrustLens Marketplace Intelligence — Deterministic Condition Parser (Phase B).
Extracts condition only when explicit lexical cues exist in the listing text.
"""

import re
from typing import List, Optional, Tuple

from trustlens.marketplace.product_taxonomy import Condition


class ConditionParser:
    """Deterministic extractor of product condition and textual cues."""

    # Patterns for condition categories (ordered by specificity)
    PATTERNS: List[Tuple[Condition, List[str], List[re.Pattern]]] = [
        (
            Condition.FOR_PARTS,
            ["for parts", "damaged", "broken", "not working", "dead", "faulty", "cracked display", "touch not working", "face id not working", "bypass"],
            [
                re.compile(r"\b(?:for\s+parts|damaged|broken|not\s+working|dead|faulty|bypass)\b", re.IGNORECASE),
                re.compile(r"\b(?:display\s+broken|screen\s+cracked|face\s*id\s+issue)\b", re.IGNORECASE),
            ],
        ),
        (
            Condition.REFURBISHED,
            ["refurbished", "renewed", "repaired", "replacement", "replaced"],
            [
                re.compile(r"\b(?:refurbished|renewed|repaired|replacement\s+piece)\b", re.IGNORECASE),
            ],
        ),
        (
            Condition.NEW,
            ["brand new", "sealed", "unopened", "unused", "box pack", "seal pack", "packed"],
            [
                re.compile(r"\b(?:brand\s+new|sealed|unopened|unused|box\s*pack|seal\s*pack|pin\s*pack)\b", re.IGNORECASE),
                re.compile(r"\bnew\s+piece\b", re.IGNORECASE),
            ],
        ),
        (
            Condition.LIKE_NEW,
            ["like new", "mint condition", "flawless", "scratchless", "as new", "super clean"],
            [
                re.compile(r"\b(?:like\s+new|mint(?:\s+condition)?|flawless|scratchless|as\s+new|super\s+clean|neat\s+and\s+clean)\b", re.IGNORECASE),
                re.compile(r"\b(?:10/10\s+condition|9\.9/10\s+condition)\b", re.IGNORECASE),
            ],
        ),
        (
            Condition.USED,
            ["used", "second hand", "pre owned", "pre-owned", "old", "months old", "days old", "year old"],
            [
                re.compile(r"\b(?:used|second\s*hand|pre[- ]owned|good\s+condition|running\s+condition)\b", re.IGNORECASE),
                re.compile(r"\b\d+\s*(?:days?|months?|years?)\s*old\b", re.IGNORECASE),
                re.compile(r"\b(?:under\s+warranty|bill\s*box)\b", re.IGNORECASE),
            ],
        ),
    ]

    # Explicit condition cue extraction patterns
    CUE_PATTERNS = [
        re.compile(r"\b\d+\s*(?:days?|months?|years?)\s*old\b", re.IGNORECASE),
        re.compile(r"\b(?:100%|9\d%|8\d%|7\d%)\s*(?:battery\s*health|battery|bh)\b", re.IGNORECASE),
        re.compile(r"\bbattery\s*(?:health)?\s*(?:100%|9\d%|8\d%|7\d%)\b", re.IGNORECASE),
        re.compile(r"\b(?:brand\s+new|sealed|seal\s*pack|box\s*pack|unopened|unused)\b", re.IGNORECASE),
        re.compile(r"\b(?:like\s+new|mint\s*condition|scratchless|flawless)\b", re.IGNORECASE),
        re.compile(r"\b(?:second\s*hand|pre[- ]owned|used)\b", re.IGNORECASE),
        re.compile(r"\b(?:bill\s*box|box\s*bill|with\s*bill|original\s*bill)\b", re.IGNORECASE),
        re.compile(r"\b(?:under\s+warranty|apple\s+warranty)\b", re.IGNORECASE),
        re.compile(r"\b(?:refurbished|renewed|repaired)\b", re.IGNORECASE),
        re.compile(r"\b(?:broken|damaged|not\s*working|for\s*parts)\b", re.IGNORECASE),
    ]

    @classmethod
    def parse_condition(cls, text: Optional[str]) -> Tuple[Condition, List[str]]:
        """
        Parses text and returns (Condition, List[condition_cues]).
        Returns (Condition.UNKNOWN, []) if no explicit condition evidence exists.
        """
        if not text or not text.strip():
            return Condition.UNKNOWN, []

        clean_text = text.strip()
        cues: List[str] = []

        # Extract all matching cues
        for pattern in cls.CUE_PATTERNS:
            for match in pattern.finditer(clean_text):
                matched_cue = match.group(0).strip()
                if matched_cue not in cues:
                    cues.append(matched_cue)

        # Determine condition priority
        detected_condition = Condition.UNKNOWN
        for cond, _, regex_list in cls.PATTERNS:
            for regex in regex_list:
                if regex.search(clean_text):
                    detected_condition = cond
                    break
            if detected_condition != Condition.UNKNOWN:
                break

        return detected_condition, cues
