"""Tests for degradation module.

F5: Tests for degraded-mode propagation signals.
"""

import pytest
from datetime import datetime, timedelta, timezone

from solstein.core.degradation import (
    DegradationContext,
    DegradationHandler,
    DegradationLevel,
    DegradationSignal,
    DegradationState,
    DegradationType,
    check_degradation,
    emit_degradation,
    get_degradation_handler,
    with_degradation_handling,
)


class TestDegradationLevel:
    """Tests for DegradationLevel enum."""

    def test_all_levels_exist(self) -> None:
        assert DegradationLevel.NONE
        assert DegradationLevel.PARTIAL
        assert DegradationLevel.SIGNIFICANT
        assert DegradationLevel.CRITICAL
        assert DegradationLevel.DOWN


class TestDegradationType:
    """Tests for DegradationType enum."""

    def test_all_types_exist(self) -> None:
        assert DegradationType.LLM_UNAVAILABLE
        assert DegradationType.DATABASE_SLOW
        assert DegradationType.EXTERNAL_API_TIMEOUT
        assert DegradationType.CACHE_MISS
        assert DegradationType.RATE_LIMITED


class TestDegradationSignal:
    """Tests for DegradationSignal dataclass."""

    def test_creation(self) -> None:
        signal = DegradationSignal(
            source="test_service",
            level=DegradationLevel.PARTIAL,
            degradation_type=DegradationType.LLM_UNAVAILABLE,
            message="LLM service slow",
        )
        assert signal.source == "test_service"
        assert signal.level == DegradationLevel.PARTIAL
        assert signal.degradation_type == DegradationType.LLM_UNAVAILABLE

    def test_is_expired(self) -> None:
        # Create expired signal
        signal = DegradationSignal(
            source="test",
            level=DegradationLevel.PARTIAL,
            degradation_type=DegradationType.LLM_UNAVAILABLE,
            message="Test",
            ttl_seconds=0,  # Expired immediately
        )
        assert signal.is_expired() is True

    def test_not_expired(self) -> None:
        signal = DegradationSignal(
            source="test",
            level=DegradationLevel.PARTIAL,
            degradation_type=DegradationType.LLM_UNAVAILABLE,
            message="Test",
            ttl_seconds=300,
        )
        assert signal.is_expired() is False

    def test_to_dict(self) -> None:
        signal = DegradationSignal(
            source="test_service",
            level=DegradationLevel.PARTIAL,
            degradation_type=DegradationType.LLM_UNAVAILABLE,
            message="Test message",
            affected_features=["scoring", "classification"],
        )
        result = signal.to_dict()

        assert result["source"] == "test_service"
        assert result["level"] == "PARTIAL"
        assert result["degradation_type"] == "llm_unavailable"
        assert result["message"] == "Test message"
        assert "expired" in result


class TestDegradationState:
    """Tests for DegradationState dataclass."""

    def test_empty_state(self) -> None:
        state = DegradationState(service_name="test")
        assert state.overall_level == DegradationLevel.NONE
        assert state.is_degraded is False

    def test_add_signal(self) -> None:
        state = DegradationState(service_name="test")
        signal = DegradationSignal(
            source="test",
            level=DegradationLevel.PARTIAL,
            degradation_type=DegradationType.LLM_UNAVAILABLE,
            message="Test",
        )
        state.add_signal(signal)

        assert len(state.signals) == 1
        assert state.is_degraded is True
        assert state.overall_level == DegradationLevel.PARTIAL

    def test_overall_level_worst_wins(self) -> None:
        state = DegradationState(service_name="test")

        # Add partial signal
        state.add_signal(
            DegradationSignal(
                source="test",
                level=DegradationLevel.PARTIAL,
                degradation_type=DegradationType.CACHE_MISS,
                message="Cache miss",
            )
        )

        # Add critical signal
        state.add_signal(
            DegradationSignal(
                source="test",
                level=DegradationLevel.CRITICAL,
                degradation_type=DegradationType.DATABASE_SLOW,
                message="DB slow",
            )
        )

        # Overall should be CRITICAL (worst)
        assert state.overall_level == DegradationLevel.CRITICAL

    def test_clear_expired(self) -> None:
        state = DegradationState(service_name="test")

        # Add expired signal
        expired_signal = DegradationSignal(
            source="test",
            level=DegradationLevel.PARTIAL,
            degradation_type=DegradationType.LLM_UNAVAILABLE,
            message="Expired",
            ttl_seconds=0,
        )
        state.add_signal(expired_signal)

        # Clear expired
        state.clear_expired()

        assert len(state.signals) == 0


class TestDegradationHandler:
    """Tests for DegradationHandler class."""

    def setup_method(self) -> None:
        """Clear handler before each test."""
        handler = get_degradation_handler()
        handler.clear_all()

    def test_register_state(self) -> None:
        handler = get_degradation_handler()
        state = handler.register_state("test_service")

        assert state.service_name == "test_service"
        assert handler.get_state("test_service") == state

    def test_emit_signal(self) -> None:
        handler = get_degradation_handler()
        signal = DegradationSignal(
            source="test_service",
            level=DegradationLevel.PARTIAL,
            degradation_type=DegradationType.LLM_UNAVAILABLE,
            message="Test",
        )
        handler.emit_signal(signal)

        state = handler.get_state("test_service")
        assert state is not None
        assert state.is_degraded is True

    def test_is_degraded(self) -> None:
        handler = get_degradation_handler()
        assert handler.is_degraded("unknown_service") is False

        handler.emit_signal(
            DegradationSignal(
                source="test_service",
                level=DegradationLevel.PARTIAL,
                degradation_type=DegradationType.LLM_UNAVAILABLE,
                message="Test",
            )
        )
        assert handler.is_degraded("test_service") is True

    def test_register_handler(self) -> None:
        handler = get_degradation_handler()
        called = False

        def test_handler(signal: DegradationSignal) -> None:
            nonlocal called
            called = True

        handler.register_handler(DegradationType.LLM_UNAVAILABLE, test_handler)

        handler.emit_signal(
            DegradationSignal(
                source="test",
                level=DegradationLevel.PARTIAL,
                degradation_type=DegradationType.LLM_UNAVAILABLE,
                message="Test",
            )
        )

        assert called is True

    def test_get_all_states(self) -> None:
        handler = get_degradation_handler()
        handler.emit_signal(
            DegradationSignal(
                source="service1",
                level=DegradationLevel.PARTIAL,
                degradation_type=DegradationType.LLM_UNAVAILABLE,
                message="Test",
            )
        )

        states = handler.get_all_states()
        assert len(states) == 1
        assert "service1" in states


class TestEmitDegradation:
    """Tests for emit_degradation convenience function."""

    def setup_method(self) -> None:
        get_degradation_handler().clear_all()

    def test_emit(self) -> None:
        emit_degradation(
            source="test_service",
            level=DegradationLevel.PARTIAL,
            degradation_type=DegradationType.LLM_UNAVAILABLE,
            message="Test message",
            affected_features=["scoring"],
        )

        state = get_degradation_handler().get_state("test_service")
        assert state is not None
        assert state.is_degraded is True


class TestCheckDegradation:
    """Tests for check_degradation function."""

    def setup_method(self) -> None:
        get_degradation_handler().clear_all()

    def test_no_degradation(self) -> None:
        level = check_degradation("unknown_service")
        assert level == DegradationLevel.NONE

    def test_with_degradation(self) -> None:
        emit_degradation(
            source="test_service",
            level=DegradationLevel.SIGNIFICANT,
            degradation_type=DegradationType.DATABASE_SLOW,
            message="DB slow",
        )

        level = check_degradation("test_service")
        assert level == DegradationLevel.SIGNIFICANT


class TestDegradationContext:
    """Tests for DegradationContext context manager."""

    def setup_method(self) -> None:
        get_degradation_handler().clear_all()

    def test_context_manager(self) -> None:
        with DegradationContext(
            source="test_service",
            degradation_type=DegradationType.LLM_UNAVAILABLE,
            message="Context test",
        ):
            # During context, degradation should be active
            state = get_degradation_handler().get_state("test_service")
            assert state is not None
            assert state.is_degraded is True


class TestWithDegradationHandling:
    """Tests for with_degradation_handling decorator."""

    def setup_method(self) -> None:
        get_degradation_handler().clear_all()

    def test_successful_execution(self) -> None:
        @with_degradation_handling(
            source="test_service",
            degradation_type=DegradationType.LLM_UNAVAILABLE,
        )
        def success_func() -> str:
            return "success"

        result = success_func()
        assert result == "success"

    def test_failure_with_fallback(self) -> None:
        @with_degradation_handling(
            source="test_service",
            degradation_type=DegradationType.LLM_UNAVAILABLE,
            fallback_value="fallback",
        )
        def fail_func() -> str:
            raise ValueError("Test error")

        result = fail_func()
        assert result == "fallback"

        # Check degradation was emitted
        state = get_degradation_handler().get_state("test_service")
        assert state is not None
        assert state.is_degraded is True

    def test_failure_without_fallback(self) -> None:
        @with_degradation_handling(
            source="test_service",
            degradation_type=DegradationType.LLM_UNAVAILABLE,
        )
        def fail_func() -> str:
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            fail_func()
