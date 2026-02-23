"""Tests for main.py — sync and async coverage of all public functions."""

from __future__ import annotations

import math

import pytest

from main import (
    Circle,
    Point,
    add,
    async_add,
    byte_length,
    classify,
    compute,
    first_item,
    from_bytearray,
    greet,
    is_zero,
    merge,
    parse_score,
    print_description,
    safe_upper,
)

# ---------------------------------------------------------------------------
# Sync tests
# ---------------------------------------------------------------------------


def test_add() -> None:
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    assert add(0, 0) == 0


def test_greet() -> None:
    assert greet("world") == "Hello, world"
    assert greet("Alice") == "Hello, Alice"


def test_first_item_with_items() -> None:
    assert first_item([10, 20, 30]) == 10


def test_first_item_empty() -> None:
    assert first_item([]) is None


def test_merge() -> None:
    assert merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}
    assert merge({}, {"x": 9}) == {"x": 9}


def test_parse_score() -> None:
    assert parse_score("42") == 42
    assert parse_score("0") == 0


def test_is_zero_true() -> None:
    assert is_zero(0) is True


def test_is_zero_false() -> None:
    assert is_zero(1) is False
    assert is_zero(-1) is False


def test_classify_positive() -> None:
    assert classify(5) == "positive"


def test_classify_negative() -> None:
    assert classify(-3) == "negative"


def test_classify_zero() -> None:
    assert classify(0) == "zero"


def test_safe_upper_none() -> None:
    assert safe_upper(None) == ""


def test_safe_upper_string() -> None:
    assert safe_upper("hello") == "HELLO"


def test_compute() -> None:
    assert compute(7) == 14
    assert compute(0) == 0


def test_point_distance() -> None:
    p = Point(3.0, 4.0)
    assert math.isclose(p.distance_from_origin(), 5.0)


def test_point_origin() -> None:
    p = Point(0.0, 0.0)
    assert math.isclose(p.distance_from_origin(), 0.0)


def test_circle_describe() -> None:
    c = Circle(radius=5.0)
    assert c.describe() == "Circle(r=5.0)"


def test_print_description(capsys: pytest.CaptureFixture[str]) -> None:
    print_description(Circle(radius=3.0))
    captured = capsys.readouterr()
    assert captured.out.strip() == "Circle(r=3.0)"


def test_byte_length() -> None:
    assert byte_length(b"hello") == 5
    assert byte_length(b"") == 0


def test_from_bytearray() -> None:
    assert from_bytearray(bytearray(b"hello")) == 5


# ---------------------------------------------------------------------------
# Async tests — pytest-asyncio (asyncio_mode = "auto", no decorator needed)
# ---------------------------------------------------------------------------


async def test_async_add() -> None:
    result = await async_add(3, 4)
    assert result == 7


async def test_async_add_zero() -> None:
    result = await async_add(0, 0)
    assert result == 0


async def test_async_add_negative() -> None:
    result = await async_add(-5, 5)
    assert result == 0


# Async fixture — pytest-asyncio handles awaiting it automatically
@pytest.fixture
async def precomputed_sum() -> int:
    return await async_add(10, 20)


async def test_async_fixture(precomputed_sum: int) -> None:
    assert precomputed_sum == 30
