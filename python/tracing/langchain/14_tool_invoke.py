"""Tool invoke."""

from _shared import flush, get_weather, init_telemetry, tracing_config


def tool_invoke() -> None:
    telemetry = init_telemetry("langchain-tool-invoke")
    try:
        response = get_weather.invoke(
            {"city": "Tokyo"},
            config=tracing_config("tool_invoke"),
        )
        print(response)
    finally:
        flush(telemetry)


if __name__ == "__main__":
    tool_invoke()
