"""Model-derived thinking config (`config.thinking_config`).

Regression guard for a real bug: `.env.example` advertises
GENERATION_MODEL=claude-haiku-4-5 as the cheap option, but adaptive thinking
only exists on Claude 4.6+, so sending {"type": "adaptive"} to Haiku 4.5
returned a 400 on every request.
"""
import pytest

from backend import config


@pytest.mark.parametrize("model", [
    "claude-opus-4-8",
    "claude-opus-4-7",
    "claude-opus-4-6",
    "claude-sonnet-5",
    "claude-sonnet-4-6",
    "claude-fable-5",
])
def test_modern_models_get_adaptive_thinking(model, monkeypatch):
    monkeypatch.setattr(config, "THINKING_ON", True)
    assert config.thinking_config(model) == {"type": "adaptive"}


@pytest.mark.parametrize("model", [
    "claude-haiku-4-5",     # advertised as the cheap option — used to 400
    "claude-sonnet-4-5",
    "claude-opus-4-1",
])
def test_pre_4_6_models_omit_thinking_instead_of_400ing(model, monkeypatch):
    monkeypatch.setattr(config, "THINKING_ON", True)
    assert config.thinking_config(model) is None


def test_thinking_off_disables_it_even_on_supported_models(monkeypatch):
    monkeypatch.setattr(config, "THINKING_ON", False)
    assert config.thinking_config("claude-opus-4-8") is None


def test_unknown_model_is_treated_as_unsupported(monkeypatch):
    # Fail safe: an unrecognised or dated-snapshot gateway ID omits thinking
    # rather than risking a 400 on every request.
    monkeypatch.setattr(config, "THINKING_ON", True)
    assert config.thinking_config("claude-opus-4-5-20251101") is None
    assert config.thinking_config("some-future-model") is None
