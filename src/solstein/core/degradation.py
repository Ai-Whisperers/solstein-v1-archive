"""Degraded-mode propagation signals.

F5: Add degraded-mode propagation
Provides mechanisms for services to signal degradation and for clients to handle it gracefully.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum, auto
from typing import Any, Callable

from loguru import logger


class DegradationLevel(Enum):
    """Levels of service degradation."""

    NONE = auto()  # Service fully operational
    PARTIAL = auto()  # Some features degraded
    SIGNIFICANT = auto()  # Most features degraded
    CRITICAL = auto()  # Service barely functional
    DOWN = auto()  # Service unavailable


class DegradationType(Enum):
    """Types of degradation."""

    LLM_UNAVAILABLE = "llm_unavailable"
    DATABASE_SLOW = "database_slow"
    EXTERNAL_API_TIMEOUT = "external_api_timeout"
    CACHE_MISS = "cache_miss"
    RATE_LIMITED = "rate_limited"
    HIGH_LOAD = "high_load"
    MEMORY_PRESSURE = "memory_pressure"


@dataclass
class DegradationSignal:
    """Signal indicating service degradation.

    F5: Propagates degradation state through the system.
    """

    source: str
    level: DegradationLevel
    degradation_type: DegradationType
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ttl_seconds: int = 300  # Time-to-live for this signal
    affected_features: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if the signal has expired."""
        age = datetime.now(timezone.utc) - self.timestamp
        return age.total_seconds() > self.ttl_seconds

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for propagation."""
        return {
            "source": self.source,
            "level": self.level.name,
            "degradation_type": self.degradation_type.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "ttl_seconds": self.ttl_seconds,
            "affected_features": self.affected_features,
            "metadata": self.metadata,
            "expired": self.is_expired(),
        }


@dataclass
class DegradationState:
    """Current degradation state of a service.

    F5: Aggregates multiple degradation signals into overall state.
    """

    service_name: str
    signals: list[DegradationSignal] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def overall_level(self) -> DegradationLevel:
        """Calculate overall degradation level from all signals."""
        if not self.signals:
            return DegradationLevel.NONE

        # Remove expired signals
        self.signals = [s for s in self.signals if not s.is_expired()]

        if not self.signals:
            return DegradationLevel.NONE

        # Return the worst level
        level_priority = [
            DegradationLevel.DOWN,
            DegradationLevel.CRITICAL,
            DegradationLevel.SIGNIFICANT,
            DegradationLevel.PARTIAL,
            DegradationLevel.NONE,
        ]
        for level in level_priority:
            if any(s.level == level for s in self.signals):
                return level

        return DegradationLevel.NONE

    @property
    def is_degraded(self) -> bool:
        """Check if service is in degraded state."""
        return self.overall_level != DegradationLevel.NONE

    def add_signal(self, signal: DegradationSignal) -> None:
        """Add a degradation signal."""
        self.signals.append(signal)
        self.last_updated = datetime.now(timezone.utc)

    def clear_expired(self) -> None:
        """Remove expired signals."""
        self.signals = [s for s in self.signals if not s.is_expired()]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "service_name": self.service_name,
            "overall_level": self.overall_level.name,
            "is_degraded": self.is_degraded,
            "signal_count": len(self.signals),
            "signals": [s.to_dict() for s in self.signals],
            "last_updated": self.last_updated.isoformat(),
        }


class DegradationHandler:
    """Handles degradation signals and coordinates fallback behavior.

    F5: Central handler for managing service degradation.
    """

    def __init__(self) -> None:
        self._states: dict[str, DegradationState] = {}
        self._handlers: dict[DegradationType, list[Callable]] = {}

    def register_state(self, service_name: str) -> DegradationState:
        """Register a service for degradation tracking."""
        if service_name not in self._states:
            self._states[service_name] = DegradationState(service_name=service_name)
        return self._states[service_name]

    def emit_signal(self, signal: DegradationSignal) -> None:
        """Emit a degradation signal."""
        state = self.register_state(signal.source)
        state.add_signal(signal)

        logger.warning(
            "Degradation signal emitted",
            source=signal.source,
            level=signal.level.name,
            type=signal.degradation_type.value,
            message=signal.message,
        )

        # Trigger registered handlers
        handlers = self._handlers.get(signal.degradation_type, [])
        for handler in handlers:
            try:
                handler(signal)
            except Exception as e:
                logger.error("Degradation handler failed", error=str(e))

    def get_state(self, service_name: str) -> DegradationState | None:
        """Get degradation state for a service."""
        return self._states.get(service_name)

    def is_degraded(self, service_name: str) -> bool:
        """Check if a service is degraded."""
        state = self._states.get(service_name)
        if not state:
            return False
        return state.is_degraded

    def register_handler(self, degradation_type: DegradationType, handler: Callable[[DegradationSignal], None]) -> None:
        """Register a handler for a specific degradation type."""
        if degradation_type not in self._handlers:
            self._handlers[degradation_type] = []
        self._handlers[degradation_type].append(handler)

    def get_all_states(self) -> dict[str, DegradationState]:
        """Get all degradation states."""
        # Clear expired signals first
        for state in self._states.values():
            state.clear_expired()
        return dict(self._states)

    def clear_all(self) -> None:
        """Clear all degradation states."""
        self._states.clear()
        self._handlers.clear()


# Global degradation handler instance
_degradation_handler: DegradationHandler | None = None


def get_degradation_handler() -> DegradationHandler:
    """Get the global degradation handler."""
    global _degradation_handler
    if _degradation_handler is None:
        _degradation_handler = DegradationHandler()
    return _degradation_handler


def emit_degradation(
    source: str,
    level: DegradationLevel,
    degradation_type: DegradationType,
    message: str,
    affected_features: list[str] | None = None,
    ttl_seconds: int = 300,
    **metadata: Any,
) -> None:
    """Convenience function to emit a degradation signal.

    Args:
        source: Service emitting the signal
        level: Degradation level
        degradation_type: Type of degradation
        message: Human-readable message
        affected_features: List of affected features
        ttl_seconds: Time-to-live for this signal
        **metadata: Additional metadata
    """
    signal = DegradationSignal(
        source=source,
        level=level,
        degradation_type=degradation_type,
        message=message,
        affected_features=affected_features or [],
        ttl_seconds=ttl_seconds,
        metadata=metadata,
    )
    get_degradation_handler().emit_signal(signal)


def check_degradation(service_name: str) -> DegradationLevel:
    """Check degradation level for a service.

    Args:
        service_name: Name of the service to check

    Returns:
        Current degradation level
    """
    handler = get_degradation_handler()
    state = handler.get_state(service_name)
    if not state:
        return DegradationLevel.NONE
    return state.overall_level


class DegradationContext:
    """Context manager for temporary degradation.

    F5: Allows code to signal degradation within a block.
    """

    def __init__(
        self,
        source: str,
        degradation_type: DegradationType,
        message: str,
        level: DegradationLevel = DegradationLevel.PARTIAL,
        affected_features: list[str] | None = None,
    ) -> None:
        self.source = source
        self.degradation_type = degradation_type
        self.message = message
        self.level = level
        self.affected_features = affected_features or []
        self.signal: DegradationSignal | None = None

    def __enter__(self) -> DegradationContext:
        self.signal = DegradationSignal(
            source=self.source,
            level=self.level,
            degradation_type=self.degradation_type,
            message=self.message,
            affected_features=self.affected_features,
            ttl_seconds=60,  # Short TTL for context-based signals
        )
        get_degradation_handler().emit_signal(self.signal)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        # Signal will expire naturally due to TTL
        pass


def with_degradation_handling(
    source: str,
    degradation_type: DegradationType,
    fallback_value: Any = None,
    affected_features: list[str] | None = None,
):
    """Decorator to handle degradation in functions.

    F5: Wraps functions to emit degradation signals on failure.

    Args:
        source: Service name
        degradation_type: Type of degradation
        fallback_value: Value to return on failure
        affected_features: Features affected by this function

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                emit_degradation(
                    source=source,
                    level=DegradationLevel.PARTIAL,
                    degradation_type=degradation_type,
                    message=f"Function {func.__name__} failed: {str(e)}",
                    affected_features=affected_features or [],
                )
                if fallback_value is not None:
                    return fallback_value
                raise

        return wrapper

    return decorator
