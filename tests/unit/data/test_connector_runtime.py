from __future__ import annotations

import pytest

from solstein.data.connectors.contracts import ConnectorRequest
from solstein.data.connectors.runtime import ConnectorRuntime
from solstein.infrastructure.retry_policy import CircuitBreaker, RetryPolicy


@pytest.mark.asyncio
async def test_runtime_success_first_attempt() -> None:
    runtime = ConnectorRuntime(retry_policy=RetryPolicy(max_attempts=3))
    request = ConnectorRequest(connector="lookup", operation="resolve")

    async def _op() -> dict[str, str]:
        return {"ticker": "ACME"}

    result = await runtime.run(request=request, operation=_op)

    assert result.status == "success"
    assert result.payload == {"ticker": "ACME"}
    assert result.metadata["attempts"] == 1


@pytest.mark.asyncio
async def test_runtime_retries_then_succeeds() -> None:
    slept: list[float] = []

    async def _sleep(seconds: float) -> None:
        slept.append(seconds)

    runtime = ConnectorRuntime(
        retry_policy=RetryPolicy(max_attempts=3, base_delay_seconds=0.01, max_delay_seconds=0.02),
        sleep_func=_sleep,
    )
    request = ConnectorRequest(connector="lookup", operation="resolve")
    state = {"attempt": 0}

    async def _op() -> dict[str, str]:
        state["attempt"] += 1
        if state["attempt"] < 2:
            raise RuntimeError("temporary")
        return {"ticker": "ACME"}

    result = await runtime.run(request=request, operation=_op, retryable_exceptions=(RuntimeError,))

    assert result.status == "success"
    assert result.payload == {"ticker": "ACME"}
    assert result.metadata["attempts"] == 2
    assert len(slept) == 1


@pytest.mark.asyncio
async def test_runtime_terminal_failure_no_retry() -> None:
    runtime = ConnectorRuntime(retry_policy=RetryPolicy(max_attempts=3))
    request = ConnectorRequest(connector="lookup", operation="resolve")

    async def _op() -> dict[str, str]:
        raise ValueError("terminal")

    result = await runtime.run(request=request, operation=_op, retryable_exceptions=(RuntimeError,))

    assert result.status == "failure"
    assert result.payload is None
    assert "terminal" in (result.error or "")
    assert result.metadata["attempts"] == 1


@pytest.mark.asyncio
async def test_runtime_open_circuit_blocks_call() -> None:
    breaker = CircuitBreaker(failure_threshold=1, cooldown_seconds=10.0)
    breaker.open()
    runtime = ConnectorRuntime(circuit_breaker=breaker)
    request = ConnectorRequest(connector="lookup", operation="resolve")

    async def _op() -> dict[str, str]:
        return {"ticker": "ACME"}

    result = await runtime.run(request=request, operation=_op)

    assert result.status == "failure"
    assert result.error == "Circuit breaker open"
    assert result.metadata["attempts"] == 0
