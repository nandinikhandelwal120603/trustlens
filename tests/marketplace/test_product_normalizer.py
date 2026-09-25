"""Unit tests for Phase B Deterministic Product Normalization."""

import pytest
from trustlens.marketplace.condition_parser import ConditionParser
from trustlens.marketplace.product_normalizer import ProductNormalizer
from trustlens.marketplace.product_taxonomy import (
    AccessoryOrDevice,
    Condition,
    ProductCategory,
    QueryMatchStatus,
)
from trustlens.marketplace.specification_parser import SpecificationParser


def test_iphone_normalization():
    # 1. iPhone 17 Pro Max 256GB
    res1 = ProductNormalizer.normalize_listing(
        raw_title="Apple iPhone 17 Pro Max 256GB Desert Titanium 100% battery health",
        search_query="iphone",
    )
    assert res1["brand"] == "Apple"
    assert res1["product_family"] == "iPhone"
    assert res1["model"] == "iPhone 17 Pro Max"
    assert res1["variant"] == "Pro Max"
    assert res1["storage_gb"] == 256
    assert res1["color"] == "Desert Titanium"
    assert res1["battery_health_percent"] == 100
    assert res1["accessory_or_device"] == "device"
    assert res1["query_match_status"] == "direct_match"
    assert res1["normalization_confidence"] == "high"

    # 2. iPhone 14 128GB Used
    res2 = ProductNormalizer.normalize_listing(
        raw_title="iPhone 14 128gb Blue 6 months old with bill box",
        search_query="iphone",
    )
    assert res2["brand"] == "Apple"
    assert res2["model"] == "iPhone 14"
    assert res2["storage_gb"] == 128
    assert res2["color"] == "Blue"
    assert res2["condition"] == "used"
    assert len(res2["condition_cues"]) > 0


def test_macbook_normalization():
    res = ProductNormalizer.normalize_listing(
        raw_title="Apple MacBook Air M1 2020 8GB 256GB Space Gray",
        search_query="macbook",
    )
    assert res["brand"] == "Apple"
    assert res["product_family"] == "MacBook"
    assert res["model"] == "MacBook Air"
    assert res["chip"] == "M1"
    assert res["ram_gb"] == 8
    assert res["storage_gb"] == 256
    assert res["year"] == 2020
    assert res["color"] == "Space Gray"
    assert res["product_category"] == "Laptop"
    assert res["query_match_status"] == "direct_match"


def test_ps5_console_vs_controller():
    # Controller
    res_ctrl = ProductNormalizer.normalize_listing(
        raw_title="Sony PS5 DualSense Wireless Controller Midnight Black",
        search_query="ps5 controller",
    )
    assert res_ctrl["brand"] == "Sony"
    assert res_ctrl["product_category"] == "Gaming Accessory"
    assert res_ctrl["model"] == "DualSense Controller"
    assert res_ctrl["query_match_status"] == "direct_match"

    # Console under controller search (Query Mismatch)
    res_console = ProductNormalizer.normalize_listing(
        raw_title="Sony PlayStation 5 Disc Edition Console 1TB",
        search_query="ps5 controller",
    )
    assert res_console["product_category"] == "Gaming Console"
    assert res_console["model"] == "PlayStation 5"
    assert res_console["query_match_status"] == "different_product"


def test_accessory_and_contamination_detection():
    # iPhone Case (Query Contamination)
    res_case = ProductNormalizer.normalize_listing(
        raw_title="Original Apple iPhone 15 Pro Max Silicone Case with MagSafe",
        search_query="iphone",
    )
    assert res_case["accessory_or_device"] == "case"
    assert res_case["product_category"] == "Accessory"
    assert res_case["query_match_status"] == "related_accessory"

    # Unrelated Phone in iPhone search
    res_samsung = ProductNormalizer.normalize_listing(
        raw_title="Samsung Galaxy S24 Ultra 256GB Titanium Gray",
        search_query="iphone",
    )
    assert res_samsung["brand"] == "Samsung"
    assert res_samsung["model"] == "Galaxy S24 Ultra"
    assert res_samsung["query_match_status"] == "different_product"


def test_condition_parser():
    cond1, cues1 = ConditionParser.parse_condition("iPhone 15 brand new sealed box pack")
    assert cond1 == Condition.NEW
    assert len(cues1) >= 1

    cond2, cues2 = ConditionParser.parse_condition("iPhone 13 display broken for parts")
    assert cond2 == Condition.FOR_PARTS

    cond3, cues3 = ConditionParser.parse_condition("iPhone 14 like new scratchless 99% battery health")
    assert cond3 == Condition.LIKE_NEW


def test_specification_parser():
    specs = SpecificationParser.parse_specs("MacBook Pro M2 Max 16 inch 32GB RAM 1TB SSD Space Black")
    assert specs["chip"] == "M2 Max"
    assert specs["screen_size_inches"] == 16.0
    assert specs["ram_gb"] == 32
    assert specs["storage_gb"] == 1024
    assert specs["color"] == "Space Black"
