"""
TrustLens — Targeted Investigation Suites & Configuration (Phase 3).
"""

from typing import Dict, List
from pydantic import BaseModel, Field


class InvestigationSuiteConfig(BaseModel):
    investigation_id: str
    name: str
    description: str
    categories: List[str]
    target_queries: List[str]
    baseline_queries: List[str]
    max_results_per_query: int = 20
    price_benchmark_discount_threshold: float = 0.35  # 35% discount triggers anomaly


INVESTIGATION_SUITES: Dict[str, InvestigationSuiteConfig] = {
    "INV-001": InvestigationSuiteConfig(
        investigation_id="INV-001",
        name="Defence / Army Relocation & Gate-Pass Fraud",
        description="Listings that leverage military / defense officer relocation stories to justify steep price cuts and demand advance gate-pass/transport tokens.",
        categories=["cars", "bikes", "smartphones", "laptops"],
        target_queries=[
            "army officer urgent sale",
            "army transfer",
            "army relocation",
            "army canteen",
            "canteen car",
            "defence canteen",
            "cisf transfer",
            "cisf officer",
            "gate pass",
            "transport fee",
            "urgent army sale",
            "Thar army transfer",
        ],
        baseline_queries=[
            "used car",
            "used bike",
            "used iphone",
            "used laptop",
            "honda city",
            "royal enfield bullet",
        ],
        max_results_per_query=20,
    ),
    "INV-002": InvestigationSuiteConfig(
        investigation_id="INV-002",
        name="High-End Tech Clearance & Booking Token Fraud",
        description="Listings offering high-value electronics (iPhone, MacBook, PS5) at substantial discounts under the pretext of warehouse clearance or urgent relocation, requiring advance tokens.",
        categories=["smartphones", "laptops", "gaming consoles", "cameras"],
        target_queries=[
            "iphone cheap",
            "iphone clearance",
            "iphone warehouse",
            "iphone company clearance",
            "macbook cheap",
            "macbook clearance",
            "macbook warehouse",
            "macbook company clearance",
            "ps5 cheap",
            "ps5 clearance",
            "ps5 urgent sale",
            "gaming laptop cheap",
            "gaming laptop clearance",
            "warehouse clearance",
            "company clearance",
        ],
        baseline_queries=[
            "iphone 15",
            "iphone 14 pro",
            "macbook air m1",
            "macbook pro m2",
            "ps5 console",
            "gaming laptop asus",
            "sony camera",
        ],
        max_results_per_query=20,
    ),
    "BASELINE": InvestigationSuiteConfig(
        investigation_id="BASELINE",
        name="Standard Marketplace Electronics Baseline",
        description="Neutral baseline dataset of standard marketplace electronics listings across key categories for statistical and signal comparison.",
        categories=["smartphones", "laptops", "gaming consoles", "cars", "cameras"],
        target_queries=[],
        baseline_queries=[
            "iphone",
            "macbook",
            "playstation 5",
            "asus rog laptop",
            "canon camera",
            "honda city car",
        ],
        max_results_per_query=20,
    ),
}


def get_investigation_config(investigation_id: str) -> InvestigationSuiteConfig:
    """Retrieve configuration suite by ID."""
    norm_id = investigation_id.upper().strip()
    if norm_id in INVESTIGATION_SUITES:
        return INVESTIGATION_SUITES[norm_id]
    raise ValueError(
        f"Unknown investigation ID: '{investigation_id}'. "
        f"Available suites: {list(INVESTIGATION_SUITES.keys())}"
    )
