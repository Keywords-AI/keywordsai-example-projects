from __future__ import annotations

import atexit
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

EXAMPLE_DIR = Path(__file__).resolve().parent
EXAMPLE_REPO_ROOT = EXAMPLE_DIR.parents[2]
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
            os.environ.setdefault(key, value)


_load_env_file(EXAMPLE_REPO_ROOT / ".env")

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


def make_respan(*, scenario: str) -> Respan:
    metadata = {
        "example_set": "python/tracing/openrouter",
        "scenario": scenario,
    }
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID")
    if run_id:
        metadata["run_id"] = run_id
        metadata["example_run_id"] = run_id
    return Respan(
        api_key=ensure_respan_api_key(),
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        app_name="openrouter-python-examples",
        instrumentations=[OpenRouterInstrumentor()],
        metadata=metadata,
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

    if any(
        isinstance(message, dict) and message.get("role") == "tool"
        for message in messages
    ):
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

    def _send_error(self, *, status_code: int, message: str) -> None:
        body = json.dumps(
            {
                "error": {
                    "code": "rate_limit_exceeded",
                    "message": message,
                    "type": "rate_limit_error",
                }
            }
        ).encode("utf-8")
        self.send_response(status_code)
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
        events.append(
            "data: "
            + json.dumps(
                {
                    "id": "chatcmpl-openrouter-mock-stream",
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [],
                    "usage": {
                        "prompt_tokens": 17,
                        "completion_tokens": 12,
                        "total_tokens": 29,
                    },
                }
            )
            + "\n\n"
        )
        # The default deterministic fixture ends after the terminal usage event and
        # lets OpenAI drain the advertised body to EOF. OpenAI 3.0.0 with
        # httpx2/httpcore2 2.10.0 can otherwise leave nested transport async
        # generators closing concurrently when it breaks early on ``[DONE]``.
        if self.headers.get("x-respan-mock-stream-termination") == "done":
            events.append("data: [DONE]\n\n")
        body = "".join(events).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.send_header("cache-control", "no-cache")
        self.send_header("content-length", str(len(body)))
        self.send_header("connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def do_POST(self) -> None:
        request = self._read_json()
        if not self.path.endswith("/chat/completions"):
            self.send_response(404)
            self.send_header("content-length", "0")
            self.end_headers()
            return
        messages = request.get("messages") or []
        if any(
            isinstance(message, dict)
            and "trigger deterministic 429" in str(message.get("content") or "")
            for message in messages
        ):
            self._send_error(
                status_code=429,
                message="deterministic OpenRouter rate limit",
            )
            return
        if request.get("stream"):
            self._send_stream(request)
            return
        self._send_json(_mock_completion_payload(request))


def _shutdown_mock_server() -> None:
    global _MOCK_SERVER, _MOCK_THREAD
    server = _MOCK_SERVER
    thread = _MOCK_THREAD
    _MOCK_SERVER = None
    _MOCK_THREAD = None
    if server is not None:
        server.shutdown()
        server.server_close()
    if thread is not None:
        thread.join(timeout=5)
        if thread.is_alive():
            raise RuntimeError("OpenRouter mock server did not stop within 5 seconds")


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


def openrouter_config(*, live: bool = False) -> dict[str, Any]:
    if not live:
        return {
            "api_key": "openrouter-mock-key",
            "base_url": _mock_base_url(),
            "model": os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL),
        }

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
    if (
        _env_truthy("OPENROUTER_USE_RESPAN_GATEWAY")
        and gateway_key
        and gateway_base_url
    ):
        return {
            "api_key": gateway_key,
            "base_url": gateway_base_url,
            "model": _first_env("OPENROUTER_MODEL", "RESPAN_MODEL")
            or DEFAULT_OPENROUTER_MODEL,
        }

    raise RuntimeError(
        "Live OpenRouter mode requires OPENROUTER_API_KEY or an explicit "
        "Respan gateway configuration"
    )


def _openrouter_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    referer = os.getenv("OPENROUTER_HTTP_REFERER")
    app_title = os.getenv("OPENROUTER_APP_TITLE")
    if referer:
        headers["HTTP-Referer"] = referer
    if app_title:
        headers["X-Title"] = app_title
    return headers


def make_client(*, live: bool = False) -> tuple[OpenAI, str]:
    config = openrouter_config(live=live)
    kwargs: dict[str, Any] = {
        "api_key": config["api_key"],
        "base_url": config["base_url"],
        "max_retries": 0,
        "timeout": 20.0,
    }
    headers = _openrouter_headers()
    if headers:
        kwargs["default_headers"] = headers
    return OpenAI(**kwargs), str(config["model"])


def make_async_client(*, live: bool = False) -> tuple[AsyncOpenAI, str]:
    config = openrouter_config(live=live)
    kwargs: dict[str, Any] = {
        "api_key": config["api_key"],
        "base_url": config["base_url"],
        "max_retries": 0,
        "timeout": 20.0,
    }
    headers = _openrouter_headers()
    if headers:
        kwargs["default_headers"] = headers
    return AsyncOpenAI(**kwargs), str(config["model"])


def make_mock_client() -> tuple[OpenAI, str]:
    model = os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)
    return (
        OpenAI(
            api_key="openrouter-mock-key",
            base_url=_mock_base_url(),
            max_retries=0,
            timeout=20.0,
        ),
        model,
    )


def close_sync(*, respan: Respan | None, client: OpenAI | None) -> None:
    errors: list[Exception] = []
    try:
        if client is not None:
            client.close()
    except Exception as exc:  # noqa: BLE001 - teardown must continue
        errors.append(exc)
    try:
        if respan is not None:
            respan.flush()
    except Exception as exc:  # noqa: BLE001 - teardown must continue
        errors.append(exc)
    try:
        if respan is not None:
            respan.shutdown()
    except Exception as exc:  # noqa: BLE001 - teardown must continue
        errors.append(exc)
    try:
        _shutdown_mock_server()
    except Exception as exc:  # noqa: BLE001 - teardown must continue
        errors.append(exc)
    if errors:
        raise errors[0]


async def close_async(*, respan: Respan | None, client: AsyncOpenAI | None) -> None:
    errors: list[Exception] = []
    try:
        if client is not None:
            await client.close()
    except Exception as exc:  # noqa: BLE001 - teardown must continue
        errors.append(exc)
    try:
        if respan is not None:
            respan.flush()
    except Exception as exc:  # noqa: BLE001 - teardown must continue
        errors.append(exc)
    try:
        if respan is not None:
            respan.shutdown()
    except Exception as exc:  # noqa: BLE001 - teardown must continue
        errors.append(exc)
    try:
        _shutdown_mock_server()
    except Exception as exc:  # noqa: BLE001 - teardown must continue
        errors.append(exc)
    if errors:
        raise errors[0]
