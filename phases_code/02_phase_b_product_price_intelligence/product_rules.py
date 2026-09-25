"""
TrustLens Marketplace Intelligence — Domain Product Rules & Pattern Matchers (Phase B).
Transparent, deterministic regex rule engine for classifying consumer electronics.
"""

import re
from typing import Any, Dict, Optional, Tuple

from trustlens.marketplace.product_taxonomy import (
    AccessoryOrDevice,
    ProductCategory,
    ProductDomain,
)


class ProductRuleMatcher:
    """Domain-specific deterministic pattern matching for electronics and marketplace categories."""

    # 1. Accessory / Noise Patterns
    ACCESSORY_PATTERNS = [
        (AccessoryOrDevice.CASE, re.compile(r"\b(?:cases?|back\s*cover|pouch|silicone\s*case|leather\s*case|magsafe\s*case|armor\s*case)\b", re.IGNORECASE)),
        (AccessoryOrDevice.COVER, re.compile(r"\b(?:covers?|flip\s*cover|skin|wrap|guard)\b", re.IGNORECASE)),
        (AccessoryOrDevice.CHARGER, re.compile(r"\b(?:chargers?|adapter|power\s*adapter|magsafe\s*charger|20w\s*charger|fast\s*charger)\b", re.IGNORECASE)),
        (AccessoryOrDevice.CABLE, re.compile(r"\b(?:cables?|lightning\s*cable|type[- ]c\s*cable|usb[- ]c\s*cable|cord)\b", re.IGNORECASE)),
        (AccessoryOrDevice.SCREEN_PROTECTOR, re.compile(r"\b(?:tempered\s*glass|screen\s*guard|screen\s*protector|membrane)\b", re.IGNORECASE)),
        (AccessoryOrDevice.PART, re.compile(r"\b(?:display\s*panel|motherboard|battery\s*replacement|spare\s*parts?|housing|body|camera\s*lens\s*glass)\b", re.IGNORECASE)),
        (AccessoryOrDevice.ACCESSORY, re.compile(r"\b(?:dummy|box\s*only|empty\s*box|controller\s*grip|charging\s*dock|cooling\s*fan|stand|earphones?|airpods\s*case)\b", re.IGNORECASE)),
    ]

    # 2. iPhone Model Hierarchy
    # Note: Handles all generations from iPhone 6 to iPhone 17 with Pro, Pro Max, Plus, Mini, SE, X, XR, XS
    IPHONE_MODEL_REGEX = re.compile(
        r"\b(?:apple\s+)?(?:i\s*phone|iphone)\s*(1[1-7]|[6-9]|x[rs]?|x|se(?:\s*[123])?)\s*(pro\s*max|pro|max|plus|mini)?\b",
        re.IGNORECASE,
    )

    # 3. MacBook Model Hierarchy
    MACBOOK_MODEL_REGEX = re.compile(
        r"\b(?:apple\s+)?(?:mac\s*book|macbook)\s*(air|pro)?\s*(m[1-4](?:\s*pro|\s*max)?|intel|\d{4})?\b",
        re.IGNORECASE,
    )

    # 4. PlayStation & Gaming Model Hierarchy
    PS5_CONTROLLER_REGEX = re.compile(
        r"\b(?:ps5\s*controller|dualsense(?:\s*edge)?|dual\s*sense|playstation\s*5\s*controller|ps5\s*remote|ps5\s*joystick)\b",
        re.IGNORECASE,
    )

    PS5_CONSOLE_REGEX = re.compile(
        r"\b(?:ps5|playstation\s*5)\s*(?:console|disc\s*edition|digital\s*edition|slim|pro)?\b",
        re.IGNORECASE,
    )

    PS4_REGEX = re.compile(
        r"\b(?:ps4|playstation\s*4)\s*(?:pro|slim|fat|jailbreak)?\b",
        re.IGNORECASE,
    )

    XBOX_REGEX = re.compile(
        r"\b(?:xbox\s*series\s*[xs]|xbox\s*one(?:\s*[xs])?|xbox\s*360)\b",
        re.IGNORECASE,
    )

    NINTENDO_REGEX = re.compile(
        r"\b(?:nintendo\s*switch(?:\s*oled|\s*lite)?|switch\s*oled)\b",
        re.IGNORECASE,
    )

    # 5. Non-Apple Smartphone Models
    SAMSUNG_REGEX = re.compile(
        r"\b(?:samsung\s+)?(?:galaxy\s+)?(s2[0-6]\s*(?:ultra|plus|\+)?|z\s*fold\s*[1-6]|z\s*flip\s*[1-6]|a\d{2}|m\d{2}|note\s*20\s*ultra)\b",
        re.IGNORECASE,
    )

    PIXEL_REGEX = re.compile(
        r"\b(?:google\s+)?pixel\s*([6-9]\s*(?:pro|a|fold)?)\b",
        re.IGNORECASE,
    )

    ONEPLUS_REGEX = re.compile(
        r"\b(?:oneplus|one\s*plus)\s*(1[0-3]|9\s*pro|nord(?:\s*ce)?\s*[1-4]?|open)\b",
        re.IGNORECASE,
    )

    # 6. Non-Apple Laptops
    LAPTOP_BRANDS_REGEX = re.compile(
        r"\b(dell\s*(?:xps|inspiron|alienware|latitude)?|hp\s*(?:omen|victus|pavilion|spectre|envy)?|lenovo\s*(?:legion|thinkpad|ideapad|loq)?|asus\s*(?:rog|tuf|zenbook|vivobook)?|acer\s*(?:predator|nitro|aspire)?)\b",
        re.IGNORECASE,
    )

    @classmethod
    def detect_accessory_or_device(cls, title: str) -> AccessoryOrDevice:
        """
        Determines if a listing title describes a primary device or an accessory/part.
        """
        if not title:
            return AccessoryOrDevice.UNKNOWN

        clean = title.strip()
        for acc_type, pattern in cls.ACCESSORY_PATTERNS:
            if pattern.search(clean):
                return acc_type

        return AccessoryOrDevice.DEVICE

    @classmethod
    def match_product(cls, title: str, category_id: Optional[Any] = None) -> Dict[str, Any]:
        """
        Deterministically matches listing title to canonical product entities.
        """
        if not title or not title.strip():
            return {
                "product_domain": ProductDomain.UNKNOWN,
                "product_category": ProductCategory.UNKNOWN,
                "brand": None,
                "product_family": None,
                "model": None,
                "variant": None,
                "generation": None,
                "accessory_or_device": AccessoryOrDevice.UNKNOWN,
                "normalization_confidence": "unknown",
                "normalization_notes": "Empty or missing title.",
            }

        clean = title.strip()
        accessory_type = cls.detect_accessory_or_device(clean)

        # -------------------------------------------------------------
        # A. Apple iPhone Matching
        # -------------------------------------------------------------
        iphone_match = cls.IPHONE_MODEL_REGEX.search(clean)
        if iphone_match:
            gen_raw = iphone_match.group(1).upper()
            var_raw = (iphone_match.group(2) or "").strip().title()

            # Normalize generation string
            if gen_raw in ["X", "XR", "XS"]:
                model_base = f"iPhone {gen_raw}"
            elif gen_raw.startswith("SE"):
                model_base = f"iPhone {gen_raw}"
            else:
                model_base = f"iPhone {gen_raw}"

            if var_raw:
                model_full = f"{model_base} {var_raw}".strip()
                variant = var_raw
            else:
                model_full = model_base
                variant = None

            is_acc = accessory_type != AccessoryOrDevice.DEVICE
            cat = ProductCategory.ACCESSORY if is_acc else ProductCategory.SMARTPHONE

            return {
                "product_domain": ProductDomain.ELECTRONICS,
                "product_category": cat,
                "brand": "Apple",
                "product_family": "iPhone",
                "model": model_full,
                "variant": variant,
                "generation": gen_raw,
                "accessory_or_device": accessory_type,
                "normalization_confidence": "high",
                "normalization_notes": "Matched deterministic iPhone regex.",
            }

        # -------------------------------------------------------------
        # B. Apple MacBook Matching
        # -------------------------------------------------------------
        macbook_match = cls.MACBOOK_MODEL_REGEX.search(clean)
        if macbook_match:
            sub_type = (macbook_match.group(1) or "").strip().title()  # Air, Pro, or ""
            chip_or_yr = (macbook_match.group(2) or "").strip().upper()

            if sub_type:
                model_full = f"MacBook {sub_type}".strip()
            else:
                model_full = "MacBook"

            is_acc = accessory_type != AccessoryOrDevice.DEVICE
            cat = ProductCategory.ACCESSORY if is_acc else ProductCategory.LAPTOP

            return {
                "product_domain": ProductDomain.ELECTRONICS,
                "product_category": cat,
                "brand": "Apple",
                "product_family": "MacBook",
                "model": model_full,
                "variant": sub_type if sub_type else None,
                "generation": chip_or_yr if chip_or_yr else None,
                "accessory_or_device": accessory_type,
                "normalization_confidence": "high",
                "normalization_notes": "Matched deterministic MacBook regex.",
            }

        # -------------------------------------------------------------
        # C. PlayStation / PS5 Controller / PS5 Console Matching
        # -------------------------------------------------------------
        # 1. PS5 Controller (Priority check before general console)
        if cls.PS5_CONTROLLER_REGEX.search(clean) or ("controller" in clean.lower() and "ps5" in clean.lower()):
            is_acc = accessory_type != AccessoryOrDevice.DEVICE
            return {
                "product_domain": ProductDomain.GAMING,
                "product_category": ProductCategory.GAMING_ACCESSORY,
                "brand": "Sony",
                "product_family": "PlayStation",
                "model": "DualSense Controller",
                "variant": "PS5 Controller",
                "generation": "PS5",
                "accessory_or_device": AccessoryOrDevice.ACCESSORY if is_acc else AccessoryOrDevice.DEVICE,
                "normalization_confidence": "high",
                "normalization_notes": "Matched PS5 Controller / DualSense.",
            }

        # 2. PS5 Console
        ps5_match = cls.PS5_CONSOLE_REGEX.search(clean)
        if ps5_match and "controller" not in clean.lower():
            is_acc = accessory_type != AccessoryOrDevice.DEVICE
            return {
                "product_domain": ProductDomain.GAMING,
                "product_category": ProductCategory.ACCESSORY if is_acc else ProductCategory.GAMING_CONSOLE,
                "brand": "Sony",
                "product_family": "PlayStation",
                "model": "PlayStation 5",
                "variant": "Console",
                "generation": "PS5",
                "accessory_or_device": accessory_type,
                "normalization_confidence": "high",
                "normalization_notes": "Matched PlayStation 5 Console.",
            }

        # 3. PS4
        ps4_match = cls.PS4_REGEX.search(clean)
        if ps4_match:
            is_acc = accessory_type != AccessoryOrDevice.DEVICE
            return {
                "product_domain": ProductDomain.GAMING,
                "product_category": ProductCategory.ACCESSORY if is_acc else ProductCategory.GAMING_CONSOLE,
                "brand": "Sony",
                "product_family": "PlayStation",
                "model": "PlayStation 4",
                "variant": None,
                "generation": "PS4",
                "accessory_or_device": accessory_type,
                "normalization_confidence": "high",
                "normalization_notes": "Matched PlayStation 4.",
            }

        # 4. Xbox
        xbox_match = cls.XBOX_REGEX.search(clean)
        if xbox_match:
            is_acc = accessory_type != AccessoryOrDevice.DEVICE
            return {
                "product_domain": ProductDomain.GAMING,
                "product_category": ProductCategory.ACCESSORY if is_acc else ProductCategory.GAMING_CONSOLE,
                "brand": "Microsoft",
                "product_family": "Xbox",
                "model": xbox_match.group(0).title(),
                "variant": None,
                "generation": "Xbox",
                "accessory_or_device": accessory_type,
                "normalization_confidence": "high",
                "normalization_notes": "Matched Xbox Console.",
            }

        # 5. Nintendo
        nintendo_match = cls.NINTENDO_REGEX.search(clean)
        if nintendo_match:
            is_acc = accessory_type != AccessoryOrDevice.DEVICE
            return {
                "product_domain": ProductDomain.GAMING,
                "product_category": ProductCategory.ACCESSORY if is_acc else ProductCategory.GAMING_CONSOLE,
                "brand": "Nintendo",
                "product_family": "Switch",
                "model": "Nintendo Switch",
                "variant": None,
                "generation": "Switch",
                "accessory_or_device": accessory_type,
                "normalization_confidence": "high",
                "normalization_notes": "Matched Nintendo Switch.",
            }

        # -------------------------------------------------------------
        # D. Other Smartphones (Samsung, Pixel, OnePlus)
        # -------------------------------------------------------------
        samsung_match = cls.SAMSUNG_REGEX.search(clean)
        if samsung_match:
            is_acc = accessory_type != AccessoryOrDevice.DEVICE
            return {
                "product_domain": ProductDomain.ELECTRONICS,
                "product_category": ProductCategory.ACCESSORY if is_acc else ProductCategory.SMARTPHONE,
                "brand": "Samsung",
                "product_family": "Galaxy",
                "model": f"Galaxy {samsung_match.group(1).title()}".strip(),
                "variant": None,
                "generation": None,
                "accessory_or_device": accessory_type,
                "normalization_confidence": "high",
                "normalization_notes": "Matched Samsung Galaxy.",
            }

        pixel_match = cls.PIXEL_REGEX.search(clean)
        if pixel_match:
            is_acc = accessory_type != AccessoryOrDevice.DEVICE
            return {
                "product_domain": ProductDomain.ELECTRONICS,
                "product_category": ProductCategory.ACCESSORY if is_acc else ProductCategory.SMARTPHONE,
                "brand": "Google",
                "product_family": "Pixel",
                "model": f"Pixel {pixel_match.group(1).title()}".strip(),
                "variant": None,
                "generation": None,
                "accessory_or_device": accessory_type,
                "normalization_confidence": "high",
                "normalization_notes": "Matched Google Pixel.",
            }

        oneplus_match = cls.ONEPLUS_REGEX.search(clean)
        if oneplus_match:
            is_acc = accessory_type != AccessoryOrDevice.DEVICE
            return {
                "product_domain": ProductDomain.ELECTRONICS,
                "product_category": ProductCategory.ACCESSORY if is_acc else ProductCategory.SMARTPHONE,
                "brand": "OnePlus",
                "product_family": "OnePlus",
                "model": f"OnePlus {oneplus_match.group(1).title()}".strip(),
                "variant": None,
                "generation": None,
                "accessory_or_device": accessory_type,
                "normalization_confidence": "high",
                "normalization_notes": "Matched OnePlus.",
            }

        # -------------------------------------------------------------
        # E. Other Laptops
        # -------------------------------------------------------------
        laptop_brand_match = cls.LAPTOP_BRANDS_REGEX.search(clean)
        if laptop_brand_match:
            brand_token = laptop_brand_match.group(1).split()[0].title()
            is_acc = accessory_type != AccessoryOrDevice.DEVICE
            return {
                "product_domain": ProductDomain.ELECTRONICS,
                "product_category": ProductCategory.ACCESSORY if is_acc else ProductCategory.LAPTOP,
                "brand": brand_token,
                "product_family": "Laptop",
                "model": laptop_brand_match.group(1).title(),
                "variant": None,
                "generation": None,
                "accessory_or_device": accessory_type,
                "normalization_confidence": "medium",
                "normalization_notes": f"Matched PC Laptop Brand: {brand_token}.",
            }

        # -------------------------------------------------------------
        # F. Generic / Ambiguous / Unknown Fallback
        # -------------------------------------------------------------
        if "phone" in clean.lower() or "mobile" in clean.lower():
            return {
                "product_domain": ProductDomain.ELECTRONICS,
                "product_category": ProductCategory.SMARTPHONE,
                "brand": "Generic / Other",
                "product_family": "Mobile Phone",
                "model": "Generic Smartphone",
                "variant": None,
                "generation": None,
                "accessory_or_device": accessory_type,
                "normalization_confidence": "low",
                "normalization_notes": "Generic smartphone keyword match.",
            }

        if "laptop" in clean.lower() or "notebook" in clean.lower():
            return {
                "product_domain": ProductDomain.ELECTRONICS,
                "product_category": ProductCategory.LAPTOP,
                "brand": "Generic / Other",
                "product_family": "Laptop",
                "model": "Generic Laptop",
                "variant": None,
                "generation": None,
                "accessory_or_device": accessory_type,
                "normalization_confidence": "low",
                "normalization_notes": "Generic laptop keyword match.",
            }

        return {
            "product_domain": ProductDomain.UNKNOWN,
            "product_category": ProductCategory.UNKNOWN,
            "brand": "Unknown",
            "product_family": "Unknown",
            "model": "Unknown Product",
            "variant": None,
            "generation": None,
            "accessory_or_device": accessory_type,
            "normalization_confidence": "unknown",
            "normalization_notes": "Unrecognized product listing title.",
        }
