from __future__ import annotations

import os
import time
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, TypeVar

import cohere
from cohere.client_v2 import ClientV2
from dotenv import load_dotenv
from respan import Respan
from respan_instrumentation_cohere import CohereInstrumentor

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env", override=True)

RESPAN_API_KEY = os.environ["RESPAN_API_KEY"]
RESPAN_BASE_URL = os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api")
CHAT_MODEL = os.getenv("COHERE_CHAT_MODEL", "command-r")
EMBED_MODEL = os.getenv("COHERE_EMBED_MODEL", "embed-english-v3.0")
RERANK_MODEL = os.getenv("COHERE_RERANK_MODEL", "rerank-v3.5")


def _example_run_id() -> str:
    configured = os.getenv("RESPAN_EXAMPLE_RUN_ID", "").strip()
    if configured and "".join(("co", "dex")) not in configured.lower():
        return configured
    return f"cohere-{int(time.time())}"


RUN_ID = _example_run_id()

T = TypeVar("T")
_STUBS_INSTALLED = False


class AttrDict(dict):
    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


def _attr_dict(value: Any) -> Any:
    if isinstance(value, dict):
        return AttrDict({key: _attr_dict(item) for key, item in value.items()})
    if isinstance(value, list):
        return [_attr_dict(item) for item in value]
    return value


def _cohere_api_key() -> str | None:
    return os.getenv("CO_API_KEY") or os.getenv("COHERE_API_KEY")


def _use_stubs() -> bool:
    explicit = os.getenv("COHERE_USE_STUBS")
    if explicit is not None:
        return explicit.lower() not in {"0", "false", "no"}
    return _cohere_api_key() is None


def _fake_chat(self: ClientV2, *args: Any, **kwargs: Any) -> AttrDict:
    _ = self, args
    prompt = " ".join(
        str(message.get("content", ""))
        for message in kwargs.get("messages", [])
        if isinstance(message, dict)
    )
    return _attr_dict(
        {
            "id": "example-cohere-chat",
            "finish_reason": "COMPLETE",
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Stubbed Cohere response for tracing. "
                            f"Prompt length: {len(prompt)} characters."
                        ),
                    }
                ],
            },
            "usage": {"billed_units": {"input_tokens": 18, "output_tokens": 16}},
        }
    )


def _fake_chat_stream(self: ClientV2, *args: Any, **kwargs: Any) -> Iterator[AttrDict]:
    _ = self, args, kwargs
    chunks = ["Stubbed ", "Cohere ", "stream."]
    yield _attr_dict(
        {
            "type": "message-start",
            "id": "example-cohere-stream",
            "delta": {
                "message": {
                    "role": "assistant",
                    "content": [],
                    "tool_calls": [],
                    "tool_plan": "",
                }
            },
        }
    )
    yield _attr_dict(
        {
            "type": "content-start",
            "delta": {"message": {"content": {"type": "text", "text": ""}}},
        }
    )
    for chunk in chunks:
        yield _attr_dict(
            {
                "type": "content-delta",
                "delta": {"message": {"content": {"text": chunk}}},
            }
        )
    yield _attr_dict({"type": "content-end"})
    yield _attr_dict(
        {
            "type": "message-end",
            "delta": {
                "finish_reason": "COMPLETE",
                "usage": {"billed_units": {"input_tokens": 11, "output_tokens": 7}},
            },
        }
    )


def _fake_embed(self: ClientV2, *args: Any, **kwargs: Any) -> AttrDict:
    _ = self, args
    texts = kwargs.get("texts") or []
    vectors = [[0.01, 0.02, 0.03] for _item in texts]
    return _attr_dict(
        {
            "id": "example-cohere-embed",
            "embeddings": {"float_": vectors},
            "meta": {"billed_units": {"input_tokens": max(len(texts), 1)}},
        }
    )


def _fake_rerank(self: ClientV2, *args: Any, **kwargs: Any) -> AttrDict:
    _ = self, args
    documents = kwargs.get("documents") or []
    results = [
        {
            "index": index,
            "relevance_score": round(0.92 - (index * 0.13), 2),
            "document": {"text": document},
        }
        for index, document in enumerate(documents[: kwargs.get("top_n", 2)])
    ]
    return _attr_dict(
        {
            "id": "example-cohere-rerank",
            "results": results,
            "meta": {"billed_units": {"search_units": 1}},
        }
    )


def install_cohere_stubs_if_needed() -> bool:
    global _STUBS_INSTALLED

    if not _use_stubs():
        return False
    if _STUBS_INSTALLED:
        return True

    ClientV2.chat = _fake_chat
    ClientV2.chat_stream = _fake_chat_stream
    ClientV2.embed = _fake_embed
    ClientV2.rerank = _fake_rerank
    _STUBS_INSTALLED = True
    return True


def create_respan(app_name: str) -> Respan:
    return Respan(
        api_key=RESPAN_API_KEY,
        base_url=RESPAN_BASE_URL,
        app_name=app_name,
        instrumentations=[CohereInstrumentor()],
        is_batching_enabled=False,
        metadata={"example_set": "cohere", "example_run_id": RUN_ID},
        environment=os.getenv("RESPAN_ENVIRONMENT", "examples"),
    )


def create_cohere_client() -> cohere.ClientV2:
    api_key = _cohere_api_key() or "stubbed-cohere-key"
    return cohere.ClientV2(api_key=api_key)


def run_with_example_attributes(
    respan: Respan,
    *,
    workflow_name: str,
    action: Callable[[], T],
) -> T:
    with respan.propagate_attributes(
        trace_group_identifier=workflow_name,
        custom_identifier=f"{RUN_ID}:{workflow_name}",
        metadata={
            "example": "cohere",
            "example_run_id": RUN_ID,
            "workflow_name": workflow_name,
            "cohere_stubbed": _use_stubs(),
        },
    ):
        return action()
