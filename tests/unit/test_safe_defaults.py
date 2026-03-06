"""Tests for safe_defaults module.

E4: Tests for safe factory patterns.
"""

import pytest
from dataclasses import dataclass, field

from solstein.data.safe_defaults import (
    SafeDefault,
    SafeDefaultsMixin,
    copy_with_safe_defaults,
    ensure_bool,
    ensure_dict,
    ensure_float,
    ensure_int,
    ensure_list,
    ensure_set,
    ensure_str,
    list_factory,
    dict_factory,
    set_factory,
    merge_safe,
)


class TestEnsureFunctions:
    """Tests for ensure_* helper functions."""

    def test_ensure_list_with_value(self) -> None:
        assert ensure_list([1, 2, 3]) == [1, 2, 3]

    def test_ensure_list_with_none(self) -> None:
        assert ensure_list(None) == []

    def test_ensure_dict_with_value(self) -> None:
        assert ensure_dict({"key": "value"}) == {"key": "value"}

    def test_ensure_dict_with_none(self) -> None:
        assert ensure_dict(None) == {}

    def test_ensure_set_with_value(self) -> None:
        assert ensure_set({1, 2, 3}) == {1, 2, 3}

    def test_ensure_set_with_none(self) -> None:
        assert ensure_set(None) == set()

    def test_ensure_str_with_value(self) -> None:
        assert ensure_str("hello") == "hello"

    def test_ensure_str_with_none(self) -> None:
        assert ensure_str(None) == ""
        assert ensure_str(None, default="N/A") == "N/A"

    def test_ensure_int_with_value(self) -> None:
        assert ensure_int(42) == 42

    def test_ensure_int_with_none(self) -> None:
        assert ensure_int(None) == 0
        assert ensure_int(None, default=100) == 100

    def test_ensure_float_with_value(self) -> None:
        assert ensure_float(3.14) == 3.14

    def test_ensure_float_with_none(self) -> None:
        assert ensure_float(None) == 0.0
        assert ensure_float(None, default=1.5) == 1.5

    def test_ensure_bool_with_value(self) -> None:
        assert ensure_bool(True) is True
        assert ensure_bool(False) is False

    def test_ensure_bool_with_none(self) -> None:
        assert ensure_bool(None) is False
        assert ensure_bool(None, default=True) is True


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_list_factory(self) -> None:
        factory = list_factory()
        assert factory() == []
        assert factory() is not factory()  # Fresh list each time

    def test_dict_factory(self) -> None:
        factory = dict_factory()
        assert factory() == {}
        assert factory() is not factory()  # Fresh dict each time

    def test_set_factory(self) -> None:
        factory = set_factory()
        assert factory() == set()
        assert factory() is not factory()  # Fresh set each time


class TestSafeDefaultDescriptor:
    """Tests for SafeDefault descriptor."""

    def test_descriptor_creates_fresh_instances(self) -> None:
        class TestClass:
            items = SafeDefault(list)
            data = SafeDefault(dict)

        obj1 = TestClass()
        obj2 = TestClass()

        # Each instance gets its own list
        obj1.items.append(1)
        assert obj1.items == [1]
        assert obj2.items == []  # Not shared!

        # Each instance gets its own dict
        obj1.data["key"] = "value"
        assert obj1.data == {"key": "value"}
        assert obj2.data == {}  # Not shared!

    def test_descriptor_allows_setting(self) -> None:
        class TestClass:
            items = SafeDefault(list)

        obj = TestClass()
        obj.items = [1, 2, 3]
        assert obj.items == [1, 2, 3]

    def test_descriptor_allows_deletion(self) -> None:
        class TestClass:
            items = SafeDefault(list)

        obj = TestClass()
        obj.items.append(1)
        del obj.items
        assert obj.items == []  # Fresh instance after deletion


class TestSafeDefaultsMixin:
    """Tests for SafeDefaultsMixin dataclass."""

    def test_fresh_instances_per_object(self) -> None:
        @dataclass
        class MyClass(SafeDefaultsMixin):
            pass

        obj1 = MyClass()
        obj2 = MyClass()

        obj1.items.append(1)
        obj1.metadata["key"] = "value"
        obj1.tags.add("tag")

        assert obj1.items == [1]
        assert obj1.metadata == {"key": "value"}
        assert obj1.tags == {"tag"}

        assert obj2.items == []
        assert obj2.metadata == {}
        assert obj2.tags == set()


class TestCopyWithSafeDefaults:
    """Tests for copy_with_safe_defaults function."""

    def test_copies_simple_values(self) -> None:
        original = {"name": "TestCo", "count": 42}
        result = copy_with_safe_defaults(original)

        assert result == original
        assert result is not original

    def test_creates_fresh_list(self) -> None:
        original = {"items": [1, 2, 3]}
        result = copy_with_safe_defaults(original)

        result["items"].append(4)
        assert len(original["items"]) == 3  # Original unchanged

    def test_creates_fresh_dict(self) -> None:
        original = {"data": {"key": "value"}}
        result = copy_with_safe_defaults(original)

        result["data"]["new"] = "added"
        assert "new" not in original["data"]  # Original unchanged

    def test_creates_fresh_set(self) -> None:
        original = {"tags": {1, 2, 3}}
        result = copy_with_safe_defaults(original)

        result["tags"].add(4)
        assert 4 not in original["tags"]  # Original unchanged


class TestMergeSafe:
    """Tests for merge_safe function."""

    def test_shallow_merge(self) -> None:
        base = {"name": "TestCo", "count": 10}
        updates = {"count": 20, "new": "value"}
        result = merge_safe(base, updates, deep=False)

        assert result["name"] == "TestCo"
        assert result["count"] == 20
        assert result["new"] == "value"

    def test_deep_merge_dicts(self) -> None:
        base = {"data": {"a": 1, "b": 2}}
        updates = {"data": {"b": 3, "c": 4}}
        result = merge_safe(base, updates, deep=True)

        assert result["data"]["a"] == 1  # Preserved from base
        assert result["data"]["b"] == 3  # Updated
        assert result["data"]["c"] == 4  # Added

    def test_merge_lists(self) -> None:
        base = {"items": [1, 2]}
        updates = {"items": [3, 4]}
        result = merge_safe(base, updates, deep=True)

        assert result["items"] == [1, 2, 3, 4]

    def test_does_not_mutate_original(self) -> None:
        base = {"items": [1, 2], "data": {"key": "value"}}
        updates = {"items": [3], "data": {"new": "added"}}
        result = merge_safe(base, updates, deep=True)

        # Original unchanged
        assert base["items"] == [1, 2]
        assert base["data"] == {"key": "value"}

        # Result has merged values
        assert result["items"] == [1, 2, 3]
        assert result["data"] == {"key": "value", "new": "added"}
