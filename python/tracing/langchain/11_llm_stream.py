"""Legacy string LLM stream."""

from langchain_core.language_models.fake import FakeStreamingListLLM

from _shared import init_telemetry, tracing_config


def llm_stream() -> None:
    telemetry = init_telemetry("langchain-llm-stream")
    llm = FakeStreamingListLLM(responses=["tokenized completion"])
    chunks = list(
        llm.stream(
            "Stream this completion.",
            config=tracing_config("llm_stream"),
        )
    )
    print("".join(chunks))
if __name__ == "__main__":
    llm_stream()
