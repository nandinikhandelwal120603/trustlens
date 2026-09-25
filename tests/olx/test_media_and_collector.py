"""
Unit tests for OLX Media Manager, Collector, and Report Generator (Phase 3).
"""

import asyncio
import hashlib
from pathlib import Path
import pytest
from trustlens.olx.collector import OLXCollector
from trustlens.olx.media import OLXMediaManager
from trustlens.olx.models import OLXMedia
from trustlens.olx.report import InvestigationReportGenerator


def test_media_manifest_and_duplicate_detection(tmp_path: Path):
    media_dir = tmp_path / "media"
    manager = OLXMediaManager(media_dir)

    # Fake media items with SHA collisions
    m1 = OLXMedia(
        media_id="MEDIA-001",
        listing_id="OLX-001",
        source_url="https://example.com/img1.jpg",
        sha256="aaaabbbbccccdddd1111222233334444",
        download_status="success",
    )
    m2 = OLXMedia(
        media_id="MEDIA-002",
        listing_id="OLX-002",
        source_url="https://example.com/img2.jpg",
        sha256="aaaabbbbccccdddd1111222233334444",  # duplicate SHA
        download_status="success",
    )
    m3 = OLXMedia(
        media_id="MEDIA-003",
        listing_id="OLX-003",
        source_url="https://example.com/img3.jpg",
        sha256="eeeeffff000011112222333344445555",
        download_status="success",
    )

    manager.append_to_manifest([m1, m2, m3])
    dups = manager.update_duplicate_groups()

    assert len(dups) == 1
    assert "aaaabbbbccccdddd1111222233334444" in dups
    assert len(dups["aaaabbbbccccdddd1111222233334444"]) == 2


def test_researcher_assisted_html_collector_ingest(tmp_path: Path):
    html_content = """
    <html>
    <head><title>Sony PS5 Disc Edition 825GB | OLX</title></head>
    <body>
        <div data-aut-id="itemDescription">Urgent sale. WhatsApp on 9988776655 for booking token.</div>
        <div data-aut-id="itemLocation">South Delhi</div>
    </body>
    </html>
    """
    html_file = tmp_path / "ps5_sample.html"
    html_file.write_text(html_content, encoding="utf-8")

    collector = OLXCollector(base_dir=tmp_path / "data")
    inv = asyncio.run(
        collector.ingest_html_file(
            file_path=html_file,
            source_url="https://www.olx.in/item/ps5-disc-iid-991122",
            investigation_id="INV-002",
            download_media=False,
        )
    )

    assert inv.listing.listing_id == "OLX-000001"
    assert inv.investigation_id == "INV-OLX-000001"
    assert "Sony PS5 Disc Edition" in inv.listing.title
    assert len(inv.signals) >= 1
    assert any(s.signal_type == "whatsapp_migration" for s in inv.signals)

    # Verify Report Generation
    report_md = InvestigationReportGenerator.generate_report(inv)
    assert "# TRUSTLENS INVESTIGATION REPORT" in report_md
    assert "INV-OLX-000001" in report_md
    assert "SCAM SCORE" not in report_md  # Adheres to no-accusation principle
    assert "NOTICE" in report_md
