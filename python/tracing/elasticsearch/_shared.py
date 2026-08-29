"""Shared local Elasticsearch server and Respan setup for the examples."""

from __future__ import annotations

import json
import os
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterator
from uuid import uuid4

from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_elasticsearch import ElasticsearchInstrumentor

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def example_run_id() -> str:
    return os.getenv("RESPAN_EXAMPLE_RUN_ID") or f"elasticsearch-{uuid4().hex[:10]}"


def make_respan(example_name: str) -> Respan:
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    api_key = os.getenv("RESPAN_API_KEY")
    if not api_key:
        raise RuntimeError("RESPAN_API_KEY must be set in respan-example-projects/.env")
    return Respan(
        api_key=api_key,
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        app_name="elasticsearch-examples",
        instrumentations=[ElasticsearchInstrumentor()],
        is_batching_enabled=False,
        metadata={
            "integration": "elasticsearch",
            "example": example_name,
            "run_id": example_run_id(),
        },
    )


def example_attributes(example_name: str):
    run_id = example_run_id()
    return propagate_attributes(
        custom_identifier=f"{run_id}:{example_name}",
        trace_group_identifier=f"{run_id}:{example_name}",
        metadata={
            "integration": "elasticsearch",
            "example": example_name,
            "run_id": run_id,
        },
    )


class _ElasticsearchHandler(BaseHTTPRequestHandler):
    server_version = "Elasticsearch/9.5.0"

    def log_message(self, format: str, *args: object) -> None:
        return None

    def _send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Elastic-Product", "Elasticsearch")
        self.end_headers()
        self.wfile.write(body)

    def do_PUT(self) -> None:
        self._send_json(
            201,
            {
                "_index": "audit-index",
                "_id": "doc-1",
                "_version": 1,
                "result": "created",
                "_shards": {"total": 1, "successful": 1, "failed": 0},
                "_seq_no": 0,
                "_primary_term": 1,
            },
        )

    def do_POST(self) -> None:
        self._send_json(
            200,
            {
                "took": 1,
                "timed_out": False,
                "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
                "hits": {
                    "total": {"value": 1, "relation": "eq"},
                    "max_score": 1.0,
                    "hits": [
                        {
                            "_index": "audit-index",
                            "_id": "doc-1",
                            "_score": 1.0,
                            "_source": {"title": "Tracing Elasticsearch"},
                        }
                    ],
                },
            },
        )

    def do_GET(self) -> None:
        self._send_json(
            404,
            {
                "_index": "audit-index",
                "_id": "missing",
                "found": False,
                "error": {
                    "type": "document_missing_exception",
                    "reason": "document [missing] is absent",
                },
                "status": 404,
            },
        )


@contextmanager
def local_elasticsearch() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _ElasticsearchHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
