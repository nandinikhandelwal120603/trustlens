"""Validation engine for incoming listing records."""

from typing import Any, Tuple

from trustlens.models.listing import CanonicalListing


class ListingValidator:
    """Validates raw and canonical listing records."""

    @staticmethod
    def validate_raw_dict(record: dict[str, Any]) -> Tuple[bool, list[str]]:
        """Perform pre-ingestion sanity checks on raw dictionary input."""
        errors: list[str] = []

        # Must have a non-empty title or source description
        title = record.get("title") or record.get("raw_title")
        if not title or not str(title).strip():
            errors.append("Missing required field: 'title'")

        # Must have a source defined
        source = record.get("source")
        if not source or not str(source).strip():
            errors.append("Missing required field: 'source'")

        # If price is present, must not be negative
        price = record.get("price") or record.get("raw_price") or record.get("normalized_price")
        if price is not None:
            try:
                # If numeric or simple float string
                clean_p = str(price).replace("₹", "").replace(",", "").replace("Rs.", "").strip()
                if clean_p and not clean_p.endswith("k") and "lakh" not in clean_p.lower():
                    if float(clean_p) < 0:
                        errors.append("Price cannot be negative")
            except (ValueError, TypeError):
                pass

        # Check media structures if provided
        media = record.get("media")
        if media is not None and not isinstance(media, list):
            errors.append("Field 'media' must be a list of media objects")

        return (len(errors) == 0, errors)

    @staticmethod
    def validate_canonical(listing: CanonicalListing) -> Tuple[bool, list[str]]:
        """Validate an instantiated CanonicalListing."""
        errors: list[str] = []

        if not listing.listing_id or not listing.listing_id.strip():
            errors.append("listing_id cannot be empty")

        if not listing.raw_title or not listing.raw_title.strip():
            errors.append("raw_title cannot be empty")

        if listing.normalized_price is not None and listing.normalized_price < 0:
            errors.append(f"normalized_price cannot be negative (got {listing.normalized_price})")

        if not listing.category or not listing.category.strip():
            errors.append("category cannot be empty")

        for i, m in enumerate(listing.media):
            if not m.source_url and not m.local_path:
                errors.append(f"Media item {i} must have either source_url or local_path")

        return (len(errors) == 0, errors)
