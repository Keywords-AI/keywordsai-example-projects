"""Shared helpers for Arize Respan examples."""

from __future__ import annotations

import concurrent.futures
import importlib
import os
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable

from arize import ArizeClient
from respan import Respan, get_client
from respan_instrumentation_arize import ArizeInstrumentor
from respan_instrumentation_arize._constants import ARIZE_CLIENT_SPECS

EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[2]
ROOT_ENV = REPO_ROOT / ".env"
CUSTOMER_IDENTIFIER = "arize-example"
_PATCHED = False


def load_repo_env() -> None:
    """Load the example repository root .env without introducing extra deps."""
    if not ROOT_ENV.exists():
        return

    for raw_line in ROOT_ENV.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip("'").strip('"')
        os.environ[key.strip()] = value


def new_run_id(example_name: str) -> str:
    return os.getenv("RESPAN_EXAMPLE_RUN_ID") or f"{example_name}-{uuid.uuid4().hex[:10]}"


def _make_completed_future(value: Any) -> concurrent.futures.Future:
    future: concurrent.futures.Future = concurrent.futures.Future()
    future.set_result(value)
    return future


def _offline_result(resource: str, method_name: str, kwargs: dict[str, Any]) -> Any:
    payload = {
        "offline": True,
        "resource": resource,
        "operation": method_name,
        "keys": sorted(kwargs),
    }
    if method_name == "log_stream":
        return _make_completed_future(payload)
    return payload


def _make_offline_method(resource: str, method_name: str) -> Callable[..., Any]:
    def offline_method(self: Any, *args: Any, **kwargs: Any) -> Any:
        return _offline_result(resource, method_name, kwargs)

    offline_method.__name__ = method_name
    return offline_method


def install_offline_arize_operations() -> None:
    """Replace outbound Arize SDK methods with deterministic local responses."""
    global _PATCHED
    if _PATCHED:
        return

    for spec in ARIZE_CLIENT_SPECS:
        module = importlib.import_module(spec.module_name)
        client_class = getattr(module, spec.class_name, None)
        if client_class is None:
            continue
        for method_name in spec.methods:
            original = getattr(client_class, method_name, None)
            if original is None or not callable(original):
                continue
            setattr(
                client_class,
                method_name,
                _make_offline_method(spec.resource, method_name),
            )
    _PATCHED = True


def create_respan(*, workflow_name: str, run_id: str, example_name: str) -> Respan:
    load_repo_env()
    return Respan(
        api_key=os.getenv("RESPAN_API_KEY") or os.getenv("RESPAN_GATEWAY_API_KEY"),
        base_url=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
        app_name="arize-example",
        instrumentations=[ArizeInstrumentor()],
        customer_identifier=CUSTOMER_IDENTIFIER,
        metadata={
            "example_set": "arize",
            "example_name": example_name,
            "workflow_name": workflow_name,
            "run_id": run_id,
        },
        environment="example",
        is_batching_enabled=False,
    )


def create_arize_client() -> ArizeClient:
    return ArizeClient(
        api_key=os.getenv("ARIZE_API_KEY", "offline-arize-key"),
        api_host="example.invalid",
        flight_host="example.invalid",
        otlp_host="example.invalid",
        request_verify=False,
    )


@contextmanager
def workflow_context(
    respan: Respan,
    *,
    workflow_name: str,
    run_id: str,
    example_name: str,
) -> Any:
    with respan.propagate_attributes(
        group_identifier=workflow_name,
        custom_identifier=run_id,
        metadata={
            "example_set": "arize",
            "example_name": example_name,
            "workflow_name": workflow_name,
            "run_id": run_id,
        },
    ):
        with get_client().start_span(workflow_name, kind="workflow"):
            yield


def print_result(label: str, result: Any) -> None:
    if isinstance(result, concurrent.futures.Future):
        result = result.result(timeout=1)
    print(f"{label}: {result}")


def print_trace_lookup(*, workflow_name: str, run_id: str) -> None:
    print(f"workflow_name={workflow_name}")
    print(f"RESPAN_EXAMPLE_RUN_ID={run_id}")


def flush_and_shutdown(respan: Respan) -> None:
    respan.flush()
    respan.shutdown()
