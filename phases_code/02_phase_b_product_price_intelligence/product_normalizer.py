"""
TrustLens Marketplace Intelligence — Master Product Normalizer Engine (Phase B).
Orchestrates deterministic product entity parsing, specification extraction, condition detection,
and query mismatch classification without any black-box AI or heuristics.
"""

from typing import Any, Dict, Optional

from trustlens.marketplace.condition_parser import ConditionParser
from trustlens.marketplace.product_rules import ProductRuleMatcher
from trustlens.marketplace.product_taxonomy import (
    AccessoryOrDevice,
    Condition,
    NormalizationConfidence,
    ProductCategory,
    ProductDomain,
    QueryMatchStatus,
)
from trustlens.marketplace.specification_parser import SpecificationParser


class ProductNormalizer:
    """Master deterministic normalizer for OLX marketplace listings."""

    @classmethod
    def normalize_listing(
        cls,
        raw_title: Optional[str],
        search_query: Optional[str] = None,
        category_id: Optional[Any] = None,
        raw_price: Optional[str] = None,
        raw_location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Normalizes a listing record into fully structured, auditable product attributes.
        """
        title_str = (raw_title or "").strip()

        # 1. Product & Brand Classification
        prod_meta = ProductRuleMatcher.match_product(title_str, category_id=category_id)

        # 2. Hardware Specifications Extraction
        specs = SpecificationParser.parse_specs(title_str)

        # 3. Condition & Cues Extraction
        condition, condition_cues = ConditionParser.parse_condition(title_str)

        # 4. Determine Query Match Status
        query_clean = (search_query or "").strip().lower()
        acc_type = prod_meta["accessory_or_device"]
        family = prod_meta.get("product_family")
        brand = prod_meta.get("brand")
        cat = prod_meta.get("product_category")
        conf = prod_meta.get("normalization_confidence", "unknown")

        query_match_status = QueryMatchStatus.UNKNOWN

        if query_clean == "iphone":
            if family == "iPhone" and acc_type == AccessoryOrDevice.DEVICE:
                query_match_status = QueryMatchStatus.DIRECT_MATCH
            elif family == "iPhone" and acc_type != AccessoryOrDevice.DEVICE:
                query_match_status = QueryMatchStatus.RELATED_ACCESSORY
            elif brand in ["Samsung", "Google", "OnePlus", "Sony", "Dell", "HP", "Lenovo"] or cat in [ProductCategory.LAPTOP, ProductCategory.GAMING_CONSOLE, ProductCategory.GAMING_ACCESSORY]:
                query_match_status = QueryMatchStatus.DIFFERENT_PRODUCT
            elif conf == "low":
                query_match_status = QueryMatchStatus.AMBIGUOUS
            else:
                query_match_status = QueryMatchStatus.UNKNOWN

        elif query_clean == "macbook":
            if family == "MacBook" and acc_type == AccessoryOrDevice.DEVICE:
                query_match_status = QueryMatchStatus.DIRECT_MATCH
            elif family == "MacBook" and acc_type != AccessoryOrDevice.DEVICE:
                query_match_status = QueryMatchStatus.RELATED_ACCESSORY
            elif cat != ProductCategory.LAPTOP or brand != "Apple":
                query_match_status = QueryMatchStatus.DIFFERENT_PRODUCT
            elif conf == "low":
                query_match_status = QueryMatchStatus.AMBIGUOUS
            else:
                query_match_status = QueryMatchStatus.UNKNOWN

        elif query_clean == "ps5 controller":
            if prod_meta.get("model") == "DualSense Controller":
                query_match_status = QueryMatchStatus.DIRECT_MATCH
            elif family == "PlayStation" and acc_type != AccessoryOrDevice.DEVICE:
                query_match_status = QueryMatchStatus.RELATED_ACCESSORY
            elif prod_meta.get("model") == "PlayStation 5" or brand in ["Apple", "Samsung", "Microsoft", "Nintendo"]:
                query_match_status = QueryMatchStatus.DIFFERENT_PRODUCT
            elif conf == "low":
                query_match_status = QueryMatchStatus.AMBIGUOUS
            else:
                query_match_status = QueryMatchStatus.UNKNOWN

        else:
            # Generic query evaluation
            if conf == "high":
                query_match_status = QueryMatchStatus.DIRECT_MATCH
            elif conf == "medium":
                query_match_status = QueryMatchStatus.DIRECT_MATCH
            elif conf == "low":
                query_match_status = QueryMatchStatus.AMBIGUOUS
            else:
                query_match_status = QueryMatchStatus.UNKNOWN

        return {
            "product_domain": prod_meta["product_domain"].value if isinstance(prod_meta["product_domain"], ProductDomain) else str(prod_meta["product_domain"]),
            "product_category": prod_meta["product_category"].value if isinstance(prod_meta["product_category"], ProductCategory) else str(prod_meta["product_category"]),
            "brand": prod_meta["brand"],
            "product_family": prod_meta["product_family"],
            "model": prod_meta["model"],
            "variant": prod_meta["variant"],
            "generation": prod_meta["generation"],
            "storage_gb": specs["storage_gb"],
            "ram_gb": specs["ram_gb"],
            "screen_size_inches": specs["screen_size_inches"],
            "battery_health_percent": specs["battery_health_percent"],
            "year": specs["year"],
            "chip": specs["chip"],
            "color": specs["color"],
            "condition": condition.value if isinstance(condition, Condition) else str(condition),
            "condition_cues": condition_cues,
            "accessory_or_device": acc_type.value if isinstance(acc_type, AccessoryOrDevice) else str(acc_type),
            "query_match_status": query_match_status.value if isinstance(query_match_status, QueryMatchStatus) else str(query_match_status),
            "normalization_confidence": conf,
            "normalization_method": "deterministic_rule_engine",
            "normalization_notes": prod_meta["normalization_notes"],
        }
