"""Focused lifecycle contract for the shared OpenAI Agents example bridge."""

from __future__ import annotations

import asyncio

import pytest

import respan_exporter_openai_agents as bridge


def test_bridge_disables_direct_openai_auto_instrumentation(monkeypatch):
    captured = None

    class FakeRespan:
        def __init__(self, **kwargs):
            nonlocal captured
            captured = kwargs

    monkeypatch.setattr(bridge, "Respan", FakeRespan)
    monkeypatch.setattr(bridge, "_RESPAN", None)

    instance = bridge._ensure_respan("test-key", "https://example.invalid/api")

    assert instance is not None
    assert captured is not None
    assert captured["is_auto_instrument"] is False
    bridge._RESPAN = None


@pytest.mark.asyncio
async def test_gateway_client_is_retained_and_closed_on_its_owner_loop(monkeypatch):
    owner_loop = asyncio.get_running_loop()
    closed_on = None

    class FakeAsyncOpenAI:
        def __init__(self, **_kwargs):
            pass

        async def close(self):
            nonlocal closed_on
            closed_on = asyncio.get_running_loop()

    monkeypatch.delenv("RESPAN_OPENAI_AGENTS_USE_OPENAI", raising=False)
    monkeypatch.setattr(bridge, "AsyncOpenAI", FakeAsyncOpenAI)
    monkeypatch.setattr(bridge, "set_default_openai_api", lambda _value: None)
    monkeypatch.setattr(bridge, "set_default_openai_client", lambda _client: None)
    monkeypatch.setattr(bridge, "_GATEWAY_CLIENT", None)
    monkeypatch.setattr(bridge, "_GATEWAY_CLIENT_CONFIGURED", False)
    monkeypatch.setattr(bridge, "_GATEWAY_CLIENT_OWNER_LOOP", None)

    bridge._configure_gateway_client("test-key")
    retained = bridge._GATEWAY_CLIENT
    bridge._claim_gateway_client_loop()

    assert retained is not None
    assert bridge._GATEWAY_CLIENT_OWNER_LOOP is owner_loop

    await bridge.shutdown_respan_async()

    assert closed_on is owner_loop
    assert bridge._GATEWAY_CLIENT is None
    assert bridge._GATEWAY_CLIENT_OWNER_LOOP is None
    assert bridge._GATEWAY_CLIENT_CONFIGURED is False
