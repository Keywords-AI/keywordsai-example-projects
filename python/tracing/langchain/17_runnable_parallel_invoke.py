"""RunnableParallel invoke."""

from langchain_core.runnables import RunnableLambda, RunnableParallel

from _shared import init_telemetry, tracing_config


def runnable_parallel_invoke() -> None:
    telemetry = init_telemetry("langchain-runnable-parallel-invoke")
    runnable = RunnableParallel(
        uppercase=RunnableLambda(lambda text: text.upper()),
        length=RunnableLambda(lambda text: len(text)),
    )
    response = runnable.invoke(
        "respan",
        config=tracing_config("runnable_parallel_invoke"),
    )
    print(response)
if __name__ == "__main__":
    runnable_parallel_invoke()
