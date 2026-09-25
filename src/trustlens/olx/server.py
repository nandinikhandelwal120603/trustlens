"""
TrustLens — Local Ingestion API Server for Browser Extension (Phase 3).
Lightweight HTTP daemon allowing browser extension to send captured OLX listings.
"""

import asyncio
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Optional

from trustlens.olx.collector import OLXCollector
from trustlens.olx.models import CollectionMethod, CollectionType
from trustlens.utils.logging import logger


class IngestionRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for local TrustLens ingestion server."""

    collector: Optional[OLXCollector] = None

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Health and status endpoint."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(
            json.dumps({
                "status": "online",
                "service": "TrustLens OLX Ingestion Server",
                "version": "0.3.0",
            }).encode("utf-8")
        )

    def do_POST(self):
        """Handle captured listing submission from browser extension."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode("utf-8"))
            url = payload.get("url")
            html = payload.get("html")
            investigation_id = payload.get("investigation_id", "INV-002")
            collection_type_str = payload.get("collection_type", "targeted")
            collection_type = CollectionType(collection_type_str)

            collector = self.collector or OLXCollector()

            if html:
                # Researcher-assisted HTML ingest
                inv = asyncio.run(
                    collector._process_listing_content(
                        content=html,
                        url=url or "https://www.olx.in/item/extension-capture",
                        investigation_id=investigation_id,
                        collection_type=collection_type,
                        method=CollectionMethod.BROWSER_EXTENSION,
                        download_media=True,
                        discovery_context=None,
                    )
                )
            elif url:
                # Direct URL ingest
                inv = asyncio.run(
                    collector.ingest_url(
                        url=url,
                        investigation_id=investigation_id,
                        collection_type=collection_type,
                        download_media=True,
                    )
                )
            else:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing 'url' or 'html' in payload"}).encode("utf-8"))
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(
                json.dumps({
                    "status": "success",
                    "investigation_id": inv.investigation_id,
                    "listing_id": inv.listing.listing_id,
                    "signals_detected": len(inv.signals),
                    "media_count": len(inv.media),
                }).encode("utf-8")
            )

        except Exception as e:
            logger.error(f"Error handling extension ingestion: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))


def start_server(host: str = "127.0.0.1", port: int = 8765, block: bool = True) -> HTTPServer:
    """Start local ingestion HTTP server."""
    IngestionRequestHandler.collector = OLXCollector()
    server = HTTPServer((host, port), IngestionRequestHandler)
    logger.info(f"TrustLens Ingestion API running at http://{host}:{port}")

    if block:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()
    else:
        t = Thread(target=server.serve_forever, daemon=True)
        t.start()

    return server
