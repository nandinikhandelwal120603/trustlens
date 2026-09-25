"""Evidence model for supporting claims in investigations."""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from trustlens.models.common import VerificationStatus


class Evidence(BaseModel):
    """Evidence model to anchor findings, web lookups, and corroborations."""

    evidence_id: str = Field(
        default_factory=lambda: f"evi_{uuid4().hex[:12]}",
        description="Internal unique evidence identifier",
    )
    case_id: str = Field(..., description="Foreign key to associated Case")
    source_type: str = Field(
        ..., description="Type of evidence source (e.g. web, registry, image_db, user)"
    )
    source_name: str = Field(
        ..., description="Name of the source (e.g. Google Search, GST Portal, Official Spec)"
    )
    source_url: Optional[str] = Field(default=None, description="URL where evidence was retrieved")
    claim: str = Field(..., description="The factual claim being verified")
    evidence_text: str = Field(
        ..., description="Snippets or structured text content of the evidence"
    )
    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when evidence was acquired",
    )
    verification_status: VerificationStatus = Field(
        default=VerificationStatus.UNVERIFIED,
        description="Status: unverified, corroborated, contradicted, or inconclusive",
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Evidence confidence score (0.0 to 1.0)"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional context or tool output metadata"
    )
