"""Run the complete Groq tracing example set."""

from importlib import import_module


def main() -> None:
    for module_name, function_name in (
        ("01_chat_completion", "run_chat_completion"),
        ("02_streaming", "run_streaming"),
        ("03_tool_calling", "run_tool_calling"),
    ):
        getattr(import_module(module_name), function_name)()


if __name__ == "__main__":
    main()
