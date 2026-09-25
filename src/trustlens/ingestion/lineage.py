"""Data lineage and provenance tracking helpers."""

from datetime import datetime, timezone
from typing import Any, Optional

from trustlens.config.settings import settings
from trustlens.models.listing import LineageMetadata


def create_lineage(
    source: str,
    source_url: Optional[str] = None,
    ingestion_batch_id: Optional[str] = None,
    extra: Optional[dict[str, Any]] = None,
) -> LineageMetadata:
    """Create a standardized provenance lineage stamp for an ingested record."""
    return LineageMetadata(
        pipeline_version=settings.pipeline_version,
        schema_version=settings.schema_version,
        source=source,
        collected_at=datetime.now(timezone.utc),
        source_url=source_url,
        ingestion_batch_id=ingestion_batch_id,
        extra=extra or {},
    )
