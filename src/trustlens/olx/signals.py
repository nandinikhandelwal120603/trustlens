"""
TrustLens — Observable Marketplace Signal Detection Engine (Phase 3).
"""

import re
from typing import Dict, List, Optional, Tuple

from trustlens.olx.models import OLXListing, OLXSignal, SignalStatus


class SignalDetector:
    """Detects observable marketplace signals from an OLX listing."""

    # Benchmark median prices for high-risk electronics/vehicles (INR)
    PRICE_BENCHMARKS: Dict[str, float] = {
        "macbook pro m2": 95000.0,
        "macbook pro": 85000.0,
        "macbook air m1": 55000.0,
        "macbook air m2": 70000.0,
        "iphone 17 pro max": 135000.0,
        "iphone 15 pro max": 90000.0,
        "iphone 15": 52000.0,
        "iphone 14": 42000.0,
        "playstation 5": 42000.0,
        "ps5": 42000.0,
        "mahindra thar": 1100000.0,
        "honda city": 450000.0,
        "canon camera": 40000.0,
        "sony alpha": 65000.0,
    }

    @classmethod
    def detect_signals(cls, listing: OLXListing) -> Tuple[List[OLXSignal], List[str]]:
        """Extract observable signals and uncertainty notes from a listing."""
        signals: List[OLXSignal] = []
        uncertainties: List[str] = []
        full_text = f"{listing.title} {listing.description}".lower()
        inv_id = listing.investigation_id
        sig_counter = 1

        # 1. Price Anomaly Detection
        if listing.price and listing.price > 0:
            benchmark = None
            sorted_benchmarks = sorted(cls.PRICE_BENCHMARKS.items(), key=lambda x: len(x[0]), reverse=True)
            if listing.product.model:
                m_key = listing.product.model.lower()
                for b_key, b_val in sorted_benchmarks:
                    if b_key == m_key or b_key in m_key:
                        benchmark = b_val
                        break
            if not benchmark:
                for b_key, b_val in sorted_benchmarks:
                    if b_key in full_text:
                        benchmark = b_val
                        break

            if benchmark:
                discount = (benchmark - listing.price) / benchmark
                if discount >= 0.35:
                    signals.append(
                        OLXSignal(
                            signal_id=f"SIG-{listing.listing_id}-{sig_counter:03d}",
                            investigation_id=inv_id,
                            signal_type="unusually_low_price",
                            status=SignalStatus.OBSERVED,
                            description=(
                                f"Listing price of ₹{listing.price:,.0f} is {discount*100:.1f}% "
                                f"below benchmark market median of ₹{benchmark:,.0f} for this model."
                            ),
                            confidence="high",
                        )
                    )
                    sig_counter += 1
            else:
                uncertainties.append("Category/model baseline price could not be automatically established.")
        else:
            uncertainties.append("Listing does not state an explicit numerical price.")

        # 2. Army / CISF Persona Signal
        if any(k in full_text for k in ["army", "cisf", "defence", "military", "air force", "soldier", "posted at"]):
            signals.append(
                OLXSignal(
                    signal_id=f"SIG-{listing.listing_id}-{sig_counter:03d}",
                    investigation_id=inv_id,
                    signal_type="army_persona",
                    status=SignalStatus.OBSERVED,
                    description="Listing text mentions military/defense officer identity or military base posting.",
                    confidence="high",
                )
            )
            sig_counter += 1
            uncertainties.append("Seller military affiliation is claimed in description but unverified.")

        # 3. Advance / Token / Gate-Pass Payment Signal
        if any(k in full_text for k in ["advance", "booking token", "token amount", "gate pass", "delivery charge first", "pay first"]):
            signals.append(
                OLXSignal(
                    signal_id=f"SIG-{listing.listing_id}-{sig_counter:03d}",
                    investigation_id=inv_id,
                    signal_type="advance_payment",
                    status=SignalStatus.OBSERVED,
                    description="Listing demands advance payment, token, or gate-pass fee before physical inspection.",
                    confidence="high",
                )
            )
            sig_counter += 1

        # 4. Off-Platform / WhatsApp Migration Signal
        if any(k in full_text for k in ["whatsapp", "wa.me", "wa only", "chat on wa", "message on whatsapp"]) or bool(re.search(r"\b[6-9]\d{9}\b", full_text)):
            signals.append(
                OLXSignal(
                    signal_id=f"SIG-{listing.listing_id}-{sig_counter:03d}",
                    investigation_id=inv_id,
                    signal_type="whatsapp_migration",
                    status=SignalStatus.OBSERVED,
                    description="Listing explicitly directs buyer to communicate off-platform via WhatsApp or phone call.",
                    confidence="high",
                )
            )
            sig_counter += 1

        # 5. Warehouse / Corporate Liquidation Claim
        if any(k in full_text for k in ["warehouse clearance", "company clearance", "liquidation", "office closing", "company closing", "bulk stock"]):
            signals.append(
                OLXSignal(
                    signal_id=f"SIG-{listing.listing_id}-{sig_counter:03d}",
                    investigation_id=inv_id,
                    signal_type="warehouse_clearance",
                    status=SignalStatus.OBSERVED,
                    description="Listing claims corporate liquidation, office closing, or warehouse stock clearance.",
                    confidence="medium",
                )
            )
            sig_counter += 1
            uncertainties.append("Corporate liquidation claim not independently verified.")

        # 6. Invoice / Canteen Receipt Claim
        if any(k in full_text for k in ["gst bill", "original bill", "invoice available", "canteen receipt", "defence receipt"]):
            signals.append(
                OLXSignal(
                    signal_id=f"SIG-{listing.listing_id}-{sig_counter:03d}",
                    investigation_id=inv_id,
                    signal_type="invoice_claim",
                    status=SignalStatus.OBSERVED,
                    description="Listing claims availability of official GST invoice or defense canteen receipt.",
                    confidence="medium",
                )
            )
            sig_counter += 1
            uncertainties.append("Claimed invoice authenticity cannot be established without physical or registry check.")

        # 7. Urgent / Distress Sale
        if any(k in full_text for k in ["urgent sale", "urgent", "distress sale", "leaving city tomorrow", "moving abroad"]):
            signals.append(
                OLXSignal(
                    signal_id=f"SIG-{listing.listing_id}-{sig_counter:03d}",
                    investigation_id=inv_id,
                    signal_type="urgent_sale",
                    status=SignalStatus.OBSERVED,
                    description="Listing creates time urgency by claiming urgent relocation or distress sale.",
                    confidence="medium",
                )
            )
            sig_counter += 1

        return signals, uncertainties
