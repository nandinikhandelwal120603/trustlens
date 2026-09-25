"""
TrustLens — Human-Readable Investigation Report Generator (Phase 3).
"""

from datetime import datetime, timezone
from trustlens.olx.models import OLXInvestigation


class InvestigationReportGenerator:
    """Generates human-readable, evidence-grounded investigation reports."""

    @classmethod
    def generate_report(cls, investigation: OLXInvestigation) -> str:
        """Generate human-readable markdown investigation report."""
        listing = investigation.listing
        seller = investigation.seller

        lines = [
            "# TRUSTLENS INVESTIGATION REPORT",
            "=================================",
            f"**Investigation ID**: `{investigation.investigation_id}`",
            f"**Listing ID**: `{listing.listing_id}`",
            f"**Target Suite**: `{listing.investigation_id}` ({listing.collection_type.value.upper()})",
            f"**Generated At**: {investigation.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "## 1. COLLECTED LISTING INFORMATION",
            "------------------------------------",
            f"* **Title**: {listing.title}",
            f"* **Observed Price**: ₹{listing.price:,.0f}" if listing.price else "* **Observed Price**: [Not Stated]",
            f"* **Location**: {listing.location or 'Unknown'}",
            f"* **Category**: {listing.category} / {listing.subcategory or 'General'}",
            f"* **Product Inferred**: {listing.product.brand or ''} {listing.product.model or ''} {listing.product.storage or ''}".strip(),
            f"* **Seller**: {seller.display_name or 'OLX User'} ({seller.seller_type or 'Individual'})",
            f"* **Seller Location**: {seller.location or listing.location or 'Unknown'}",
            f"* **Source URL**: {listing.listing_url}",
            "",
            "## 2. SELLER / LISTING CLAIMS",
            "------------------------------",
        ]

        if listing.claims:
            for clm in listing.claims:
                lines.append(f"* **[{clm.claim_id}]**: {clm.claim_text} *(Status: {clm.status.value})*")
        else:
            lines.append("* No explicit promotional/distress claims extracted from listing text.")

        lines.extend([
            "",
            "## 3. OBSERVED MARKETPLACE SIGNALS",
            "-----------------------------------",
        ])

        if investigation.signals:
            for idx, sig in enumerate(investigation.signals, 1):
                evi_str = ", ".join(sig.evidence_ids) if sig.evidence_ids else "Direct Observation"
                lines.append(f"### {idx}. {sig.signal_type.replace('_', ' ').title()}")
                lines.append(f"* **Description**: {sig.description}")
                lines.append(f"* **Status**: `{sig.status.value.upper()}` | **Confidence**: `{sig.confidence}`")
                lines.append(f"* **Supporting Evidence**: `{evi_str}`")
                lines.append("")
        else:
            lines.append("* No anomalous risk signals observed on this listing.")
            lines.append("")

        lines.extend([
            "## 4. INDEPENDENT VERIFICATION CHECKS",
            "--------------------------------------",
        ])

        if investigation.verification_checks:
            for chk in investigation.verification_checks:
                lines.append(f"* **{chk.check_type.replace('_', ' ').title()}** (`{chk.check_id}`):")
                lines.append(f"  - Target Claim: {chk.target_claim}")
                lines.append(f"  - External Observation: {chk.external_observation}")
                lines.append(f"  - Status: `{chk.verification_status.value.upper()}`")
                if chk.notes:
                    lines.append(f"  - Guidance: {chk.notes}")
        else:
            lines.append("* Standard baseline verification protocol applied.")

        lines.extend([
            "",
            "## 5. ATTACHED MEDIA OBSERVATIONS",
            "----------------------------------",
        ])

        if listing.media:
            for m in listing.media:
                dim_str = f"{m.width}x{m.height}" if m.width and m.height else "dimensions uninspected"
                sha_str = f"`{m.sha256[:16]}...`" if m.sha256 else "pending hash"
                lines.append(f"* **[{m.media_id}]**: {m.mime_type or 'image'} ({dim_str}) | SHA-256: {sha_str}")
        else:
            lines.append("* Zero media assets attached to this listing.")

        lines.extend([
            "",
            "## 6. IMPORTANT UNCERTAINTIES",
            "------------------------------",
        ])

        if investigation.uncertainties:
            for unc in investigation.uncertainties:
                lines.append(f"* {unc}")
        else:
            lines.append("* All primary listing parameters directly observed from source.")

        lines.extend([
            "",
            "## 7. RECOMMENDED NEXT VERIFICATION STEPS",
            "------------------------------------------",
        ])

        for step in investigation.next_steps:
            lines.append(f"* {step}")

        lines.extend([
            "",
            "## 8. OVERALL INVESTIGATION STATUS",
            "-----------------------------------",
            "> **NOTICE**: Multiple observable signals require verification before transacting.",
            "> This report presents empirical observations and does **NOT** establish that the seller is fraudulent.",
            "> Never transfer funds prior to physical handover and inspection in a safe public location.",
        ])

        return "\n".join(lines)
