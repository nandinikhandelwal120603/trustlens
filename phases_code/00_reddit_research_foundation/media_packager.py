"""Reddit Media Downloader & Case-Mapped Multimodal Dataset Packager.

Processes raw Reddit posts JSON, downloads attached media assets asynchronously,
generates deterministic post-to-media mappings and manifests, runs strict integrity
validations, and packages the results into a ZIP ready for Claude Web multimodal analysis.
"""

import asyncio
import json
import os
import re
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import httpx

from trustlens.media.hasher import compute_sha256
from trustlens.media.inspector import inspect_image
from trustlens.media.validator import DatasetValidator, ValidationResult
from trustlens.utils.logging import logger

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 "
    "TrustLensResearch/1.0"
)


class RedditMediaPackager:
    """Orchestrates downloading media and building the case-mapped multimodal dataset."""

    def __init__(
        self,
        input_json_path: Path,
        output_dir: Path,
        concurrency: int = 5,
        timeout_sec: int = 20,
        max_size_mb: int = 50,
        create_zip: bool = True,
        zip_path: Optional[Path] = None,
    ):
        self.input_json_path = Path(input_json_path)
        self.output_dir = Path(output_dir)
        self.concurrency = concurrency
        self.timeout_sec = timeout_sec
        self.max_bytes = max_size_mb * 1024 * 1024
        self.create_zip_file = create_zip
        self.zip_path = Path(zip_path) if zip_path else self.output_dir.parent / f"{self.output_dir.name}.zip"

    def _extract_media_urls(self, post: dict[str, Any]) -> list[str]:
        """Extract and deduplicate media URLs from post, preserving ordering."""
        urls: list[str] = []
        seen: set[str] = set()

        def add_url(raw_u: Optional[str]):
            if not raw_u or not isinstance(raw_u, str):
                return
            u = raw_u.strip().replace("&amp;", "&")
            if (
                u
                and u.startswith("http")
                and not any(x in u for x in ["avatar", "snoo", "styles.redditmedia.com", "redditstatic.com", "icon", "/emote/"])
                and u not in seen
            ):
                seen.add(u)
                urls.append(u)

        # 1. Inspect 'media' array if provided
        media_field = post.get("media", [])
        if isinstance(media_field, list):
            for m in media_field:
                if isinstance(m, dict):
                    add_url(m.get("url"))
                elif isinstance(m, str):
                    add_url(m)

        # 2. Inspect media_metadata (Reddit galleries)
        media_meta = post.get("media_metadata")
        if isinstance(media_meta, dict):
            for v in media_meta.values():
                if isinstance(v, dict) and v.get("status") == "valid":
                    u = v.get("s", {}).get("u") or v.get("s", {}).get("gif")
                    add_url(u)

        # 3. Inspect preview images
        preview = post.get("preview")
        if isinstance(preview, dict):
            for img_obj in preview.get("images", []):
                add_url(img_obj.get("source", {}).get("url"))

        # 4. Inspect direct post url if it points to an image
        direct_url = post.get("url") or post.get("url_overridden_by_dest")
        if direct_url and any(direct_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]):
            add_url(direct_url)

        # 5. Check crosspost parent list
        crosspost_list = post.get("crosspost_parent_list")
        if isinstance(crosspost_list, list) and crosspost_list:
            parent = crosspost_list[0]
            if isinstance(parent, dict):
                p_meta = parent.get("media_metadata")
                if isinstance(p_meta, dict):
                    for v in p_meta.values():
                        if isinstance(v, dict) and v.get("status") == "valid":
                            add_url(v.get("s", {}).get("u") or v.get("s", {}).get("gif"))
                p_preview = parent.get("preview")
                if isinstance(p_preview, dict):
                    for img_obj in p_preview.get("images", []):
                        add_url(img_obj.get("source", {}).get("url"))
                p_direct = parent.get("url") or parent.get("url_overridden_by_dest")
                if p_direct and any(p_direct.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]):
                    add_url(p_direct)

        return urls

    async def _download_single_media(
        self,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        post_id: str,
        media_id: str,
        source_url: str,
        gallery_index: Optional[int],
        post_media_dir: Path,
    ) -> dict[str, Any]:
        """Download a single media asset, compute metadata, and save untouched bytes."""
        record: dict[str, Any] = {
            "media_id": media_id,
            "post_id": post_id,
            "source_url": source_url,
            "gallery_index": gallery_index,
            "download_status": "failed",
            "failure_reason": None,
            "local_path": None,
            "media_type": "image",
            "mime_type": None,
            "file_size_bytes": 0,
            "width": None,
            "height": None,
            "sha256": None,
            "downloaded_at": None,
            "attempted_at": datetime.now(timezone.utc).isoformat(),
        }

        async with semaphore:
            for attempt in range(3):
                try:
                    response = await client.get(source_url)
                    if response.status_code != 200:
                        record["download_status"] = "failed"
                        record["failure_reason"] = f"HTTP {response.status_code}"
                        if response.status_code in [403, 404, 410]:
                            break
                        await asyncio.sleep(1.0 * (attempt + 1))
                        continue

                    content = response.content
                    if len(content) > self.max_bytes:
                        record["download_status"] = "failed"
                        record["failure_reason"] = f"File size {len(content)} exceeds max limit {self.max_bytes}"
                        break

                    # Inspect MIME type and dimensions
                    mime_type, width, height, file_size = inspect_image(content)
                    if not mime_type:
                        mime_type = response.headers.get("content-type", "image/jpeg").split(";")[0].strip()

                    # Determine file extension safely
                    ext = ".jpg"
                    if mime_type:
                        if "png" in mime_type:
                            ext = ".png"
                        elif "webp" in mime_type:
                            ext = ".webp"
                        elif "gif" in mime_type:
                            ext = ".gif"
                            record["media_type"] = "gif"
                        elif "mp4" in mime_type or "video" in mime_type:
                            ext = ".mp4"
                            record["media_type"] = "video"

                    file_name = f"{media_id}{ext}"
                    local_dest = post_media_dir / file_name
                    local_dest.write_bytes(content)

                    # Checksum
                    sha256_hash = compute_sha256(content)

                    record["download_status"] = "success"
                    record["failure_reason"] = None
                    record["local_path"] = str(local_dest.relative_to(self.output_dir))
                    record["mime_type"] = mime_type
                    record["file_size_bytes"] = len(content)
                    record["width"] = width
                    record["height"] = height
                    record["sha256"] = sha256_hash
                    record["downloaded_at"] = datetime.now(timezone.utc).isoformat()
                    return record

                except httpx.TimeoutException:
                    record["download_status"] = "timeout"
                    record["failure_reason"] = "Connection / Read Timeout"
                    await asyncio.sleep(1.0 * (attempt + 1))
                except Exception as e:
                    record["download_status"] = "failed"
                    record["failure_reason"] = str(e)
                    await asyncio.sleep(1.0 * (attempt + 1))

        return record

    async def run_async(self) -> ValidationResult:
        """Run the full package generation workflow asynchronously."""
        start_time = datetime.now(timezone.utc)
        run_id = f"MEDIA-RUN-{uuid.uuid4().hex[:8].upper()}"

        logger.info(f"Reading raw dataset from: {self.input_json_path}")
        with open(self.input_json_path, "r", encoding="utf-8") as f:
            source_posts: list[dict[str, Any]] = json.load(f)

        # Prepare clean output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        posts_base_dir = self.output_dir / "posts"
        posts_base_dir.mkdir(parents=True, exist_ok=True)

        post_media_map: dict[str, Any] = {}
        all_download_tasks = []
        media_manifest_records: list[dict[str, Any]] = []

        timeout = httpx.Timeout(self.timeout_sec)
        headers = {"User-Agent": USER_AGENT, "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"}
        semaphore = asyncio.Semaphore(self.concurrency)

        async with httpx.AsyncClient(headers=headers, timeout=timeout, follow_redirects=True) as client:
            for idx, post in enumerate(source_posts):
                raw_pid = str(post.get("post_id") or "").strip()
                if not raw_pid or raw_pid == "unknown":
                    # Derive or fallback to index
                    raw_pid = f"post_{idx+1:03d}"
                post_id = re.sub(r"[^\w\-]", "_", raw_pid.replace("t3_", ""))

                # Setup directory
                post_dir = posts_base_dir / post_id
                media_dir = post_dir / "media"
                media_dir.mkdir(parents=True, exist_ok=True)

                urls = self._extract_media_urls(post)

                # Initialize post map entry
                post_media_map[post_id] = {
                    "media_count": 0,
                    "media_ids": [],
                    "media_paths": [],
                }

                # Schedule downloads
                for media_idx, url in enumerate(urls, 1):
                    media_id = f"MEDIA-{post_id}-{media_idx:03d}"
                    gallery_idx = media_idx if len(urls) > 1 else None
                    task = self._download_single_media(
                        client=client,
                        semaphore=semaphore,
                        post_id=post_id,
                        media_id=media_id,
                        source_url=url,
                        gallery_index=gallery_idx,
                        post_media_dir=media_dir,
                    )
                    all_download_tasks.append((post_id, media_id, task))

            logger.info(f"Downloading {len(all_download_tasks)} media assets concurrently (concurrency={self.concurrency})...")

            # Execute download tasks
            if all_download_tasks:
                results = await asyncio.gather(*(t[2] for t in all_download_tasks))
                for (post_id, media_id, _), record in zip(all_download_tasks, results, strict=True):
                    media_manifest_records.append(record)
                    if record.get("download_status") == "success":
                        post_media_map[post_id]["media_count"] += 1
                        post_media_map[post_id]["media_ids"].append(media_id)
                        post_media_map[post_id]["media_paths"].append(record["local_path"])

        # Write post_metadata.json for each post
        for idx, post in enumerate(source_posts):
            raw_pid = str(post.get("post_id") or "").strip()
            if not raw_pid or raw_pid == "unknown":
                raw_pid = f"post_{idx+1:03d}"
            post_id = re.sub(r"[^\w\-]", "_", raw_pid.replace("t3_", ""))

            post_meta = {
                "post_id": post_id,
                "reddit_url": post.get("post_url") or "",
                "subreddit": post.get("subreddit") or "",
                "title": post.get("title") or "",
                "body": post.get("body") or "",
                "author": post.get("author"),
                "created_at": post.get("created_at"),
                "score": post.get("score"),
                "num_comments": post.get("num_comments"),
                "media_count": post_media_map[post_id]["media_count"],
                "media_ids": post_media_map[post_id]["media_ids"],
            }
            meta_path = posts_base_dir / post_id / "post_metadata.json"
            meta_path.write_text(json.dumps(post_meta, indent=2, ensure_ascii=False), encoding="utf-8")

        # 1. Write media_manifest.jsonl
        media_manifest_path = self.output_dir / "media_manifest.jsonl"
        with open(media_manifest_path, "w", encoding="utf-8") as f:
            for rec in media_manifest_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        # 2. Write post_media_map.json
        post_media_map_path = self.output_dir / "post_media_map.json"
        with open(post_media_map_path, "w", encoding="utf-8") as f:
            json.dump(post_media_map, f, indent=2, ensure_ascii=False)

        # 3. Calculate statistics and write download_report.json
        end_time = datetime.now(timezone.utc)
        posts_total = len(source_posts)
        posts_with_media = sum(1 for p in post_media_map.values() if p["media_count"] > 0)
        posts_without_media = posts_total - posts_with_media
        total_urls = len(media_manifest_records)
        successful_downloads = sum(1 for r in media_manifest_records if r["download_status"] == "success")
        failed_downloads = sum(1 for r in media_manifest_records if r["download_status"] != "success")

        failure_breakdown: dict[str, int] = {}
        for r in media_manifest_records:
            if r["download_status"] != "success":
                reason = r.get("failure_reason") or "Unknown"
                failure_breakdown[reason] = failure_breakdown.get(reason, 0) + 1

        download_report = {
            "run_id": run_id,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "duration_seconds": round((end_time - start_time).total_seconds(), 2),
            "source_file": str(self.input_json_path.resolve()),
            "posts_total": posts_total,
            "posts_with_media": posts_with_media,
            "posts_without_media": posts_without_media,
            "media_urls_found": total_urls,
            "downloads_successful": successful_downloads,
            "downloads_failed": failed_downloads,
            "failure_breakdown": failure_breakdown,
        }
        download_report_path = self.output_dir / "download_report.json"
        with open(download_report_path, "w", encoding="utf-8") as f:
            json.dump(download_report, f, indent=2, ensure_ascii=False)

        # 4. Write manifest.json
        manifest_data = {
            "dataset_name": "TrustLens Reddit Multimodal Dataset",
            "version": "1.0.0",
            "run_id": run_id,
            "created_at": end_time.isoformat(),
            "posts_total": posts_total,
            "posts_with_media": posts_with_media,
            "posts_without_media": posts_without_media,
            "total_media_assets": successful_downloads,
            "failed_media_assets": failed_downloads,
            "structure": {
                "posts_dir": "posts/<post_id>/",
                "post_metadata": "posts/<post_id>/post_metadata.json",
                "media_dir": "posts/<post_id>/media/",
                "post_media_map": "post_media_map.json",
                "media_manifest": "media_manifest.jsonl",
                "download_report": "download_report.json",
            },
        }
        manifest_path = self.output_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)

        # 5. Write README.md
        self._write_readme(
            posts_total=posts_total,
            posts_with_media=posts_with_media,
            posts_without_media=posts_without_media,
            total_assets=successful_downloads,
            failed_assets=failed_downloads,
        )

        # 6. Validate the entire dataset using DatasetValidator
        logger.info("Running dataset integrity validation (Checks A through G)...")
        validator = DatasetValidator(dataset_dir=self.output_dir, source_posts=source_posts)
        validation_result = validator.validate()

        if not validation_result.is_valid:
            logger.error(f"Dataset validation failed with errors: {validation_result.errors}")
            return validation_result

        # 7. Package ZIP if requested
        if self.create_zip_file:
            logger.info(f"Creating ZIP archive at {self.zip_path}...")
            self._create_zip()

        return validation_result

    def _write_readme(
        self,
        posts_total: int,
        posts_with_media: int,
        posts_without_media: int,
        total_assets: int,
        failed_assets: int,
    ) -> None:
        """Write human-readable README.md explaining the multimodal package."""
        content = f"""# TrustLens Reddit Multimodal Evidence Dataset

## Dataset Summary
- **Total Reddit Posts:** {posts_total}
- **Posts With Media:** {posts_with_media}
- **Posts Without Media:** {posts_without_media}
- **Successfully Downloaded Media Assets:** {total_assets}
- **Failed Media Downloads:** {failed_assets}

---

## Directory Organization & Hierarchy

Every Reddit post in this archive maintains its own dedicated case folder inside `posts/`:

```text
trustlens_reddit_multimodal_dataset/
├── README.md                 # This document
├── manifest.json             # Dataset high-level metadata & summary
├── media_manifest.jsonl      # Machine-readable per-asset download log
├── post_media_map.json       # O(1) post_id -> media mapping
├── download_report.json      # Comprehensive download statistics & failure breakdown
└── posts/
    ├── <POST_ID>/
    │   ├── post_metadata.json # Post context (title, body, subreddit, author, media_ids)
    │   └── media/
    │       ├── MEDIA-<POST_ID>-001.jpg
    │       └── MEDIA-<POST_ID>-002.png
    └── ...
```

---

## Post-to-Media Mapping
The invariant relationship is strictly deterministic:
```text
post_id
    ↓
posts/<post_id>/post_metadata.json
    ↓
0, 1, or N media assets in posts/<post_id>/media/
    ↓
media_id: MEDIA-<post_id>-<001>.<ext>
```

For posts with zero media assets, the directory `posts/<post_id>/media/` exists intentionally as empty, and `post_metadata.json` clearly indicates `"media_count": 0, "media_ids": []`.

---

## Important Research & Integrity Notes
1. **Original Raw Data Remains Unchanged**: The source Reddit posts JSON was treated as strictly immutable raw data.
2. **Untouched Original Binary Assets**: Downloaded media files are original binary bytes without compression, resizing, watermarking, redaction, or format conversion.
3. **Traceability**: No media file exists detached from its parent Reddit `post_id`.
4. **Failure Transparency**: Any URL that failed to download is logged in `media_manifest.jsonl` with its HTTP status / error reason.
5. **Privacy & PII Warning**: Screenshots collected from Reddit contain real-world scam communications (WhatsApp chats, UPI IDs, phone numbers, merchant QR codes). Handle with research care according to ethical data guidelines.
"""
        readme_path = self.output_dir / "README.md"
        readme_path.write_text(content, encoding="utf-8")

    def _create_zip(self) -> None:
        """Create a clean ZIP archive of the dataset directory preserving internal paths."""
        self.zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(self.zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(self.output_dir):
                for file in files:
                    full_path = Path(root) / file
                    # Store relative to dataset root
                    rel_path = full_path.relative_to(self.output_dir)
                    archive_name = Path(self.output_dir.name) / rel_path
                    zf.write(full_path, arcname=str(archive_name))

    def print_summary(self, val_result: ValidationResult, report: dict[str, Any]) -> None:
        """Print the required Section 18 summary report."""
        images_count = report.get("downloads_successful", 0)
        zip_str = str(self.zip_path.name if self.create_zip_file else "None (skipped)")

        summary = f"""========================================
TRUSTLENS REDDIT MEDIA COLLECTION
========================================

Posts processed:        {report.get('posts_total', 0)}
Posts with media:       {report.get('posts_with_media', 0)}
Posts without media:    {report.get('posts_without_media', 0)}

Media URLs found:       {report.get('media_urls_found', 0)}
Successful downloads:   {report.get('downloads_successful', 0)}
Failed downloads:       {report.get('downloads_failed', 0)}

Images:                 {images_count}
Videos/GIFs:            0
Other:                  0

Exact duplicate files:  {val_result.duplicate_files_count}

Validation:
{chr(10).join('✓ ' + c for c in val_result.checks_passed)}

ZIP:
{zip_str}

Ready for Claude Web multimodal analysis.
========================================"""
        print(summary)


def run_media_collection(
    input_file: Path,
    output_dir: Path,
    concurrency: int = 5,
    timeout: int = 20,
    max_size_mb: int = 50,
    create_zip: bool = True,
    zip_path: Optional[Path] = None,
) -> ValidationResult:
    """Synchronous entrypoint to run the media packager."""
    packager = RedditMediaPackager(
        input_json_path=input_file,
        output_dir=output_dir,
        concurrency=concurrency,
        timeout_sec=timeout,
        max_size_mb=max_size_mb,
        create_zip=create_zip,
        zip_path=zip_path,
    )
    res = asyncio.run(packager.run_async())
    if res.is_valid:
        report_file = output_dir / "download_report.json"
        report_data = {}
        if report_file.exists():
            with open(report_file, "r", encoding="utf-8") as f:
                report_data = json.load(f)
        packager.print_summary(res, report_data)
    else:
        print("ERROR: Dataset validation failed:")
        for err in res.errors:
            print(f"  ✗ {err}")
    return res
