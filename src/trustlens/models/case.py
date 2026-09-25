"""Case model representing an investigation lifecycle."""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from trustlens.models.common import CaseStatus


class Case(BaseModel):
    """Investigation case container linking a listing, evidence, and lifecycle status."""

    case_id: str = Field(
        default_factory=lambda: f"case_{uuid4().hex[:12]}",
        description="Internal unique case identifier",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the case was initialized",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the case was last modified",
    )
    source: str = Field(
        ..., description="Origin source of the case (user_submission, crawl, dataset)"
    )
    listing_id: Optional[str] = Field(
        default=None, description="Primary listing under investigation"
    )
    status: CaseStatus = Field(
        default=CaseStatus.NEW,
        description="Investigation state (new, collecting, processing, review, labeled, completed)",
    )
    labels: list[str] = Field(
        default_factory=list, description="Ground truth or categorization tags"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary case-level context and flags"
    )
