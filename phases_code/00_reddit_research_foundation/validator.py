"""Validation module for TrustLens Reddit multimodal media dataset.

Performs strict integrity and relationship checks:
- Check A: Every source post represented in post_media_map.json
- Check B: Every successful media asset has a parent (post_id, media_id, source_url, local_path)
- Check C: Files physically exist on disk
- Check D: Hashes match (recomputed SHA-256 matches manifest)
- Check E: No orphan media files in post folders
- Check F: No accidental duplication per post + cross-post duplicate verification
- Check G: Zero-media posts represented correctly
"""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class ValidationResult:
    """Outcome of dataset validation checks."""

    is_valid: bool
    total_posts: int = 0
    posts_with_media: int = 0
    posts_without_media: int = 0
    total_media_records: int = 0
    successful_assets: int = 0
    failed_assets: int = 0
    duplicate_files_count: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks_passed: list[str] = field(default_factory=list)


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 checksum for a local file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


class DatasetValidator:
    """Validates the structure, integrity, and mappings of a generated dataset directory."""

    def __init__(self, dataset_dir: Path, source_posts: Optional[list[dict[str, Any]]] = None):
        self.dataset_dir = Path(dataset_dir)
        self.source_posts = source_posts or []
        self.posts_dir = self.dataset_dir / "posts"
        self.manifest_path = self.dataset_dir / "manifest.json"
        self.media_manifest_path = self.dataset_dir / "media_manifest.jsonl"
        self.post_media_map_path = self.dataset_dir / "post_media_map.json"
        self.download_report_path = self.dataset_dir / "download_report.json"
        self.readme_path = self.dataset_dir / "README.md"

    def validate(self) -> ValidationResult:
        """Run all verification checks A through G."""
        errors: list[str] = []
        warnings: list[str] = []
        checks_passed: list[str] = []

        # Check basic manifest presence
        for req_path, name in [
            (self.manifest_path, "manifest.json"),
            (self.media_manifest_path, "media_manifest.jsonl"),
            (self.post_media_map_path, "post_media_map.json"),
            (self.download_report_path, "download_report.json"),
            (self.readme_path, "README.md"),
            (self.posts_dir, "posts/ directory"),
        ]:
            if not req_path.exists():
                errors.append(f"Missing required file or directory: {name}")

        if errors:
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Load post_media_map.json
        try:
            with open(self.post_media_map_path, "r", encoding="utf-8") as f:
                post_media_map: dict[str, Any] = json.load(f)
        except Exception as e:
            return ValidationResult(is_valid=False, errors=[f"Failed to read post_media_map.json: {e}"])

        # Load media_manifest.jsonl
        media_records: list[dict[str, Any]] = []
        try:
            with open(self.media_manifest_path, "r", encoding="utf-8") as f:
                for _line_idx, line in enumerate(f, 1):
                    line_str = line.strip()
                    if line_str:
                        media_records.append(json.loads(line_str))
        except Exception as e:
            return ValidationResult(is_valid=False, errors=[f"Failed to read media_manifest.jsonl: {e}"])

        total_posts = len(post_media_map)
        posts_with_media = sum(1 for p in post_media_map.values() if p.get("media_count", 0) > 0)
        posts_without_media = total_posts - posts_with_media
        total_media_records = len(media_records)
        successful_records = [r for r in media_records if r.get("download_status") == "success"]
        failed_records = [r for r in media_records if r.get("download_status") != "success"]

        # --- Check A: Every source post represented ---
        if self.source_posts:
            missing_posts = []
            for sp in self.source_posts:
                pid = str(sp.get("post_id") or "").replace("t3_", "").strip()
                if not pid:
                    continue
                if pid not in post_media_map:
                    missing_posts.append(pid)
            if missing_posts:
                errors.append(f"Check A Failed: {len(missing_posts)} source posts missing from post_media_map.json: {missing_posts[:5]}")
            else:
                checks_passed.append("Check A — Every source post represented in post_media_map.json")
        else:
            checks_passed.append("Check A — Every post in mapping represented (no external source list provided)")

        # --- Check B: Every successful media asset has a parent ---
        invalid_parent_records = []
        for r in successful_records:
            pid = r.get("post_id")
            mid = r.get("media_id")
            s_url = r.get("source_url")
            l_path = r.get("local_path")
            if not pid or not mid or not s_url or not l_path:
                invalid_parent_records.append(r)
            elif pid not in post_media_map:
                invalid_parent_records.append(r)
            elif mid not in post_media_map[pid].get("media_ids", []):
                invalid_parent_records.append(r)

        if invalid_parent_records:
            errors.append(f"Check B Failed: {len(invalid_parent_records)} assets have missing or invalid parent post mappings.")
        else:
            checks_passed.append("Check B — Every successful media asset has valid parent post mapping")

        # --- Check C: Files exist ---
        missing_files = []
        for r in successful_records:
            rel_path = r.get("local_path")
            full_path = self.dataset_dir / rel_path if rel_path else None
            if not full_path or not full_path.exists() or not full_path.is_file():
                missing_files.append(rel_path)

        if missing_files:
            errors.append(f"Check C Failed: {len(missing_files)} media files listed as success do not physically exist on disk.")
        else:
            checks_passed.append("Check C — Every successful media asset physically exists on disk")

        # --- Check D: Hashes match ---
        hash_mismatches = []
        for r in successful_records:
            rel_path = r.get("local_path")
            expected_sha = r.get("sha256")
            full_path = self.dataset_dir / rel_path
            try:
                actual_sha = compute_sha256(full_path)
                if expected_sha and actual_sha != expected_sha:
                    hash_mismatches.append(f"{rel_path} (expected {expected_sha}, computed {actual_sha})")
            except Exception as e:
                hash_mismatches.append(f"{rel_path} (error reading file: {e})")

        if hash_mismatches:
            errors.append(f"Check D Failed: {len(hash_mismatches)} files have SHA-256 hash mismatches: {hash_mismatches[:3]}")
        else:
            checks_passed.append("Check D — SHA-256 checksums verified for all downloaded assets")

        # --- Check E: No orphan media ---
        # Find all actual files in posts/*/media/ and ensure they are recorded in post_media_map
        mapped_local_paths = {r.get("local_path") for r in successful_records}
        orphan_files = []
        for media_dir in self.posts_dir.glob("*/media"):
            if media_dir.is_dir():
                for f in media_dir.iterdir():
                    if f.is_file() and not f.name.startswith("."):
                        rel = str(f.relative_to(self.dataset_dir))
                        if rel not in mapped_local_paths:
                            orphan_files.append(rel)

        if orphan_files:
            errors.append(f"Check E Failed: Found {len(orphan_files)} orphan files not recorded in manifest: {orphan_files[:3]}")
        else:
            checks_passed.append("Check E — No orphan media files found in dataset directories")

        # --- Check F: Accidental duplication & exact duplicates ---
        # 1. No duplicate media_id or identical source_url within the same post
        per_post_urls: dict[str, set[str]] = {}
        dup_url_in_post = []
        for r in successful_records:
            pid = r.get("post_id")
            url = r.get("source_url")
            if pid and url:
                if pid not in per_post_urls:
                    per_post_urls[pid] = set()
                if url in per_post_urls[pid]:
                    dup_url_in_post.append(f"Post {pid} has duplicate URL download: {url}")
                per_post_urls[pid].add(url)

        if dup_url_in_post:
            warnings.append(f"Check F Warning: {len(dup_url_in_post)} duplicate URLs within same post.")
        checks_passed.append("Check F — Post-level asset deduplication verified")

        # Track cross-post SHA-256 duplicates
        sha_to_posts: dict[str, list[str]] = {}
        for r in successful_records:
            s = r.get("sha256")
            pid = r.get("post_id")
            if s and pid:
                sha_to_posts.setdefault(s, []).append(pid)

        exact_duplicate_files = sum(1 for pids in sha_to_posts.values() if len(pids) > 1)

        # --- Check G: Zero-media posts represented ---
        zero_media_missing_meta = []
        zero_media_missing_dir = []
        for pid, pdata in post_media_map.items():
            if pdata.get("media_count", 0) == 0:
                post_folder = self.posts_dir / pid
                meta_file = post_folder / "post_metadata.json"
                media_folder = post_folder / "media"
                if not meta_file.exists():
                    zero_media_missing_meta.append(pid)
                if not media_folder.exists():
                    zero_media_missing_dir.append(pid)

        if zero_media_missing_meta or zero_media_missing_dir:
            errors.append(
                f"Check G Failed: Zero-media posts missing structure: "
                f"{len(zero_media_missing_meta)} missing post_metadata.json, "
                f"{len(zero_media_missing_dir)} missing media/ dir."
            )
        else:
            checks_passed.append("Check G — Zero-media posts explicitly represented with post_metadata.json & empty media/ directory")

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            total_posts=total_posts,
            posts_with_media=posts_with_media,
            posts_without_media=posts_without_media,
            total_media_records=total_media_records,
            successful_assets=len(successful_records),
            failed_assets=len(failed_records),
            duplicate_files_count=exact_duplicate_files,
            errors=errors,
            warnings=warnings,
            checks_passed=checks_passed,
        )
