"""One-script example for ChatPromptBuilder."""

from _shared import configure_respan, finish_respan, print_result


def run_chat_prompt_builder_example():
    respan = configure_respan("haystack-chat-prompt-builder")
    try:
        from haystack.components.builders import ChatPromptBuilder
        from haystack.dataclasses import ChatMessage

        template = [
            ChatMessage.from_system("You are concise."),
            ChatMessage.from_user("Explain {{ topic }}."),
        ]
        builder = ChatPromptBuilder(template, required_variables=["topic"])
        result = builder.run(topic="retrieval augmented generation")
        print_result("ChatPromptBuilder", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_chat_prompt_builder_example()
