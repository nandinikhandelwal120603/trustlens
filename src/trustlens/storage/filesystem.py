"""Filesystem manager for raw inputs, normalized JSONL/Parquet, and validation errors."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from trustlens.config.settings import settings
from trustlens.models.listing import CanonicalListing


class StorageManager:
    """Manages reading and writing artifacts to the local filesystem."""

    def __init__(
        self,
        raw_dir: Optional[Path] = None,
        normalized_dir: Optional[Path] = None,
    ):
        self.raw_dir = raw_dir or settings.raw_data_dir
        self.normalized_dir = normalized_dir or settings.normalized_data_dir
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.normalized_dir.mkdir(parents=True, exist_ok=True)

    def save_raw_artifact(
        self,
        case_id: str,
        filename: str,
        content: str | bytes | dict[str, Any],
    ) -> Path:
        """Save a raw artifact (JSON, HTML, image, screenshot) under data/raw/<case_id>/."""
        case_dir = self.raw_dir / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        target_path = case_dir / filename

        if isinstance(content, bytes):
            target_path.write_bytes(content)
        elif isinstance(content, dict):
            target_path.write_text(json.dumps(content, indent=2, default=str), encoding="utf-8")
        else:
            target_path.write_text(str(content), encoding="utf-8")

        return target_path

    def append_validation_error(
        self,
        source: str,
        raw_record: dict[str, Any],
        errors: list[str],
        case_id: Optional[str] = None,
    ) -> Path:
        """Record an invalid record to data/raw/validation_errors.jsonl without halting ingestion."""
        error_file = self.raw_dir / "validation_errors.jsonl"
        error_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "case_id": case_id,
            "source": source,
            "errors": errors,
            "raw_record": raw_record,
        }
        with open(error_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_entry, default=str) + "\n")
        return error_file

    def append_normalized_listing(self, listing: CanonicalListing) -> Path:
        """Append a normalized listing to data/normalized/listings.jsonl."""
        jsonl_path = self.normalized_dir / "listings.jsonl"
        with open(jsonl_path, "a", encoding="utf-8") as f:
            f.write(listing.model_dump_json() + "\n")
        return jsonl_path

    def export_normalized_to_parquet(self) -> Optional[Path]:
        """Export normalized JSONL records into a compressed Parquet dataset."""
        jsonl_path = self.normalized_dir / "listings.jsonl"
        if not jsonl_path.exists():
            return None

        records = []
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        if not records:
            return None

        # Flatten records for tabular parquet representation
        flattened = []
        for r in records:
            seller = r.get("seller") or {}
            media_list = r.get("media") or []
            flattened.append(
                {
                    "listing_id": r.get("listing_id"),
                    "case_id": r.get("case_id"),
                    "source": r.get("source"),
                    "source_listing_id": r.get("source_listing_id"),
                    "source_url": r.get("source_url"),
                    "raw_title": r.get("raw_title"),
                    "normalized_title": r.get("normalized_title"),
                    "raw_description": r.get("raw_description"),
                    "normalized_description": r.get("normalized_description"),
                    "category": r.get("category"),
                    "subcategory": r.get("subcategory"),
                    "brand": r.get("brand"),
                    "model": r.get("model"),
                    "raw_price": r.get("raw_price"),
                    "normalized_price": r.get("normalized_price"),
                    "raw_currency": r.get("raw_currency"),
                    "normalized_currency": r.get("normalized_currency"),
                    "condition": r.get("condition"),
                    "location_raw": r.get("location_raw"),
                    "location_city": r.get("location_city"),
                    "location_state": r.get("location_state"),
                    "posted_at": r.get("posted_at"),
                    "collected_at": r.get("collected_at"),
                    "is_synthetic": r.get("is_synthetic", False),
                    "seller_id": seller.get("seller_id"),
                    "seller_display_name": seller.get("display_name"),
                    "seller_phone_hash": seller.get("phone_hash"),
                    "media_count": len(media_list),
                }
            )

        df = pd.DataFrame(flattened)
        parquet_path = self.normalized_dir / "listings.parquet"
        df.to_parquet(parquet_path, engine="pyarrow", index=False)
        return parquet_path
