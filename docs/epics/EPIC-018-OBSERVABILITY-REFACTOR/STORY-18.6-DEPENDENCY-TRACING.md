# Story 18.6: Add Dependency Tracing

> **Epic**: EPIC-018 Observability and Error Handling Refactor
> **Priority**: P1  > **Effort**: 1 story point  > **Dependencies**: Story 18.2 (Context Propagation)

---

## Description

Add comprehensive tracing for outbound dependency calls (database queries, LLM requests, external API calls) with timing, correlation ID propagation, and failure tracking. This enables identification of slow dependencies and root cause analysis for failures.

### Current Broken State

```python
# llm/enhanced_client.py (current)
async def generate(self, prompt: str, **kwargs):
    # No logging of request start
    response = await self._call_provider(prompt, **kwargs)
    # No logging of duration or response
    return response

# data/fetchers (typical)
async def fetch_company_data(company_id: str):
    # No trace of external call
    data = await http_client.get(f"https://api.example.com/companies/{company_id}")
    return data
```

**Problems:**
- No visibility into which dependencies are slow
- Cannot trace request flow across services
- No correlation between app logs and external service logs
- Retry/fallback attempts not visible
- Cannot identify if errors are from dependencies or internal code

---

## Acceptance Criteria

- [ ] All database queries logged with timing (SQL + duration_ms)
- [ ] All LLM calls logged with provider, model, timing, token usage
- [ ] All external HTTP calls logged with URL, method, timing, status
- [ ] Correlation ID propagated to all external services via headers
- [ ] Retry attempts logged with attempt number and reason
- [ ] Fallback/circuit breaker state changes logged
- [ ] Performance metrics collected: p50, p95, p99 latency per dependency

---

## Implementation

### Step 1: Create Dependency Tracer

```python
# utils/tracing.py
"""Dependency tracing and metrics collection."""

import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from dataclasses import dataclass, field
from collections import defaultdict
from statistics import median
from loguru import logger
from .context import get_current_context


@dataclass
class DependencyCall:
    """Record of a dependency call."""
    service: str  # 'postgresql', 'openai', 'crunchbase', etc.
    operation: str  # 'query', 'generate', 'get_company', etc.
    duration_ms: float
    success: bool
    error_type: str | None = None
    metadata: dict = field(default_factory=dict)


class DependencyTracer:
    """Trace and collect metrics for dependency calls."""

    def __init__(self):
        self._calls: list[DependencyCall] = []
        self._max_calls = 10000  # Prevent unbounded growth

    @asynccontextmanager
    async def trace(
        self,
        service: str,
        operation: str,
        **metadata: Any,
    ) -> AsyncGenerator[dict, None]:
        """Context manager for tracing a dependency call.

        Usage:
            async with tracer.trace("openai", "generate", model="gpt-4") as span:
                span["request_tokens"] = 100  # Add metadata during call
                response = await openai.generate(prompt)
                span["response_tokens"] = 50
        """
        start = time.perf_counter()
        span_metadata = dict(metadata)
        error = None

        # Get correlation context
        context = get_current_context()

        logger.debug(
            f"Dependency call started: {service}.{operation}",
            service=service,
            operation=operation,
            **context,
            **metadata,
        )

        try:
            yield span_metadata
            success = True
        except Exception as e:
            success = False
            error = e
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000

            call = DependencyCall(
                service=service,
                operation=operation,
                duration_ms=duration_ms,
                success=success,
                error_type=type(error).__name__ if error else None,
                metadata=span_metadata,
            )

            self._record_call(call)

            log_level = "error" if not success else ("warning" if duration_ms > 1000 else "debug")
            logger.log(
                log_level,
                f"Dependency call completed: {service}.{operation}",
                service=service,
                operation=operation,
                duration_ms=round(duration_ms, 2),
                success=success,
                error_type=call.error_type,
                **context,
                **span_metadata,
            )

    def _record_call(self, call: DependencyCall) -> None:
        """Record call, maintaining size limit."""
        if len(self._calls) >= self._max_calls:
            self._calls = self._calls[len(self._calls)//2:]  # Drop oldest half
        self._calls.append(call)

    def get_metrics(self, service: str | None = None) -> dict[str, Any]:
        """Get aggregated metrics for dependencies.

        Returns:
            Dictionary with p50, p95, p99 latencies and error rates per service.
        """
        calls = self._calls
        if service:
            calls = [c for c in calls if c.service == service]

        if not calls:
            return {}

        # Group by service
        by_service = defaultdict(list)
        for call in calls:
            by_service[call.service].append(call)

        metrics = {}
        for svc, svc_calls in by_service.items():
            durations = [c.duration_ms for c in svc_calls]
            errors = sum(1 for c in svc_calls if not c.success)

            metrics[svc] = {
                "total_calls": len(svc_calls),
                "error_count": errors,
                "error_rate": errors / len(svc_calls),
                "latency_ms": {
                    "p50": median(durations),
                    "p95": self._percentile(durations, 95),
                    "p99": self._percentile(durations, 99),
                    "avg": sum(durations) / len(durations),
                    "max": max(durations),
                },
            }

        return metrics

    def _percentile(self, data: list[float], percentile: int) -> float:
        """Calculate percentile of data."""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


# Global tracer instance
tracer = DependencyTracer()


def get_tracer() -> DependencyTracer:
    """Get the global dependency tracer."""
    return tracer
```

### Step 2: Database Query Tracing

```python
# infrastructure/database_tracing.py
"""SQLAlchemy event listeners for query tracing."""

from sqlalchemy import event
from sqlalchemy.engine import Engine
from loguru import logger
from ..utils.tracing import get_tracer
from ..utils.context import get_current_context


def setup_query_tracing():
    """Set up SQLAlchemy event listeners for query tracing."""

    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._query_start_time = __import__('time').perf_counter()

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        tracer = get_tracer()
        duration_ms = (__import__('time').perf_counter() - context._query_start_time) * 1000

        # Extract operation type from statement
        operation = statement.split()[0].upper() if statement else "UNKNOWN"

        # Log query details
        ctx = get_current_context()
        logger.debug(
            "Database query executed",
            operation=operation,
            duration_ms=round(duration_ms, 2),
            statement=statement[:200],  # Truncate long queries
            **ctx,
        )

        # Record for metrics (async-compatible)
        # Note: This runs synchronously, use background task for async


# Alternative: Manual tracing for async queries
async def execute_with_tracing(session, statement, **params):
    """Execute statement with tracing."""
    tracer = get_tracer()

    async with tracer.trace("postgresql", "execute", statement=str(statement)[:100]) as span:
        try:
            result = await session.execute(statement, params)
            span["row_count"] = result.rowcount if hasattr(result, 'rowcount') else None
            return result
        except Exception as e:
            span["error"] = str(e)
            raise
```

### Step 3: LLM Client Tracing

```python
# llm/traced_client.py (wrapper)
"""Traced wrapper for LLM client."""

from typing import Any
from .enhanced_client import EnhancedLLMClient
from ..utils.tracing import get_tracer


class TracedLLMClient:
    """LLM client with dependency tracing."""

    def __init__(self, client: EnhancedLLMClient):
        self._client = client
        self._tracer = get_tracer()

    async def generate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        provider: str | None = None,
        **kwargs
    ) -> dict[str, Any]:
        """Generate with tracing."""
        provider_name = provider or self._client.default_provider
        model_name = model or self._client.default_model

        async with self._tracer.trace(
            service=provider_name,  # 'openai', 'anthropic', etc.
            operation="generate",
            model=model_name,
            prompt_tokens=self._estimate_tokens(prompt),
        ) as span:
            try:
                response = await self._client.generate(
                    prompt, model=model, provider=provider, **kwargs
                )

                # Extract usage if available
                if "usage" in response:
                    span["prompt_tokens"] = response["usage"].get("prompt_tokens")
                    span["completion_tokens"] = response["usage"].get("completion_tokens")
                    span["total_tokens"] = response["usage"].get("total_tokens")

                span["success"] = True
                return response

            except Exception as e:
                span["error"] = str(e)
                span["error_type"] = type(e).__name__
                raise

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars per token)."""
        return len(text) // 4


# Usage in existing code:
# client = TracedLLMClient(EnhancedLLMClient())
```

### Step 4: HTTP Client Tracing

```python
# infrastructure/http_tracing.py
"""Traced HTTP client wrapper."""

from typing import Any
import httpx
from ..utils.tracing import get_tracer
from ..utils.context import CORRELATION_ID


class TracedHTTPClient:
    """HTTP client with tracing and correlation ID propagation."""

    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client or httpx.AsyncClient()
        self._tracer = get_tracer()

    async def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """Make traced HTTP request."""
        # Propagate correlation ID
        headers = kwargs.pop("headers", {})
        try:
            correlation_id = CORRELATION_ID.get()
            if correlation_id:
                headers["X-Correlation-ID"] = correlation_id
        except LookupError:
            pass

        service = self._extract_service_name(url)

        async with self._tracer.trace(
            service=service,
            operation=f"{method.lower()}_request",
            url=url.split("?")[0],  # Remove query params
        ) as span:
            try:
                response = await self._client.request(
                    method, url, headers=headers, **kwargs
                )
                span["status_code"] = response.status_code
                span["success"] = response.is_success
                return response
            except httpx.HTTPError as e:
                span["error"] = str(e)
                span["error_type"] = type(e).__name__
                raise

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("POST", url, **kwargs)

    def _extract_service_name(self, url: str) -> str:
        """Extract service name from URL."""
        try:
            host = url.split("/")[2]  # https://api.example.com/path
            # Map known hosts to service names
            service_map = {
                "api.crunchbase.com": "crunchbase",
                "api.linkedin.com": "linkedin",
                "api.openai.com": "openai",
                "api.anthropic.com": "anthropic",
            }
            return service_map.get(host, host)
        except IndexError:
            return "unknown"

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self._client.aclose()
```

### Step 5: Retry/Fallback Tracing

```python
# utils/retry_tracing.py
"""Tracing for retry and circuit breaker patterns."""

from loguru import logger
from .context import get_current_context


def log_retry_attempt(
    operation: str,
    attempt: int,
    max_attempts: int,
    exception: Exception,
    delay: float,
):
    """Log retry attempt."""
    ctx = get_current_context()
    logger.warning(
        f"Retrying {operation} after failure",
        operation=operation,
        attempt=attempt,
        max_attempts=max_attempts,
        error_type=type(exception).__name__,
        error=str(exception),
        delay_ms=round(delay * 1000, 2),
        **ctx,
    )


def log_retry_exhausted(operation: str, attempts: int, final_exception: Exception):
    """Log when all retries are exhausted."""
    ctx = get_current_context()
    logger.error(
        f"All retries exhausted for {operation}",
        operation=operation,
        attempts=attempts,
        final_error_type=type(final_exception).__name__,
        final_error=str(final_exception),
        **ctx,
    )


def log_fallback_triggered(operation: str, reason: str):
    """Log fallback activation."""
    ctx = get_current_context()
    logger.info(
        f"Fallback triggered for {operation}",
        operation=operation,
        reason=reason,
        **ctx,
    )


def log_circuit_breaker_state_change(service: str, old_state: str, new_state: str):
    """Log circuit breaker state change."""
    ctx = get_current_context()
    logger.warning(
        f"Circuit breaker state changed: {service}",
        service=service,
        old_state=old_state,
        new_state=new_state,
        **ctx,
    )
```

### Step 6: Metrics Endpoint

```python
# api/routers/metrics.py (add to existing or create new)
"""Metrics endpoint for dependency health."""

from fastapi import APIRouter
from ...utils.tracing import get_tracer

router = APIRouter()


@router.get("/metrics/dependencies")
async def get_dependency_metrics():
    """Get dependency health metrics."""
    tracer = get_tracer()
    return tracer.get_metrics()


@router.get("/metrics/dependencies/{service}")
async def get_service_metrics(service: str):
    """Get metrics for specific service."""
    tracer = get_tracer()
    return tracer.get_metrics(service=service)
```

---

## Testing

```python
# tests/unit/test_tracing.py
import pytest
import asyncio
from unittest.mock import patch
from solstein.utils.tracing import DependencyTracer, DependencyCall


@pytest.fixture
def tracer():
    return DependencyTracer()


@pytest.mark.asyncio
async def test_trace_successful_call(tracer):
    """Test tracing successful dependency call."""
    async with tracer.trace("test-service", "test-operation", param="value") as span:
        span["additional"] = "data"
        await asyncio.sleep(0.01)

    assert len(tracer._calls) == 1
    call = tracer._calls[0]
    assert call.service == "test-service"
    assert call.operation == "test-operation"
    assert call.success is True
    assert call.metadata["param"] == "value"
    assert call.metadata["additional"] == "data"


@pytest.mark.asyncio
async def test_trace_failed_call(tracer):
    """Test tracing failed dependency call."""
    with pytest.raises(ValueError):
        async with tracer.trace("test-service", "failing-operation"):
            raise ValueError("Test error")

    assert len(tracer._calls) == 1
    call = tracer._calls[0]
    assert call.success is False
    assert call.error_type == "ValueError"


def test_metrics_calculation(tracer):
    """Test metrics calculation."""
    # Add test calls
    tracer._calls = [
        DependencyCall("db", "query", 10.0, True),
        DependencyCall("db", "query", 20.0, True),
        DependencyCall("db", "query", 100.0, False),  # Slow failure
        DependencyCall("api", "get", 50.0, True),
    ]

    metrics = tracer.get_metrics()

    assert "db" in metrics
    assert "api" in metrics

    db_metrics = metrics["db"]
    assert db_metrics["total_calls"] == 3
    assert db_metrics["error_count"] == 1
    assert db_metrics["error_rate"] == 1/3
    assert db_metrics["latency_ms"]["p50"] == 20.0
    assert db_metrics["latency_ms"]["max"] == 100.0


def test_metrics_max_calls_limit(tracer):
    """Test that old calls are dropped when limit reached."""
    tracer._max_calls = 10

    for i in range(15):
        tracer._record_call(DependencyCall("svc", "op", float(i), True))

    # Should have dropped oldest half
    assert len(tracer._calls) < 15
    assert tracer._calls[0].duration_ms >= 5  # Oldest were dropped
```

---

## Verification Steps

1. **Test database tracing:**
   ```python
   # Run a query
   result = await session.execute(select(Company))
   # Check logs show "Database query executed" with duration
   ```

2. **Test LLM tracing:**
   ```python
   response = await traced_client.generate("test prompt")
   # Check logs show provider, model, duration, token usage
   ```

3. **Test HTTP tracing:**
   ```python
   response = await traced_http.get("https://api.example.com/data")
   # Check logs show service, method, duration, status
   # Check X-Correlation-ID header was sent
   ```

4. **Check metrics endpoint:**
   ```bash
   curl http://localhost:8000/api/v1/metrics/dependencies
   # Should show p50/p95/p99 latencies and error rates
   ```

---

## Related Files

- `src/solstein/utils/tracing.py` - Core tracing utilities (new)
- `src/solstein/infrastructure/database_tracing.py` - Database tracing (new)
- `src/solstein/infrastructure/http_tracing.py` - HTTP tracing (new)
- `src/solstein/llm/traced_client.py` - LLM tracing wrapper (new)
- `src/solstein/utils/retry_tracing.py` - Retry logging (new)
- `src/solstein/api/routers/metrics.py` - Metrics endpoint (update)
