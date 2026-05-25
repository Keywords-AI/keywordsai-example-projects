"""Run a Pipecat LLM pipeline through the Respan gateway."""

from __future__ import annotations

import asyncio
from pathlib import Path

from pipecat.frames.frames import (
    EndFrame,
    Frame,
    LLMContextFrame,
    LLMFullResponseEndFrame,
    LLMTextFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.openai.llm import OpenAILLMService
from respan import workflow

from _shared import create_respan, load_example_env

SCRIPT_NAME = Path(__file__).name


class TextCollector(FrameProcessor):
    def __init__(self) -> None:
        super().__init__(name="text_collector", enable_direct_mode=True)
        self.text: list[str] = []
        self.done = asyncio.Event()

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        await super().process_frame(frame, direction)
        if isinstance(frame, LLMTextFrame):
            self.text.append(frame.text)
        elif isinstance(frame, LLMFullResponseEndFrame):
            self.done.set()
        await self.push_frame(frame, direction)


@workflow(name=SCRIPT_NAME)
async def run_gateway_pipeline() -> str:
    env = load_example_env()
    collector = TextCollector()
    llm = OpenAILLMService(
        api_key=env["gateway_api_key"],
        base_url=env["gateway_base_url"],
        settings=OpenAILLMService.Settings(model=env["model"]),
    )
    pipeline = Pipeline([llm, collector])
    task = PipelineTask(
        pipeline,
        cancel_on_idle_timeout=False,
        enable_rtvi=False,
        conversation_id="gateway-pipecat-session",
    )

    async def push_frames() -> None:
        await asyncio.sleep(0.05)
        context = LLMContext(
            messages=[
                {
                    "role": "user",
                    "content": "Reply in one short sentence about Pipecat tracing.",
                }
            ]
        )
        await task.queue_frame(LLMContextFrame(context))
        await asyncio.wait_for(collector.done.wait(), timeout=30)
        await asyncio.sleep(0.2)
        await task.queue_frame(EndFrame())

    runner = PipelineRunner(handle_sigint=False)
    await asyncio.gather(runner.run(task), push_frames())
    return "".join(collector.text)


async def main() -> None:
    respan, run_id = create_respan(SCRIPT_NAME, mode="gateway")
    try:
        result = await run_gateway_pipeline()
        print(f"run_id={run_id}")
        print(result)
    finally:
        await asyncio.sleep(1)
        respan.flush()


if __name__ == "__main__":
    asyncio.run(main())
