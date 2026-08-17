"""Bounded Marqo protocol fixture for deterministic tracing examples."""

from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit


class _LoopbackState:
    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []


class _LoopbackServer(ThreadingHTTPServer):
    state: _LoopbackState


class _MarqoHandler(BaseHTTPRequestHandler):
    server: _LoopbackServer

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _send_json(self, status: int, payload: object) -> None:
        content = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if not length:
            return {}
        return json.loads(self.rfile.read(length))

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/":
            self._send_json(200, {"version": "3.18.2"})
            return
        if path.endswith("/health"):
            self._send_json(
                503,
                {
                    "message": "loopback Marqo service unavailable",
                    "code": "service_unavailable",
                    "type": "service_unavailable",
                    "link": "",
                },
            )
            return
        self._send_json(404, {"message": "not found"})

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        payload = self._read_json()
        if path.endswith("/documents"):
            self.server.state.documents = list(payload.get("documents", []))
            self._send_json(
                200,
                {
                    "errors": False,
                    "items": [
                        {"_id": document.get("_id"), "status": 200}
                        for document in self.server.state.documents
                    ],
                    "processingTimeMs": 1,
                },
            )
            return
        if path.endswith("/search"):
            hits = [
                {**document, "_score": round(0.95 - index * 0.05, 2)}
                for index, document in enumerate(self.server.state.documents[:2])
            ]
            self._send_json(200, {"hits": hits, "processingTimeMs": 1})
            return
        if path.startswith("/indexes/"):
            self._send_json(200, {"acknowledged": True})
            return
        self._send_json(404, {"message": "not found"})

    def do_DELETE(self) -> None:
        path = urlsplit(self.path).path
        if path.startswith("/indexes/"):
            self.server.state.documents = []
            self._send_json(200, {"acknowledged": True})
            return
        self._send_json(404, {"message": "not found"})


@contextmanager
def loopback_marqo_url() -> Iterator[str]:
    """Yield an ephemeral localhost endpoint and always stop its server."""

    server = _LoopbackServer(("127.0.0.1", 0), _MarqoHandler)
    server.state = _LoopbackState()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
