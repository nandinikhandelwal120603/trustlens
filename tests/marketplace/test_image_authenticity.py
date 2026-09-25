"""Unit and integration tests for Phase G Image Authenticity, Provenance & Forensics."""

from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
import pytest

from trustlens.marketplace.image_authenticity import ImageAuthenticityEngine


def test_c2pa_inspection_clean():
    """Verify C2PA provenance detection on binary headers."""
    with tempfile.NamedTemporaryFile(suffix=".webp") as tmp:
        tmp.write(b"RIFF\x00\x00\x00\x00WEBPVP8 \x00\x00\x00\x00clean_image_data")
        tmp.flush()
        res = ImageAuthenticityEngine.inspect_c2pa_provenance(Path(tmp.name))

        assert res["c2pa_present"] is False
        assert res["c2pa_status"] == "ABSENT"
        assert res["provenance_status"] == "ABSENT"


def test_c2pa_inspection_with_marker():
    """Verify C2PA detection when container box is present."""
    with tempfile.NamedTemporaryFile(suffix=".webp") as tmp:
        tmp.write(b"RIFF\x00\x00\x00\x00WEBPVP8 \x00\x00\x00\x00c2pa_manifest_jumb_box")
        tmp.flush()
        res = ImageAuthenticityEngine.inspect_c2pa_provenance(Path(tmp.name))

        assert res["c2pa_present"] is True
        assert res["c2pa_status"] == "PRESENT"
        assert res["provenance_status"] == "PROVENANCE_INDICATED"


def test_image_type_classification():
    """Verify deterministic image type classification heuristics."""
    # Mobile UI screenshot
    res_screen = ImageAuthenticityEngine.classify_image_type(
        width=1080, height=2400, aspect_ratio=0.45,
        ocr_bbox_density=1.5, character_count=25, ocr_status="success_text"
    )
    assert res_screen["image_type"] == "SCREENSHOT"

    # Clean product photo
    res_photo = ImageAuthenticityEngine.classify_image_type(
        width=800, height=600, aspect_ratio=1.33,
        ocr_bbox_density=0.0, character_count=0, ocr_status="success_no_text"
    )
    assert res_photo["image_type"] == "PHOTO"

    # Text heavy image
    res_text = ImageAuthenticityEngine.classify_image_type(
        width=800, height=600, aspect_ratio=1.33,
        ocr_bbox_density=3.5, character_count=120, ocr_status="success_text"
    )
    assert res_text["image_type"] == "TEXT_HEAVY"


def test_detector_spectral_forensics_reproducibility():
    """Verify detector A generates deterministic spectral energy ratio."""
    # Create simple synthetic test image
    from PIL import Image
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        img = Image.new("RGB", (100, 100), color=(128, 128, 128))
        img.save(tmp.name)

        det1 = ImageAuthenticityEngine.compute_detector_a_spectral_forensics(Path(tmp.name))
        det2 = ImageAuthenticityEngine.compute_detector_a_spectral_forensics(Path(tmp.name))

        assert det1["detector_a_score"] == det2["detector_a_score"]
        assert det1["spectral_hf_ratio"] == det2["spectral_hf_ratio"]
        assert det1["detector_a_status"] in ("BORDERLINE", "REAL_IMAGE_CANDIDATE", "NO_CONCLUSIVE_SIGNAL")
