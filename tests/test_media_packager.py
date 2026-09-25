"""Unit and integration tests for Reddit Media Downloader and Dataset Packager."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from trustlens.media.media_packager import RedditMediaPackager
from trustlens.media.validator import DatasetValidator


@pytest.fixture
def sample_reddit_posts():
    return [
        {
            "source": "reddit",
            "subreddit": "IsThisAScamIndia",
            "post_id": "test_post_001",
            "post_url": "https://reddit.com/r/IsThisAScamIndia/comments/test_post_001",
            "title": "OLX phone scam with screenshots",
            "body": "Detailed scam report with 2 images.",
            "author": "victim1",
            "created_at": "2026-08-01T10:00:00Z",
            "score": 45,
            "num_comments": 12,
            "media": [
                {"type": "image", "url": "https://preview.redd.it/img1.jpg"},
                {"type": "image", "url": "https://preview.redd.it/img2.png"},
                {"type": "image", "url": "https://preview.redd.it/img1.jpg"},  # duplicate in post
            ],
        },
        {
            "source": "reddit",
            "subreddit": "IsThisAScamIndia",
            "post_id": "test_post_002",
            "post_url": "https://reddit.com/r/IsThisAScamIndia/comments/test_post_002",
            "title": "OLX scam discussion without images",
            "body": "No media attached to this text-only post.",
            "author": "victim2",
            "created_at": "2026-08-02T12:00:00Z",
            "score": 10,
            "num_comments": 3,
            "media": [],
        },
    ]


def test_extract_media_urls(sample_reddit_posts, tmp_path):
    packager = RedditMediaPackager(
        input_json_path=tmp_path / "dummy.json",
        output_dir=tmp_path / "output",
    )
    urls_p1 = packager._extract_media_urls(sample_reddit_posts[0])
    assert len(urls_p1) == 2  # Deduplicated from 3 to 2
    assert urls_p1 == [
        "https://preview.redd.it/img1.jpg",
        "https://preview.redd.it/img2.png",
    ]

    urls_p2 = packager._extract_media_urls(sample_reddit_posts[1])
    assert len(urls_p2) == 0


@pytest.mark.asyncio
async def test_full_packager_workflow(sample_reddit_posts, tmp_path):
    input_file = tmp_path / "input_posts.json"
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(sample_reddit_posts, f)

    output_dir = tmp_path / "trustlens_test_dataset"
    zip_path = tmp_path / "trustlens_test_dataset.zip"

    # Mock single image byte response
    fake_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\xff\xc0\x00\x11\x08\x00\x0a\x00\x0a\x03\x01"\
                b"\x22\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00"\
                b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xbf\x00\xff\xd9"

    class FakeResponse:
        status_code = 200
        content = fake_jpeg
        headers = {"content-type": "image/jpeg"}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = FakeResponse()

        packager = RedditMediaPackager(
            input_json_path=input_file,
            output_dir=output_dir,
            concurrency=2,
            create_zip=True,
            zip_path=zip_path,
        )

        result = await packager.run_async()
        assert result.is_valid is True
        assert result.total_posts == 2
        assert result.posts_with_media == 1
        assert result.posts_without_media == 1
        assert result.successful_assets == 2

        # Verify folder layout
        assert (output_dir / "manifest.json").exists()
        assert (output_dir / "media_manifest.jsonl").exists()
        assert (output_dir / "post_media_map.json").exists()
        assert (output_dir / "download_report.json").exists()
        assert (output_dir / "README.md").exists()
        assert zip_path.exists()

        # Check post 1
        p1_dir = output_dir / "posts" / "test_post_001"
        assert p1_dir.exists()
        assert (p1_dir / "post_metadata.json").exists()
        assert (p1_dir / "media" / "MEDIA-test_post_001-001.jpg").exists()
        assert (p1_dir / "media" / "MEDIA-test_post_001-002.jpg").exists()

        # Check post 2 (zero-media post)
        p2_dir = output_dir / "posts" / "test_post_002"
        assert p2_dir.exists()
        assert (p2_dir / "post_metadata.json").exists()
        assert (p2_dir / "media").exists()
        assert len(list((p2_dir / "media").iterdir())) == 0


def test_validator_fails_on_corrupt_data(tmp_path):
    output_dir = tmp_path / "corrupt_dataset"
    output_dir.mkdir(parents=True)
    posts_dir = output_dir / "posts" / "post_123" / "media"
    posts_dir.mkdir(parents=True)

    # Place an orphan file
    orphan = posts_dir / "MEDIA-post_123-001.jpg"
    orphan.write_bytes(b"hello")

    # Create dummy manifests without registering the file
    (output_dir / "manifest.json").write_text("{}", encoding="utf-8")
    (output_dir / "media_manifest.jsonl").write_text("", encoding="utf-8")
    (output_dir / "post_media_map.json").write_text('{"post_123": {"media_count": 0, "media_ids": [], "media_paths": []}}', encoding="utf-8")
    (output_dir / "download_report.json").write_text("{}", encoding="utf-8")
    (output_dir / "README.md").write_text("# Test", encoding="utf-8")

    validator = DatasetValidator(dataset_dir=output_dir)
    res = validator.validate()
    assert res.is_valid is False
    assert any("orphan" in err.lower() for err in res.errors)
