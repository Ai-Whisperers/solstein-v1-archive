from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from solstein.config import get_settings
from solstein.infrastructure.retry_policy import (
    CircuitBreaker,
    FailureClassification,
    RetryPolicy,
)

from .contracts import ConnectorRequest, ConnectorResponse

PayloadT = TypeVar("PayloadT")


class ConnectorRuntime:
    def __init__(
        self,
        *,
        retry_policy: RetryPolicy | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        sleep_func: Callable[[float], Awaitable[None]] | None = None,
    ) -> None:
        self.retry_policy = retry_policy or RetryPolicy(max_attempts=3)
        if circuit_breaker is not None:
            self.circuit_breaker = circuit_breaker
        else:
            _cb = get_settings().circuit_breaker
            self.circuit_breaker = CircuitBreaker(
                failure_threshold=_cb.failure_threshold,
                cooldown_seconds=_cb.cooldown_seconds,
            )
        self.sleep_func = sleep_func or asyncio.sleep

    async def run(
        self,
        *,
        request: ConnectorRequest,
        operation: Callable[[], Awaitable[PayloadT]],
        retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
        empty_error: str | None = None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> ConnectorResponse[PayloadT]:
        """Run an operation with retry and circuit-breaker protection.

        Args:
            request: Connector request metadata.
            operation: Zero-argument async callable to execute.
            retryable_exceptions: Exception types that trigger a retry.
            empty_error: If not ``None``, treat an empty/falsy payload as a
                degraded response with this error message.
            extra_metadata: Additional metadata to include in the response.
        """
        metadata = dict(extra_metadata or {})
        if not self.circuit_breaker.allow_request():
            return ConnectorResponse(
                status="failure",
                connector=request.connector,
                operation=request.operation,
                payload=None,
                error="Circuit breaker open",
                metadata={**metadata, "attempts": 0, "circuit_state": self.circuit_breaker.state.value},
            )

        last_error = ""
        for attempt in range(1, self.retry_policy.max_attempts + 1):
            try:
                payload = await operation()
                self.circuit_breaker.record_success()

                if empty_error is not None and not payload:
                    return ConnectorResponse(
                        status="degraded",
                        connector=request.connector,
                        operation=request.operation,
                        payload=payload,
                        error=empty_error,
                        metadata={**metadata, "attempts": attempt},
                    )

                return ConnectorResponse(
                    status="success",
                    connector=request.connector,
                    operation=request.operation,
                    payload=payload,
                    metadata={**metadata, "attempts": attempt},
                )
            except Exception as exc:
                last_error = str(exc)
                is_retryable = isinstance(exc, retryable_exceptions)
                classification = self.retry_policy.classify_failure(retryable=is_retryable)
                decision = self.retry_policy.evaluate(
                    attempt=attempt,
                    key=f"{request.connector}:{request.operation}",
                    classification=classification,
                )

                if classification is FailureClassification.TERMINAL:
                    self.circuit_breaker.record_failure()
                    return ConnectorResponse(
                        status="failure",
                        connector=request.connector,
                        operation=request.operation,
                        payload=None,
                        error=last_error,
                        metadata={
                            **metadata,
                            "attempts": attempt,
                            "classification": classification.value,
                        },
                    )

                if not decision.should_retry:
                    self.circuit_breaker.record_failure()
                    return ConnectorResponse(
                        status="degraded",
                        connector=request.connector,
                        operation=request.operation,
                        payload=None,
                        error=last_error,
                        metadata={
                            **metadata,
                            "attempts": attempt,
                            "classification": classification.value,
                        },
                    )

                await self.sleep_func(decision.delay_seconds)

        self.circuit_breaker.record_failure()
        return ConnectorResponse(
            status="degraded",
            connector=request.connector,
            operation=request.operation,
            payload=None,
            error=last_error or "Retry attempts exhausted",
            metadata={**metadata, "attempts": self.retry_policy.max_attempts},
        )
