"""Shared setup for Vertex AI tracing examples."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = REPO_ROOT / ".env"


def load_repo_env() -> None:
    load_dotenv(ENV_PATH, override=True)


def should_use_real_vertexai() -> bool:
    if os.getenv("RESPAN_VERTEXAI_EXAMPLE_MODE", "").lower() == "fake":
        return False
    return all(
        os.getenv(name)
        for name in (
            "GOOGLE_CLOUD_PROJECT",
            "GOOGLE_CLOUD_LOCATION",
            "GOOGLE_APPLICATION_CREDENTIALS",
        )
    )


def prepare_vertexai_runtime() -> bool:
    load_repo_env()
    if not should_use_real_vertexai():
        from _fake_vertexai import install_fake_vertexai

        install_fake_vertexai()
        return False

    import vertexai

    vertexai.init(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ["GOOGLE_CLOUD_LOCATION"],
    )
    return True


def model_name() -> str:
    return os.getenv("VERTEXAI_MODEL", "gemini-2.0-flash")
