"""
Unit tests for OLX Signal Detector and Evidence Linker (Phase 3).
"""

import pytest
from trustlens.olx.evidence import EvidenceLinker
from trustlens.olx.models import (
    CollectionType,
    OLXClaim,
    OLXListing,
    OLXProduct,
    OLXSeller,
    VerificationStatus,
)
from trustlens.olx.signals import SignalDetector


def test_detect_price_anomaly_and_signals():
    listing = OLXListing(
        listing_id="OLX-000001",
        source="olx",
        listing_url="https://www.olx.in/item/macbook-m2-clearance",
        investigation_id="INV-002",
        collection_type=CollectionType.TARGETED,
        title="Apple MacBook Pro M2 16GB",
        description="Urgent company clearance sale. Army officer posted in remote base. WhatsApp on 9876543210. Need 2000 advance token. GST invoice available.",
        price=35000.0,
        currency="INR",
        location="Pune",
        product=OLXProduct(brand="Apple", model="MacBook Pro M2", storage="512GB", ram="16GB"),
        seller=OLXSeller(display_name="Tech Resale"),
    )

    signals, uncertainties = SignalDetector.detect_signals(listing)
    sig_types = [s.signal_type for s in signals]

    # Check that key signals fired
    assert "unusually_low_price" in sig_types
    assert "army_persona" in sig_types
    assert "advance_payment" in sig_types
    assert "whatsapp_migration" in sig_types
    assert "warehouse_clearance" in sig_types
    assert "invoice_claim" in sig_types
    assert "urgent_sale" in sig_types

    # Link evidence
    evidence, signals = EvidenceLinker.link_evidence(listing, signals)
    assert len(evidence) >= 2
    for sig in signals:
        assert len(sig.evidence_ids) > 0

    # Verify default verification status is UNVERIFIED
    for evi in evidence:
        assert evi.verification_status == VerificationStatus.UNVERIFIED


def test_neutral_baseline_no_unsupported_signals():
    listing = OLXListing(
        listing_id="OLX-000002",
        source="olx",
        listing_url="https://www.olx.in/item/iphone-15-fair",
        investigation_id="BASELINE",
        collection_type=CollectionType.BASELINE,
        title="iPhone 15 128GB Black",
        description="Used phone in good condition with original box and cable. Hand to hand deal in Indiranagar.",
        price=50000.0,
        currency="INR",
        location="Bangalore",
        product=OLXProduct(brand="Apple", model="iPhone 15", storage="128GB"),
        seller=OLXSeller(display_name="Rahul"),
    )

    signals, uncertainties = SignalDetector.detect_signals(listing)
    sig_types = [s.signal_type for s in signals]

    # No anomalous fraud signals should fire on a normal baseline listing
    assert "unusually_low_price" not in sig_types
    assert "army_persona" not in sig_types
    assert "advance_payment" not in sig_types
    assert "whatsapp_migration" not in sig_types
