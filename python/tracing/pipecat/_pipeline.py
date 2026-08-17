"""Current Pipecat worker fixtures shared by the runnable examples."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from pipecat.frames.frames import (
    EndFrame,
    ErrorFrame,
    Frame,
    LLMContextFrame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
)
from pipecat.metrics.metrics import LLMTokenUsage
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.llm_service import LLMService, LLMSettings
from pipecat.workers.runner import WorkerRunner


class ProviderHTTPError(RuntimeError):
    def __init__(self, message: str, *, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class OfflineLLMService(LLMService):
    def __init__(self, *, response: str, fail_status: int | None = None) -> None:
        super().__init__(
            name="OfflineLLMService",
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
        self._response = response
        self._fail_status = fail_status

    def can_generate_metrics(self) -> bool:
        return True

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        await super().process_frame(frame, direction)
        if not isinstance(frame, LLMContextFrame):
            await self.push_frame(frame, direction)
            return
        await self.push_frame(LLMFullResponseStartFrame())
        if self._fail_status is not None:
            error = ProviderHTTPError(
                "deterministic provider authorization failure",
                status_code=self._fail_status,
            )
            await self.push_frame(
                ErrorFrame(
                    error="deterministic provider authorization failure",
                    exception=error,
                    processor=self,
                )
            )
            return
        await self.push_frame(LLMTextFrame(self._response))
        await self.start_llm_usage_metrics(
            LLMTokenUsage(prompt_tokens=8, completion_tokens=6, total_tokens=14)
        )
        await self.push_frame(LLMFullResponseEndFrame())


class TextCollector(FrameProcessor):
    def __init__(self) -> None:
        super().__init__(name="text_collector", enable_direct_mode=True)
        self.text: list[str] = []
        self.error: str | None = None
        self.done = asyncio.Event()

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        await super().process_frame(frame, direction)
        if isinstance(frame, LLMTextFrame):
            self.text.append(frame.text)
        elif isinstance(frame, ErrorFrame):
            self.error = frame.error
            self.done.set()
        elif isinstance(frame, LLMFullResponseEndFrame):
            self.done.set()
        await self.push_frame(frame, direction)


@dataclass(frozen=True)
class PipelineResult:
    text: str
    error: str | None


async def run_pipeline(
    service: LLMService, *, prompt: str, conversation_id: str
) -> PipelineResult:
    collector = TextCollector()
    worker = PipelineWorker(
        Pipeline([service, collector]),
        cancel_on_idle_timeout=False,
        enable_rtvi=False,
        conversation_id=conversation_id,
        params=PipelineParams(enable_metrics=True, enable_usage_metrics=True),
    )
    runner = WorkerRunner(handle_sigint=False)
    await runner.add_workers(worker)

    async def drive() -> None:
        await asyncio.sleep(0.05)
        await worker.queue_frame(
            LLMContextFrame(LLMContext(messages=[{"role": "user", "content": prompt}]))
        )
        await asyncio.wait_for(collector.done.wait(), timeout=30)
        await worker.queue_frame(EndFrame())

    await asyncio.wait_for(asyncio.gather(runner.run(), drive()), timeout=40)
    return PipelineResult(text="".join(collector.text), error=collector.error)
