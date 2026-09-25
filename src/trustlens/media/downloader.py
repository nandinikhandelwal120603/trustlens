"""Asynchronous media downloader for TrustLens."""

import asyncio
from pathlib import Path
from typing import Optional

import httpx

from trustlens.config.settings import settings
from trustlens.media.hasher import compute_perceptual_hash, compute_sha256
from trustlens.media.inspector import inspect_image
from trustlens.models.common import MediaType
from trustlens.models.media import Media
from trustlens.utils.logging import logger


class MediaDownloader:
    """Safely downloads remote media assets with rate limits, timeouts, and size caps."""

    def __init__(
        self,
        max_concurrent: int = settings.media_max_concurrent_downloads,
        timeout_sec: int = settings.media_download_timeout_sec,
        max_size_mb: int = settings.media_max_file_size_mb,
    ):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.timeout = httpx.Timeout(timeout_sec)
        self.max_bytes = max_size_mb * 1024 * 1024

    async def download_media(
        self,
        media: Media,
        destination_dir: Path,
        client: Optional[httpx.AsyncClient] = None,
    ) -> Media:
        """Download remote media asset, inspect properties, compute hashes, and update Media object."""
        if not media.source_url:
            return media

        destination_dir.mkdir(parents=True, exist_ok=True)

        async with self.semaphore:
            should_close = False
            if client is None:
                client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
                should_close = True

            try:
                response = await client.get(media.source_url)
                response.raise_for_status()

                content = response.content
                if len(content) > self.max_bytes:
                    logger.warning(
                        f"Media {media.source_url} exceeds max size {self.max_bytes} bytes. Skipping."
                    )
                    return media

                # Inspect content
                mime_type, width, height, file_size = inspect_image(content)

                # Determine extension
                ext = ".jpg"
                if mime_type:
                    if "png" in mime_type:
                        ext = ".png"
                    elif "webp" in mime_type:
                        ext = ".webp"
                    elif "mp4" in mime_type or "video" in mime_type:
                        ext = ".mp4"
                        media.media_type = MediaType.VIDEO

                final_path = destination_dir / f"{media.media_id}{ext}"
                final_path.write_bytes(content)

                # Hashes
                sha256 = compute_sha256(content)
                p_hash = (
                    compute_perceptual_hash(content)
                    if media.media_type == MediaType.IMAGE
                    else None
                )

                # Update media attributes
                media.local_path = str(final_path)
                media.mime_type = mime_type or response.headers.get("content-type")
                media.file_size = file_size
                media.width = width
                media.height = height
                media.sha256 = sha256
                media.perceptual_hash = p_hash

            except Exception as e:
                logger.warning(f"Failed to download media {media.source_url}: {e}")
            finally:
                if should_close:
                    await client.aclose()

        return media

    async def download_all_for_listing(
        self,
        media_list: list[Media],
        destination_dir: Path,
    ) -> list[Media]:
        """Download all media items for a listing concurrently."""
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            tasks = [self.download_media(m, destination_dir, client=client) for m in media_list]
            return await asyncio.gather(*tasks)
