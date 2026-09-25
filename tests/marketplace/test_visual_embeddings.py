"""Unit tests for Phase D DINOv2 Visual Embeddings & Dense Nearest-Neighbor Search."""

from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
import pytest

from trustlens.marketplace.visual_embeddings import DINOv2VisualEmbeddingEngine


def test_l2_normalization_and_exact_cosine():
    """Verify that normalized dot product computes exact cosine similarity."""
    dim = 384
    num_vecs = 50

    # Random synthetic vectors
    rng = np.random.default_rng(42)
    raw_vecs = rng.standard_normal((num_vecs, dim)).astype(np.float32)

    # L2 normalize
    norms = np.linalg.norm(raw_vecs, axis=1, keepdims=True)
    norm_vecs = raw_vecs / norms

    # Check norm == 1.0
    computed_norms = np.linalg.norm(norm_vecs, axis=1)
    np.testing.assert_allclose(computed_norms, 1.0, atol=1e-5)

    # Cosine matrix
    sim_matrix = norm_vecs @ norm_vecs.T
    # Diagonal should be ~1.0
    np.testing.assert_allclose(np.diag(sim_matrix), 1.0, atol=1e-5)


def test_query_nearest_neighbors_self_exclusion_and_ranking():
    """Verify top-k retrieval excludes self-match and ranks 1 to k monotonically."""
    dim = 384
    num_items = 15

    rng = np.random.default_rng(123)
    raw_vecs = rng.standard_normal((num_items, dim)).astype(np.float32)
    norms = np.linalg.norm(raw_vecs, axis=1, keepdims=True)
    norm_vecs = raw_vecs / norms

    # Mock embedding records
    records = []
    for i in range(num_items):
        records.append({
            "media_id": f"MED-{i:03d}",
            "file_id": f"FILE-{i:03d}",
            "listing_id": f"LST-{i % 5:03d}",  # 5 distinct listings
            "source_url": f"http://example.com/img{i}.webp",
            "local_path": f"/tmp/img{i}.webp",
            "sha256": f"sha256_{i}",
            "embedding": norm_vecs[i].tolist(),
        })

    engine = DINOv2VisualEmbeddingEngine()

    top_k = 5
    df_neighbors, df_relationships = engine.query_nearest_neighbors(
        norm_vecs, records, top_k=top_k
    )

    # Check neighbors shape and ranking
    assert len(df_neighbors) == num_items * top_k
    for q_mid, grp in df_neighbors.groupby("query_media_id"):
        assert len(grp) == top_k
        ranks = list(grp["rank"])
        assert ranks == list(range(1, top_k + 1))
        # Self should NEVER appear as neighbor
        assert q_mid not in list(grp["neighbor_media_id"])
        # Similarities must be sorted descending
        sims = list(grp["similarity"])
        assert sims == sorted(sims, reverse=True)


def test_pipeline_with_mock_embeddings():
    """Verify end-to-end Phase D artifacts and reports generation with synthetic images."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        vault_dir = tmp_path / "media"
        proc_dir = tmp_path / "processed"
        rep_dir = tmp_path / "reports"
        fig_dir = tmp_path / "figures"

        vault_dir.mkdir()
        proc_dir.mkdir()

        # Create dummy fingerprints.parquet
        mock_fps = [
            {
                "media_id": f"MED-{i}",
                "file_id": f"FID-{i}",
                "listing_id": f"LST-{i}",
                "source_url": f"http://example.com/{i}.webp",
                "local_path": None,  # Mocked
                "fingerprint_status": "available" if i < 10 else "unavailable",
                "sha256": f"sha_{i}",
                "phash": "0000000000000000",
                "dhash": "0000000000000000",
                "ahash": "0000000000000000",
                "width": 200,
                "height": 200,
            }
            for i in range(12)
        ]
        pd.DataFrame(mock_fps).to_parquet(proc_dir / "fingerprints.parquet", index=False)

        # Create mock normalized_listings.parquet
        mock_listings = [
            {"listing_id": f"LST-{i}", "city": "Delhi" if i % 2 == 0 else "Bengaluru", "price_amount": 50000.0 + i * 1000, "model": "iPhone 15", "category": "smartphones"}
            for i in range(12)
        ]
        pd.DataFrame(mock_listings).to_parquet(proc_dir / "normalized_listings.parquet", index=False)

        engine = DINOv2VisualEmbeddingEngine(
            media_vault_dir=vault_dir,
            processed_dir=proc_dir,
            reports_dir=rep_dir,
            figures_dir=fig_dir,
        )

        # Mock generate_embeddings to return synthetic vectors
        dim = 384
        num_avail = 10
        rng = np.random.default_rng(42)
        raw_vecs = rng.standard_normal((num_avail, dim)).astype(np.float32)
        norms = np.linalg.norm(raw_vecs, axis=1, keepdims=True)
        synthetic_embs = raw_vecs / norms

        synthetic_records = [
            {
                "media_id": f"MED-{i}",
                "file_id": f"FID-{i}",
                "listing_id": f"LST-{i}",
                "source_url": f"http://example.com/{i}.webp",
                "local_path": f"/tmp/{i}.webp",
                "width": 200,
                "height": 200,
                "sha256": f"sha_{i}",
                "model_name": "facebook/dinov2-small",
                "embedding_dim": 384,
                "embedding_dtype": "float32",
                "embedding_created_at": "2026-09-24T00:00:00",
                "embedding": synthetic_embs[i].tolist(),
            }
            for i in range(num_avail)
        ]

        engine.generate_embeddings = lambda df: (synthetic_embs, synthetic_records)

        res = engine.run_pipeline()

        assert res["images_embedded"] == 10
        assert res["embedding_dimension"] == 384
        assert res["vectors_indexed"] == 10
        assert res["total_nearest_neighbors_retrieved"] == 90  # 10 * 9 (since N=10, search_k=10)

        # Verify artifacts
        assert (proc_dir / "image_embeddings.parquet").exists()
        assert (proc_dir / "image_embeddings.npy").exists()
        assert (proc_dir / "visual_neighbors.parquet").exists()
        assert (proc_dir / "deep_visual_relationships.parquet").exists()
        assert (rep_dir / "DEEP_VISUAL_EMBEDDINGS.md").exists()
        assert (rep_dir / "visual_gallery.html").exists()
