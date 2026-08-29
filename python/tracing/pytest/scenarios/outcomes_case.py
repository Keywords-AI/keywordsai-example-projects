from __future__ import annotations

import pytest
from respan import task


@task(name="calculate_total")
def calculate_total(subtotal: int, tax: int) -> int:
    return subtotal + tax


def test_nested_application_task() -> None:
    assert calculate_total(40, 2) == 42


@pytest.mark.parametrize(("left", "right", "expected"), [(2, 3, 5), (7, 8, 15)])
def test_parametrized_addition(left: int, right: int, expected: int) -> None:
    assert left + right == expected


@pytest.mark.skip(reason="deterministic skipped outcome")
def test_skipped_case() -> None:
    raise AssertionError("skip marker was ignored")


@pytest.mark.xfail(reason="deterministic expected failure")
def test_expected_failure() -> None:
    expected, actual = 1, 2
    assert expected == actual
