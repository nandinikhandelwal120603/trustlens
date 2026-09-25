"""Unit tests for the Normalizer engine."""

from trustlens.ingestion.normalizer import Normalizer
from trustlens.models.common import ItemCondition


def test_price_normalization_various_formats():
    """Verify price parser handles rupees symbol, commas, 'k', 'lakh', and bare numbers."""
    # Rupee symbol with comma
    raw, norm, raw_c, norm_c = Normalizer.normalize_price("₹45,000")
    assert norm == 45000.0
    assert norm_c == "INR"

    # '45k' suffix
    raw, norm, raw_c, norm_c = Normalizer.normalize_price("45k")
    assert norm == 45000.0
    assert norm_c == "INR"

    # 'Rs. 45000'
    raw, norm, raw_c, norm_c = Normalizer.normalize_price("Rs. 45000")
    assert norm == 45000.0
    assert norm_c == "INR"

    # 'INR 45,000'
    raw, norm, raw_c, norm_c = Normalizer.normalize_price("INR 45,000")
    assert norm == 45000.0
    assert norm_c == "INR"

    # Numeric int input
    raw, norm, raw_c, norm_c = Normalizer.normalize_price(45000)
    assert norm == 45000.0
    assert norm_c == "INR"

    # Float input
    raw, norm, raw_c, norm_c = Normalizer.normalize_price(78500.50)
    assert norm == 78500.50

    # Lakh format
    raw, norm, raw_c, norm_c = Normalizer.normalize_price("1.5 Lakh")
    assert norm == 150000.0

    # None input
    raw, norm, raw_c, norm_c = Normalizer.normalize_price(None)
    assert norm is None

    # USD currency
    raw, norm, raw_c, norm_c = Normalizer.normalize_price("$499")
    assert norm == 499.0
    assert norm_c == "USD"


def test_condition_normalization():
    """Test mapping vernacular condition strings into ItemCondition enums."""
    assert Normalizer.normalize_condition("Brand New Sealed") == ItemCondition.NEW
    assert Normalizer.normalize_condition("seal pack") == ItemCondition.NEW
    assert Normalizer.normalize_condition("mint condition") == ItemCondition.LIKE_NEW
    assert Normalizer.normalize_condition("like new") == ItemCondition.LIKE_NEW
    assert Normalizer.normalize_condition("open box") == ItemCondition.LIKE_NEW
    assert Normalizer.normalize_condition("clean working condition") == ItemCondition.GOOD
    assert Normalizer.normalize_condition("used") == ItemCondition.GOOD
    assert Normalizer.normalize_condition("fair with scratches") == ItemCondition.FAIR
    assert Normalizer.normalize_condition("broken screen for parts") == ItemCondition.POOR
    assert Normalizer.normalize_condition("") == ItemCondition.UNKNOWN
    assert Normalizer.normalize_condition(None) == ItemCondition.UNKNOWN


def test_category_normalization():
    """Test taxonomic matching against Electronics Taxonomy and aliases."""
    # Direct canonical match
    cat, sub = Normalizer.normalize_category("Smartphones", "iPhone")
    assert cat == "Smartphones"
    assert sub == "iPhone"

    # Subcategory inferred from title
    cat, sub = Normalizer.normalize_category("Smartphones", None, title="Apple iPhone 15 Pro")
    assert cat == "Smartphones"
    assert sub == "iPhone"

    # Category alias ('mobile' -> 'Smartphones')
    cat, sub = Normalizer.normalize_category("mobile", "samsung")
    assert cat == "Smartphones"
    assert sub == "Samsung"

    # Gaming alias ('ps5' -> Gaming/PlayStation)
    cat, sub = Normalizer.normalize_category("gaming", None, title="Sony PS5 Disc Edition")
    assert cat == "Gaming"
    assert sub == "PlayStation"

    # Laptop alias ('macbook' -> Laptops/MacBook)
    cat, sub = Normalizer.normalize_category("laptops", None, title="MacBook Air M2")
    assert cat == "Laptops"
    assert sub == "MacBook"


def test_text_normalization():
    """Test whitespace stripping and unicode normalization."""
    raw = "  Apple   iPhone 15   \t\n  Pro  "
    assert Normalizer.normalize_text(raw) == "Apple iPhone 15 Pro"
    assert Normalizer.normalize_text("") is None
    assert Normalizer.normalize_text(None) is None


def test_location_parsing():
    """Test city and state extraction from comma-separated location strings."""
    city, state = Normalizer.parse_location("Indiranagar, Bangalore, Karnataka")
    assert city == "Bangalore"
    assert state == "Karnataka"

    city, state = Normalizer.parse_location("Bandra, Mumbai")
    assert city == "Bandra"
    assert state == "Mumbai"

    city, state = Normalizer.parse_location("Delhi")
    assert city == "Delhi"
    assert state is None
