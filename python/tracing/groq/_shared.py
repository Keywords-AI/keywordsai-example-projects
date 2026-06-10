from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from groq import Groq
import httpx
from respan import Respan, propagate_attributes
from respan_instrumentation_groq import GroqInstrumentor

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_GATEWAY_MODEL = "gpt-4.1-nano"
DEFAULT_DIRECT_GROQ_MODEL = "llama-3.1-8b-instant"


def load_root_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=True)


def require_respan_api_key() -> str:
    load_root_env()
    api_key = os.getenv("RESPAN_API_KEY")
    if not api_key:
        raise RuntimeError("RESPAN_API_KEY must be set in the repo root .env file")
    return api_key


def respan_base_url() -> str:
    return os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/")


def respan_gateway_api_base_url() -> str:
    base_url = respan_base_url()
    if base_url.endswith("/api"):
        return base_url
    return f"{base_url}/api"


def model_name() -> str:
    configured_model = os.getenv("GROQ_MODEL") or os.getenv("RESPAN_GROQ_MODEL")
    if configured_model:
        return configured_model
    return DEFAULT_DIRECT_GROQ_MODEL if groq_api_key() else DEFAULT_GATEWAY_MODEL


def make_respan(example_name: str) -> Respan:
    api_key = require_respan_api_key()
    return Respan(
        api_key=api_key,
        base_url=respan_base_url(),
        app_name="groq-examples",
        instrumentations=[GroqInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={"integration": "groq", "example": example_name},
    )


def groq_api_key() -> str | None:
    return os.getenv("GROQ_API_KEY")


class RespanGroqGatewayTransport(httpx.BaseTransport):
    def __init__(self) -> None:
        self._transport = httpx.HTTPTransport()

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/openai/v1/chat/completions"):
            request.url = request.url.copy_with(
                path=path.replace(
                    "/openai/v1/chat/completions",
                    "/chat/completions",
                    1,
                )
            )
        return self._transport.handle_request(request)

    def close(self) -> None:
        self._transport.close()


def make_client() -> Groq:
    direct_api_key = groq_api_key()
    if direct_api_key:
        return Groq(api_key=direct_api_key)

    return Groq(
        api_key=require_respan_api_key(),
        base_url=respan_gateway_api_base_url(),
        http_client=httpx.Client(transport=RespanGroqGatewayTransport()),
    )


def workflow_name(example_name: str) -> str:
    normalized_name = example_name.replace("-", "_")
    return f"groq_{normalized_name}"


def make_custom_identifier(example_name: str) -> str:
    return f"groq-{example_name}-{uuid4().hex[:8]}"


@contextmanager
def example_attributes(example_name: str, custom_identifier: str | None = None):
    custom_identifier = custom_identifier or make_custom_identifier(example_name)
    current_workflow_name = workflow_name(example_name)
    with propagate_attributes(
        custom_identifier=custom_identifier,
        trace_group_identifier=current_workflow_name,
        metadata={
            "example": example_name,
            "run_id": custom_identifier,
            "workflow_name": current_workflow_name,
        },
    ):
        yield custom_identifier


def client_mode() -> str:
    return "direct-groq" if groq_api_key() else "respan-gateway"


def print_result(example_name: str, custom_identifier: str, text: str) -> None:
    print(f"example={example_name}")
    print(f"custom_identifier={custom_identifier}")
    print(f"client_mode={client_mode()}")
    print(text.strip())
