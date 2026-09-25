"""
TrustLens — OLX Media Downloader and Deduplication Engine (Phase 3).
"""

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional
import httpx
from PIL import Image

from trustlens.olx.models import OLXMedia
from trustlens.utils.logging import logger


class OLXMediaManager:
    """Manages downloading, hashing, storing, and deduplicating OLX listing images."""

    def __init__(self, media_dir: Path):
        self.media_dir = media_dir
        self.media_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.media_dir / "olx_media_manifest.jsonl"
        self.duplicates_path = self.media_dir / "duplicate_media_groups.json"

    async def download_media(
        self,
        media: OLXMedia,
        client: Optional[httpx.AsyncClient] = None,
        timeout: float = 15.0,
    ) -> OLXMedia:
        """Download a single media asset and extract SHA-256 and dimensions."""
        if not media.source_url or not media.source_url.startswith("http"):
            media.download_status = "failed"
            return media

        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)
            should_close = True

        try:
            resp = await client.get(media.source_url)
            if resp.status_code != 200:
                media.download_status = f"http_{resp.status_code}"
                return media

            content = resp.content
            media.file_size_bytes = len(content)
            media.sha256 = hashlib.sha256(content).hexdigest()

            # Determine file extension and write to disk
            ext = "webp"
            content_type = resp.headers.get("content-type", "").lower()
            if "jpeg" in content_type or "jpg" in content_type:
                ext = "jpg"
            elif "png" in content_type:
                ext = "png"
            elif "webp" in content_type:
                ext = "webp"

            file_name = f"{media.media_id}.{ext}"
            file_path = self.media_dir / file_name
            with open(file_path, "wb") as f:
                f.write(content)

            media.local_path = str(file_path.relative_to(self.media_dir.parent))
            media.mime_type = content_type or f"image/{ext}"

            # Inspect dimensions using PIL
            try:
                with Image.open(file_path) as img:
                    media.width, media.height = img.size
            except Exception:
                pass

            media.download_status = "success"
            return media

        except Exception as e:
            logger.warning(f"Failed to download media {media.source_url}: {e}")
            media.download_status = f"error: {str(e)[:50]}"
            return media
        finally:
            if should_close and client:
                await client.aclose()

    async def download_listing_media_batch(
        self,
        media_list: List[OLXMedia],
        concurrency: int = 5,
    ) -> List[OLXMedia]:
        """Download a batch of media assets with controlled concurrency."""
        sem = asyncio.Semaphore(concurrency)
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:

            async def _worker(m: OLXMedia):
                async with sem:
                    return await self.download_media(m, client=client)

            tasks = [_worker(m) for m in media_list]
            return await asyncio.gather(*tasks)

    def append_to_manifest(self, media_list: List[OLXMedia]):
        """Append downloaded media records to media_manifest.jsonl."""
        with open(self.manifest_path, "a", encoding="utf-8") as f:
            for m in media_list:
                f.write(m.model_dump_json() + "\n")

    def update_duplicate_groups(self) -> Dict[str, List[str]]:
        """Scan manifest for SHA-256 collisions and update duplicate_media_groups.json."""
        if not self.manifest_path.exists():
            return {}

        sha_map: Dict[str, List[str]] = {}
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    sha = item.get("sha256")
                    mid = item.get("media_id")
                    if sha and mid:
                        sha_map.setdefault(sha, []).append(mid)

        duplicates = {sha: mids for sha, mids in sha_map.items() if len(mids) > 1}
        with open(self.duplicates_path, "w", encoding="utf-8") as f:
            json.dump({
                "duplicate_count": len(duplicates),
                "clusters": [
                    {"sha256": sha, "media_ids": mids, "count": len(mids)}
                    for sha, mids in duplicates.items()
                ]
            }, f, indent=2)

        return duplicates
