from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

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
        self.circuit_breaker = circuit_breaker or CircuitBreaker(failure_threshold=5, cooldown_seconds=30.0)
        self.sleep_func = sleep_func or asyncio.sleep

    async def run(
        self,
        *,
        request: ConnectorRequest,
        operation: Callable[[], Awaitable[PayloadT]],
        retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
        empty_is_degraded: bool = False,
        empty_error: str = "No payload returned",
        extra_metadata: dict[str, Any] | None = None,
    ) -> ConnectorResponse[PayloadT]:
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

                if empty_is_degraded and not payload:
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
