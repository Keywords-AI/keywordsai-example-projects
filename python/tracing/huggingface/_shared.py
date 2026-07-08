"""Shared helpers for Hugging Face tracing examples."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_huggingface import HuggingFaceInstrumentor

REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(REPO_ROOT / ".env", override=True)

DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_CUSTOMER_IDENTIFIER = "huggingface-example-user"
DEFAULT_RUN_ID = datetime.now(timezone.utc).strftime("huggingface-%Y%m%d-%H%M%S")


def install_compatible_transformers_module() -> type:
    """Install a small module that matches the wrapped Transformers API."""

    transformers_module = ModuleType("transformers")

    class TextGenerationPipeline:
        def __init__(
            self,
            *,
            model_name: str = "respan-compatible-tiny-generator",
            model_type: str = "causal-lm",
            **forward_params: Any,
        ) -> None:
            self.model = SimpleNamespace(
                config=SimpleNamespace(
                    name_or_path=model_name,
                    model_type=model_type,
                )
            )
            self._forward_params = {
                "temperature": 0.4,
                "top_p": 0.92,
                "max_length": 48,
                "repetition_penalty": 1.05,
                **forward_params,
            }

        def __call__(self, prompts: str | list[str], **kwargs: Any) -> list[dict[str, str]]:
            self._forward_params.update(
                {
                    key: value
                    for key, value in kwargs.items()
                    if key in {"temperature", "top_p", "max_length", "repetition_penalty"}
                }
            )
            prompt_list = [prompts] if isinstance(prompts, str) else list(prompts)
            return [
                {
                    "generated_text": (
                        f"{prompt} Respan captured this Hugging Face text "
                        f"generation call."
                    )
                }
                for prompt in prompt_list
            ]

    transformers_module.TextGenerationPipeline = TextGenerationPipeline
    sys.modules["transformers"] = transformers_module
    return TextGenerationPipeline


def build_respan(
    *,
    example_name: str,
    workflow_name: str,
    trace_content: bool = True,
) -> Respan:
    api_key = _required_env("RESPAN_API_KEY")
    base_url = os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL)
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", DEFAULT_RUN_ID)
    os.environ["TRACELOOP_TRACE_CONTENT"] = "true" if trace_content else "false"

    return Respan(
        api_key=api_key,
        base_url=base_url,
        app_name=f"huggingface-{example_name}",
        instrumentations=[HuggingFaceInstrumentor()],
        customer_identifier=os.getenv(
            "RESPAN_EXAMPLE_CUSTOMER_IDENTIFIER",
            DEFAULT_CUSTOMER_IDENTIFIER,
        ),
        metadata={
            "example": example_name,
            "run_id": run_id,
            "workflow_name": workflow_name,
        },
        environment="examples",
        is_batching_enabled=False,
        log_level=os.getenv("RESPAN_LOG_LEVEL", "WARNING"),
    )


def print_result(label: str, value: Any) -> None:
    print(f"{label}: {value}")


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"Missing {name} in {REPO_ROOT / '.env'}")
