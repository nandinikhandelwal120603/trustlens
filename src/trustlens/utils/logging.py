"""Structured logging for TrustLens pipeline stages and operations."""

import logging
import time
from typing import Any, Optional

from rich.logging import RichHandler

from trustlens.config.settings import settings

# Configure root logger
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
)

logger = logging.getLogger("trustlens")


class StageTimer:
    """Context manager for structured logging of pipeline execution stages."""

    def __init__(
        self,
        stage: str,
        case_id: Optional[str] = None,
        listing_id: Optional[str] = None,
        **extra: Any,
    ):
        self.stage = stage
        self.case_id = case_id or "unknown"
        self.listing_id = listing_id or "unknown"
        self.extra = extra
        self.start_time = 0.0

    def __enter__(self) -> "StageTimer":
        self.start_time = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Any,
    ) -> None:
        duration_ms = int((time.perf_counter() - self.start_time) * 1000)
        status = "failed" if exc_val else "success"
        error_info = f" error={exc_val}" if exc_val else ""

        logger.info(
            f"[INGEST] case={self.case_id} listing={self.listing_id} "
            f"stage={self.stage} status={status} duration={duration_ms}ms{error_info} "
        )
        # Do not suppress exceptions
