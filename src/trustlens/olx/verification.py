"""
TrustLens — Independent Verification & Contextual Comparison Framework (Phase 3).
"""

from typing import List, Tuple
from trustlens.olx.models import (
    OLXListing,
    OLXVerificationCheck,
    VerificationStatus,
)


class VerificationEngine:
    """Performs structured verification task formulations and next-step recommendations."""

    @classmethod
    def run_checks(cls, listing: OLXListing) -> Tuple[List[OLXVerificationCheck], List[str]]:
        """Formulate verification check tasks and recommended next steps for human investigators."""
        checks: List[OLXVerificationCheck] = []
        next_steps: List[str] = []
        inv_id = listing.investigation_id
        check_counter = 1

        # 1. Business Identity Verification Check
        if listing.seller.business_claim or "company" in listing.description.lower():
            checks.append(
                OLXVerificationCheck(
                    check_id=f"CHK-{listing.listing_id}-{check_counter:03d}",
                    investigation_id=inv_id,
                    check_type="business_identity",
                    target_claim=listing.seller.business_claim or "Company / Warehouse clearance claim",
                    external_observation="Public registry check not executed; business credentials remain unverified.",
                    verification_status=VerificationStatus.NOT_CHECKED,
                    notes="Check official MCA / GST registry for claimed legal entity name before transacting.",
                )
            )
            check_counter += 1
            next_steps.append("Verify claimed business entity registration in official MCA / GST portals.")

        # 2. Invoice Authenticity Check
        if any(k in listing.description.lower() for k in ["invoice", "bill", "receipt", "gst"]):
            checks.append(
                OLXVerificationCheck(
                    check_id=f"CHK-{listing.listing_id}-{check_counter:03d}",
                    investigation_id=inv_id,
                    check_type="invoice_authenticity",
                    target_claim="Original bill / GST invoice available",
                    external_observation="Invoice document authenticity cannot be verified from visual listing photos alone.",
                    verification_status=VerificationStatus.NOT_CHECKED,
                    notes="Inspect physical invoice and cross-verify seller GSTIN on the official GST portal.",
                )
            )
            check_counter += 1
            next_steps.append("Inspect physical invoice and verify seller GSTIN on the official government GST portal.")

        # 3. Product Ownership & Serial Number Check
        next_steps.append("Verify device serial number / IMEI on official manufacturer portal (e.g. Apple Check Coverage) during physical inspection.")
        next_steps.append("Strictly avoid transferring any advance booking token or gate-pass fee before physical item inspection in a public location.")

        return checks, next_steps
