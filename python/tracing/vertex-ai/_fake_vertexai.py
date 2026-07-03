"""Local Vertex AI compatibility objects for runnable tracing examples."""

from __future__ import annotations

import sys
from collections.abc import Iterator
from types import ModuleType
from typing import Any


class _Obj:
    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)


class FunctionDeclaration:
    def __init__(
        self,
        *,
        name: str,
        description: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.parameters = parameters


class Tool:
    def __init__(self, *, function_declarations: list[FunctionDeclaration]) -> None:
        self.function_declarations = function_declarations


class _Usage:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_token_count = prompt_tokens
        self.candidates_token_count = completion_tokens
        self.total_token_count = prompt_tokens + completion_tokens


class _Response:
    def __init__(
        self,
        text: str,
        *,
        usage: _Usage,
        parts: list[Any] | None = None,
    ) -> None:
        self.text = text
        content = _Obj(role="model", parts=parts if parts is not None else [_Obj(text=text)])
        self.candidates = [_Obj(content=content)]
        self.usage_metadata = usage


class ChatSession:
    def __init__(self, model: "GenerativeModel") -> None:
        self.model = model

    def send_message(self, content: str, *, stream: bool = False, **_: Any) -> Any:
        if stream:
            return iter(
                [
                    _Response("Vertex ", usage=_Usage(0, 0)),
                    _Response("chat response", usage=_Usage(9, 13)),
                ]
            )
        return _Response(f"Vertex chat response: {content}", usage=_Usage(9, 13))

    async def send_message_async(self, content: str, **_: Any) -> _Response:
        return _Response(f"Async Vertex chat response: {content}", usage=_Usage(9, 13))


class GenerativeModel:
    def __init__(
        self,
        model_name: str,
        *,
        system_instruction: str | None = None,
        tools: list[Tool] | None = None,
        **_: Any,
    ) -> None:
        self._model_name = model_name
        self._system_instruction = system_instruction
        self._tools = tools

    def generate_content(self, contents: str, *, stream: bool = False, **_: Any) -> Any:
        if stream:
            return self._stream_response()
        return _Response(
            f"Vertex generated answer: {contents}",
            usage=_Usage(12, 18),
        )

    async def generate_content_async(self, contents: str, **_: Any) -> _Response:
        return _Response(f"Async Vertex generated answer: {contents}", usage=_Usage(12, 18))

    def start_chat(self, **_: Any) -> ChatSession:
        return ChatSession(self)

    def _stream_response(self) -> Iterator[_Response]:
        yield _Response("Vertex ", usage=_Usage(0, 0))
        yield _Response("streamed answer", usage=_Usage(12, 18))


def install_fake_vertexai() -> None:
    vertexai_module = ModuleType("vertexai")
    generative_models_module = ModuleType("vertexai.generative_models")

    def init(**_: Any) -> None:
        return None

    vertexai_module.init = init  # type: ignore[attr-defined]
    vertexai_module.generative_models = generative_models_module  # type: ignore[attr-defined]
    generative_models_module.GenerativeModel = GenerativeModel  # type: ignore[attr-defined]
    generative_models_module.ChatSession = ChatSession  # type: ignore[attr-defined]
    generative_models_module.FunctionDeclaration = FunctionDeclaration  # type: ignore[attr-defined]
    generative_models_module.Tool = Tool  # type: ignore[attr-defined]

    sys.modules["vertexai"] = vertexai_module
    sys.modules["vertexai.generative_models"] = generative_models_module
