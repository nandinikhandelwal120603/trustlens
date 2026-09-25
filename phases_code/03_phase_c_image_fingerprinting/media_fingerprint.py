"""Deterministic media fingerprinting (SHA-256, pHash, dHash, aHash)."""

import hashlib
import io
import mimetypes
from pathlib import Path
from typing import Optional, Tuple, Union

import imagehash
from PIL import Image

from trustlens.marketplace.models import (
    DownloadStatus,
    FingerprintStatus,
    MediaFingerprint,
)


class MediaFingerprinter:
    """Computes exact and perceptual image fingerprints when image bytes are present."""

    @staticmethod
    def compute_sha256(content: Union[bytes, Path]) -> str:
        """Compute SHA-256 digest from bytes or file path."""
        if isinstance(content, Path):
            hasher = hashlib.sha256()
            with open(content, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def compute_perceptual_hashes(
        content: Union[bytes, Path]
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[int], Optional[int]]:
        """
        Compute pHash, dHash, aHash and extract image dimensions.
        Returns: (phash, dhash, ahash, width, height)
        """
        try:
            if isinstance(content, Path):
                with Image.open(content) as img:
                    img_rgb = img.convert("RGB")
                    phash_val = str(imagehash.phash(img_rgb))
                    dhash_val = str(imagehash.dhash(img_rgb))
                    ahash_val = str(imagehash.average_hash(img_rgb))
                    w, h = img.size
                    return phash_val, dhash_val, ahash_val, w, h
            else:
                with Image.open(io.BytesIO(content)) as img:
                    img_rgb = img.convert("RGB")
                    phash_val = str(imagehash.phash(img_rgb))
                    dhash_val = str(imagehash.dhash(img_rgb))
                    ahash_val = str(imagehash.average_hash(img_rgb))
                    w, h = img.size
                    return phash_val, dhash_val, ahash_val, w, h
        except Exception:
            return None, None, None, None, None

    @classmethod
    def fingerprint_media(
        cls,
        media_id: str,
        listing_id: str,
        source_url: Optional[str] = None,
        local_path: Optional[Union[str, Path]] = None,
        content_bytes: Optional[bytes] = None,
    ) -> MediaFingerprint:
        """
        Create a MediaFingerprint record.
        Strictly distinguishes between URL-only metadata and downloaded bytes.
        """
        path_obj = Path(local_path) if local_path else None

        # 1. If no local bytes/file available, return record with status unavailable
        if not content_bytes and (not path_obj or not path_obj.exists()):
            return MediaFingerprint(
                media_id=media_id,
                listing_id=listing_id,
                source_url=source_url,
                local_path=str(path_obj) if path_obj else None,
                download_status=DownloadStatus.NOT_ATTEMPTED if not path_obj else DownloadStatus.FAILED,
                fingerprint_status=FingerprintStatus.UNAVAILABLE,
                download_error=None if not path_obj else "Local file does not exist",
            )

        # 2. Compute hashes from available content
        target = content_bytes or path_obj
        assert target is not None

        try:
            sha256_val = cls.compute_sha256(target)
            phash_val, dhash_val, ahash_val, width, height = cls.compute_perceptual_hashes(target)

            file_size = len(content_bytes) if content_bytes else path_obj.stat().st_size  # type: ignore

            mime_type = None
            if path_obj:
                mime_type, _ = mimetypes.guess_type(str(path_obj))
            if not mime_type and source_url:
                mime_type, _ = mimetypes.guess_type(source_url)
            if not mime_type:
                mime_type = "image/jpeg"

            is_computed = phash_val is not None and dhash_val is not None

            return MediaFingerprint(
                media_id=media_id,
                listing_id=listing_id,
                source_url=source_url,
                local_path=str(path_obj) if path_obj else None,
                download_status=DownloadStatus.DOWNLOADED,
                fingerprint_status=FingerprintStatus.COMPUTED if is_computed else FingerprintStatus.UNAVAILABLE,
                sha256=sha256_val,
                phash=phash_val,
                dhash=dhash_val,
                ahash=ahash_val,
                width=width,
                height=height,
                file_size=file_size,
                mime_type=mime_type,
            )

        except Exception as e:
            return MediaFingerprint(
                media_id=media_id,
                listing_id=listing_id,
                source_url=source_url,
                local_path=str(path_obj) if path_obj else None,
                download_status=DownloadStatus.FAILED,
                fingerprint_status=FingerprintStatus.UNAVAILABLE,
                download_error=str(e),
            )
