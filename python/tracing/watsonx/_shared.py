from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from respan import Respan, propagate_attributes
from respan_instrumentation_watsonx import WatsonxInstrumentor

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
DEFAULT_WATSONX_URL = "https://us-south.ml.cloud.ibm.com"
DEFAULT_MODEL = "ibm/granite-3-8b-instruct"
DEFAULT_EMBEDDING_MODEL = "ibm/slate-125m-english-rtrvr"


def load_root_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def require_trace_api_key() -> str:
    load_root_env()
    api_key = _first_env("RESPAN_API_KEY", "RESPAN_GATEWAY_API_KEY")
    if not api_key:
        raise RuntimeError(
            "RESPAN_API_KEY or RESPAN_GATEWAY_API_KEY must be set in the repo root .env file"
        )
    return api_key


def respan_base_url() -> str:
    return os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/")


def model_name() -> str:
    return os.getenv("WATSONX_MODEL_ID", DEFAULT_MODEL)


def embedding_model_name() -> str:
    return os.getenv("WATSONX_EMBEDDING_MODEL_ID", DEFAULT_EMBEDDING_MODEL)


def watsonx_live_mode() -> bool:
    load_root_env()
    has_key = bool(_first_env("WATSONX_API_KEY", "IBM_CLOUD_API_KEY"))
    has_scope = bool(_first_env("WATSONX_PROJECT_ID", "WATSONX_SPACE_ID"))
    return has_key and has_scope


def example_run_id() -> str:
    return os.getenv("RESPAN_EXAMPLE_RUN_ID") or f"watsonx-{uuid4().hex[:12]}"


def _offline_model_id(self) -> str:
    return getattr(self, "_model_id", model_name())


def _offline_embedding_model_id(self) -> str:
    return getattr(self, "_model_id", embedding_model_name())


def _install_offline_backend() -> None:
    from ibm_watsonx_ai.foundation_models import Embeddings, ModelInference

    if getattr(ModelInference, "_respan_offline_backend", False):
        return

    def generate(self, prompt=None, **kwargs):
        return {
            "model_id": _offline_model_id(self),
            "results": [
                {
                    "generated_text": f"Offline Watsonx generated text for: {prompt}",
                    "input_token_count": 12,
                    "generated_token_count": 9,
                }
            ],
        }

    def generate_text(self, prompt=None, **kwargs):
        if prompt == "RESPAN_EXPECTED_WATSONX_ERROR":
            error = RuntimeError("Watsonx deterministic provider limit")
            error.status_code = 429
            raise error
        return f"Offline Watsonx text response for: {prompt}"

    def generate_text_stream(self, prompt=None, **kwargs):
        yield {"results": [{"generated_text": "Offline ", "input_token_count": 8}]}
        yield {
            "results": [
                {
                    "generated_text": "Watsonx stream response.",
                    "generated_token_count": 5,
                }
            ]
        }

    async def agenerate(self, prompt=None, **kwargs):
        return {
            "model_id": _offline_model_id(self),
            "results": [
                {
                    "generated_text": f"Offline async Watsonx generation for: {prompt}",
                    "input_token_count": 10,
                    "generated_token_count": 8,
                }
            ],
        }

    async def agenerate_stream(self, prompt=None, **kwargs):
        async def chunks():
            yield {
                "results": [
                    {"generated_text": "Offline async ", "input_token_count": 7}
                ]
            }
            yield {
                "results": [
                    {"generated_text": "Watsonx stream.", "generated_token_count": 4}
                ]
            }

        return chunks()

    def chat(self, messages, **kwargs):
        if messages and messages[-1].get("role") == "tool":
            return {
                "model_id": _offline_model_id(self),
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "Tokyo is sunny and 24°C.",
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 22,
                    "completion_tokens": 7,
                    "total_tokens": 29,
                },
            }
        return {
            "model_id": _offline_model_id(self),
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Offline Watsonx chat used the weather tool and returned a concise answer.",
                        "tool_calls": [
                            {
                                "id": "call_weather_tokyo",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": {"city": "Tokyo"},
                                },
                            }
                        ],
                    }
                }
            ],
            "usage": {"prompt_tokens": 18, "completion_tokens": 13, "total_tokens": 31},
        }

    def chat_stream(self, messages, **kwargs):
        yield {"choices": [{"delta": {"content": "Offline chat "}}]}
        yield {
            "choices": [{"delta": {"content": "stream response."}}],
            "usage": {"prompt_tokens": 6, "completion_tokens": 4, "total_tokens": 10},
        }

    async def achat(self, messages, **kwargs):
        return {
            "model_id": _offline_model_id(self),
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Offline async chat response.",
                    }
                }
            ],
            "usage": {"prompt_tokens": 7, "completion_tokens": 5, "total_tokens": 12},
        }

    async def achat_stream(self, messages, **kwargs):
        async def chunks():
            yield {"choices": [{"delta": {"content": "Offline async "}}]}
            yield {
                "choices": [{"delta": {"content": "chat stream."}}],
                "usage": {
                    "prompt_tokens": 5,
                    "completion_tokens": 4,
                    "total_tokens": 9,
                },
            }

        return chunks()

    def embeddings_generate(self, inputs, **kwargs):
        return {
            "model_id": _offline_embedding_model_id(self),
            "results": [
                {"input": text, "embedding": [0.01, 0.02, 0.03]} for text in inputs
            ],
            "input_token_count": 11,
        }

    def embed_documents(self, texts, **kwargs):
        return [[0.01, 0.02, 0.03] for _ in texts]

    def embed_query(self, text, **kwargs):
        return [0.04, 0.05, 0.06]

    async def aembeddings_generate(self, inputs, **kwargs):
        return embeddings_generate(self, inputs, **kwargs)

    async def aembed_documents(self, texts, **kwargs):
        return embed_documents(self, texts, **kwargs)

    async def aembed_query(self, text, **kwargs):
        return embed_query(self, text, **kwargs)

    ModelInference.generate = generate
    ModelInference.generate_text = generate_text
    ModelInference.generate_text_stream = generate_text_stream
    ModelInference.agenerate = agenerate
    ModelInference.agenerate_stream = agenerate_stream
    ModelInference.chat = chat
    ModelInference.chat_stream = chat_stream
    ModelInference.achat = achat
    ModelInference.achat_stream = achat_stream
    ModelInference._respan_offline_backend = True

    Embeddings.generate = embeddings_generate
    Embeddings.embed_documents = embed_documents
    Embeddings.embed_query = embed_query
    Embeddings.agenerate = aembeddings_generate
    Embeddings.aembed_documents = aembed_documents
    Embeddings.aembed_query = aembed_query
    Embeddings._respan_offline_backend = True


def _new_uninitialized(instance_class, model_id: str):
    instance = object.__new__(instance_class)
    object.__setattr__(instance, "_model_id", model_id)
    return instance


def make_model(*, force_offline: bool = False):
    load_root_env()
    from ibm_watsonx_ai.foundation_models import ModelInference

    if force_offline or not watsonx_live_mode():
        _install_offline_backend()
        return _new_uninitialized(ModelInference, model_name())

    from ibm_watsonx_ai import Credentials

    credentials = Credentials(
        api_key=_first_env("WATSONX_API_KEY", "IBM_CLOUD_API_KEY"),
        url=os.getenv("WATSONX_URL", DEFAULT_WATSONX_URL),
    )
    kwargs = {
        "model_id": model_name(),
        "credentials": credentials,
        "validate": False,
    }
    project_id = os.getenv("WATSONX_PROJECT_ID")
    space_id = os.getenv("WATSONX_SPACE_ID")
    if project_id:
        kwargs["project_id"] = project_id
    if space_id:
        kwargs["space_id"] = space_id
    return ModelInference(**kwargs)


def make_embeddings():
    load_root_env()
    from ibm_watsonx_ai.foundation_models import Embeddings

    if not watsonx_live_mode():
        _install_offline_backend()
        return _new_uninitialized(Embeddings, embedding_model_name())

    from ibm_watsonx_ai import Credentials

    credentials = Credentials(
        api_key=_first_env("WATSONX_API_KEY", "IBM_CLOUD_API_KEY"),
        url=os.getenv("WATSONX_URL", DEFAULT_WATSONX_URL),
    )
    kwargs = {
        "model_id": embedding_model_name(),
        "credentials": credentials,
    }
    project_id = os.getenv("WATSONX_PROJECT_ID")
    space_id = os.getenv("WATSONX_SPACE_ID")
    if project_id:
        kwargs["project_id"] = project_id
    if space_id:
        kwargs["space_id"] = space_id
    return Embeddings(**kwargs)


def make_respan(example_name: str) -> Respan:
    if not watsonx_live_mode():
        _install_offline_backend()
    return Respan(
        api_key=require_trace_api_key(),
        base_url=respan_base_url(),
        app_name="watsonx-examples",
        instrumentations=[WatsonxInstrumentor()],
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={
            "integration": "watsonx",
            "example": example_name,
            "example_set": "watsonx",
            "example_run_id": example_run_id(),
            "run_id": example_run_id(),
        },
        is_batching_enabled=False,
    )


def workflow_name(example_name: str) -> str:
    return f"watsonx_{example_name.replace('-', '_')}"


def make_custom_identifier(example_name: str) -> str:
    return f"watsonx-{example_name}-{uuid4().hex[:8]}"


@contextmanager
def example_attributes(example_name: str, custom_identifier: str | None = None):
    custom_identifier = custom_identifier or make_custom_identifier(example_name)
    current_workflow_name = workflow_name(example_name)
    with propagate_attributes(
        custom_identifier=custom_identifier,
        trace_group_identifier=current_workflow_name,
        metadata={
            "example": example_name,
            "example_set": "watsonx",
            "example_run_id": example_run_id(),
            "run_id": example_run_id(),
            "workflow_name": current_workflow_name,
            "client_mode": client_mode(),
        },
    ):
        yield custom_identifier


def client_mode() -> str:
    return "direct-watsonx" if watsonx_live_mode() else "offline-watsonx"


def generated_text(response) -> str:
    if isinstance(response, str):
        return response
    results = response.get("results", []) if isinstance(response, dict) else []
    if results:
        return str(results[0].get("generated_text", ""))
    return str(response or "")


def chat_text(response) -> str:
    choices = response.get("choices", []) if isinstance(response, dict) else []
    if not choices:
        return str(response or "")
    message = choices[0].get("message", {})
    return str(message.get("content", ""))


def stream_chunk_text(chunk) -> str:
    if isinstance(chunk, str):
        return chunk
    if not isinstance(chunk, dict):
        return str(chunk or "")
    choices = chunk.get("choices", [])
    if choices:
        delta = choices[0].get("delta", {})
        if delta.get("content"):
            return str(delta["content"])
    results = chunk.get("results", [])
    if results:
        return str(results[0].get("generated_text", ""))
    return str(chunk.get("generated_text", ""))


def print_lookup(example_name: str, custom_identifier: str, output) -> None:
    print(f"example={example_name}")
    print(f"custom_identifier={custom_identifier}")
    print(f"workflow_name={workflow_name(example_name)}")
    print(f"client_mode={client_mode()}")
    print(f"example_run_id={example_run_id()}")
    if isinstance(output, str):
        print(output.strip())
    else:
        print(json.dumps(output, sort_keys=True))


def close_provider(value) -> None:
    close = getattr(value, "close", None)
    if callable(close):
        close()
