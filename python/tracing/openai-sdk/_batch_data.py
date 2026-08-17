from __future__ import annotations

from typing import Any

from _shared import model_name


def batch_requests() -> list[dict[str, Any]]:
    return [
        {
            "custom_id": f"topic-{index}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model_name(),
                "messages": [{"role": "user", "content": f"Summarize {topic}."}],
            },
        }
        for index, topic in enumerate(
            ("quantum computing", "blockchain", "edge computing")
        )
    ]


def batch_results(requests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "custom_id": request["custom_id"],
            "response": {
                "status_code": 200,
                "body": {
                    "id": f"chat_{request['custom_id']}",
                    "object": "chat.completion",
                    "created": 1_786_972_800 + index,
                    "model": model_name(),
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": f"Deterministic summary {index + 1}.",
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 5 + index,
                        "completion_tokens": 3,
                        "total_tokens": 8 + index,
                    },
                },
            },
        }
        for index, request in enumerate(requests)
    ]
