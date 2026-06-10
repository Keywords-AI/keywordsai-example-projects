from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from portkey_ai import AsyncPortkey, Portkey
from respan import Respan, propagate_attributes
from respan_instrumentation_portkey import PortkeyInstrumentor

from _local_gateway import local_gateway_base_url

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_MODEL = "gpt-4.1-nano"


def load_root_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=True)


def env_value(name: str) -> str | None:
    value = os.getenv(name)
    if not value:
        return None
    value = value.strip()
    if not value or value.upper() == name:
        return None
    if value.lower() in {"none", "null", "your_api_key_here"}:
        return None
    return value


def require_env(name: str) -> str:
    value = env_value(name)
    if not value:
        raise RuntimeError(f"{name} must be set in the repo root .env file")
    return value


def respan_api_key() -> str:
    load_root_env()
    return require_env("RESPAN_API_KEY")


def respan_base_url() -> str:
    return os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/")


def gateway_api_key() -> str:
    return respan_api_key() or require_env("RESPAN_GATEWAY_API_KEY")


def gateway_base_url() -> str:
    return (
        os.getenv("RESPAN_GATEWAY_BASE_URL")
        or os.getenv("RESPAN_BASE_URL")
        or DEFAULT_RESPAN_BASE_URL
    ).rstrip("/")


def model_name() -> str:
    return os.getenv("PORTKEY_MODEL") or os.getenv("RESPAN_MODEL", DEFAULT_MODEL)


def workflow_name(example_name: str) -> str:
    normalized_name = example_name.replace("-", "_")
    return f"portkey_{normalized_name}"


def make_custom_identifier(example_name: str) -> str:
    return f"portkey-{example_name}-{uuid4().hex[:8]}"


def make_respan(example_name: str) -> Respan:
    return Respan(
        api_key=respan_api_key(),
        base_url=respan_base_url(),
        app_name="portkey-examples",
        instrumentations=[PortkeyInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={"integration": "portkey", "example": example_name},
    )


def _portkey_client_kwargs() -> dict[str, object]:
    load_root_env()
    portkey_api_key = env_value("PORTKEY_API_KEY")
    if portkey_api_key:
        kwargs: dict[str, object] = {"api_key": portkey_api_key}
        if portkey_base_url := env_value("PORTKEY_BASE_URL"):
            kwargs["base_url"] = portkey_base_url.rstrip("/")
        if portkey_provider := env_value("PORTKEY_PROVIDER"):
            kwargs["provider"] = portkey_provider
        if portkey_config := env_value("PORTKEY_CONFIG"):
            kwargs["config"] = portkey_config
        return kwargs

    if env_value("PORTKEY_EXAMPLE_USE_LIVE_GATEWAY"):
        return {
            "api_key": gateway_api_key(),
            "base_url": gateway_base_url(),
        }

    if openai_api_key := env_value("OPENAI_API_KEY"):
        if env_value("PORTKEY_EXAMPLE_USE_OPENAI"):
            return {
                "api_key": openai_api_key,
                "base_url": env_value("OPENAI_BASE_URL") or "https://api.openai.com/v1",
            }

    return {
        "api_key": "local-portkey-example-key",
        "base_url": local_gateway_base_url(),
    }


def make_client() -> Portkey:
    return Portkey(**_portkey_client_kwargs())


def make_async_client() -> AsyncPortkey:
    return AsyncPortkey(**_portkey_client_kwargs())


def client_mode() -> str:
    if env_value("PORTKEY_API_KEY"):
        return "portkey-gateway"
    if env_value("PORTKEY_EXAMPLE_USE_LIVE_GATEWAY"):
        return "respan-gateway"
    if env_value("PORTKEY_EXAMPLE_USE_OPENAI") and env_value("OPENAI_API_KEY"):
        return "openai-api"
    return "local-openai-compatible"


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


def print_result(example_name: str, custom_identifier: str, text: str) -> None:
    print(f"example={example_name}")
    print(f"custom_identifier={custom_identifier}")
    print(f"workflow_name={workflow_name(example_name)}")
    print(f"client_mode={client_mode()}")
    print(text.strip())
