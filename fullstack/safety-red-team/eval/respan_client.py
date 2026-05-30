"""Thin async wrapper over the Respan gateway (OpenAI-compatible).

Every call is routed through https://api.respan.ai/api and tagged with a shared
trace group plus metadata, so the whole run shows up grouped in the Respan
dashboard. Returns text, token usage, cost (when the gateway reports it), and
wall-clock latency. Network/rate-limit/bad-model errors are captured, not raised.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Optional

from openai import AsyncOpenAI

DEFAULT_BASE_URL = "https://api.respan.ai/api"


@dataclass
class Call:
    text: str
    latency_ms: int
    cost_usd: float
    prompt_tokens: int
    completion_tokens: int
    error: Optional[str] = None


def build_client() -> AsyncOpenAI:
    key = os.environ.get("RESPAN_API_KEY")
    if not key:
        raise SystemExit(
            "RESPAN_API_KEY is not set. Copy .env.example to .env and add your key "
            "(free credits at https://platform.respan.ai)."
        )
    base = os.environ.get("RESPAN_BASE_URL", DEFAULT_BASE_URL)
    # max_retries gives the SDK exponential backoff on 429s (the gateway rate-limits free keys).
    return AsyncOpenAI(api_key=key, base_url=base, max_retries=8, timeout=90.0)


def _extract_cost(resp: Any) -> float:
    """Respan reports cost differently across versions; read it best-effort."""
    for obj in (getattr(resp, "usage", None), resp):
        if obj is None:
            continue
        for attr in ("cost", "total_cost", "cost_usd"):
            v = getattr(obj, attr, None)
            if isinstance(v, (int, float)):
                return float(v)
        extra = getattr(obj, "model_extra", None) or {}
        for attr in ("cost", "total_cost", "cost_usd"):
            v = extra.get(attr)
            if isinstance(v, (int, float)):
                return float(v)
    return 0.0


async def call_model(
    client: AsyncOpenAI,
    *,
    model: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    trace_group: str,
    custom_identifier: str,
    metadata: dict,
) -> Call:
    t0 = time.perf_counter()
    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            extra_body={
                "trace_group_identifier": trace_group,
                "custom_identifier": custom_identifier,
                "metadata": metadata,
            },
        )
        dt = int((time.perf_counter() - t0) * 1000)
        usage = getattr(resp, "usage", None)
        return Call(
            text=(resp.choices[0].message.content or "").strip(),
            latency_ms=dt,
            cost_usd=_extract_cost(resp),
            prompt_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) or 0,
        )
    except Exception as e:
        dt = int((time.perf_counter() - t0) * 1000)
        return Call("", dt, 0.0, 0, 0, error=str(e)[:200])
