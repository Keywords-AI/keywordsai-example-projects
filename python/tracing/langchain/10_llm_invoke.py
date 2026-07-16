"""Legacy string LLM invoke."""

from langchain_core.language_models.fake import FakeListLLM

from _shared import init_telemetry, tracing_config


def llm_invoke() -> None:
    telemetry = init_telemetry("langchain-llm-invoke")
    llm = FakeListLLM(responses=["legacy completion output"])
    response = llm.invoke(
        "Complete this phrase: Respan traces",
        config=tracing_config("llm_invoke"),
    )
    print(response)
if __name__ == "__main__":
    llm_invoke()
