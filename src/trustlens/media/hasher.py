"""Cryptographic and perceptual hashing utilities for media assets."""

import hashlib
import io
from pathlib import Path
from typing import Optional, Union

import imagehash
from PIL import Image


def compute_sha256(content: Union[bytes, Path]) -> str:
    """Compute SHA-256 hexadecimal digest from bytes or file path."""
    if isinstance(content, Path):
        hasher = hashlib.sha256()
        with open(content, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    return hashlib.sha256(content).hexdigest()


def compute_perceptual_hash(content: Union[bytes, Path]) -> Optional[str]:
    """Compute difference hash (dhash) for image similarity comparison."""
    try:
        if isinstance(content, Path):
            with Image.open(content) as img:
                return str(imagehash.dhash(img))
        else:
            with Image.open(io.BytesIO(content)) as img:
                return str(imagehash.dhash(img))
    except Exception:
        return None
