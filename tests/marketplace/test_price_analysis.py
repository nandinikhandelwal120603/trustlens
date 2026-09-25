"""Unit tests for Phase B Price Analysis & Comparable Grouping Engine."""

from pathlib import Path
import tempfile
import pandas as pd
import pytest

from trustlens.marketplace.price_analysis import PriceAnalysisEngine


def test_price_analysis_pipeline_execution():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        proc_dir = tmp_path / "processed"
        rep_dir = tmp_path / "reports"
        fig_dir = tmp_path / "figures"
        nb_dir = tmp_path / "notebooks"

        proc_dir.mkdir()

        # Create mock listings.parquet with 10 comparable iPhone 15 items
        mock_data = []
        for i in range(10):
            mock_data.append({
                "listing_id": f"LST-{i:03d}",
                "source_url": f"https://olx.in/item/{i}",
                "first_seen_at": "2026-09-21T17:11:28Z",
                "last_seen_at": "2026-09-21T17:11:28Z",
                "observation_count": 1,
                "search_queries": "iphone",
                "category_ids": "1453",
                "raw_title": f"Apple iPhone 15 128GB Blue item {i}",
                "normalized_title": f"Apple iPhone 15 128GB Blue item {i}",
                "raw_price": "₹ 50,000" if i > 1 else "₹ 25,000",
                "price_amount": 50000.0 if i > 1 else 25000.0,
                "price_currency": "INR",
                "raw_location": "Bengaluru, Karnataka",
                "city": "Bengaluru",
                "state": "Karnataka",
                "country": "India",
                "geography_confidence": "high",
                "has_media": True,
                "media_count": 1,
                "badge_featured": False,
                "badge_verified": False,
                "badge_elite": False,
            })

        df_mock = pd.DataFrame(mock_data)
        df_mock.to_parquet(proc_dir / "listings.parquet", index=False)

        engine = PriceAnalysisEngine(
            processed_dir=proc_dir,
            reports_dir=rep_dir,
            figures_dir=fig_dir,
            notebooks_dir=nb_dir,
        )

        res = engine.run_pipeline()

        assert res["total_listings"] == 10
        assert res["valid_prices"] == 10
        assert "iPhone 15" in res["model_stats"]

        stats = res["model_stats"]["iPhone 15"]
        assert stats["count"] == 10
        assert stats["median"] == 50000.0

        # Check threshold evaluation (the two 25k items are 50% below 50k median)
        assert res["threshold_counts"]["le_35_pct"] == 2
        assert res["threshold_counts"]["le_50_pct"] == 2

        # Check generated artifacts
        assert (proc_dir / "normalized_listings.parquet").exists()
        assert (rep_dir / "PRODUCT_NORMALIZATION.md").exists()
        assert (rep_dir / "PRICE_ANALYSIS.md").exists()
        assert (fig_dir / "01_search_query_composition.png").exists()
        assert (fig_dir / "07_price_delta_threshold_analysis.png").exists()
        assert (nb_dir / "phase_b_product_price_analysis.ipynb").exists()
