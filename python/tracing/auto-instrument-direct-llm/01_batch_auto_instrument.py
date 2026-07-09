from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from pathlib import Path
from typing import Callable, Optional
from uuid import uuid4

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESPAN_BASE_URL = "https://api.respan.ai/api"
EXAMPLE_NAME = "python-auto-instrument-direct-llm"


def add_local_respan_paths() -> None:
    """Prefer a sibling local respan checkout when this example is run in-repo."""

    repo = Path(os.getenv("RESPAN_REPO", PROJECT_ROOT.parent / "respan"))
    if not repo.exists():
        return

    paths = [
        repo / "python-sdks" / "respan" / "src",
        repo / "python-sdks" / "respan-tracing" / "src",
        repo / "python-sdks" / "respan-sdk" / "src",
        *sorted((repo / "python-sdks" / "instrumentations").glob("*/src")),
    ]
    for path in reversed(paths):
        if path.exists():
            path_text = str(path)
            if path_text not in sys.path:
                sys.path.insert(0, path_text)


add_local_respan_paths()

from respan import Respan, workflow, list_auto_instrumentation_specs


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    status: str
    detail: str


@dataclass(frozen=True)
class RunnableCase:
    case_id: str
    sdk_import: str
    run: Callable[[], str]
    gateway_backed: bool
    required_env: tuple[str, ...] = ()


def load_root_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=True)


def has_import(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except ModuleNotFoundError:
        return False


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def respan_api_key() -> str:
    return require_env("RESPAN_API_KEY")


def gateway_api_key() -> str:
    return os.getenv("RESPAN_GATEWAY_API_KEY") or respan_api_key()


def respan_base_url() -> str:
    return os.getenv("RESPAN_BASE_URL", DEFAULT_RESPAN_BASE_URL).rstrip("/")


def gateway_base_url() -> str:
    return os.getenv("RESPAN_GATEWAY_BASE_URL", respan_base_url()).rstrip("/")


def anthropic_gateway_base_url() -> str:
    explicit = os.getenv("RESPAN_ANTHROPIC_GATEWAY_BASE_URL")
    if explicit:
        return explicit.rstrip("/")
    base_url = gateway_base_url()
    if base_url.endswith("/anthropic"):
        return base_url
    return f"{base_url}/anthropic"


def google_genai_gateway_base_url() -> str:
    explicit = os.getenv("RESPAN_GOOGLE_GENAI_GATEWAY_BASE_URL")
    if explicit:
        return explicit.rstrip("/")
    base_url = gateway_base_url()
    if base_url.endswith("/google/gemini"):
        return base_url
    return f"{base_url}/google/gemini"


class _MockHandler(BaseHTTPRequestHandler):
    response_text = "mock response from auto instrumentation batch"

    def do_POST(self) -> None:
        content_length = int(self.headers.get("content-length", "0") or "0")
        if content_length:
            self.rfile.read(content_length)

        if self.path.endswith("/api/chat"):
            payload = {
                "model": "llama3.2",
                "message": {"role": "assistant", "content": self.response_text},
                "done": True,
                "prompt_eval_count": 8,
                "eval_count": 9,
            }
        elif self.path.endswith("/v2/chat") or self.path.endswith("/chat"):
            payload = {
                "id": "cohere-auto-instrument-mock",
                "finish_reason": "COMPLETE",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": self.response_text}],
                },
                "usage": {
                    "billed_units": {"input_tokens": 8, "output_tokens": 9},
                    "tokens": {"input_tokens": 8, "output_tokens": 9},
                },
            }
        else:
            payload = {
                "id": "chatcmpl-auto-instrument-mock",
                "object": "chat.completion",
                "created": 1,
                "model": "openai/gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": self.response_text,
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 8,
                    "completion_tokens": 9,
                    "total_tokens": 17,
                },
            }

        data = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, _format: str, *_args) -> None:
        return


class LocalMockServer:
    def __init__(self, *, response_text: str) -> None:
        handler = type(
            "AutoInstrumentMockHandler",
            (_MockHandler,),
            {"response_text": response_text},
        )
        self._server = HTTPServer(("127.0.0.1", 0), handler)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            daemon=True,
        )

    def __enter__(self) -> str:
        self._thread.start()
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    def __exit__(self, _exc_type, _exc, _tb) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)


def print_registry() -> None:
    print("known_auto_instrumentations:")
    for spec in list_auto_instrumentation_specs():
        mode = "auto" if spec.enabled_by_default else "manual"
        reason = f" reason={spec.auto_disabled_reason}" if spec.auto_disabled_reason else ""
        print(f"  - {spec.id}: {mode} sdk={spec.sdk_package}{reason}")


def print_runtime_status(respan: Respan) -> None:
    print("runtime_auto_status:")
    for status in respan.get_auto_instrumentation_status():
        reason = f" reason={status['reason']}" if status.get("reason") else ""
        print(
            "  - {id}: {status} sdk={sdk}{reason}".format(
                id=status["id"],
                status=status["status"],
                sdk=status["sdk_package"],
                reason=reason,
            )
        )


def _cohere_response_text(response) -> str:
    message = getattr(response, "message", None)
    content = getattr(message, "content", None)
    if content:
        first = content[0]
        return getattr(first, "text", str(first))
    return "Cohere response did not include text content"


@workflow(name="python_auto_instrument_openai_gateway")
def run_openai_gateway() -> str:
    from openai import OpenAI

    client = OpenAI(api_key=gateway_api_key(), base_url=gateway_base_url())
    response = client.chat.completions.create(
        model=os.getenv("RESPAN_MODEL", "gpt-4o-mini"),
        messages=[
            {
                "role": "user",
                "content": "Reply with one concise sentence about Python tracing.",
            }
        ],
        max_tokens=48,
    )
    return response.choices[0].message.content or ""


@workflow(name="python_auto_instrument_anthropic_gateway")
def run_anthropic_gateway() -> str:
    from anthropic import Anthropic

    client = Anthropic(api_key=gateway_api_key(), base_url=anthropic_gateway_base_url())
    response = client.messages.create(
        model=os.getenv("RESPAN_ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929"),
        max_tokens=48,
        messages=[
            {
                "role": "user",
                "content": "Reply with one concise sentence about Python tracing.",
            }
        ],
    )
    for block in response.content:
        text = getattr(block, "text", None)
        if text:
            return text
    return ""


@workflow(name="python_auto_instrument_vertexai_native")
def run_vertexai_native() -> str:
    import vertexai
    from vertexai.generative_models import GenerativeModel

    vertexai.init(
        project=require_env("VERTEXAI_PROJECT"),
        location=os.getenv("VERTEXAI_LOCATION", "us-central1"),
    )
    model = GenerativeModel(os.getenv("VERTEXAI_MODEL", "gemini-2.0-flash"))
    response = model.generate_content(
        "Reply with one concise sentence about Python tracing.",
    )
    return response.text or ""


@workflow(name="python_auto_instrument_google_genai_gateway")
def run_google_genai_gateway() -> str:
    from google import genai

    client = genai.Client(
        api_key=gateway_api_key(),
        http_options={"base_url": google_genai_gateway_base_url()},
    )
    response = client.models.generate_content(
        model=os.getenv("RESPAN_GOOGLE_GENAI_MODEL", "gemini-3.5-flash"),
        contents="Reply with one concise sentence about Python tracing.",
    )
    return response.text or ""


@workflow(name="python_auto_instrument_aws_bedrock_stub")
def run_aws_bedrock_stub() -> str:
    import boto3
    from botocore.response import StreamingBody
    from botocore.stub import Stubber

    model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    body = json.dumps(
        {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": "Reply with one concise sentence about Python tracing."}],
                }
            ]
        }
    )
    response_body = json.dumps(
        {
            "output": {
                "message": {
                    "role": "assistant",
                    "content": [{"text": "stubbed Bedrock response"}],
                }
            },
            "usage": {"inputTokens": 8, "outputTokens": 9, "totalTokens": 17},
        }
    ).encode("utf-8")
    client = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id="test",
        aws_secret_access_key="test",
        aws_session_token="test",
    )
    with Stubber(client) as stubber:
        stubber.add_response(
            "invoke_model",
            {
                "body": StreamingBody(BytesIO(response_body), len(response_body)),
                "contentType": "application/json",
                "ResponseMetadata": {"HTTPStatusCode": 200},
            },
            {
                "modelId": model_id,
                "body": body,
                "contentType": "application/json",
                "accept": "application/json",
            },
        )
        client.invoke_model(
            modelId=model_id,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
    return "stubbed Bedrock response"


@workflow(name="python_auto_instrument_cohere_native")
def run_cohere_native() -> str:
    import cohere

    if os.getenv("COHERE_API_KEY"):
        client = cohere.ClientV2(api_key=os.environ["COHERE_API_KEY"])
        response = client.chat(
            model=os.getenv("COHERE_MODEL", "command-r-plus"),
            messages=[
                {
                    "role": "user",
                    "content": "Reply with one concise sentence about Python tracing.",
                }
            ],
        )
        return _cohere_response_text(response)

    with LocalMockServer(
        response_text="mock Cohere response from auto instrumentation batch",
    ) as server_url:
        client = cohere.ClientV2(api_key="mock-cohere-key", base_url=server_url)
        response = client.chat(
            model=os.getenv("COHERE_MODEL", "command-r-plus"),
            messages=[
                {
                    "role": "user",
                    "content": "Reply with one concise sentence about Python tracing.",
                }
            ],
        )
    return _cohere_response_text(response)


@workflow(name="python_auto_instrument_together_gateway")
def run_together_gateway() -> str:
    from together import Together

    client = Together(api_key=gateway_api_key(), base_url=gateway_base_url())
    response = client.chat.completions.create(
        model=os.getenv(
            "RESPAN_TOGETHER_MODEL",
            "together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo",
        ),
        messages=[
            {
                "role": "user",
                "content": "Reply with one concise sentence about Python tracing.",
            }
        ],
        max_tokens=48,
    )
    return response.choices[0].message.content or ""


@workflow(name="python_auto_instrument_groq_native")
def run_groq_native() -> str:
    from groq import Groq

    if os.getenv("GROQ_API_KEY"):
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {
                    "role": "user",
                    "content": "Reply with one concise sentence about Python tracing.",
                }
            ],
            max_tokens=48,
        )
        return response.choices[0].message.content or ""

    with LocalMockServer(
        response_text="mock Groq response from auto instrumentation batch",
    ) as server_url:
        client = Groq(api_key="mock-groq-key", base_url=server_url)
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {
                    "role": "user",
                    "content": "Reply with one concise sentence about Python tracing.",
                }
            ],
            max_tokens=48,
        )
    return response.choices[0].message.content or ""


@workflow(name="python_auto_instrument_mistralai_gateway")
def run_mistralai_gateway() -> str:
    try:
        from mistralai import Mistral
    except ImportError:
        from mistralai.client import Mistral

    client = Mistral(api_key=gateway_api_key(), server_url=gateway_base_url())
    response = client.chat.complete(
        model=os.getenv("RESPAN_MISTRAL_MODEL", "mistral/mistral-small"),
        messages=[
            {
                "role": "user",
                "content": "Reply with one concise sentence about Python tracing.",
            }
        ],
        max_tokens=48,
    )
    return response.choices[0].message.content or ""


@workflow(name="python_auto_instrument_ollama_mock")
def run_ollama_mock() -> str:
    from ollama import Client

    with LocalMockServer(
        response_text="mock Ollama response from auto instrumentation batch",
    ) as server_url:
        client = Client(host=server_url)
        response = client.chat(
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            messages=[
                {
                    "role": "user",
                    "content": "Reply with one concise sentence about Python tracing.",
                }
            ],
        )
    return response["message"]["content"]


@workflow(name="python_auto_instrument_aleph_alpha_direct")
def run_aleph_alpha_direct() -> str:
    from aleph_alpha_client import ChatRequest, Client, Message
    from aleph_alpha_client.chat import Role

    model_name = os.getenv("ALEPH_ALPHA_MODEL", "llama-3.1-8b-instruct")
    client = Client(token=require_env("ALEPH_ALPHA_API_KEY"))
    response = client.chat(
        request=ChatRequest(
            model=model_name,
            messages=[
                Message(
                    role=Role.User,
                    content="Reply with one concise sentence about Python tracing.",
                )
            ],
        ),
        model=model_name,
    )
    return response.message.content


@workflow(name="python_auto_instrument_huggingface_local")
def run_huggingface_local() -> str:
    from transformers import pipeline

    model_name = require_env("HUGGINGFACE_TEXT_GENERATION_MODEL")
    generator = pipeline("text-generation", model=model_name)
    response = generator(
        "Reply with one concise sentence about Python tracing.",
        max_new_tokens=32,
    )
    return response[0]["generated_text"]


@workflow(name="python_auto_instrument_litellm_gateway")
def run_litellm_gateway() -> str:
    import litellm

    response = litellm.completion(
        api_key=gateway_api_key(),
        api_base=gateway_base_url(),
        model=os.getenv("RESPAN_MODEL", "gpt-4o-mini"),
        messages=[
            {
                "role": "user",
                "content": "Reply with one concise sentence about Python tracing.",
            }
        ],
        max_tokens=48,
    )
    return response.choices[0].message.content or ""


@workflow(name="python_auto_instrument_replicate_direct")
def run_replicate_direct() -> str:
    import replicate

    output = replicate.run(
        os.getenv("REPLICATE_MODEL", "meta/meta-llama-3-8b-instruct"),
        input={
            "prompt": "Reply with one concise sentence about Python tracing.",
            "max_new_tokens": 48,
        },
    )
    if isinstance(output, str):
        return output
    return "".join(str(part) for part in output)


@workflow(name="python_auto_instrument_sagemaker_stub")
def run_sagemaker_stub() -> str:
    import boto3
    from botocore.response import StreamingBody
    from botocore.stub import Stubber

    request_body = json.dumps(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Reply with one concise sentence about Python tracing.",
                }
            ]
        }
    )
    response_body = json.dumps(
        {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "stubbed SageMaker response",
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 8,
                "completion_tokens": 9,
                "total_tokens": 17,
            },
        }
    ).encode("utf-8")
    client = boto3.client(
        "sagemaker-runtime",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id="test",
        aws_secret_access_key="test",
        aws_session_token="test",
    )
    endpoint_name = os.getenv("SAGEMAKER_ENDPOINT_NAME", "respan-auto-example")
    with Stubber(client) as stubber:
        stubber.add_response(
            "invoke_endpoint",
            {
                "Body": StreamingBody(BytesIO(response_body), len(response_body)),
                "ContentType": "application/json",
                "ResponseMetadata": {"HTTPStatusCode": 200},
            },
            {
                "EndpointName": endpoint_name,
                "Body": request_body,
                "ContentType": "application/json",
                "Accept": "application/json",
            },
        )
        client.invoke_endpoint(
            EndpointName=endpoint_name,
            Body=request_body,
            ContentType="application/json",
            Accept="application/json",
        )
    return "stubbed SageMaker response"


@workflow(name="python_auto_instrument_watsonx_direct")
def run_watsonx_direct() -> str:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference

    client = ModelInference(
        model_id=os.getenv("WATSONX_MODEL_ID", "ibm/granite-13b-chat-v2"),
        credentials=Credentials(
            api_key=require_env("WATSONX_API_KEY"),
            url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
        ),
        project_id=require_env("WATSONX_PROJECT_ID"),
    )
    return client.generate_text(
        prompt="Reply with one concise sentence about Python tracing.",
    )


@workflow(name="python_auto_instrument_writer_direct")
def run_writer_direct() -> str:
    from writerai import Writer

    client = Writer(api_key=require_env("WRITER_API_KEY"))
    response = client.chat.chat(
        model=os.getenv("WRITER_MODEL", "palmyra-x5"),
        messages=[
            {
                "role": "user",
                "content": "Reply with one concise sentence about Python tracing.",
            }
        ],
        max_tokens=48,
    )
    return response.choices[0].message.content or ""


@workflow(name="python_auto_instrument_portkey_direct")
def run_portkey_direct() -> str:
    from portkey_ai import Portkey

    client = Portkey(
        api_key=require_env("PORTKEY_API_KEY"),
        provider=os.getenv("PORTKEY_PROVIDER"),
        config=os.getenv("PORTKEY_CONFIG"),
    )
    response = client.chat.completions.create(
        model=os.getenv("PORTKEY_MODEL", "gpt-4o-mini"),
        messages=[
            {
                "role": "user",
                "content": "Reply with one concise sentence about Python tracing.",
            }
        ],
        max_tokens=48,
    )
    return response.choices[0].message.content or ""


@workflow(name="python_auto_instrument_openrouter_direct")
def run_openrouter_direct() -> str:
    from openai import OpenAI

    if os.getenv("OPENROUTER_API_KEY"):
        client = OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        )
        response = client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            messages=[
                {
                    "role": "user",
                    "content": "Reply with one concise sentence about Python tracing.",
                }
            ],
            max_tokens=48,
        )
        return response.choices[0].message.content or ""

    with LocalMockServer(
        response_text="mock OpenRouter response from auto instrumentation batch",
    ) as server_url:
        client = OpenAI(
            api_key="mock-openrouter-key",
            base_url=f"{server_url}/openrouter.ai/api/v1",
        )
        response = client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            messages=[
                {
                    "role": "user",
                    "content": "Reply with one concise sentence about Python tracing.",
                }
            ],
            max_tokens=48,
        )
    return response.choices[0].message.content or ""


RUNNABLE_CASES = {
    "openai": RunnableCase("openai", "openai", run_openai_gateway, True),
    "anthropic": RunnableCase("anthropic", "anthropic", run_anthropic_gateway, True),
    "vertexai": RunnableCase(
        "vertexai",
        "vertexai",
        run_vertexai_native,
        False,
        ("VERTEXAI_PROJECT",),
    ),
    "google-genai": RunnableCase("google-genai", "google.genai", run_google_genai_gateway, True),
    "aws-bedrock": RunnableCase("aws-bedrock", "boto3", run_aws_bedrock_stub, False),
    "cohere": RunnableCase("cohere", "cohere", run_cohere_native, False),
    "together": RunnableCase("together", "together", run_together_gateway, True),
    "groq": RunnableCase("groq", "groq", run_groq_native, False),
    "mistralai": RunnableCase("mistralai", "mistralai", run_mistralai_gateway, True),
    "ollama": RunnableCase("ollama", "ollama", run_ollama_mock, False),
    "aleph-alpha": RunnableCase(
        "aleph-alpha",
        "aleph_alpha_client",
        run_aleph_alpha_direct,
        False,
        ("ALEPH_ALPHA_API_KEY",),
    ),
    "huggingface": RunnableCase(
        "huggingface",
        "transformers",
        run_huggingface_local,
        False,
        ("HUGGINGFACE_TEXT_GENERATION_MODEL",),
    ),
    "litellm": RunnableCase("litellm", "litellm", run_litellm_gateway, True),
    "replicate": RunnableCase(
        "replicate",
        "replicate",
        run_replicate_direct,
        False,
        ("REPLICATE_API_TOKEN",),
    ),
    "sagemaker": RunnableCase("sagemaker", "boto3", run_sagemaker_stub, False),
    "watsonx": RunnableCase(
        "watsonx",
        "ibm_watsonx_ai",
        run_watsonx_direct,
        False,
        ("WATSONX_API_KEY", "WATSONX_PROJECT_ID"),
    ),
    "writer": RunnableCase(
        "writer",
        "writerai",
        run_writer_direct,
        False,
        ("WRITER_API_KEY",),
    ),
    "portkey": RunnableCase(
        "portkey",
        "portkey_ai",
        run_portkey_direct,
        False,
        ("PORTKEY_API_KEY",),
    ),
    "openrouter": RunnableCase("openrouter", "openai", run_openrouter_direct, False),
}


def selected_case_ids(only: Optional[str]) -> list[str]:
    all_auto_ids = [
        spec.id for spec in list_auto_instrumentation_specs(include_disabled=False)
    ]
    if not only:
        return all_auto_ids
    requested = [item.strip() for item in only.split(",") if item.strip()]
    known = set(all_auto_ids)
    unknown = [item for item in requested if item not in known]
    if unknown:
        raise RuntimeError(f"Unknown auto-instrumentation case(s): {', '.join(unknown)}")
    return requested


def run_case(case_id: str, respan: Respan, run_id: str) -> CaseResult:
    runnable = RUNNABLE_CASES.get(case_id)
    if runnable is None:
        return CaseResult(case_id, "failed", "example runner is not wired")
    if not has_import(runnable.sdk_import):
        return CaseResult(
            case_id,
            "skipped",
            f"SDK package import is unavailable: {runnable.sdk_import}",
        )
    if runnable.gateway_backed and not os.getenv("RESPAN_API_KEY"):
        return CaseResult(case_id, "skipped", "RESPAN_API_KEY is not set")
    missing_env = [name for name in runnable.required_env if not os.getenv(name)]
    if missing_env:
        return CaseResult(
            case_id,
            "skipped",
            "required env is not set: %s" % ", ".join(missing_env),
        )

    try:
        with respan.propagate_attributes(
            trace_group_identifier=f"{EXAMPLE_NAME}-{run_id}",
            custom_identifier=f"{EXAMPLE_NAME}-{case_id}-{run_id}",
            metadata={
                "example": EXAMPLE_NAME,
                "case": case_id,
                "run_id": run_id,
                "gateway_backed": runnable.gateway_backed,
            },
        ):
            text = runnable.run().strip()
        return CaseResult(case_id, "ok", text[:240])
    except Exception as exc:
        return CaseResult(case_id, "failed", f"{type(exc).__name__}: {exc}")


def main() -> int:
    load_root_env()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only",
        help="Comma-separated auto instrumentation IDs to run, for example openai,anthropic.",
    )
    args = parser.parse_args()

    print_registry()
    run_id = os.getenv("RESPAN_EXAMPLE_RUN_ID", uuid4().hex[:8])
    print(f"example_run_id={run_id}")
    print(f"trace_group_identifier={EXAMPLE_NAME}-{run_id}")
    respan = Respan(
        api_key=os.getenv("RESPAN_API_KEY"),
        base_url=respan_base_url(),
        app_name=EXAMPLE_NAME,
        environment=os.getenv("RESPAN_ENVIRONMENT", "example"),
        metadata={"example": EXAMPLE_NAME, "run_id": run_id},
    )
    print_runtime_status(respan)

    results = []
    try:
        for case_id in selected_case_ids(args.only):
            result = run_case(case_id, respan, run_id)
            results.append(result)
            print(f"case={result.case_id} status={result.status} detail={result.detail}")
    finally:
        respan.shutdown()

    failed = [result for result in results if result.status == "failed"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
