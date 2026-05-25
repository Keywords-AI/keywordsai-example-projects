"""Run a local Pipecat pipeline and export Respan spans."""

from __future__ import annotations

import asyncio
from pathlib import Path

from pipecat.frames.frames import (
    EndFrame,
    Frame,
    LLMContextFrame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.llm_service import LLMService, LLMSettings
from respan import workflow

from _shared import create_respan

SCRIPT_NAME = Path(__file__).name


class OfflineLLMService(LLMService):
    """Small local LLM service that emits Pipecat LLM frames without network."""

    def __init__(self) -> None:
        super().__init__(
            name="offline_llm",
            settings=LLMSettings(
                model="offline-pipecat-demo",
                system_instruction=None,
                temperature=None,
                max_tokens=None,
                top_p=None,
                top_k=None,
                frequency_penalty=None,
                presence_penalty=None,
                seed=None,
                filter_incomplete_user_turns=False,
                user_turn_completion_config=None,
            ),
        )

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        await super().process_frame(frame, direction)

        if isinstance(frame, LLMContextFrame):
            await self.push_frame(LLMFullResponseStartFrame())
            await self.push_frame(LLMTextFrame("Pipecat instrumentation is active."))
            await self.push_frame(LLMFullResponseEndFrame())
        else:
            await self.push_frame(frame, direction)


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
async def run_offline_pipeline() -> str:
    collector = TextCollector()
    pipeline = Pipeline([OfflineLLMService(), collector])
    task = PipelineTask(
        pipeline,
        cancel_on_idle_timeout=False,
        enable_rtvi=False,
        conversation_id="offline-pipecat-session",
    )

    async def push_frames() -> None:
        await asyncio.sleep(0.05)
        context = LLMContext(
            messages=[
                {
                    "role": "user",
                    "content": "Confirm that the Pipecat pipeline is traced.",
                }
            ]
        )
        await task.queue_frame(LLMContextFrame(context))
        await asyncio.wait_for(collector.done.wait(), timeout=10)
        await asyncio.sleep(0.2)
        await task.queue_frame(EndFrame())

    runner = PipelineRunner(handle_sigint=False)
    await asyncio.gather(runner.run(task), push_frames())
    return "".join(collector.text)


async def main() -> None:
    respan, run_id = create_respan(SCRIPT_NAME, mode="offline")
    try:
        result = await run_offline_pipeline()
        print(f"run_id={run_id}")
        print(result)
    finally:
        await asyncio.sleep(1)
        respan.flush()


if __name__ == "__main__":
    asyncio.run(main())
