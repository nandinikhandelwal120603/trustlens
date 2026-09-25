"""Core Ingestion Pipeline coordinating Raw Storage, Validation, Normalization, Deduplication, and Persistence."""

from dataclasses import dataclass
from typing import Any, Optional

from sqlalchemy.orm import Session

from trustlens.ingestion.deduplicator import Deduplicator
from trustlens.ingestion.validators import ListingValidator
from trustlens.models.listing import CanonicalListing
from trustlens.storage.filesystem import StorageManager
from trustlens.storage.repository import Repository
from trustlens.utils.logging import StageTimer, logger


@dataclass
class IngestionResult:
    """Outcome metrics for an ingestion run."""

    total_received: int = 0
    valid_count: int = 0
    invalid_count: int = 0
    duplicates_detected: int = 0
    persisted_count: int = 0
    case_ids: list[str] = None  # type: ignore

    def __post_init__(self):
        if self.case_ids is None:
            self.case_ids = []


class IngestionPipeline:
    """Main orchestration pipeline for TrustLens marketplace data ingestion."""

    def __init__(
        self,
        session: Session,
        storage: Optional[StorageManager] = None,
    ):
        self.session = session
        self.repo = Repository(session)
        self.storage = storage or StorageManager()
        self.deduplicator = Deduplicator(self.repo)

    def ingest_canonical(
        self,
        listing: CanonicalListing,
        raw_payload: Optional[dict[str, Any]] = None,
    ) -> tuple[bool, Optional[str]]:
        """Ingest a single canonical listing through all pipeline stages.

        Returns (success: bool, error_or_listing_id).
        """
        case_id = listing.case_id
        listing_id = listing.listing_id

        # Stage 1: Raw Data Preservation
        with StageTimer("raw_preservation", case_id=case_id, listing_id=listing_id):
            raw_to_save = raw_payload or listing.model_dump(mode="json")
            self.storage.save_raw_artifact(
                case_id=case_id,
                filename="source.json",
                content=raw_to_save,
            )

        # Stage 2: Validation
        with StageTimer("validation", case_id=case_id, listing_id=listing_id):
            is_valid, errors = ListingValidator.validate_canonical(listing)
            if not is_valid:
                self.storage.append_validation_error(
                    source=listing.source,
                    raw_record=raw_to_save,
                    errors=errors,
                    case_id=case_id,
                )
                logger.warning(
                    f"Validation failed for listing {listing_id} (case {case_id}): {', '.join(errors)}"
                )
                return False, f"Validation error: {', '.join(errors)}"

        # Stage 3: Deduplication
        with StageTimer("deduplication", case_id=case_id, listing_id=listing_id):
            dup_info = self.deduplicator.check_duplicate(listing)
            if dup_info:
                orig_id, dup_type, reason = dup_info
                logger.info(
                    f"Duplicate detected: listing {listing_id} is a {dup_type.value} match with {orig_id} ({reason})"
                )
                self.deduplicator.record_duplicate(
                    original_listing_id=orig_id,
                    duplicate_listing_id=listing_id,
                    duplicate_type=dup_type,
                    match_reason=reason,
                )
                listing.extracted_claims["is_duplicate"] = True
                listing.extracted_claims["duplicate_of"] = orig_id
                listing.extracted_claims["duplicate_type"] = dup_type.value
                listing.extracted_claims["duplicate_reason"] = reason

        # Stage 4: Relational Persistence
        with StageTimer("database_persist", case_id=case_id, listing_id=listing_id):
            self.repo.save_listing(listing)

        # Stage 5: Normalized Tabular/JSONL Export
        with StageTimer("export_normalized", case_id=case_id, listing_id=listing_id):
            self.storage.append_normalized_listing(listing)

        return True, listing_id

    def ingest_batch(
        self,
        listings: list[CanonicalListing],
        raw_records: Optional[list[dict[str, Any]]] = None,
    ) -> IngestionResult:
        """Ingest a batch of listings, collecting overall metrics."""
        result = IngestionResult(total_received=len(listings))

        for idx, listing in enumerate(listings):
            raw_item = raw_records[idx] if raw_records and idx < len(raw_records) else None
            success, msg = self.ingest_canonical(listing, raw_payload=raw_item)
            if success:
                result.valid_count += 1
                result.persisted_count += 1
                result.case_ids.append(listing.case_id)
                if listing.extracted_claims.get("is_duplicate"):
                    result.duplicates_detected += 1
            else:
                result.invalid_count += 1

        # Optionally refresh parquet export
        try:
            self.storage.export_normalized_to_parquet()
        except Exception as e:
            logger.debug(f"Parquet export skipped or failed: {e}")

        return result
