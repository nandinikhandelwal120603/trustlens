"""Unit tests for deterministic text normalizer and token overlap."""

from trustlens.marketplace.text_normalizer import TextNormalizer


def test_normalize_text_case_punctuation_whitespace():
    raw1 = "  APPLE   IPHONE 15 PRO   (BOX PACK)!!  "
    raw2 = "apple iphone 15 pro box pack"

    norm1 = TextNormalizer.normalize_text(raw1)
    norm2 = TextNormalizer.normalize_text(raw2)

    assert norm1 == "apple iphone 15 pro box pack"
    assert norm1 == norm2


def test_unicode_normalization():
    # Full-width characters and ligatures
    unicode_text = "ｉＰｈｏｎｅ　１５"
    norm = TextNormalizer.normalize_text(unicode_text)
    assert norm == "iphone 15"


def test_jaccard_token_similarity():
    title_a = "Apple iPhone 15 Pro 256GB Natural Titanium"
    title_b = "Apple iPhone 15 Pro 256GB Blue Titanium"
    title_c = "Sony Playstation 5 Disc Edition"

    score_ab = TextNormalizer.calculate_jaccard_similarity(title_a, title_b)
    score_ac = TextNormalizer.calculate_jaccard_similarity(title_a, title_c)

    # 5 matching tokens out of 7 total unique tokens
    assert score_ab > 0.70
    assert score_ac == 0.0


def test_compare_titles_exact_and_similar():
    t1 = "iPhone 15 Pro 128GB"
    t2 = "iphone 15 pro 128gb"
    t3 = "iPhone 15 Pro 128GB Urgent Sale"
    t4 = "Samsung Galaxy S24"

    is_exact1, is_sim1, _ = TextNormalizer.compare_titles(t1, t2)
    assert is_exact1 is True
    assert is_sim1 is True

    is_exact2, is_sim2, score2 = TextNormalizer.compare_titles(t1, t3, threshold=0.60)
    assert is_exact2 is False
    assert is_sim2 is True
    assert score2 >= 0.60

    is_exact3, is_sim3, _ = TextNormalizer.compare_titles(t1, t4)
    assert is_exact3 is False
    assert is_sim3 is False
