from __future__ import annotations

import atexit
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

EXAMPLE_DIR = Path(__file__).resolve().parent
EXAMPLE_REPO_ROOT = EXAMPLE_DIR.parents[2]
WORKSPACE_ROOT = EXAMPLE_REPO_ROOT.parent
RESPAN_REPO_ROOT = WORKSPACE_ROOT / "respan"
DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "openai/gpt-4o-mini"
_MOCK_SERVER: ThreadingHTTPServer | None = None
_MOCK_THREAD: threading.Thread | None = None


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            os.environ[key] = value


def _add_local_respan_paths() -> None:
    local_paths = [
        RESPAN_REPO_ROOT / "python-sdks" / "respan" / "src",
        RESPAN_REPO_ROOT / "python-sdks" / "respan-tracing" / "src",
        RESPAN_REPO_ROOT / "python-sdks" / "respan-sdk" / "src",
        RESPAN_REPO_ROOT
        / "python-sdks"
        / "instrumentations"
        / "respan-instrumentation-openai"
        / "src",
        RESPAN_REPO_ROOT
        / "python-sdks"
        / "instrumentations"
        / "respan-instrumentation-openrouter"
        / "src",
    ]
    for path in reversed(local_paths):
        if path.exists():
            path_text = str(path)
            if path_text not in sys.path:
                sys.path.insert(0, path_text)


_load_env_file(EXAMPLE_REPO_ROOT / ".env")
_add_local_respan_paths()

from openai import AsyncOpenAI, OpenAI
from respan import Respan
from respan_instrumentation_openrouter import OpenRouterInstrumentor


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def _env_truthy(name: str) -> bool:
    return (os.getenv(name) or "").lower() in {"1", "true", "yes", "on"}


def _require(value: str | None, message: str) -> str:
    if not value:
        raise RuntimeError(message)
    return value


def ensure_respan_api_key() -> str:
    api_key = _require(
        _first_env("RESPAN_API_KEY", "RESPAN_GATEWAY_API_KEY"),
        "Set RESPAN_API_KEY or RESPAN_GATEWAY_API_KEY in respan-example-projects/.env",
    )
    os.environ.setdefault("RESPAN_API_KEY", api_key)
    return api_key


def make_respan() -> Respan:
    return Respan(
        api_key=ensure_respan_api_key(),
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        app_name="openrouter-python-examples",
        instrumentations=[OpenRouterInstrumentor()],
        metadata={"example_set": "python/tracing/openrouter"},
    )


def _chat_response(
    *,
    model: str,
    message: dict[str, Any],
    finish_reason: str = "stop",
) -> dict[str, Any]:
    return {
        "id": "chatcmpl-openrouter-mock",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": message,
                "finish_reason": finish_reason,
            }
        ],
        "usage": {
            "prompt_tokens": 12,
            "completion_tokens": 9,
            "total_tokens": 21,
        },
    }


def _mock_completion_payload(request: dict[str, Any]) -> dict[str, Any]:
    model = str(request.get("model") or DEFAULT_OPENROUTER_MODEL)
    messages = request.get("messages") or []
    if request.get("tools") and request.get("tool_choice"):
        city = "Tokyo"
        return _chat_response(
            model=model,
            message={
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_openrouter_mock_weather",
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": json.dumps({"city": city}),
                        },
                    }
                ],
            },
            finish_reason="tool_calls",
        )

    if any(isinstance(message, dict) and message.get("role") == "tool" for message in messages):
        return _chat_response(
            model=model,
            message={
                "role": "assistant",
                "content": "The mocked tool result says Tokyo is sunny and 72F.",
            },
        )

    if request.get("response_format") == {"type": "json_object"}:
        return _chat_response(
            model=model,
            message={
                "role": "assistant",
                "content": json.dumps(
                    {
                        "title": "OpenRouter observability plan",
                        "difficulty": "easy",
                        "steps": [
                            "Enable tracing",
                            "Send one request",
                            "Inspect the exported span",
                        ],
                    }
                ),
            },
        )

    return _chat_response(
        model=model,
        message={
            "role": "assistant",
            "content": "Hello from the OpenRouter-compatible mock response.",
        },
    )


class _OpenRouterMockHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        return None

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("content-length", "0") or "0")
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_json(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_stream(self, request: dict[str, Any]) -> None:
        model = str(request.get("model") or DEFAULT_OPENROUTER_MODEL)
        created = int(time.time())
        chunks = ["Trace ", "data ", "flows ", "clearly."]
        events: list[str] = []
        for chunk in chunks:
            payload = {
                "id": "chatcmpl-openrouter-mock-stream",
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": chunk},
                        "finish_reason": None,
                    }
                ],
            }
            events.append("data: " + json.dumps(payload) + "\n\n")
        events.append("data: [DONE]\n\n")
        body = "".join(events).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.send_header("cache-control", "no-cache")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        request = self._read_json()
        if not self.path.endswith("/chat/completions"):
            self.send_response(404)
            self.send_header("content-length", "0")
            self.end_headers()
            return
        if request.get("stream"):
            self._send_stream(request)
            return
        self._send_json(_mock_completion_payload(request))


def _shutdown_mock_server() -> None:
    global _MOCK_SERVER
    if _MOCK_SERVER is not None:
        _MOCK_SERVER.shutdown()
        _MOCK_SERVER.server_close()
        _MOCK_SERVER = None


def _mock_base_url() -> str:
    global _MOCK_SERVER, _MOCK_THREAD
    if _MOCK_SERVER is None:
        _MOCK_SERVER = ThreadingHTTPServer(("127.0.0.1", 0), _OpenRouterMockHandler)
        _MOCK_THREAD = threading.Thread(
            target=_MOCK_SERVER.serve_forever,
            daemon=True,
        )
        _MOCK_THREAD.start()
        atexit.register(_shutdown_mock_server)
    host, port = _MOCK_SERVER.server_address
    return f"http://{host}:{port}/api/v1"


def openrouter_config() -> dict[str, Any]:
    direct_key = os.getenv("OPENROUTER_API_KEY")
    if direct_key:
        return {
            "api_key": direct_key,
            "base_url": os.getenv(
                "OPENROUTER_BASE_URL",
                DEFAULT_OPENROUTER_BASE_URL,
            ),
            "model": os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL),
        }

    gateway_key = os.getenv("RESPAN_GATEWAY_API_KEY")
    gateway_base_url = _first_env("RESPAN_GATEWAY_BASE_URL", "RESPAN_BASE_URL")
    if _env_truthy("OPENROUTER_USE_RESPAN_GATEWAY") and gateway_key and gateway_base_url:
        return {
            "api_key": gateway_key,
            "base_url": gateway_base_url,
            "model": _first_env("OPENROUTER_MODEL", "RESPAN_MODEL")
            or DEFAULT_OPENROUTER_MODEL,
        }

    return {
        "api_key": "openrouter-mock-key",
        "base_url": _mock_base_url(),
        "model": os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL),
    }


def _openrouter_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    referer = os.getenv("OPENROUTER_HTTP_REFERER")
    app_title = os.getenv("OPENROUTER_APP_TITLE")
    if referer:
        headers["HTTP-Referer"] = referer
    if app_title:
        headers["X-Title"] = app_title
    return headers


def make_client() -> tuple[OpenAI, str]:
    config = openrouter_config()
    kwargs: dict[str, Any] = {
        "api_key": config["api_key"],
        "base_url": config["base_url"],
    }
    headers = _openrouter_headers()
    if headers:
        kwargs["default_headers"] = headers
    return OpenAI(**kwargs), str(config["model"])


def make_async_client() -> tuple[AsyncOpenAI, str]:
    config = openrouter_config()
    kwargs: dict[str, Any] = {
        "api_key": config["api_key"],
        "base_url": config["base_url"],
    }
    headers = _openrouter_headers()
    if headers:
        kwargs["default_headers"] = headers
    return AsyncOpenAI(**kwargs), str(config["model"])
