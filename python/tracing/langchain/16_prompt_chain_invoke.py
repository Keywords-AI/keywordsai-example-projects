"""Prompt chain invoke."""

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from _shared import flush, init_telemetry, tracing_config


def prompt_chain_invoke() -> None:
    telemetry = init_telemetry("langchain-prompt-chain-invoke")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You write concise release notes."),
            ("human", "Summarize this change: {change}"),
        ]
    )
    model = FakeListChatModel(responses=["Added LangChain tracing examples."])
    chain = prompt | model | StrOutputParser()
    try:
        response = chain.invoke(
            {"change": "New numbered examples for callback coverage."},
            config=tracing_config("prompt_chain_invoke"),
        )
        print(response)
    finally:
        flush(telemetry)


if __name__ == "__main__":
    prompt_chain_invoke()
