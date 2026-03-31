"""Safe factory patterns for mutable defaults.

E4: Replace mutable defaults with safe factories
Provides factory functions and descriptors to prevent mutable default argument bugs.

Anti-pattern this module fixes:
    def bad(items=[]):  # Mutable default!
        items.append(1)
        return items

Pattern this module enables:
    def good(items=None):
        items = ensure_list(items)
        items.append(1)
        return items
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

T = TypeVar("T")


def ensure_list(value: list[T] | None) -> list[T]:
    """Ensure a value is a list, converting None to empty list.

    Args:
        value: Optional list value

    Returns:
        List (empty if input was None)
    """
    return value if value is not None else []


def ensure_dict(value: dict[str, T] | None) -> dict[str, T]:
    """Ensure a value is a dict, converting None to empty dict.

    Args:
        value: Optional dict value

    Returns:
        Dict (empty if input was None)
    """
    return value if value is not None else {}


def ensure_set(value: set[T] | None) -> set[T]:
    """Ensure a value is a set, converting None to empty set.

    Args:
        value: Optional set value

    Returns:
        Set (empty if input was None)
    """
    return value if value is not None else set()


def ensure_str(value: str | None, default: str = "") -> str:
    """Ensure a value is a string, converting None to default.

    Args:
        value: Optional string value
        default: Default if value is None

    Returns:
        String (default if input was None)
    """
    return value if value is not None else default


def ensure_int(value: int | None, default: int = 0) -> int:
    """Ensure a value is an int, converting None to default.

    Args:
        value: Optional int value
        default: Default if value is None

    Returns:
        Int (default if input was None)
    """
    return value if value is not None else default


def ensure_float(value: float | None, default: float = 0.0) -> float:
    """Ensure a value is a float, converting None to default.

    Args:
        value: Optional float value
        default: Default if value is None

    Returns:
        Float (default if input was None)
    """
    return value if value is not None else default


def ensure_bool(value: bool | None, default: bool = False) -> bool:
    """Ensure a value is a bool, converting None to default.

    Args:
        value: Optional bool value
        default: Default if value is None

    Returns:
        Bool (default if input was None)
    """
    return value if value is not None else default


def list_factory() -> Callable[[], list[Any]]:
    """Factory function for dataclass list fields.

    Usage:
        @dataclass
        class MyClass:
            items: list[str] = field(default_factory=list_factory())
    """
    return list


def dict_factory() -> Callable[[], dict[str, Any]]:
    """Factory function for dataclass dict fields.

    Usage:
        @dataclass
        class MyClass:
            data: dict[str, int] = field(default_factory=dict_factory())
    """
    return dict


def set_factory() -> Callable[[], set[Any]]:
    """Factory function for dataclass set fields.

    Usage:
        @dataclass
        class MyClass:
            tags: set[str] = field(default_factory=set_factory())
    """
    return set


class SafeDefault:
    """Descriptor for safe mutable defaults in classes.

    Prevents the common bug where mutable defaults are shared across instances.

    Usage:
        class MyClass:
            items = SafeDefault(list)
            data = SafeDefault(dict)
            tags = SafeDefault(set)

    Each instance gets its own fresh mutable object.
    """

    def __init__(self, factory: Callable[[], T]) -> None:
        self.factory = factory
        self.name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance: Any, owner: type) -> T:
        if instance is None:
            return self.factory()  # type: ignore

        # Check if already set on instance
        if self.name not in instance.__dict__:
            instance.__dict__[self.name] = self.factory()

        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: T) -> None:
        instance.__dict__[self.name] = value

    def __delete__(self, instance: Any) -> None:
        if self.name in instance.__dict__:
            del instance.__dict__[self.name]


# Convenience instances for common use cases
def SafeList():
    return SafeDefault(list)
def SafeDict():
    return SafeDefault(dict)
def SafeSet():
    return SafeDefault(set)


@dataclass
class SafeDefaultsMixin:
    """Mixin class demonstrating safe default patterns.

    Use this as a reference for implementing safe defaults in your classes.
    """

    # Use field(default_factory=...) for dataclasses
    items: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: set[str] = field(default_factory=set)

    # For non-dataclass usage, use SafeDefault descriptor
    # (defined at class level, not instance level)


def copy_with_safe_defaults(original: dict[str, Any]) -> dict[str, Any]:
    """Copy a dict ensuring all mutable values are fresh copies.

    Args:
        original: Original dictionary

    Returns:
        Deep copy with fresh mutable objects
    """
    result: dict[str, Any] = {}
    for key, value in original.items():
        if isinstance(value, list):
            result[key] = list(value)
        elif isinstance(value, dict):
            result[key] = dict(value)
        elif isinstance(value, set):
            result[key] = set(value)
        else:
            result[key] = value
    return result


def merge_safe(
    base: dict[str, Any],
    updates: dict[str, Any],
    deep: bool = True,
) -> dict[str, Any]:
    """Merge two dicts with safe handling of mutable values.

    Args:
        base: Base dictionary
        updates: Updates to apply
        deep: Whether to deep merge nested dicts/lists

    Returns:
        New merged dictionary
    """
    result = copy_with_safe_defaults(base)

    for key, value in updates.items():
        if deep and key in result:
            existing = result[key]
            if isinstance(existing, dict) and isinstance(value, dict):
                result[key] = merge_safe(existing, value, deep=True)
                continue
            elif isinstance(existing, list) and isinstance(value, list):
                result[key] = existing + value
                continue

        # Default: shallow copy for mutable types
        if isinstance(value, list):
            result[key] = list(value)
        elif isinstance(value, dict):
            result[key] = dict(value)
        elif isinstance(value, set):
            result[key] = set(value)
        else:
            result[key] = value

    return result
