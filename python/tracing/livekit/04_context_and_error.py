from __future__ import annotations

import asyncio

from livekit.agents import llm

from _shared import (
    MockLiveKitLLM,
    chat_context,
    example_attributes,
    finish_respan,
    make_custom_identifier,
    make_respan,
    print_result,
    print_start,
)


async def main() -> None:
    example_name = "04-context-and-error"
    custom_identifier = make_custom_identifier(example_name)
    respan = make_respan(example_name)
    try:
        print_start(example_name, custom_identifier)
        model = MockLiveKitLLM()
        with example_attributes(example_name, custom_identifier):
            response = await model.chat(
                chat_ctx=chat_context("Demonstrate propagated attributes."),
                extra_kwargs={"scenario": "missing_tool"},
            ).collect()
            missing_result = await llm.execute_function_call(
                response.tool_calls[0],
                llm.ToolContext.empty(),
            )
        print_result("response", response.model_dump())
        print_result(
            "missing_tool",
            {
                "name": missing_result.fnc_call.name,
                "output": missing_result.fnc_call_out.output
                if missing_result.fnc_call_out
                else None,
                "is_error": missing_result.fnc_call_out.is_error
                if missing_result.fnc_call_out
                else None,
            },
        )
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
