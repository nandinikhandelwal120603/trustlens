"""
TrustLens — OLX Page & Search Structured Parser (Phase 3).
Extracts structured product, seller, media, and claim attributes from OLX HTML/JSON-LD.
"""

import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from trustlens.olx.models import (
    ClaimStatus,
    CollectionType,
    DiscoveryContext,
    OLXClaim,
    OLXListing,
    OLXMedia,
    OLXProduct,
    OLXSeller,
)


class OLXParser:
    """Parser for OLX listing pages and search result feeds."""

    @classmethod
    def extract_source_listing_id(cls, url: str) -> Optional[str]:
        """Extract OLX numeric item ID from URL."""
        # e.g. https://www.olx.in/item/iphone-15-pro-max-iid-1784920194
        match = re.search(r"iid-(\d+)", url)
        if match:
            return match.group(1)
        # Match trailing digits e.g. /item/1784920194
        match = re.search(r"/(\d{6,})", url)
        if match:
            return match.group(1)
        return None

    @classmethod
    def parse_search_results(cls, content: str, search_url: str = "") -> List[Dict[str, Any]]:
        """Extract discovered listing cards from an OLX search page HTML or raw API response."""
        results: List[Dict[str, Any]] = []

        # 1. Try __NEXT_DATA__ JSON state
        next_data_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', content, re.DOTALL)
        if next_data_match:
            try:
                data = json.loads(next_data_match.group(1))
                page_props = data.get("props", {}).get("pageProps", {})
                ads = (
                    page_props.get("ads", [])
                    or page_props.get("items", [])
                    or page_props.get("data", {}).get("ads", [])
                )
                for ad in ads:
                    item_id = str(ad.get("id") or "")
                    title = ad.get("title") or "OLX Listing"
                    price_val = None
                    if "price" in ad:
                        p_val = ad["price"].get("value", {}).get("raw") if isinstance(ad["price"], dict) else ad["price"]
                        price_val = float(p_val) if p_val is not None else None
                    
                    loc = ad.get("locations_resolved", {}).get("ADMIN_LEVEL_3_name") if isinstance(ad.get("locations_resolved"), dict) else None
                    item_url = ad.get("url") or (f"https://www.olx.in/item/{item_id}" if item_id else None)
                    
                    if item_url:
                        if not item_url.startswith("http"):
                            item_url = f"https://www.olx.in{item_url}"
                        results.append({
                            "source_listing_id": item_id,
                            "title": title,
                            "price": price_val,
                            "location": loc,
                            "url": item_url,
                        })
                if results:
                    return results
            except Exception:
                pass

        # 2. Try JSON-LD ItemList
        json_ld_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
        for j_str in json_ld_matches:
            try:
                j_obj = json.loads(j_str)
                if j_obj.get("@type") == "ItemList":
                    for elem in j_obj.get("itemListElement", []):
                        item = elem.get("item", {})
                        i_url = item.get("url") or elem.get("url")
                        if i_url:
                            results.append({
                                "title": item.get("name") or "OLX Listing",
                                "price": item.get("offers", {}).get("price"),
                                "url": i_url,
                                "source_listing_id": cls.extract_source_listing_id(i_url),
                            })
            except Exception:
                pass

        # 3. Fallback Regex link extraction
        if not results:
            item_links = set(re.findall(r'href="(/item/[^"]+)"', content))
            for link in item_links:
                full_url = f"https://www.olx.in{link}" if not link.startswith("http") else link
                results.append({
                    "title": "Discovered OLX Listing",
                    "url": full_url,
                    "source_listing_id": cls.extract_source_listing_id(full_url),
                })

        return results

    @classmethod
    def parse_listing_page(
        cls,
        content: str,
        url: str,
        investigation_id: str = "INV-002",
        collection_type: CollectionType = CollectionType.TARGETED,
        discovery_context: Optional[DiscoveryContext] = None,
        listing_index: int = 1,
    ) -> OLXListing:
        """Parse complete listing page HTML or JSON state into an OLXListing instance."""
        source_id = cls.extract_source_listing_id(url)
        listing_id = f"OLX-{listing_index:06d}"

        title = "OLX Listing"
        description = ""
        price: Optional[float] = None
        currency = "INR"
        location: Optional[str] = None
        posted_at: Optional[datetime] = None
        category = "other"
        subcategory = None

        product_brand = None
        product_model = None
        product_cond = None
        product_storage = None
        product_ram = None
        product_year = None
        product_color = None
        attributes: Dict[str, Any] = {}

        seller_id = None
        seller_name = "OLX User"
        seller_loc = None
        seller_age = None
        seller_type = None
        seller_badges: List[str] = []
        business_claim = None

        image_urls: List[str] = []

        # 1. Parse JSON-LD metadata if present
        json_ld_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
        for j_str in json_ld_matches:
            try:
                j_obj = json.loads(j_str)
                if j_obj.get("@type") in ["Product", "Offer", "IndividualProduct"]:
                    title = j_obj.get("name") or title
                    description = j_obj.get("description") or description
                    if "offers" in j_obj:
                        offer = j_obj["offers"]
                        p_raw = offer.get("price")
                        if p_raw:
                            price = float(p_raw)
                        currency = offer.get("priceCurrency") or currency
                    if "image" in j_obj:
                        imgs = j_obj["image"]
                        if isinstance(imgs, list):
                            image_urls.extend(imgs)
                        elif isinstance(imgs, str):
                            image_urls.append(imgs)
                    if "brand" in j_obj:
                        b = j_obj["brand"]
                        product_brand = b.get("name") if isinstance(b, dict) else str(b)
            except Exception:
                pass

        # 2. Parse __NEXT_DATA__ state
        next_data_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', content, re.DOTALL)
        if next_data_match:
            try:
                data = json.loads(next_data_match.group(1))
                page_props = data.get("props", {}).get("pageProps", {})
                ad = page_props.get("ad") or page_props.get("item") or {}
                if ad:
                    title = ad.get("title") or title
                    description = ad.get("description") or description
                    if "price" in ad:
                        p_val = ad["price"].get("value", {}).get("raw") if isinstance(ad["price"], dict) else ad["price"]
                        if p_val is not None:
                            price = float(p_val)
                    if "created_at" in ad:
                        try:
                            posted_at = datetime.fromisoformat(ad["created_at"].replace("Z", "+00:00"))
                        except Exception:
                            pass
                    
                    # Photos
                    for photo in ad.get("photos", []):
                        if isinstance(photo, dict) and "url" in photo:
                            image_urls.append(photo["url"])
                        elif isinstance(photo, str):
                            image_urls.append(photo)

                    # User / Seller
                    user = ad.get("user") or {}
                    if user:
                        seller_id = str(user.get("id") or "")
                        seller_name = user.get("name") or seller_name
                        if user.get("is_business"):
                            seller_type = "business"
                            business_claim = "Registered Business Seller on OLX"
                        if user.get("verification_status"):
                            seller_badges.append(str(user["verification_status"]))

                    # Category
                    category = ad.get("category_name") or category
                    subcategory = ad.get("subcategory_name")
            except Exception:
                pass

        # 3. HTML Regex Fallback Extraction
        if title == "OLX Listing":
            t_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
            if t_match:
                title = re.sub(r"\s*\|\s*OLX.*", "", t_match.group(1)).strip()

        if not description:
            d_match = re.search(r'data-aut-id="itemDescription"[^>]*>(.*?)</div>', content, re.DOTALL)
            if d_match:
                description = re.sub(r"<[^>]+>", " ", d_match.group(1)).strip()

        if price is None:
            p_match = re.search(r"(?:₹|Rs\.?)\s*([\d,]+)", content)
            if p_match:
                try:
                    price = float(p_match.group(1).replace(",", ""))
                except Exception:
                    pass

        if not location:
            loc_match = re.search(r'data-aut-id="itemLocation"[^>]*>(.*?)(?:</div>|</span>)', content, re.DOTALL)
            if loc_match:
                location = re.sub(r"<[^>]+>", "", loc_match.group(1)).strip()

        # Image URLs fallback
        if not image_urls:
            raw_imgs = re.findall(r'https://apollo\.olx\.in/v1/files/[a-zA-Z0-9_-]+/image[^\s"\'>]*', content)
            image_urls = list(dict.fromkeys(raw_imgs))

        # Infer Product Info
        full_text = f"{title} {description}".lower()
        if any(k in full_text for k in ["iphone", "pixel", "samsung", "oneplus", "phone", "mobile", "smartphone"]):
            category = "smartphones"
            if "iphone" in full_text:
                product_brand = "Apple"
                m = re.search(r"iphone\s*(\d+\s*(?:pro\s*max|pro|plus)?|x|xr|xs)", full_text)
                product_model = m.group(0).title() if m else "iPhone"
            elif "pixel" in full_text:
                product_brand = "Google"
                product_model = "Pixel"
            elif "samsung" in full_text:
                product_brand = "Samsung"
                product_model = "Galaxy"
        elif any(k in full_text for k in ["macbook", "laptop", "asus", "rog", "thinkpad", "dell", "hp"]):
            category = "laptops"
            if "macbook" in full_text:
                product_brand = "Apple"
                product_model = "MacBook Pro" if "pro" in full_text else "MacBook Air"
            elif "asus" in full_text:
                product_brand = "ASUS"
                product_model = "ROG / TUF"
        elif any(k in full_text for k in ["ps5", "ps4", "playstation", "xbox", "console"]):
            category = "gaming_consoles"
            if "ps5" in full_text or "playstation 5" in full_text:
                product_brand = "Sony"
                product_model = "PlayStation 5"
        elif any(k in full_text for k in ["car", "thar", "honda city", "swift", "creta", "bullet", "bike"]):
            category = "cars" if not any(k in full_text for k in ["bullet", "bike", "scooter"]) else "bikes"
            if "thar" in full_text:
                product_brand = "Mahindra"
                product_model = "Thar"
            elif "honda" in full_text or "city" in full_text:
                product_brand = "Honda"
                product_model = "City"
        elif any(k in full_text for k in ["camera", "canon", "nikon", "sony alpha", "digicam"]):
            category = "cameras"

        # Check storage / RAM
        stor_match = re.search(r"\b(128gb|256gb|512gb|1tb|2tb)\b", full_text)
        if stor_match:
            product_storage = stor_match.group(1).upper()
        ram_match = re.search(r"\b(8gb|16gb|24gb|32gb|64gb)\s*(?:ram)?\b", full_text)
        if ram_match:
            product_ram = ram_match.group(1).upper()

        product = OLXProduct(
            category=category,
            subcategory=subcategory,
            brand=product_brand,
            model=product_model,
            storage=product_storage,
            ram=product_ram,
            year=product_year,
            condition=product_cond,
            color=product_color,
            attributes=attributes,
        )

        seller = OLXSeller(
            seller_id=seller_id,
            display_name=seller_name,
            location=seller_loc or location,
            account_age=seller_age,
            seller_type=seller_type,
            verification_badges=seller_badges,
            business_claim=business_claim,
        )

        # Extract Claims & Contact Signals
        claims: List[OLXClaim] = []
        claim_idx = 1

        claim_triggers = [
            ("Army / Defence Officer Relocation", r"\b(army|cisf|defence|military|canteen|gate\s*pass)\b"),
            ("Urgent / Distress Sale", r"\b(urgent|distress|leaving\s*city|transfer|moving\s*abroad)\b"),
            ("Warehouse / Corporate Clearance", r"\b(clearance|warehouse|liquidation|office\s*closing|company\s*closing)\b"),
            ("Invoice / GST Bill Available", r"\b(invoice|bill|gst|receipt|original\s*bill)\b"),
            ("Advance / Token Required", r"\b(advance|token|booking|deposit|delivery\s*fee)\b"),
            ("WhatsApp / Off-Platform Contact", r"\b(whatsapp|wa\.me|call\s*on|message\s*on)\b"),
        ]

        contact_signals: List[str] = []
        for c_label, c_regex in claim_triggers:
            match = re.search(c_regex, full_text)
            if match:
                claims.append(
                    OLXClaim(
                        claim_id=f"CLM-{listing_id}-{claim_idx:03d}",
                        claim_text=f"Claim in {c_label}: '{match.group(0)}'",
                        source="listing_description",
                        status=ClaimStatus.REPORTED,
                    )
                )
                claim_idx += 1
                if c_label == "WhatsApp / Off-Platform Contact":
                    contact_signals.append("whatsapp_contact_demanded")

        # Media items
        media_list: List[OLXMedia] = []
        for m_idx, img_url in enumerate(image_urls, 1):
            media_list.append(
                OLXMedia(
                    media_id=f"MEDIA-{listing_id}-{m_idx:03d}",
                    listing_id=listing_id,
                    source_url=img_url,
                    download_status="pending",
                )
            )

        return OLXListing(
            listing_id=listing_id,
            source="olx",
            source_listing_id=source_id,
            listing_url=url,
            investigation_id=investigation_id,
            collection_type=collection_type,
            title=title,
            description=description,
            category=category,
            subcategory=subcategory,
            price=price,
            currency=currency,
            location=location,
            posted_at=posted_at,
            product=product,
            seller=seller,
            claims=claims,
            media=media_list,
            contact_signals=contact_signals,
            discovery_context=discovery_context,
        )
