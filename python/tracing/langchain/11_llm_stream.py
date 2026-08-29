"""Legacy string LLM stream."""

from collections.abc import Iterator
from typing import Any

from _shared import init_telemetry, tracing_config
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk


class CallbackStreamingLLM(LLM):
    """Deterministic LLM that exercises LangChain's token callback contract."""

    response: str

    @property
    def _llm_type(self) -> str:
        return "callback-streaming-list"

    def _call(
        self,
        prompt: str,
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> str:
        return self.response

    def _stream(
        self,
        prompt: str,
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        for token in self.response.splitlines(keepends=True):
            chunk = GenerationChunk(text=token)
            if run_manager is not None:
                run_manager.on_llm_new_token(token, chunk=chunk)
            yield chunk


def llm_stream() -> None:
    init_telemetry("langchain-llm-stream")
    llm = CallbackStreamingLLM(response="tokenized completion\nwith callbacks")
    chunks = list(
        llm.stream(
            "Stream this completion.",
            config=tracing_config("llm_stream"),
        )
    )
    print("".join(chunks))


if __name__ == "__main__":
    llm_stream()
