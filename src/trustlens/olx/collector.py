"""
TrustLens — Targeted OLX Acquisition & Investigation Collector (Phase 3).
"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import httpx

from trustlens.config.settings import settings
from trustlens.olx.config import get_investigation_config
from trustlens.olx.evidence import EvidenceLinker
from trustlens.olx.media import OLXMediaManager
from trustlens.olx.models import (
    CollectionMethod,
    CollectionType,
    DiscoveryContext,
    OLXCollectionMetadata,
    OLXCollectionRun,
    OLXInvestigation,
    OLXListing,
)
from trustlens.olx.parser import OLXParser
from trustlens.olx.report import InvestigationReportGenerator
from trustlens.olx.signals import SignalDetector
from trustlens.olx.verification import VerificationEngine
from trustlens.utils.logging import logger


class OLXCollector:
    """End-to-end acquisition & investigation pipeline for OLX marketplace."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or (settings.data_dir / "olx_pilot")
        self.raw_dir = self.base_dir / "raw"
        self.norm_dir = self.base_dir / "normalized"
        self.media_dir = self.base_dir / "media"
        self.inv_dir = self.base_dir / "investigations"
        self.reports_dir = self.base_dir / "reports"

        for d in [self.raw_dir, self.norm_dir, self.media_dir, self.inv_dir, self.reports_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.media_manager = OLXMediaManager(self.media_dir)
        self.listings_file = self.norm_dir / "olx_listings.jsonl"
        self.sellers_file = self.norm_dir / "olx_sellers.jsonl"
        self.runs_file = self.base_dir / "olx_collection_runs.jsonl"
        self.failures_file = self.base_dir / "olx_failures.jsonl"

    async def fetch_page(self, url: str, timeout: float = 15.0) -> Tuple[str, int]:
        """Retrieve web page content via httpx client with fallback headers."""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
            resp = await client.get(url)
            return resp.text, resp.status_code

    async def ingest_url(
        self,
        url: str,
        investigation_id: str = "INV-002",
        collection_type: CollectionType = CollectionType.TARGETED,
        download_media: bool = True,
        discovery_context: Optional[DiscoveryContext] = None,
        run_id: Optional[str] = None,
    ) -> OLXInvestigation:
        """Fetch, parse, analyze, and persist a single OLX listing URL."""
        logger.info(f"Ingesting OLX listing URL: {url}")
        content, status_code = await self.fetch_page(url)

        if status_code != 200 or not content:
            self._record_failure(url, f"HTTP status {status_code}", run_id)
            raise ValueError(f"Failed to fetch OLX listing (HTTP {status_code})")

        return await self._process_listing_content(
            content=content,
            url=url,
            investigation_id=investigation_id,
            collection_type=collection_type,
            method=CollectionMethod.HTTP_CLIENT,
            download_media=download_media,
            discovery_context=discovery_context,
            run_id=run_id,
        )

    async def ingest_html_file(
        self,
        file_path: Path,
        source_url: str = "https://www.olx.in/item/saved-researcher-page",
        investigation_id: str = "INV-002",
        collection_type: CollectionType = CollectionType.TARGETED,
        download_media: bool = False,
    ) -> OLXInvestigation:
        """Ingest saved researcher HTML file (fallback mode)."""
        logger.info(f"Ingesting saved HTML file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return await self._process_listing_content(
            content=content,
            url=source_url,
            investigation_id=investigation_id,
            collection_type=collection_type,
            method=CollectionMethod.RESEARCHER_ASSISTED,
            download_media=download_media,
            discovery_context=DiscoveryContext(
                investigation_id=investigation_id,
                query="manual_researcher_upload",
            ),
        )

    async def _process_listing_content(
        self,
        content: str,
        url: str,
        investigation_id: str,
        collection_type: CollectionType,
        method: CollectionMethod,
        download_media: bool,
        discovery_context: Optional[DiscoveryContext],
        run_id: Optional[str] = None,
    ) -> OLXInvestigation:
        """Internal processing pipeline: parse -> media -> signals -> evidence -> report."""
        # Determine deterministic index
        existing_count = 0
        if self.listings_file.exists():
            with open(self.listings_file, "r", encoding="utf-8") as f:
                existing_count = sum(1 for line in f if line.strip())

        listing = OLXParser.parse_listing_page(
            content=content,
            url=url,
            investigation_id=investigation_id,
            collection_type=collection_type,
            discovery_context=discovery_context,
            listing_index=existing_count + 1,
        )

        listing.collection_metadata = OLXCollectionMetadata(
            source="olx",
            collection_method=method,
            discovered_via="targeted_suite" if collection_type == CollectionType.TARGETED else "baseline",
            run_id=run_id,
            collected_at=datetime.now(timezone.utc),
        )

        # Save immutable raw content
        raw_run_dir = self.raw_dir / (run_id or "adhoc")
        raw_run_dir.mkdir(parents=True, exist_ok=True)
        raw_file = raw_run_dir / f"{listing.listing_id}.html"
        with open(raw_file, "w", encoding="utf-8") as f:
            f.write(content)

        # Download media if requested
        if download_media and listing.media:
            downloaded_media = await self.media_manager.download_listing_media_batch(listing.media)
            listing.media = downloaded_media
            self.media_manager.append_to_manifest(downloaded_media)
            self.media_manager.update_duplicate_groups()

        # Signal Detection
        signals, uncertainties = SignalDetector.detect_signals(listing)

        # Evidence Linking
        evidence, signals = EvidenceLinker.link_evidence(listing, signals)

        # Verification Formulations
        verification_checks, next_steps = VerificationEngine.run_checks(listing)

        # Build Investigation Instance
        investigation = OLXInvestigation(
            investigation_id=f"INV-{listing.listing_id}",
            source="olx",
            listing=listing,
            seller=listing.seller,
            claims=listing.claims,
            media=listing.media,
            signals=signals,
            evidence=evidence,
            verification_checks=verification_checks,
            uncertainties=uncertainties,
            next_steps=next_steps,
        )

        # Persist normalized listings & sellers
        with open(self.listings_file, "a", encoding="utf-8") as f:
            f.write(listing.model_dump_json() + "\n")

        with open(self.sellers_file, "a", encoding="utf-8") as f:
            f.write(listing.seller.model_dump_json() + "\n")

        # Persist structured investigation JSON
        inv_file = self.inv_dir / f"{investigation.investigation_id}.json"
        with open(inv_file, "w", encoding="utf-8") as f:
            f.write(investigation.model_dump_json(indent=2))

        # Generate & save human-readable report
        report_text = InvestigationReportGenerator.generate_report(investigation)
        report_file = self.reports_dir / f"{investigation.investigation_id}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_text)

        logger.info(f"Processed investigation {investigation.investigation_id} for listing {listing.listing_id}")
        return investigation

    async def discover_and_collect_query(
        self,
        investigation_id: str,
        query: str,
        collection_type: CollectionType = CollectionType.TARGETED,
        limit: int = 10,
        location: str = "india",
        run_id: Optional[str] = None,
        download_media: bool = True,
    ) -> OLXCollectionRun:
        """Execute search discovery and collection for a single search query."""
        run_id = run_id or f"OLX-RUN-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        loc_path = f"{location.lower().strip()}/" if location and location.lower() != "all" else "items/"
        search_url = f"https://www.olx.in/{loc_path}q-{query.replace(' ', '-')}"

        run_record = OLXCollectionRun(
            run_id=run_id,
            investigation_id=investigation_id,
            query=query,
            collection_type=collection_type,
            search_url=search_url,
            start_time=datetime.now(timezone.utc),
        )

        try:
            content, status = await self.fetch_page(search_url)
            discovered = OLXParser.parse_search_results(content, search_url=search_url)
            run_record.discovered_count = len(discovered)

            logger.info(f"Discovered {len(discovered)} listings for query '{query}' (limit: {limit})")

            for item in discovered[:limit]:
                i_url = item.get("url")
                if not i_url:
                    continue
                try:
                    inv = await self.ingest_url(
                        url=i_url,
                        investigation_id=investigation_id,
                        collection_type=collection_type,
                        download_media=download_media,
                        discovery_context=DiscoveryContext(
                            investigation_id=investigation_id,
                            query=query,
                            search_url=search_url,
                            run_id=run_id,
                        ),
                        run_id=run_id,
                    )
                    run_record.collected_count += 1
                    run_record.listing_ids.append(inv.listing.listing_id)
                except Exception as e:
                    run_record.failed_count += 1
                    run_record.failure_reasons.append({"url": i_url, "error": str(e)[:100]})

        except Exception as e:
            run_record.failure_reasons.append({"search_url": search_url, "error": str(e)})

        run_record.end_time = datetime.now(timezone.utc)
        self._record_run(run_record)
        return run_record

    async def run_investigation_suite(
        self,
        investigation_id: str,
        max_results_per_query: int = 5,
        location: str = "india",
        download_media: bool = True,
    ) -> List[OLXCollectionRun]:
        """Execute full targeted investigation suite across all target & baseline queries."""
        config = get_investigation_config(investigation_id)
        suite_runs: List[OLXCollectionRun] = []
        batch_id = f"OLX-SUITE-{investigation_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        logger.info(f"Launching investigation suite {investigation_id} ({config.name}) in location: {location}")

        # 1. Target Queries
        for q in config.target_queries:
            run = await self.discover_and_collect_query(
                investigation_id=investigation_id,
                query=q,
                collection_type=CollectionType.TARGETED,
                limit=max_results_per_query,
                location=location,
                run_id=f"{batch_id}-TGT",
                download_media=download_media,
            )
            suite_runs.append(run)

        # 2. Baseline Queries
        for q in config.baseline_queries:
            run = await self.discover_and_collect_query(
                investigation_id=investigation_id,
                query=q,
                collection_type=CollectionType.BASELINE,
                limit=max_results_per_query,
                location=location,
                run_id=f"{batch_id}-BASE",
                download_media=download_media,
            )
            suite_runs.append(run)

        return suite_runs

    def _record_run(self, run: OLXCollectionRun):
        """Append run record to olx_collection_runs.jsonl."""
        with open(self.runs_file, "a", encoding="utf-8") as f:
            f.write(run.model_dump_json() + "\n")

    def _record_failure(self, url: str, reason: str, run_id: Optional[str]):
        """Append failure entry to olx_failures.jsonl."""
        with open(self.failures_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "url": url,
                "reason": reason,
                "run_id": run_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }) + "\n")
