"""Marketplace Ingestion Engine."""

import json
import uuid
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from trustlens.marketplace.cluster import RelationalClusterManager
from trustlens.marketplace.evidence import EvidenceRelationshipManager
from trustlens.marketplace.media_fingerprint import MediaFingerprinter
from trustlens.marketplace.media_index import MarketplaceObservationIndex
from trustlens.marketplace.models import (
    DownloadStatus,
    IngestionReport,
    MatchType,
    MediaFingerprint,
    RelationshipType,
    SimilarityThresholds,
)
from trustlens.marketplace.orm_models import (
    MarketplaceObservationORM,
)
from trustlens.marketplace.text_normalizer import TextNormalizer
from trustlens.storage.database import SessionLocal, init_db
from trustlens.storage.orm_models import CaseORM, ListingORM, MediaORM


class MarketplaceIngestionEngine:
    """Ingests capture-olx extension JSON files into local marketplace observation index."""

    def __init__(
        self,
        session: Optional[Session] = None,
        thresholds: Optional[SimilarityThresholds] = None,
        download_media: bool = False,
    ):
        self._external_session = session is not None
        self.session = session or SessionLocal()
        self.thresholds = thresholds or SimilarityThresholds()
        self.download_media = download_media

        self.index = MarketplaceObservationIndex(self.session)
        self.cluster_mgr = RelationalClusterManager(self.session)
        self.evidence_mgr = EvidenceRelationshipManager(self.session)

    def close(self):
        if not self._external_session and self.session:
            self.session.close()

    def ingest_file(self, file_path: Union[str, Path]) -> IngestionReport:
        """Ingest a capture-olx exported JSON file."""
        init_db()
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Capture file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return self.ingest_data(data)

    def ingest_data(self, data: Dict[str, Any]) -> IngestionReport:
        """Ingest structured capture JSON payload."""
        init_db()
        captures = data.get("captures", [])
        if not captures and "listings" in data:
            # Single envelope passed directly
            captures = [data]

        report = IngestionReport(
            capture_id=data.get("captures", [{}])[0].get("capture_id", f"cap-{uuid.uuid4().hex[:8]}") if captures else "unknown",
            source_url=data.get("captures", [{}])[0].get("source_url") if captures else None,
            search_query=data.get("captures", [{}])[0].get("capture_context", {}).get("search_query") if captures else None,
        )

        # Ensure a default Case exists for marketplace observations
        default_case = self.session.get(CaseORM, "CASE-MARKETPLACE")
        if not default_case:
            default_case = CaseORM(
                case_id="CASE-MARKETPLACE",
                status="active",
                source="olx",
                labels=["marketplace_observation"],
                metadata_={"description": "Global marketplace observation index"},
            )
            self.session.add(default_case)
            self.session.flush()

        for cap in captures:
            ctx = cap.get("capture_context", {})
            capture_id = cap.get("capture_id") or f"cap-{uuid.uuid4().hex[:8]}"
            source_url = cap.get("source_url")
            search_query = ctx.get("search_query")
            category_id = ctx.get("category_id")
            collection_type = cap.get("page_type") or "search_capture"
            
            raw_captured_at = cap.get("captured_at")
            if raw_captured_at:
                try:
                    captured_at = datetime.fromisoformat(raw_captured_at.replace("Z", "+00:00"))
                except Exception:
                    captured_at = datetime.now(timezone.utc)
            else:
                captured_at = datetime.now(timezone.utc)

            for item in cap.get("listings", []):
                report.listings_observed += 1
                listing_res = self._ingest_single_listing(
                    item=item,
                    capture_id=capture_id,
                    source_url=source_url,
                    search_query=search_query,
                    category_id=category_id,
                    collection_type=collection_type,
                    captured_at=captured_at,
                    report=report,
                )

        self.session.commit()
        return report

    def _ingest_single_listing(
        self,
        item: Dict[str, Any],
        capture_id: str,
        source_url: Optional[str],
        search_query: Optional[str],
        category_id: Optional[str],
        collection_type: str,
        captured_at: datetime,
        report: IngestionReport,
    ) -> str:
        """Process and persist a single listing, its media, and relationships."""
        source_listing_id = str(item.get("listing_id") or "").strip()
        item_source_url = item.get("source_url") or source_url or ""
        canonical_listing_id = f"OLX-{source_listing_id}" if source_listing_id else f"OLX-{uuid.uuid4().hex[:8]}"

        raw_data = item.get("raw", {})
        norm_data = item.get("normalized", {})

        title_raw = norm_data.get("title") or raw_data.get("title") or "OLX Listing"
        norm_title = TextNormalizer.normalize_text(title_raw)

        price_amount = None
        if "price" in norm_data and isinstance(norm_data["price"], dict):
            price_amount = norm_data["price"].get("amount")
        elif "price" in norm_data and isinstance(norm_data["price"], (int, float)):
            price_amount = float(norm_data["price"])

        location_str = norm_data.get("location") or raw_data.get("location")

        # 1. Record Provenance in marketplace_observations
        obs_id = f"OBS-{uuid.uuid4().hex[:12].upper()}"
        self.session.add(
            MarketplaceObservationORM(
                observation_id=obs_id,
                listing_id=canonical_listing_id,
                source="olx",
                source_url=item_source_url,
                search_query=search_query,
                category_id=category_id,
                investigation_id="INV-002",
                capture_id=capture_id,
                collection_type=collection_type,
                captured_at=captured_at,
                recorded_at=datetime.now(timezone.utc),
                metadata_={"badges": item.get("badges", {}), "contact_actions": item.get("contact_actions", {})},
            )
        )

        # 2. Idempotent ListingORM creation or temporal update
        existing_listing = self.session.get(ListingORM, canonical_listing_id)
        if existing_listing:
            report.existing_listings_updated += 1
            existing_listing.updated_at = captured_at
            # Update observation count in lineage metadata
            meta = dict(existing_listing.collection_metadata or {})
            meta["observation_count"] = meta.get("observation_count", 1) + 1
            meta["last_seen_at"] = captured_at.isoformat()
            existing_listing.collection_metadata = meta
        else:
            report.new_listings += 1
            new_listing = ListingORM(
                listing_id=canonical_listing_id,
                case_id="CASE-MARKETPLACE",
                source="olx",
                source_listing_id=source_listing_id,
                source_url=item_source_url,
                raw_title=title_raw,
                normalized_title=norm_title,
                raw_description=item.get("description", {}).get("text"),
                normalized_description=item.get("description", {}).get("text"),
                category="mobile-phones" if category_id == "1453" else "marketplace",
                raw_price=price_amount,
                normalized_price=price_amount,
                location_raw=location_str,
                posted_at=captured_at,
                collected_at=captured_at,
                is_synthetic=False,
                collection_metadata={
                    "first_seen_at": captured_at.isoformat(),
                    "last_seen_at": captured_at.isoformat(),
                    "observation_count": 1,
                    "search_query": search_query,
                },
            )
            self.session.add(new_listing)

        self.session.flush()

        # 3. Check Text Reuse (Exact normalized title and token overlap)
        text_matches = self.index.find_text_reuse(
            current_listing_id=canonical_listing_id,
            current_title=title_raw,
            threshold=self.thresholds.text_jaccard_threshold,
        )
        for matched_lid, matched_title, jaccard_score, is_exact in text_matches:
            rel_type = RelationshipType.SAME_TITLE if is_exact else RelationshipType.SIMILAR_DESCRIPTION
            if is_exact:
                report.exact_title_reuse_count += 1
            else:
                report.similar_title_count += 1

            self.evidence_mgr.record_relationship(
                listing_a=canonical_listing_id,
                listing_b=matched_lid,
                relationship_type=rel_type,
                evidence_data={
                    "current_title": title_raw,
                    "matched_title": matched_title,
                    "jaccard_similarity": round(jaccard_score, 3),
                    "is_exact_match": is_exact,
                },
                timestamp=captured_at,
            )
            report.relationships_recorded += 1

        # 4. Media Processing & Fingerprinting
        for idx, m_item in enumerate(item.get("media", [])):
            report.images_observed += 1
            src_url = m_item.get("src")
            file_id = m_item.get("file_id") or f"{canonical_listing_id}-{idx}"
            media_id = f"MED-{file_id}"

            content_bytes: Optional[bytes] = None
            local_path: Optional[str] = m_item.get("local_path")

            # If download requested and src_url is available
            if self.download_media and src_url and not content_bytes and not local_path:
                try:
                    req = urllib.request.Request(
                        src_url,
                        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
                    )
                    with urllib.request.urlopen(req, timeout=5) as response:
                        content_bytes = response.read()
                except Exception as dl_err:
                    # Non-fatal; recording download status failed
                    pass

            # Fingerprint media
            fp = MediaFingerprinter.fingerprint_media(
                media_id=media_id,
                listing_id=canonical_listing_id,
                source_url=src_url,
                local_path=local_path,
                content_bytes=content_bytes,
            )

            # Persist MediaORM if new
            existing_media = self.session.get(MediaORM, media_id)
            if not existing_media:
                self.session.add(
                    MediaORM(
                        media_id=media_id,
                        listing_id=canonical_listing_id,
                        source_url=src_url,
                        local_path=fp.local_path,
                        sha256=fp.sha256,
                        perceptual_hash=fp.phash,
                        file_size=fp.file_size,
                        width=fp.width,
                        height=fp.height,
                        mime_type=fp.mime_type,
                        collection_timestamp=captured_at,
                        metadata_={"gallery_index": m_item.get("gallery_index", idx)},
                    )
                )

            # Upsert fingerprint into observation index
            self.index.upsert_fingerprint(fp)

            if fp.fingerprint_status.value == "computed":
                report.images_fingerprinted += 1

                # Match against index
                matches = self.index.compare_and_match(fp, thresholds=self.thresholds)
                for match in matches:
                    if match.match_type == MatchType.EXACT_SHA256:
                        report.exact_image_matches += 1
                    else:
                        report.perceptual_candidate_matches += 1

                    # Update relational cluster
                    cluster_id = self.cluster_mgr.add_match_to_clusters(
                        media_a=match.media_a,
                        media_b=match.media_b,
                        listing_a=match.listing_a,
                        listing_b=match.listing_b,
                        timestamp=captured_at,
                    )
                    report.clusters_updated += 1

                    # Record Evidence Relationship
                    rel_type = (
                        RelationshipType.SAME_IMAGE
                        if match.match_type == MatchType.EXACT_SHA256
                        else RelationshipType.SIMILAR_IMAGE
                    )
                    self.evidence_mgr.record_relationship(
                        listing_a=match.listing_a,
                        listing_b=match.listing_b,
                        relationship_type=rel_type,
                        evidence_data={
                            "media_a": match.media_a,
                            "media_b": match.media_b,
                            "match_type": match.match_type.value,
                            "sha256_match": match.sha256_match,
                            "phash_distance": match.phash_distance,
                            "dhash_distance": match.dhash_distance,
                            "ahash_distance": match.ahash_distance,
                            "cluster_id": cluster_id,
                        },
                        timestamp=captured_at,
                    )
                    report.relationships_recorded += 1

                    report.detailed_matches.append(
                        {
                            "match_id": match.match_id,
                            "listing_a": match.listing_a,
                            "listing_b": match.listing_b,
                            "media_a": match.media_a,
                            "media_b": match.media_b,
                            "match_type": match.match_type.value,
                            "phash_distance": match.phash_distance,
                            "dhash_distance": match.dhash_distance,
                            "cluster_id": cluster_id,
                        }
                    )

        return canonical_listing_id
