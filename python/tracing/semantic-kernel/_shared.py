"""Shared helpers for the Semantic Kernel Respan examples."""

from __future__ import annotations

import os
from collections.abc import Iterable
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from respan import Respan
from respan_instrumentation_semantic_kernel import SemanticKernelInstrumentor
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion


DEFAULT_RUN_ID = datetime.now(timezone.utc).strftime("semantic-kernel-%Y%m%d-%H%M%S")


@dataclass(frozen=True)
class GatewaySettings:
    api_key: str
    base_url: str
    model: str


def load_repo_env() -> None:
    """Load environment variables from respan-example-projects/.env."""
    repo_root = Path(__file__).resolve().parents[3]
    load_dotenv(repo_root / ".env", override=True)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} must be set in respan-example-projects/.env")
    return value


def gateway_settings() -> GatewaySettings:
    load_repo_env()
    api_key = os.getenv("RESPAN_GATEWAY_API_KEY") or require_env("RESPAN_API_KEY")
    base_url = os.getenv(
        "RESPAN_GATEWAY_BASE_URL",
        os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
    )
    return GatewaySettings(
        api_key=api_key,
        base_url=base_url,
        model=os.getenv("RESPAN_MODEL", "gpt-4o-mini"),
    )


def create_respan(app_name: str) -> Respan:
    load_repo_env()
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", DEFAULT_RUN_ID)
    return Respan(
        app_name=app_name,
        api_key=require_env("RESPAN_API_KEY"),
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        instrumentations=[SemanticKernelInstrumentor()],
        is_batching_enabled=False,
        metadata={
            "integration": "semantic-kernel",
            "example": app_name,
            "run_id": run_id,
        },
        environment="examples",
    )


def create_kernel(*, with_chat_service: bool = True) -> Kernel:
    kernel = Kernel()
    if not with_chat_service:
        return kernel

    settings = gateway_settings()
    client = AsyncOpenAI(
        api_key=settings.api_key,
        base_url=settings.base_url,
    )
    kernel.add_service(
        OpenAIChatCompletion(
            ai_model_id=settings.model,
            service_id="chat",
            async_client=client,
        )
    )
    return kernel


def print_result(label: str, value: object) -> None:
    print(f"{label}: {value}")


def _env_paths_from(*, start: Path) -> Iterable[Path]:
    current = start.resolve()
    chain: list[Path] = []
    while True:
        chain.append(current)
        if (current / ".git").exists():
            break
        if current.parent == current:
            break
        current = current.parent

    seen: set[Path] = set()
    for directory in reversed(chain):
        env_path = directory / ".env"
        if env_path.exists() and env_path not in seen:
            seen.add(env_path)
            yield env_path
