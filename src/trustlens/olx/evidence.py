"""
TrustLens — Evidence Linker & Provenance Tracker (Phase 3).
"""

from typing import List, Tuple
from trustlens.olx.models import (
    OLXEvidence,
    OLXListing,
    OLXSignal,
    VerificationStatus,
)


class EvidenceLinker:
    """Builds structured evidence records linking signals to observed listing context."""

    @classmethod
    def link_evidence(
        cls,
        listing: OLXListing,
        signals: List[OLXSignal],
    ) -> Tuple[List[OLXEvidence], List[OLXSignal]]:
        """Create evidence items and attach their IDs to corresponding signals."""
        evidence_list: List[OLXEvidence] = []
        evi_counter = 1

        # 1. Base Evidence: Listing Existence & Price
        base_evi_id = f"EVID-{listing.listing_id}-{evi_counter:04d}"
        evi_counter += 1
        evidence_list.append(
            OLXEvidence(
                evidence_id=base_evi_id,
                investigation_id=listing.investigation_id,
                source_type="olx_listing",
                source_reference=listing.listing_url,
                description=f"Public OLX listing page '{listing.title}' with observed price ₹{listing.price or 0:,.0f}",
                evidence_text=f"Title: {listing.title} | Price: ₹{listing.price} | Location: {listing.location}",
                claim_or_observation="Directly observed public listing on OLX marketplace",
                relationship_to_claim="supports",
                verification_status=VerificationStatus.UNVERIFIED,
            )
        )

        # 2. Text Evidence: Description Claims
        if listing.description:
            desc_evi_id = f"EVID-{listing.listing_id}-{evi_counter:04d}"
            evi_counter += 1
            evidence_list.append(
                OLXEvidence(
                    evidence_id=desc_evi_id,
                    investigation_id=listing.investigation_id,
                    source_type="listing_description",
                    source_reference=listing.listing_url,
                    description="Listing description text provided by the seller",
                    evidence_text=listing.description[:500],
                    claim_or_observation="Seller-authored listing description text",
                    relationship_to_claim="supports",
                    verification_status=VerificationStatus.UNVERIFIED,
                )
            )

        # 3. Media Evidence: Attached Images
        for m in listing.media:
            m_evi_id = f"EVID-{listing.listing_id}-{evi_counter:04d}"
            evi_counter += 1
            evidence_list.append(
                OLXEvidence(
                    evidence_id=m_evi_id,
                    investigation_id=listing.investigation_id,
                    source_type="listing_image",
                    source_reference=m.source_url,
                    related_media_id=m.media_id,
                    description=f"Public listing photo {m.media_id} (SHA-256: {m.sha256 or 'pending'})",
                    claim_or_observation="Attached public product/document image",
                    relationship_to_claim="does_not_verify",
                    verification_status=VerificationStatus.UNVERIFIED,
                )
            )

        # Attach evidence IDs to signals
        for sig in signals:
            if sig.signal_type == "unusually_low_price":
                sig.evidence_ids.append(base_evi_id)
            elif sig.signal_type in ["army_persona", "advance_payment", "whatsapp_migration", "warehouse_clearance", "invoice_claim", "urgent_sale"]:
                sig.evidence_ids.append(desc_evi_id if listing.description else base_evi_id)

        return evidence_list, signals
