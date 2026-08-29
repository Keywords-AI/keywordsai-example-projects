from __future__ import annotations

import atexit
import json
import os
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread, current_thread
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from ollama import Client
from respan import Respan, propagate_attributes
from respan_instrumentation_ollama import OllamaInstrumentor

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MODEL = "llama3.2"
DEFAULT_RUN_ID = f"ollama-{uuid4().hex[:10]}"
_FAKE_SERVER: ThreadingHTTPServer | None = None
_FAKE_SERVER_THREAD: Thread | None = None


def load_root_env() -> None:
    # Invocation-scoped values, especially the exact QA marker, take precedence.
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def require_respan_api_key() -> str:
    load_root_env()
    api_key = os.getenv("RESPAN_API_KEY")
    if not api_key:
        raise RuntimeError("RESPAN_API_KEY must be set in the repo root .env file")
    return api_key


def respan_base_url() -> str:
    return os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/")


def model_name() -> str:
    return (
        os.getenv("RESPAN_OLLAMA_MODEL") or os.getenv("OLLAMA_MODEL") or DEFAULT_MODEL
    )


def example_run_id() -> str:
    load_root_env()
    return os.getenv("RESPAN_EXAMPLE_RUN_ID", DEFAULT_RUN_ID)


def make_respan(example_name: str) -> Respan:
    api_key = require_respan_api_key()
    run_id = example_run_id()
    return Respan(
        api_key=api_key,
        base_url=respan_base_url(),
        app_name="ollama-examples",
        instrumentations=[OllamaInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={
            "integration": "ollama",
            "example": example_name,
            "example_run_id": run_id,
        },
        is_batching_enabled=False,
    )


def make_client(*, force_compat_server: bool = False) -> Client:
    load_root_env()
    return Client(host=ollama_host(force_compat_server=force_compat_server))


def ollama_host(*, force_compat_server: bool = False) -> str | None:
    configured_host = os.getenv("OLLAMA_HOST")
    if configured_host and not force_compat_server:
        return configured_host
    return _start_fake_ollama_server()


def workflow_name(example_name: str) -> str:
    normalized_name = example_name.replace("-", "_")
    return f"ollama_{normalized_name}"


def make_custom_identifier(example_name: str) -> str:
    return f"ollama-{example_name}-{uuid4().hex[:8]}"


@contextmanager
def example_attributes(example_name: str, custom_identifier: str | None = None):
    custom_identifier = custom_identifier or make_custom_identifier(example_name)
    current_workflow_name = workflow_name(example_name)
    run_id = example_run_id()
    with propagate_attributes(
        custom_identifier=custom_identifier,
        trace_group_identifier=current_workflow_name,
        metadata={
            "example": example_name,
            "example_run_id": run_id,
            "case_id": custom_identifier,
            "workflow_name": current_workflow_name,
        },
    ):
        yield custom_identifier


def client_mode() -> str:
    return "ollama-host" if os.getenv("OLLAMA_HOST") else "local-compat-server"


def response_message_content(response: Any) -> str:
    message = _field(response, "message", {})
    return str(_field(message, "content", "") or "")


def response_tool_calls(response: Any) -> list[Any]:
    message = _field(response, "message", {})
    tool_calls = _field(message, "tool_calls", []) or []
    return list(tool_calls)


def tool_call_name(tool_call: Any) -> str:
    function = _field(tool_call, "function", {})
    return str(_field(function, "name", ""))


def tool_call_arguments(tool_call: Any) -> dict[str, Any]:
    function = _field(tool_call, "function", {})
    arguments = _field(function, "arguments", {}) or {}
    if isinstance(arguments, str):
        try:
            parsed = json.loads(arguments)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return arguments if isinstance(arguments, dict) else {}


def print_result(example_name: str, custom_identifier: str, text: str) -> None:
    print(f"example={example_name}")
    print(f"custom_identifier={custom_identifier}")
    print(f"RESPAN_EXAMPLE_RUN_ID={example_run_id()}")
    print(f"workflow_name={workflow_name(example_name)}")
    print(f"client_mode={client_mode()}")
    print(text.strip())


def flush_and_shutdown(respan: Respan) -> None:
    try:
        respan.flush()
    finally:
        try:
            respan.shutdown()
        finally:
            _stop_fake_ollama_server()


def _field(value: Any, name: str, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get(name, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        try:
            return getter(name, default)
        except Exception:  # noqa: BLE001 - fall back to attribute access
            return getattr(value, name, default)
    return getattr(value, name, default)


def _start_fake_ollama_server() -> str:
    global _FAKE_SERVER, _FAKE_SERVER_THREAD
    if _FAKE_SERVER is None:
        _FAKE_SERVER = ThreadingHTTPServer(("127.0.0.1", 0), _FakeOllamaHandler)
        _FAKE_SERVER_THREAD = Thread(target=_FAKE_SERVER.serve_forever, daemon=True)
        _FAKE_SERVER_THREAD.start()
        atexit.register(_stop_fake_ollama_server)
    host, port = _FAKE_SERVER.server_address
    return f"http://{host}:{port}"


def _stop_fake_ollama_server() -> None:
    global _FAKE_SERVER, _FAKE_SERVER_THREAD
    server = _FAKE_SERVER
    thread = _FAKE_SERVER_THREAD
    _FAKE_SERVER = None
    _FAKE_SERVER_THREAD = None
    if server is None:
        return
    server.shutdown()
    server.server_close()
    if thread is not None and thread is not current_thread():
        thread.join(timeout=2)


class _FakeOllamaHandler(BaseHTTPRequestHandler):
    server_version = "RespanFakeOllama/1.0"

    def do_POST(self) -> None:
        length = int(self.headers.get("content-length", "0") or "0")
        payload = json.loads(self.rfile.read(length) or b"{}")
        if self.path == "/api/chat":
            self._handle_chat(payload)
            return
        if self.path == "/api/generate":
            self._handle_generate(payload)
            return
        if self.path in {"/api/embed", "/api/embeddings"}:
            self._write_json(
                {
                    "model": payload.get("model") or model_name(),
                    "embeddings": [[0.1, 0.2, 0.3]],
                    "embedding": [0.1, 0.2, 0.3],
                    "prompt_eval_count": 4,
                    "done": True,
                }
            )
            return
        self.send_error(404, "unknown fake Ollama endpoint")

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _handle_chat(self, payload: dict[str, Any]) -> None:
        messages = payload.get("messages") or []
        if any(
            "force expected provider error" in str(message.get("content", ""))
            for message in messages
            if isinstance(message, dict)
        ):
            self._write_json(
                {"error": "Ollama compatibility server unavailable"},
                status_code=503,
            )
            return
        if any(
            message.get("role") == "tool"
            for message in messages
            if isinstance(message, dict)
        ):
            content = "Tool result received: sunny and 22 C in Tokyo."
            message = {"role": "assistant", "content": content}
        elif payload.get("tools"):
            message = {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": {"city": "Tokyo"},
                        },
                    }
                ],
            }
        else:
            message = {
                "role": "assistant",
                "content": "Ollama traces are visible in Respan.",
            }
        self._write_json(
            {
                "model": payload.get("model") or model_name(),
                "created_at": "2026-05-28T00:00:00Z",
                "message": message,
                "done": True,
                "prompt_eval_count": 9,
                "eval_count": 7,
            }
        )

    def _handle_generate(self, payload: dict[str, Any]) -> None:
        if payload.get("stream"):
            self.send_response(200)
            self.send_header("content-type", "application/x-ndjson")
            self.end_headers()
            chunks = [
                {
                    "model": payload.get("model") or model_name(),
                    "response": "Streaming ",
                    "done": False,
                },
                {
                    "model": payload.get("model") or model_name(),
                    "response": "generation captured.",
                    "done": True,
                    "prompt_eval_count": 6,
                    "eval_count": 5,
                },
            ]
            for chunk in chunks:
                self.wfile.write(json.dumps(chunk).encode("utf-8") + b"\n")
            return
        self._write_json(
            {
                "model": payload.get("model") or model_name(),
                "created_at": "2026-05-28T00:00:00Z",
                "response": "Generated completion captured.",
                "done": True,
                "prompt_eval_count": 6,
                "eval_count": 5,
            }
        )

    def _write_json(self, payload: dict[str, Any], status_code: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
