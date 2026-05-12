"""Chat: call the LlamaIndex OpenAI chat API."""

from llama_index.core.llms import ChatMessage, MessageRole

from _shared import build_llm, create_respan, print_result, traced_example


def run_chat() -> None:
    context = create_respan(
        app_name="llama-index-02-chat",
        example_name="02_chat",
    )
    llm = build_llm(settings=context.settings)
    messages = [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content="Answer in one concise sentence.",
        ),
        ChatMessage(
            role=MessageRole.USER,
            content="What can Respan trace in a LlamaIndex application?",
        ),
    ]

    with traced_example(context):
        response = llm.chat(messages)

    print_result("Chat response", response)
    print_result("Example run id", context.run_id)
    context.respan.flush()


if __name__ == "__main__":
    run_chat()
