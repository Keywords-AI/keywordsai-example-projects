from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from mistralai.client import Mistral
from respan import Respan, propagate_attributes
from respan_instrumentation_mistralai import MistralAIInstrumentor

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MISTRAL_MODEL = "mistral/mistral-small"


def load_root_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=True)


def require_respan_api_key() -> str:
    load_root_env()
    api_key = os.getenv("RESPAN_API_KEY")
    if not api_key:
        raise RuntimeError("RESPAN_API_KEY must be set in the repo root .env file")
    return api_key


def gateway_api_key() -> str:
    return os.getenv("RESPAN_GATEWAY_API_KEY") or require_respan_api_key()


def respan_base_url() -> str:
    return os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/")


def model_name() -> str:
    configured_model = os.getenv("RESPAN_MISTRALAI_MODEL")
    if configured_model:
        return configured_model
    if mistral_api_key():
        return os.getenv("MISTRALAI_MODEL", DEFAULT_MISTRAL_MODEL)
    return os.getenv("RESPAN_MODEL", DEFAULT_MISTRAL_MODEL)


def make_respan(example_name: str) -> Respan:
    api_key = require_respan_api_key()
    return Respan(
        api_key=api_key,
        base_url=respan_base_url(),
        app_name="mistralai-examples",
        instrumentations=[MistralAIInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={"integration": "mistralai", "example": example_name},
    )


def mistral_api_key() -> str | None:
    return os.getenv("MISTRAL_API_KEY")


def make_client() -> Mistral:
    direct_api_key = mistral_api_key()
    if direct_api_key:
        return Mistral(api_key=direct_api_key)

    return Mistral(
        api_key=gateway_api_key(),
        server_url=respan_base_url(),
    )


def workflow_name(example_name: str) -> str:
    normalized_name = example_name.replace("-", "_")
    return f"mistralai_{normalized_name}"


def make_custom_identifier(example_name: str) -> str:
    return f"mistralai-{example_name}-{uuid4().hex[:8]}"


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
    return "direct-mistral" if mistral_api_key() else "respan-gateway"


def content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks = []
        for item in content:
            text = getattr(item, "text", None)
            if text is None and isinstance(item, dict):
                text = item.get("text") or item.get("content")
            chunks.append(str(text if text is not None else item))
        return "".join(chunks)
    return str(content)


def print_result(example_name: str, custom_identifier: str, text: str) -> None:
    print(f"example={example_name}")
    print(f"workflow_name={workflow_name(example_name)}")
    print(f"custom_identifier={custom_identifier}")
    print(f"client_mode={client_mode()}")
    print(f"model={model_name()}")
    print(text.strip())
