"""Shared helpers for the Agno Respan examples."""

from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_agno import AgnoInstrumentor


@dataclass(frozen=True)
class GatewaySettings:
    api_key: str
    base_url: str
    model: str


def load_gateway_settings() -> GatewaySettings:
    _load_env_files()
    api_key = os.environ["RESPAN_API_KEY"]
    base_url = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_BASE_URL"] = base_url
    return GatewaySettings(
        api_key=api_key,
        base_url=base_url,
        model=os.getenv("RESPAN_MODEL", "gpt-4o-mini"),
    )


def create_respan(*, app_name: str, **kwargs) -> tuple[Respan, GatewaySettings]:
    settings = load_gateway_settings()
    respan = Respan(
        app_name=app_name,
        api_key=settings.api_key,
        base_url=settings.base_url,
        instrumentations=[AgnoInstrumentor()],
        **kwargs,
    )
    return respan, settings


def build_agent(
    *,
    name: str,
    instructions: str | list[str] | None = None,
    tools: list | None = None,
) -> Agent:
    settings = load_gateway_settings()
    return Agent(
        name=name,
        model=OpenAIChat(id=settings.model),
        instructions=instructions,
        tools=tools,
    )


def print_result(label: str, value: object) -> None:
    print(f"{label}: {value}")


def _load_env_files() -> None:
    for env_path in _env_paths_from(start=Path(__file__).resolve().parent):
        load_dotenv(env_path, override=True)
    for env_path in _env_paths_from(start=Path.cwd()):
        load_dotenv(env_path, override=True)


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
