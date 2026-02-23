"""
MyPy strict-mode type checking test.

Each section exercises a different class of rule enforced by our config.
Run: uv run mypy main.py
"""

from __future__ import annotations

import functools
import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

# ---------------------------------------------------------------------------
# 1. disallow_untyped_defs / disallow_incomplete_defs
#    Every argument and return value must be annotated.
# ---------------------------------------------------------------------------


def add(x: int, y: int) -> int:
    return x + y


def greet(name: str) -> str:
    return f"Hello, {name}"


# ---------------------------------------------------------------------------
# 2. disallow_any_generics
#    Generic types must be parameterised — no bare list/dict/tuple.
# ---------------------------------------------------------------------------


def first_item(items: list[int]) -> int | None:
    return items[0] if items else None


def merge(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    return {**a, **b}


# ---------------------------------------------------------------------------
# 3. warn_return_any / check_untyped_defs
#    Return types must be specific; no implicit Any.
# ---------------------------------------------------------------------------


def parse_score(raw: str) -> int:
    return int(raw)


# ---------------------------------------------------------------------------
# 4. strict_equality
#    Mypy flags comparisons that are always True/False due to incompatible
#    types. This function is correct — both sides are int.
# ---------------------------------------------------------------------------


def is_zero(value: int) -> bool:
    return value == 0


# ---------------------------------------------------------------------------
# 5. warn_unreachable
#    Mypy flags code that can never execute. This exhaustive if/else has
#    no dead branches.
# ---------------------------------------------------------------------------


def classify(n: int) -> str:
    if n > 0:
        return "positive"
    elif n < 0:
        return "negative"
    else:
        return "zero"


# ---------------------------------------------------------------------------
# 6. Optional / None handling (strict_optional on by default under strict)
#    Must explicitly check for None before using the value.
# ---------------------------------------------------------------------------


def safe_upper(text: str | None) -> str:
    if text is None:
        return ""
    return text.upper()


# ---------------------------------------------------------------------------
# 7. disallow_untyped_decorators
#    Decorators must be fully typed. functools.wraps is typed in typeshed.
#    Python 3.12 type parameter syntax replaces TypeVar.
# ---------------------------------------------------------------------------


def log_call[F: Callable[..., object]](func: F) -> F:
    @functools.wraps(func)
    def wrapper(*args: object, **kwargs: object) -> object:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


@log_call
def compute(x: int) -> int:
    return x * 2


# ---------------------------------------------------------------------------
# 8. Dataclass with full annotations
# ---------------------------------------------------------------------------


@dataclass
class Point:
    x: float
    y: float

    def distance_from_origin(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)


# ---------------------------------------------------------------------------
# 9. Protocol (structural subtyping) — exercises no_implicit_reexport
# ---------------------------------------------------------------------------


class Describable(Protocol):
    def describe(self) -> str: ...


@dataclass
class Circle:
    radius: float

    def describe(self) -> str:
        return f"Circle(r={self.radius})"


def print_description(obj: Describable) -> None:
    print(obj.describe())


# ---------------------------------------------------------------------------
# 10. strict_bytes
#     bytearray is not treated as bytes — must convert explicitly.
# ---------------------------------------------------------------------------


def byte_length(data: bytes) -> int:
    return len(data)


def from_bytearray(buf: bytearray) -> int:
    return byte_length(bytes(buf))


# ---------------------------------------------------------------------------
# Async function — demonstrates pytest-asyncio pattern
# ---------------------------------------------------------------------------


async def async_add(x: int, y: int) -> int:
    """Async version of add, used to demonstrate pytest-asyncio."""
    return x + y


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    print(add(1, 2))
    print(greet("world"))
    print(first_item([10, 20, 30]))
    print(merge({"a": 1}, {"b": 2}))
    print(parse_score("42"))
    print(is_zero(0))
    print(classify(-5))
    print(safe_upper(None))
    print(safe_upper("hello"))
    print(compute(7))
    p = Point(3.0, 4.0)
    print(p.distance_from_origin())
    print_description(Circle(radius=5.0))
    print(from_bytearray(bytearray(b"hello")))


if __name__ == "__main__":
    main()
