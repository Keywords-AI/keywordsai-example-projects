"""Run every bounded LangChain example in a fresh process."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLES = tuple(
    f"{index:02d}_{name}.py"
    for index, name in enumerate(
        (
            "quickstart",
            "chat_model_invoke",
            "chat_model_stream",
            "chat_model_batch",
            "chat_model_batch_as_completed",
            "chat_model_ainvoke",
            "chat_model_astream",
            "chat_model_abatch",
            "chat_model_abatch_as_completed",
            "chat_model_astream_events",
            "llm_invoke",
            "llm_stream",
            "model_bind_tools",
            "model_with_structured_output",
            "tool_invoke",
            "tool_ainvoke",
            "prompt_chain_invoke",
            "runnable_parallel_invoke",
            "retriever_invoke",
            "agent_invoke",
            "agent_stream_updates",
            "agent_stream_messages",
            "agent_stream_custom",
            "agent_structured_output",
            "custom_event",
            "runnable_with_retry",
            "chain_error",
            "tool_error",
            "retriever_error",
        )
    )
)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    for script_name in EXAMPLES:
        print(f"\n=== {script_name} ===", flush=True)
        subprocess.run([sys.executable, str(base_dir / script_name)], check=True)


if __name__ == "__main__":
    main()
