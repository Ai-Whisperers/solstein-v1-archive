"""Tests for contextvars-based request context propagation.

This module tests the context propagation system that ensures
request_id, correlation_id, tenant_id, and user_id flow through
all layers of the application.
"""

import asyncio
from contextvars import copy_context

import pytest

from solstein.utils.context import (
    CORRELATION_ID,
    OPERATION,
    REQUEST_ID,
    TENANT_ID,
    USER_ID,
    clear_context,
    generate_correlation_id,
    generate_request_id,
    get_current_context,
    reset_context,
    set_context,
    with_context,
)


class TestContextBasics:
    """Test basic context variable operations."""

    def test_set_and_get_context(self):
        """Test setting and retrieving context values."""
        tokens = set_context(
            request_id="req-123",
            correlation_id="corr-456",
            tenant_id="tenant-abc",
            user_id="user-xyz",
            operation="GET_/test",
        )

        try:
            assert REQUEST_ID.get() == "req-123"
            assert CORRELATION_ID.get() == "corr-456"
            assert TENANT_ID.get() == "tenant-abc"
            assert USER_ID.get() == "user-xyz"
            assert OPERATION.get() == "GET_/test"
        finally:
            reset_context(tokens)

    def test_get_current_context(self):
        """Test getting all context as dictionary."""
        tokens = set_context(
            request_id="req-test",
            correlation_id="corr-test",
        )

        try:
            ctx = get_current_context()
            assert ctx["request_id"] == "req-test"
            assert ctx["correlation_id"] == "corr-test"
        finally:
            reset_context(tokens)

    def test_get_current_context_empty(self):
        """Test getting context when nothing is set."""
        clear_context()
        ctx = get_current_context()
        assert ctx == {}


class TestContextIsolation:
    """Test that context is properly isolated between scopes."""

    def test_context_isolation_between_calls(self):
        """Test that context doesn't leak between function calls."""

        def scope1():
            tokens = set_context(request_id="scope1")
            result = REQUEST_ID.get()
            reset_context(tokens)
            return result

        def scope2():
            tokens = set_context(request_id="scope2")
            result = REQUEST_ID.get()
            reset_context(tokens)
            return result

        # Run in isolation using copy_context
        ctx1 = copy_context()
        ctx2 = copy_context()

        result1 = ctx1.run(scope1)
        result2 = ctx2.run(scope2)

        assert result1 == "scope1"
        assert result2 == "scope2"

    @pytest.mark.asyncio
    async def test_context_isolation_async(self):
        """Test context isolation in async operations."""

        async def task1():
            tokens = set_context(request_id="task1")
            await asyncio.sleep(0.01)
            result = REQUEST_ID.get()
            reset_context(tokens)
            return result

        async def task2():
            tokens = set_context(request_id="task2")
            await asyncio.sleep(0.01)
            result = REQUEST_ID.get()
            reset_context(tokens)
            return result

        result1, result2 = await asyncio.gather(task1(), task2())

        assert result1 == "task1"
        assert result2 == "task2"


class TestContextHelpers:
    """Test helper functions and decorators."""

    def test_generate_request_id(self):
        """Test request ID generation."""
        req_id = generate_request_id()
        assert len(req_id) == 8
        assert req_id.isalnum()

        # Should be different each time
        req_id2 = generate_request_id()
        assert req_id != req_id2

    def test_generate_correlation_id(self):
        """Test correlation ID generation."""
        corr_id = generate_correlation_id()
        # UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        assert len(corr_id) == 36
        assert corr_id.count("-") == 4

    def test_with_context_decorator(self):
        """Test the with_context decorator."""

        @with_context(operation="test_operation")
        def my_function():
            return OPERATION.get()

        result = my_function()
        assert result == "test_operation"

        # Context should be cleared after function
        assert get_current_context().get("operation") is None


class TestContextReset:
    """Test context reset and cleanup."""

    def test_reset_context(self):
        """Test that reset_context properly clears values."""
        tokens = set_context(
            request_id="test",
            correlation_id="corr",
            tenant_id="tenant",
        )

        # Verify set
        assert REQUEST_ID.get() == "test"

        # Reset
        reset_context(tokens)

        # Verify cleared
        with pytest.raises(LookupError):
            REQUEST_ID.get()
        with pytest.raises(LookupError):
            CORRELATION_ID.get()

    def test_clear_context(self):
        """Test clear_context clears all variables."""
        set_context(
            request_id="test",
            correlation_id="corr",
        )

        # Verify set
        assert get_current_context() != {}

        # Clear
        clear_context()

        # Verify all cleared
        assert get_current_context() == {}


class TestPartialContext:
    """Test setting partial context."""

    def test_set_only_request_id(self):
        """Test setting only request_id."""
        tokens = set_context(request_id="only-req")

        try:
            assert REQUEST_ID.get() == "only-req"
            # Others should not be set
            with pytest.raises(LookupError):
                CORRELATION_ID.get()
        finally:
            reset_context(tokens)

    def test_set_only_tenant_id(self):
        """Test setting only tenant_id."""
        tokens = set_context(tenant_id="only-tenant")

        try:
            assert TENANT_ID.get() == "only-tenant"
            ctx = get_current_context()
            assert ctx == {"tenant_id": "only-tenant"}
        finally:
            reset_context(tokens)
