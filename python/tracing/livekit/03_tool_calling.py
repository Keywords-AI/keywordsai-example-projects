from __future__ import annotations

import asyncio

from livekit.agents import llm

from _shared import (
    MockLiveKitLLM,
    chat_context,
    example_attributes,
    finish_respan,
    lookup_room_status,
    make_custom_identifier,
    make_respan,
    print_result,
    print_start,
)


async def main() -> None:
    example_name = "03-tool-calling"
    custom_identifier = make_custom_identifier(example_name)
    respan = make_respan(example_name)
    try:
        print_start(example_name, custom_identifier)
        model = MockLiveKitLLM()
        with example_attributes(example_name, custom_identifier):
            response = await model.chat(
                chat_ctx=chat_context("Check the blue room status."),
                tools=[lookup_room_status],
                extra_kwargs={"scenario": "tool"},
            ).collect()
            tool_ctx = llm.ToolContext([lookup_room_status])
            tool_results = [
                await llm.execute_function_call(tool_call, tool_ctx)
                for tool_call in response.tool_calls
            ]
        print_result("llm_response", response.model_dump())
        print_result(
            "tool_results",
            [
                {
                    "name": result.fnc_call.name,
                    "output": result.fnc_call_out.output if result.fnc_call_out else None,
                    "is_error": result.fnc_call_out.is_error
                    if result.fnc_call_out
                    else None,
                }
                for result in tool_results
            ],
        )
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    asyncio.run(main())
