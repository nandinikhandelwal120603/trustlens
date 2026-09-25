"""Deterministic text normalization and token similarity matching."""

import re
import unicodedata
from typing import Optional, Set, Tuple


class TextNormalizer:
    """Deterministic normalizer and token similarity comparator for titles and descriptions."""

    @staticmethod
    def normalize_text(text: Optional[str]) -> str:
        """
        Normalize text deterministically:
        - Unicode NFKC normalization
        - Lowercase
        - Remove punctuation & symbols
        - Collapse consecutive whitespace
        """
        if not text:
            return ""

        # 1. Unicode normalization (NFKC decomposes compatibility characters)
        normalized = unicodedata.normalize("NFKC", text)

        # 2. Lowercase
        normalized = normalized.lower()

        # 3. Strip special punctuation, keep alphanumeric and basic spaces
        normalized = re.sub(r"[^\w\s]", " ", normalized)

        # 4. Collapse extra whitespace
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    @classmethod
    def tokenize(cls, text: Optional[str]) -> Set[str]:
        """Tokenize normalized text into unique word tokens."""
        norm = cls.normalize_text(text)
        if not norm:
            return set()
        return set(norm.split())

    @classmethod
    def calculate_jaccard_similarity(cls, text_a: Optional[str], text_b: Optional[str]) -> float:
        """
        Calculate Jaccard token overlap similarity between two text strings:
        J(A, B) = |A ∩ B| / |A ∪ B|
        """
        tokens_a = cls.tokenize(text_a)
        tokens_b = cls.tokenize(text_b)

        if not tokens_a or not tokens_b:
            return 0.0

        intersection = tokens_a.intersection(tokens_b)
        union = tokens_a.union(tokens_b)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    @classmethod
    def compare_titles(
        cls, title_a: Optional[str], title_b: Optional[str], threshold: float = 0.70
    ) -> Tuple[bool, bool, float]:
        """
        Compare two titles deterministically.
        Returns: (is_exact_match, is_similar_candidate, jaccard_score)
        """
        norm_a = cls.normalize_text(title_a)
        norm_b = cls.normalize_text(title_b)

        if not norm_a or not norm_b:
            return False, False, 0.0

        is_exact = norm_a == norm_b
        score = cls.calculate_jaccard_similarity(title_a, title_b)
        is_similar = score >= threshold

        return is_exact, is_similar, score
