"""Inspection utilities for media assets (MIME type, dimensions, file size)."""

import io
from pathlib import Path
from typing import Optional, Tuple, Union

from PIL import Image


def inspect_image(
    content: Union[bytes, Path],
) -> Tuple[Optional[str], Optional[int], Optional[int], Optional[int]]:
    """Inspect image bytes or file.

    Returns (mime_type, width, height, file_size).
    """
    try:
        if isinstance(content, Path):
            file_size = content.stat().st_size
            with Image.open(content) as img:
                mime_type = Image.MIME.get(img.format) if img.format else "image/jpeg"
                return (mime_type, img.width, img.height, file_size)
        else:
            file_size = len(content)
            with Image.open(io.BytesIO(content)) as img:
                mime_type = Image.MIME.get(img.format) if img.format else "image/jpeg"
                return (mime_type, img.width, img.height, file_size)
    except Exception:
        size = content.stat().st_size if isinstance(content, Path) else len(content)
        return (None, None, None, size)
