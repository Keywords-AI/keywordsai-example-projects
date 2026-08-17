"""Shared import, marker, and lifecycle helpers for the example suite."""

import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# These legacy entry points are executed once as standalone processes by
# ``run_all.py`` so their module-global setup and explicit shutdown are tested.
# Excluding them here prevents duplicate traces under the same exact marker.
collect_ignore = [
    "complex_edge_cases_test.py",
    "handoffs/message_filter_streaming_test.py",
    "handoffs/message_filter_test.py",
]

_CONTRACT_ONLY_FILES = {
    "bridge_contract.py",
    "contract_scenarios_test.py",
    "runner_contract.py",
}


@pytest.fixture(autouse=True)
def _flush_after_example():
    yield
    from respan_exporter_openai_agents import flush_respan

    flush_respan()


@pytest_asyncio.fixture(scope="session", autouse=True, loop_scope="session")
async def _shutdown_clients_after_session():
    yield
    from respan_exporter_openai_agents import shutdown_respan_async

    await shutdown_respan_async()


def pytest_collection_modifyitems(items):
    from respan_exporter_openai_agents import has_direct_responses_credentials

    direct_responses = has_direct_responses_credentials()
    for item in items:
        relative = item.path.relative_to(ROOT).as_posix()
        if relative not in _CONTRACT_ONLY_FILES:
            item.add_marker(pytest.mark.live)

        reason = None
        eligible = direct_responses
        if relative in {"tools/web_search_test.py", "research_bot/main_test.py"}:
            reason = "requires a direct OpenAI Responses API credential"
        elif relative == "tools/file_search_test.py":
            reason = "requires direct Responses credentials and OPENAI_VECTOR_STORE_ID"
            eligible = eligible and bool(os.getenv("OPENAI_VECTOR_STORE_ID"))
        elif relative == "tools/computer_use_test.py":
            reason = "requires direct Responses credentials and an enabled Playwright browser"
            eligible = eligible and (
                os.getenv("RESPAN_OPENAI_AGENTS_ENABLE_COMPUTER") == "1"
            )
        if reason:
            item.add_marker(pytest.mark.hosted)
            if not eligible:
                item.add_marker(pytest.mark.skip(reason=reason))
