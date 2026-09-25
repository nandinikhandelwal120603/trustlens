"""
TrustLens Marketplace Intelligence — Async Media Downloader (Phase C).
Fast concurrent downloader for Apollo marketplace image assets with caching and retry.
"""

import asyncio
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx
import pandas as pd


class MediaDownloader:
    """Async downloader for marketplace media assets."""

    def __init__(
        self,
        media_vault_dir: Path = Path("data/olx_media"),
        concurrency_limit: int = 30,
        timeout_seconds: float = 12.0,
        max_retries: int = 2,
    ):
        self.media_vault_dir = Path(media_vault_dir)
        self.concurrency_limit = concurrency_limit
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.media_vault_dir.mkdir(parents=True, exist_ok=True)

    async def download_all(self, media_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Downloads all unique media items concurrently, skipping already downloaded files.
        """
        # Deduplicate by file_id / source_url
        unique_tasks: Dict[str, Dict[str, Any]] = {}
        for m in media_records:
            fid = m.get("file_id") or m.get("source_url")
            url = m.get("source_url")
            if fid and url and fid not in unique_tasks:
                unique_tasks[fid] = {
                    "file_id": fid,
                    "source_url": url,
                    "target_path": self.media_vault_dir / f"{fid}.webp",
                }

        total_unique = len(unique_tasks)
        already_downloaded = sum(1 for t in unique_tasks.values() if t["target_path"].exists())
        to_download = [t for t in unique_tasks.values() if not t["target_path"].exists()]

        semaphore = asyncio.Semaphore(self.concurrency_limit)
        results: Dict[str, Dict[str, Any]] = {}

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout_seconds),
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=50, max_connections=100),
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"},
        ) as client:

            async def _fetch(item: Dict[str, Any]) -> Tuple[str, bool, Optional[str]]:
                fid = item["file_id"]
                url = item["source_url"]
                path: Path = item["target_path"]

                if path.exists() and path.stat().st_size > 0:
                    return fid, True, None

                async with semaphore:
                    for attempt in range(self.max_retries + 1):
                        try:
                            resp = await client.get(url)
                            if resp.status_code == 200 and len(resp.content) > 0:
                                with open(path, "wb") as fp:
                                    fp.write(resp.content)
                                return fid, True, None
                            elif resp.status_code == 404:
                                return fid, False, "HTTP 404 Not Found"
                        except Exception as e:
                            if attempt == self.max_retries:
                                return fid, False, str(e)
                            await asyncio.sleep(0.5 * (attempt + 1))

                    return fid, False, "Max retries exceeded"

            tasks = [_fetch(item) for item in to_download]
            if tasks:
                download_outcomes = await asyncio.gather(*tasks)
            else:
                download_outcomes = []

        success_count = already_downloaded
        failed_count = 0
        error_reasons: Dict[str, int] = Counter()

        for fid, success, err in download_outcomes:
            if success:
                success_count += 1
            else:
                failed_count += 1
                if err:
                    error_reasons[err] += 1

        return {
            "total_unique_assets": total_unique,
            "cached_pre_existing": already_downloaded,
            "newly_downloaded": len(download_outcomes) - failed_count,
            "total_available": success_count,
            "failed_count": failed_count,
            "error_reasons": dict(error_reasons),
        }

    def run_sync(self, media_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synchronous wrapper for downloading."""
        return asyncio.run(self.download_all(media_records))
