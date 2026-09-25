"""Unit tests for media fingerprinting and hash computation."""

import io
from PIL import Image
from trustlens.marketplace.media_fingerprint import MediaFingerprinter
from trustlens.marketplace.models import DownloadStatus, FingerprintStatus


def create_test_image(color=(255, 0, 0), size=(100, 100)) -> bytes:
    """Helper to generate in-memory image bytes."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_sha256_exact_match():
    bytes1 = create_test_image((255, 0, 0), (100, 100))
    bytes2 = create_test_image((255, 0, 0), (100, 100))
    bytes_diff = create_test_image((0, 255, 0), (100, 100))

    sha1 = MediaFingerprinter.compute_sha256(bytes1)
    sha2 = MediaFingerprinter.compute_sha256(bytes2)
    sha_diff = MediaFingerprinter.compute_sha256(bytes_diff)

    assert sha1 == sha2
    assert sha1 != sha_diff


def test_perceptual_hashes_resizing():
    # Same visual content at different resolutions
    bytes_large = create_test_image((120, 50, 200), (400, 400))
    bytes_small = create_test_image((120, 50, 200), (100, 100))

    phash_l, dhash_l, ahash_l, w_l, h_l = MediaFingerprinter.compute_perceptual_hashes(bytes_large)
    phash_s, dhash_s, ahash_s, w_s, h_s = MediaFingerprinter.compute_perceptual_hashes(bytes_small)

    assert phash_l is not None and phash_s is not None
    assert phash_l == phash_s
    assert dhash_l == dhash_s
    assert ahash_l == ahash_s
    assert w_l == 400 and w_s == 100


def test_fingerprint_media_with_bytes():
    content = create_test_image((0, 0, 255), (150, 150))
    fp = MediaFingerprinter.fingerprint_media(
        media_id="MED-001",
        listing_id="OLX-001",
        source_url="https://apollo.olx.in/v1/files/img1/image",
        content_bytes=content,
    )

    assert fp.media_id == "MED-001"
    assert fp.listing_id == "OLX-001"
    assert fp.download_status == DownloadStatus.DOWNLOADED
    assert fp.fingerprint_status == FingerprintStatus.COMPUTED
    assert fp.sha256 is not None
    assert fp.phash is not None
    assert fp.dhash is not None
    assert fp.ahash is not None
    assert fp.width == 150
    assert fp.height == 150


def test_fingerprint_media_without_bytes_no_fabrication():
    # When bytes are not present, do NOT invent hashes
    fp = MediaFingerprinter.fingerprint_media(
        media_id="MED-002",
        listing_id="OLX-002",
        source_url="https://apollo.olx.in/v1/files/img2/image",
        content_bytes=None,
    )

    assert fp.media_id == "MED-002"
    assert fp.download_status == DownloadStatus.NOT_ATTEMPTED
    assert fp.fingerprint_status == FingerprintStatus.UNAVAILABLE
    assert fp.sha256 is None
    assert fp.phash is None
    assert fp.dhash is None
    assert fp.ahash is None
    assert fp.width is None
    assert fp.height is None
