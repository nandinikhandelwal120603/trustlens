"""
Unit tests for OLX Structured Parser (Phase 3).
"""

import pytest
from trustlens.olx.models import CollectionType
from trustlens.olx.parser import OLXParser


SAMPLE_LISTING_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Apple MacBook Pro M2 16GB 512GB - Company Clearance | OLX</title>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "Apple MacBook Pro M2 16GB 512GB",
        "description": "Urgent sale due to company closing. WhatsApp on 9876543210. Original bill available. Need 2000 advance token.",
        "offers": {
            "@type": "Offer",
            "price": "35000",
            "priceCurrency": "INR"
        },
        "brand": {
            "@type": "Brand",
            "name": "Apple"
        },
        "image": [
            "https://apollo.olx.in/v1/files/abc123xyz/image;s=1080x1080",
            "https://apollo.olx.in/v1/files/def456uvw/image;s=1080x1080"
        ]
    }
    </script>
</head>
<body>
    <div data-aut-id="itemLocation">Indiranagar, Bangalore</div>
</body>
</html>
"""


SAMPLE_SEARCH_HTML = """
<!DOCTYPE html>
<html>
<head>
    <script id="__NEXT_DATA__" type="application/json">
    {
        "props": {
            "pageProps": {
                "ads": [
                    {
                        "id": "1804928192",
                        "title": "iPhone 15 Pro Max 256GB Urgent Sale",
                        "price": {"value": {"raw": 45000}},
                        "url": "/item/iphone-15-pro-max-iid-1804928192",
                        "locations_resolved": {"ADMIN_LEVEL_3_name": "Mumbai"}
                    },
                    {
                        "id": "1804928193",
                        "title": "Sony PS5 Disc Edition",
                        "price": {"value": {"raw": 25000}},
                        "url": "/item/sony-ps5-iid-1804928193",
                        "locations_resolved": {"ADMIN_LEVEL_3_name": "Delhi"}
                    }
                ]
            }
        }
    }
    </script>
</head>
</html>
"""


def test_extract_source_listing_id():
    url1 = "https://www.olx.in/item/apple-macbook-pro-iid-1804928192"
    url2 = "https://www.olx.in/item/1804928192"
    assert OLXParser.extract_source_listing_id(url1) == "1804928192"
    assert OLXParser.extract_source_listing_id(url2) == "1804928192"


def test_parse_search_results():
    results = OLXParser.parse_search_results(SAMPLE_SEARCH_HTML)
    assert len(results) == 2
    assert results[0]["source_listing_id"] == "1804928192"
    assert results[0]["price"] == 45000.0
    assert "https://www.olx.in/item/iphone-15-pro-max-iid-1804928192" in results[0]["url"]
    assert results[1]["price"] == 25000.0


def test_parse_listing_page():
    url = "https://www.olx.in/item/apple-macbook-pro-iid-1804928192"
    listing = OLXParser.parse_listing_page(
        content=SAMPLE_LISTING_HTML,
        url=url,
        investigation_id="INV-002",
        collection_type=CollectionType.TARGETED,
    )

    assert listing.source_listing_id == "1804928192"
    assert "MacBook Pro M2" in listing.title
    assert listing.price == 35000.0
    assert listing.currency == "INR"
    assert listing.location == "Indiranagar, Bangalore"
    assert listing.product.brand == "Apple"
    assert listing.product.storage == "512GB"
    assert listing.product.ram == "16GB"
    assert len(listing.media) == 2
    assert len(listing.claims) >= 3
    assert "whatsapp_contact_demanded" in listing.contact_signals
