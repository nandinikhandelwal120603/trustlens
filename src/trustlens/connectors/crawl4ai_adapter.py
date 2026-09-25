"""Crawl4AI WebExtractor adapter for authorized web pages."""

import re

import httpx

from trustlens.config.settings import settings
from trustlens.connectors.web_extractor import RawPage, WebExtractor
from trustlens.utils.logging import logger


class Crawl4AIWebExtractor(WebExtractor):
    """WebExtractor implementation using Crawl4AI with graceful fallback.

    Used ONLY for authorized or user-submitted URLs. Never bypasses robots.txt
    or anti-bot controls.
    """

    def __init__(self, headless: bool = settings.crawl4ai_headless):
        self.headless = headless

    async def extract(self, url: str) -> RawPage:
        """Extract content using Crawl4AI if available, falling back to HTTP client."""
        try:
            from crawl4ai import AsyncWebCrawler  # type: ignore

            logger.info(f"Extracting permitted URL via Crawl4AI: {url}")
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(url=url)
                title = getattr(result, "title", None)
                html = getattr(result, "html", "") or ""
                text = getattr(result, "markdown", "") or getattr(result, "cleaned_html", "") or ""

                return RawPage(
                    url=url,
                    html=html,
                    text=text,
                    title=title,
                    status_code=getattr(result, "status_code", 200) or 200,
                    metadata={"extractor": "crawl4ai"},
                )

        except ImportError:
            logger.info(
                f"Crawl4AI not installed (install via `pip install -e '.[web]'`). "
                f"Falling back to standard HTTP extractor for permitted URL: {url}"
            )
            return await self._fallback_extract(url)

    async def _fallback_extract(self, url: str) -> RawPage:
        """Lightweight HTTP fallback using httpx."""
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url)
            html = response.text

            # Simple title extraction
            title = None
            title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()

            # Simple strip tags for text
            text = re.sub(r"<[^>]+>", " ", html)
            text = re.sub(r"\s+", " ", text).strip()

            return RawPage(
                url=url,
                html=html,
                text=text,
                title=title,
                status_code=response.status_code,
                metadata={"extractor": "httpx_fallback"},
            )
