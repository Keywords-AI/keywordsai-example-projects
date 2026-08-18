from __future__ import annotations


def test_success_before_failure() -> None:
    assert "otel".upper() == "OTEL"


def test_expected_assertion_failure() -> None:
    assert {"expected": 42} == {"actual": 41}
