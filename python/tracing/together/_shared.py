from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_together import TogetherInstrumentor
from together import APIConnectionError, APIStatusError, APITimeoutError, AsyncTogether, Together

EXAMPLE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EXAMPLE_DIR.parents[2]

DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_DIRECT_CHAT_MODEL = "meta-llama/Llama-3.2-3B-Instruct-Turbo"
DEFAULT_GATEWAY_CHAT_MODEL = "openai/gpt-4.1-mini"
DEFAULT_COMPLETION_MODEL = DEFAULT_DIRECT_CHAT_MODEL
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
DEFAULT_RERANK_MODEL = "Salesforce/Llama-Rank-v1"
DEFAULT_IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell-Free"
SDK_UNAVAILABLE_ERRORS = (APIConnectionError, APIStatusError, APITimeoutError)


def load_root_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=True)


def require_env(*names: str) -> str:
    load_root_env()
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    raise RuntimeError(f"One of {', '.join(names)} must be set in the repo root .env")


def respan_api_key() -> str:
    return require_env("RESPAN_API_KEY", "RESPAN_GATEWAY_API_KEY")


def gateway_api_key() -> str:
    return os.getenv("TOGETHER_API_KEY") or require_env(
        "RESPAN_GATEWAY_API_KEY",
        "RESPAN_API_KEY",
    )


def respan_base_url() -> str:
    load_root_env()
    return os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/")


def gateway_base_url() -> str | None:
    load_root_env()
    if os.getenv("TOGETHER_API_KEY"):
        return os.getenv("TOGETHER_BASE_URL")
    return (
        os.getenv("RESPAN_GATEWAY_BASE_URL")
        or os.getenv("RESPAN_BASE_URL")
        or DEFAULT_RESPAN_BASE_URL
    ).rstrip("/")


def client_mode() -> str:
    return "direct-together" if os.getenv("TOGETHER_API_KEY") else "respan-gateway"


def model_name() -> str:
    load_root_env()
    default_model = (
        DEFAULT_DIRECT_CHAT_MODEL
        if os.getenv("TOGETHER_API_KEY")
        else DEFAULT_GATEWAY_CHAT_MODEL
    )
    return os.getenv("RESPAN_TOGETHER_MODEL", default_model)


def completion_model_name() -> str:
    load_root_env()
    return os.getenv("RESPAN_TOGETHER_COMPLETION_MODEL", DEFAULT_COMPLETION_MODEL)


def embedding_model_name() -> str:
    load_root_env()
    return os.getenv("RESPAN_TOGETHER_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)


def rerank_model_name() -> str:
    load_root_env()
    return os.getenv("RESPAN_TOGETHER_RERANK_MODEL", DEFAULT_RERANK_MODEL)


def image_model_name() -> str:
    load_root_env()
    return os.getenv("RESPAN_TOGETHER_IMAGE_MODEL", DEFAULT_IMAGE_MODEL)


def make_client() -> Together:
    base_url = gateway_base_url()
    kwargs: dict[str, Any] = {"api_key": gateway_api_key()}
    if base_url:
        kwargs["base_url"] = base_url
    return Together(**kwargs)


def make_async_client() -> AsyncTogether:
    base_url = gateway_base_url()
    kwargs: dict[str, Any] = {"api_key": gateway_api_key()}
    if base_url:
        kwargs["base_url"] = base_url
    return AsyncTogether(**kwargs)


def make_respan(example_name: str) -> Respan:
    return Respan(
        api_key=respan_api_key(),
        base_url=respan_base_url(),
        app_name="together-examples",
        instrumentations=[TogetherInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={"integration": "together", "example": example_name},
    )


def workflow_name(example_name: str) -> str:
    return f"together_{example_name.replace('-', '_')}"


def make_custom_identifier(example_name: str) -> str:
    return f"together-{example_name}-{uuid4().hex[:8]}"


@contextmanager
def example_attributes(example_name: str, custom_identifier: str | None = None):
    custom_identifier = custom_identifier or make_custom_identifier(example_name)
    current_workflow_name = workflow_name(example_name)
    with propagate_attributes(
        custom_identifier=custom_identifier,
        trace_group_identifier=current_workflow_name,
        customer_identifier="together-example-user",
        thread_identifier=f"{custom_identifier}-thread",
        metadata={
            "example": example_name,
            "run_id": custom_identifier,
            "workflow_name": current_workflow_name,
            "client_mode": client_mode(),
        },
    ):
        yield custom_identifier


def first_message_text(response: Any) -> str:
    choices = getattr(response, "choices", None) or []
    if not choices:
        return ""
    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    text = getattr(choices[0], "text", None)
    return text if isinstance(text, str) else ""


def first_text_completion(response: Any) -> str:
    choices = getattr(response, "choices", None) or []
    if not choices:
        return ""
    text = getattr(choices[0], "text", None)
    return text if isinstance(text, str) else ""


def print_start(example_name: str, custom_identifier: str) -> None:
    print(f"custom_identifier={custom_identifier}", flush=True)
    print(f"workflow_name={workflow_name(example_name)}", flush=True)
    print(f"client_mode={client_mode()}", flush=True)


def print_result(example_name: str, custom_identifier: str, text: str) -> None:
    print(f"example={example_name}")
    print(f"custom_identifier={custom_identifier}")
    print(f"workflow_name={workflow_name(example_name)}")
    print(f"client_mode={client_mode()}")
    print(text.strip())


def unavailable_text(feature: str, exc: BaseException) -> str:
    detail = str(exc).replace("\n", " ")
    if len(detail) > 240:
        detail = f"{detail[:237]}..."
    return f"{feature} unavailable for {client_mode()}: {exc.__class__.__name__}: {detail}"


def close_async_client(client: AsyncTogether) -> None:
    close = getattr(client, "close", None)
    if callable(close):
        result = close()
        if hasattr(result, "__await__"):
            raise RuntimeError("Use await client.close() for async clients")
