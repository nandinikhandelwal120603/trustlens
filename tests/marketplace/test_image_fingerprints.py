"""Unit tests for Phase C Image Fingerprinting, Perceptual Matching & Clustering."""

from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
from PIL import Image
import pytest

from trustlens.marketplace.image_fingerprinting import (
    ImageFingerprintEngine,
    compute_hamming_distance,
)


def test_compute_hamming_distance():
    # Identical
    assert compute_hamming_distance("0000000000000000", "0000000000000000") == 0

    # 1 bit flip (0x1 = 0001)
    assert compute_hamming_distance("0000000000000000", "0000000000000001") == 1

    # Max difference for 64-bit hash (0x00...00 vs 0xFF...FF)
    assert compute_hamming_distance("0000000000000000", "ffffffffffffffff") == 64

    # Empty / malformed returns max distance
    assert compute_hamming_distance("", "ffffffffffffffff") == 64


def test_fingerprint_pipeline_execution():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        vault_dir = tmp_path / "media_vault"
        proc_dir = tmp_path / "processed"
        rep_dir = tmp_path / "reports"
        fig_dir = tmp_path / "figures"

        vault_dir.mkdir()
        proc_dir.mkdir()

        # Create two sample images (one exact duplicate, one slightly altered)
        img1 = Image.new("RGB", (200, 200), color=(255, 0, 0))
        img1.save(vault_dir / "file_1.webp")

        img2 = Image.new("RGB", (200, 200), color=(255, 0, 0))  # Identical to img1
        img2.save(vault_dir / "file_2.webp")

        img3 = Image.new("RGB", (200, 200), color=(0, 255, 0))  # Distinct image
        img3.save(vault_dir / "file_3.webp")

        # Mock media.parquet
        mock_media = [
            {"media_id": "MED-101-0", "listing_id": "LST-101", "file_id": "file_1", "source_url": "http://example.com/file_1", "gallery_index": 0},
            {"media_id": "MED-102-0", "listing_id": "LST-102", "file_id": "file_2", "source_url": "http://example.com/file_2", "gallery_index": 0},
            {"media_id": "MED-103-0", "listing_id": "LST-103", "file_id": "file_3", "source_url": "http://example.com/file_3", "gallery_index": 0},
        ]
        df_media = pd.DataFrame(mock_media)
        df_media.to_parquet(proc_dir / "media.parquet", index=False)

        # Mock normalized_listings.parquet
        mock_listings = [
            {"listing_id": "LST-101", "city": "Bengaluru", "price_amount": 50000.0, "model": "iPhone 15", "normalized_title": "iPhone 15"},
            {"listing_id": "LST-102", "city": "Mumbai", "price_amount": 35000.0, "model": "iPhone 15", "normalized_title": "iPhone 15"},
            {"listing_id": "LST-103", "city": "Delhi", "price_amount": 40000.0, "model": "iPhone 14", "normalized_title": "iPhone 14"},
        ]
        df_listings = pd.DataFrame(mock_listings)
        df_listings.to_parquet(proc_dir / "normalized_listings.parquet", index=False)

        engine = ImageFingerprintEngine(
            media_vault_dir=vault_dir,
            processed_dir=proc_dir,
            reports_dir=rep_dir,
            figures_dir=fig_dir,
        )

        res = engine.run_pipeline()

        assert res["total_media_records"] == 3
        assert res["fingerprints_available"] == 3
        assert res["exact_reuse_pairs_count"] == 1
        assert res["total_clusters_count"] >= 1

        # Check generated artifacts
        assert (proc_dir / "fingerprints.parquet").exists()
        assert (proc_dir / "image_relationships.parquet").exists()
        assert (proc_dir / "image_clusters.parquet").exists()
        assert (rep_dir / "IMAGE_FINGERPRINTING.md").exists()
        assert (fig_dir / "09_hamming_distance_distribution.png").exists()
        assert (fig_dir / "10_threshold_sensitivity_curve.png").exists()
