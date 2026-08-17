from __future__ import annotations

import atexit
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any

_server: ThreadingHTTPServer | None = None
_thread: Thread | None = None


class _LocalGatewayHandler(BaseHTTPRequestHandler):
    server_version = "PortkeyExampleGateway/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/chat/completions":
            self.send_error(404)
            return

        content_length = int(self.headers.get("content-length", "0"))
        raw_body = self.rfile.read(content_length) if content_length else b"{}"
        try:
            request = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            request = {}

        model = request.get("model") or "local-portkey-model"
        messages = request.get("messages") or []
        if model == "error-401":
            payload = json.dumps(
                {"error": {"message": "deterministic Portkey authorization failure"}}
            ).encode()
            self.send_response(401)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        last_message = messages[-1] if messages else {}
        user_text = (
            last_message.get("content") if isinstance(last_message, dict) else ""
        )
        tools = request.get("tools") or []
        has_tool_result = any(
            isinstance(message, dict) and message.get("role") == "tool"
            for message in messages
        )
        if request.get("stream"):
            chunks = ["Portkey ", "streaming ", "works."]
            self.send_response(200)
            self.send_header("content-type", "text/event-stream")
            self.end_headers()
            for index, content in enumerate(chunks):
                event = {
                    "id": "chatcmpl-portkey-stream",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "role": "assistant" if index == 0 else None,
                                "content": content,
                            },
                            "finish_reason": None,
                        }
                    ],
                }
                self.wfile.write(f"data: {json.dumps(event)}\n\n".encode())
                self.wfile.flush()
            terminal = {
                "id": "chatcmpl-portkey-stream",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model,
                "choices": [],
                "usage": {
                    "prompt_tokens": 7,
                    "completion_tokens": 5,
                    "total_tokens": 12,
                },
            }
            self.wfile.write(f"data: {json.dumps(terminal)}\n\n".encode())
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
            return

        content = f"Local Portkey-compatible response for: {user_text}"
        message: dict[str, Any] = {"role": "assistant", "content": content}
        finish_reason = "stop"
        if tools and not has_tool_result:
            message = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "portkey-weather-1",
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": '{"city":"Tokyo"}',
                        },
                    }
                ],
            }
            finish_reason = "tool_calls"
        elif has_tool_result:
            content = "Tokyo is sunny and 72F."
            message = {"role": "assistant", "content": content}
        response = {
            "id": "chatcmpl-portkey-local",
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
        payload = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def local_gateway_base_url() -> str:
    global _server, _thread
    if _server is None:
        _server = ThreadingHTTPServer(("127.0.0.1", 0), _LocalGatewayHandler)
        _thread = Thread(target=_server.serve_forever, daemon=True)
        _thread.start()
        atexit.register(shutdown_local_gateway)
    host, port = _server.server_address
    return f"http://{host}:{port}"


def shutdown_local_gateway() -> None:
    global _server, _thread
    if _server is not None:
        _server.shutdown()
        _server.server_close()
    if _thread is not None:
        _thread.join(timeout=1)
    _server = None
    _thread = None
