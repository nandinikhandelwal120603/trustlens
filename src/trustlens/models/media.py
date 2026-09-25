"""Media asset model for marketplace images and videos."""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from trustlens.models.common import MediaType


class Media(BaseModel):
    """Media artifact attached to a listing (image or video)."""

    media_id: str = Field(
        default_factory=lambda: f"med_{uuid4().hex[:12]}",
        description="Internal unique media identifier",
    )
    listing_id: Optional[str] = Field(default=None, description="Reference to parent listing_id")
    media_type: MediaType = Field(
        default=MediaType.IMAGE, description="Media category (image or video)"
    )
    source_url: Optional[str] = Field(default=None, description="Original remote URL of the media")
    local_path: Optional[str] = Field(default=None, description="Relative or absolute path on disk")
    mime_type: Optional[str] = Field(
        default=None, description="MIME content type (e.g. image/jpeg, video/mp4)"
    )
    file_size: Optional[int] = Field(default=None, ge=0, description="File size in bytes")
    width: Optional[int] = Field(default=None, ge=0, description="Width in pixels")
    height: Optional[int] = Field(default=None, ge=0, description="Height in pixels")
    duration: Optional[float] = Field(default=None, ge=0.0, description="Video duration in seconds")
    sha256: Optional[str] = Field(
        default=None, description="SHA-256 cryptographic hash of the file bytes"
    )
    perceptual_hash: Optional[str] = Field(
        default=None, description="Perceptual hash (dhash or phash) for image similarity"
    )
    collection_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this media asset was collected",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional media metadata (EXIF, codec, etc.)"
    )
