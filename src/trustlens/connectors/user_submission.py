"""User Submission Connector for JSON, CSV, and direct dictionary inputs."""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncGenerator, Optional
from uuid import uuid4

from trustlens.connectors.base import MarketplaceConnector
from trustlens.ingestion.lineage import create_lineage
from trustlens.ingestion.normalizer import Normalizer
from trustlens.models.common import MediaType
from trustlens.models.listing import CanonicalListing
from trustlens.models.media import Media
from trustlens.models.seller import Seller


class UserSubmissionConnector(MarketplaceConnector):
    """Handles listings provided directly by users via JSON, CSV, or form submissions."""

    def __init__(self, source_name: str = "user_submission"):
        super().__init__(source_name=source_name)

    async def fetch_listings(self, **kwargs: Any) -> AsyncGenerator[CanonicalListing, None]:
        """Yield canonical listings from file path, json string, or records list."""
        if "file_path" in kwargs:
            path = Path(kwargs["file_path"])
            if path.suffix.lower() == ".csv":
                async for item in self.from_csv(path):
                    yield item
            else:
                async for item in self.from_json(path):
                    yield item
        elif "records" in kwargs:
            for rec in kwargs["records"]:
                yield self.dict_to_canonical(rec)

    async def fetch_listing_by_id(self, listing_id: str) -> Optional[CanonicalListing]:
        """User submissions do not support remote ID lookups."""
        return None

    async def from_json(self, json_path: Path) -> AsyncGenerator[CanonicalListing, None]:
        """Read listings from a JSON file."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        records = data if isinstance(data, list) else [data]
        for rec in records:
            yield self.dict_to_canonical(rec, default_source="user_submission")

    async def from_csv(self, csv_path: Path) -> AsyncGenerator[CanonicalListing, None]:
        """Read listings from a CSV file."""
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert CSV row into listing dict
                rec = {
                    "source": row.get("source") or "user_submission",
                    "source_listing_id": row.get("source_listing_id"),
                    "source_url": row.get("source_url"),
                    "title": row.get("title") or row.get("raw_title"),
                    "description": row.get("description") or row.get("raw_description"),
                    "category": row.get("category"),
                    "subcategory": row.get("subcategory"),
                    "brand": row.get("brand"),
                    "model": row.get("model"),
                    "price": row.get("price") or row.get("raw_price"),
                    "currency": row.get("currency") or row.get("raw_currency") or "INR",
                    "condition": row.get("condition"),
                    "location": row.get("location") or row.get("location_raw"),
                    "posted_at": row.get("posted_at"),
                    "seller": {
                        "display_name": row.get("seller_name") or row.get("seller_display_name"),
                        "phone": row.get("seller_phone"),
                        "email": row.get("seller_email"),
                    },
                    "synthetic": row.get("synthetic", "").lower() in ["true", "1", "yes"],
                }
                yield self.dict_to_canonical(rec, default_source="user_submission")

    def dict_to_canonical(
        self, record: dict[str, Any], default_source: str = "user_submission"
    ) -> CanonicalListing:
        """Transform a raw dictionary into a CanonicalListing with normalized fields."""
        source = record.get("source") or default_source
        source_id = record.get("source_listing_id")
        source_url = record.get("source_url")

        raw_title = record.get("title") or record.get("raw_title") or "[NO TITLE]"
        raw_desc = record.get("description") or record.get("raw_description")

        # Normalization
        norm_title = Normalizer.normalize_text(raw_title)
        norm_desc = Normalizer.normalize_text(raw_desc) if raw_desc else None

        # Price parsing
        raw_price_input = record.get("price") or record.get("raw_price")
        raw_curr_input = record.get("currency") or record.get("raw_currency")
        raw_price, norm_price, raw_curr, norm_curr = Normalizer.normalize_price(
            raw_price_input, raw_curr_input
        )

        # Condition parsing
        cond_input = record.get("condition")
        condition = Normalizer.normalize_condition(cond_input)

        # Category normalization
        cat_input = record.get("category")
        sub_input = record.get("subcategory")
        category, subcategory = Normalizer.normalize_category(cat_input, sub_input, title=raw_title)

        # Location parsing
        raw_loc = record.get("location") or record.get("location_raw")
        loc_city, loc_state = Normalizer.parse_location(raw_loc)

        # Timestamps
        posted_at = None
        if p_at := record.get("posted_at"):
            try:
                if isinstance(p_at, str):
                    posted_at = datetime.fromisoformat(p_at.replace("Z", "+00:00"))
                elif isinstance(p_at, datetime):
                    posted_at = p_at
            except Exception:
                pass

        # Seller
        seller_obj = None
        if s_data := record.get("seller"):
            if isinstance(s_data, dict):
                seller_obj = Seller.from_raw(
                    source=source,
                    display_name=s_data.get("display_name"),
                    source_seller_id=s_data.get("source_seller_id"),
                    raw_phone=s_data.get("phone") or s_data.get("raw_phone"),
                    raw_email=s_data.get("email") or s_data.get("raw_email"),
                    account_age=s_data.get("account_age"),
                    profile_location=s_data.get("profile_location"),
                    verification_status=s_data.get("verification_status"),
                    seller_type=s_data.get("seller_type", "individual"),
                    listing_count=s_data.get("listing_count"),
                    business_name_claim=s_data.get("business_name_claim"),
                    gstin_claim=s_data.get("gstin_claim"),
                    website_claim=s_data.get("website_claim"),
                    metadata=s_data.get("metadata", {}),
                )

        # Media
        media_list: list[Media] = []
        for m in record.get("media", []):
            if isinstance(m, dict):
                m_type = MediaType.VIDEO if m.get("media_type") == "video" else MediaType.IMAGE
                media_list.append(
                    Media(
                        media_type=m_type,
                        source_url=m.get("source_url"),
                        local_path=m.get("local_path"),
                        mime_type=m.get("mime_type"),
                        sha256=m.get("sha256"),
                        perceptual_hash=m.get("perceptual_hash"),
                        metadata=m.get("metadata", {}),
                    )
                )

        # Lineage
        lineage = create_lineage(
            source=source,
            source_url=source_url,
            extra={"raw_format": "dict"},
        )

        return CanonicalListing(
            case_id=f"case_{uuid4().hex[:12]}",
            source=source,
            source_listing_id=source_id,
            source_url=source_url,
            raw_title=raw_title,
            normalized_title=norm_title,
            raw_description=raw_desc,
            normalized_description=norm_desc,
            category=category,
            subcategory=subcategory,
            brand=record.get("brand"),
            model=record.get("model"),
            raw_price=raw_price,
            normalized_price=norm_price,
            raw_currency=raw_curr,
            normalized_currency=norm_curr,
            condition=condition,
            location_raw=raw_loc,
            location_city=loc_city,
            location_state=loc_state,
            posted_at=posted_at,
            seller=seller_obj,
            media=media_list,
            extracted_claims=record.get("extracted_claims", {}),
            collection_metadata=lineage,
            is_synthetic=bool(record.get("synthetic", False) or record.get("is_synthetic", False)),
        )
