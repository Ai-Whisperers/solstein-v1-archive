"""LLM usage and cost monitoring.

EPIC-026 Story 4: Tracks LLM usage including:
- Token consumption by provider/model
- Cost tracking and attribution
- Request latency monitoring
- Provider availability
- Cost alerting

Usage:
    from solstein.monitoring.llm_tracker import LLMTracker

    tracker = LLMTracker()
    tracker.track_call(
        provider="openai",
        model="gpt-4",
        tokens_in=1000,
        tokens_out=500,
        duration=2.5,
        tenant_id="tenant_123"
    )
"""

import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
from typing import Any

from loguru import logger

from solstein.monitoring.metrics import track_llm_call


# Token costs per 1K tokens (approximate, update regularly)
TOKEN_COSTS = {
    "openai": {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    },
    "anthropic": {
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    },
    "groq": {
        "llama-3-70b": {"input": 0.0007, "output": 0.0008},
        "llama-3-8b": {"input": 0.0001, "output": 0.0001},
    },
    "gemini": {
        "gemini-pro": {"input": 0.0005, "output": 0.0015},
        "gemini-ultra": {"input": 0.0035, "output": 0.0105},
    },
}


def calculate_cost(provider: str, model: str, tokens_in: int, tokens_out: int) -> float:
    """Calculate LLM call cost.

    Args:
        provider: Provider name.
        model: Model name.
        tokens_in: Input token count.
        tokens_out: Output token count.

    Returns:
        Cost in USD.
    """
    provider_costs = TOKEN_COSTS.get(provider, {})
    model_costs = provider_costs.get(model, {"input": 0.0, "output": 0.0})

    input_cost = (tokens_in / 1000) * model_costs["input"]
    output_cost = (tokens_out / 1000) * model_costs["output"]

    return input_cost + output_cost


@dataclass
class LLMCallRecord:
    """Record of a single LLM call."""

    provider: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    duration_seconds: float
    timestamp: float
    tenant_id: str | None = None
    cached: bool = False
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "model": self.model,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "cost_usd": round(self.cost_usd, 6),
            "duration_seconds": round(self.duration_seconds, 3),
            "timestamp": self.timestamp,
            "tenant_id": self.tenant_id,
            "cached": self.cached,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class LLMUsageSummary:
    """Summary of LLM usage over a period."""

    period_start: float
    period_end: float
    total_calls: int = 0
    total_tokens: dict[str, int] = field(default_factory=lambda: {"input": 0, "output": 0})
    total_cost_usd: float = 0.0
    by_provider: dict[str, dict[str, Any]] = field(default_factory=dict)
    by_model: dict[str, dict[str, Any]] = field(default_factory=dict)
    by_tenant: dict[str, float] = field(default_factory=dict)
    avg_latency_ms: float = 0.0
    cache_hit_rate: float = 0.0
    success_rate: float = 1.0


class LLMTracker:
    """Track LLM usage and costs."""

    def __init__(self, max_history: int = 10000):
        """Initialize LLM tracker.

        Args:
            max_history: Maximum history records to keep.
        """
        self.max_history = max_history
        self.history: list[LLMCallRecord] = []
        self.provider_status: dict[str, bool] = {}

    def track_call(
        self,
        provider: str,
        model: str,
        tokens_in: int,
        tokens_out: int,
        duration: float,
        tenant_id: str | None = None,
        cached: bool = False,
        success: bool = True,
        error: str | None = None,
    ) -> LLMCallRecord:
        """Track an LLM call.

        Args:
            provider: Provider name.
            model: Model name.
            tokens_in: Input token count.
            tokens_out: Output token count.
            duration: Request duration in seconds.
            tenant_id: Tenant identifier for attribution.
            cached: Whether response was cached.
            success: Whether call succeeded.
            error: Error message if failed.

        Returns:
            LLMCallRecord.
        """
        cost = 0.0 if cached else calculate_cost(provider, model, tokens_in, tokens_out)

        record = LLMCallRecord(
            provider=provider,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost,
            duration_seconds=duration,
            timestamp=time.time(),
            tenant_id=tenant_id,
            cached=cached,
            success=success,
            error=error,
        )

        self.history.append(record)

        # Trim history if needed
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

        # Update Prometheus metrics
        track_llm_call(provider, model, tokens_in, tokens_out, cost, duration)

        # Log for attribution
        logger.info(
            "LLM call tracked",
            provider=provider,
            model=model,
            cost_usd=cost,
            tokens=tokens_in + tokens_out,
            tenant_id=tenant_id,
            cached=cached,
        )

        return record

    def set_provider_status(self, provider: str, available: bool):
        """Update provider availability status.

        Args:
            provider: Provider name.
            available: Whether provider is available.
        """
        self.provider_status[provider] = available

        # Update Prometheus gauge
        from solstein.monitoring.metrics import LLM_PROVIDER_AVAILABLE

        LLM_PROVIDER_AVAILABLE.labels(provider=provider).set(1 if available else 0)

    def get_daily_summary(self, days: int = 1) -> LLMUsageSummary:
        """Get usage summary for the last N days.

        Args:
            days: Number of days to summarize.

        Returns:
            LLMUsageSummary.
        """
        cutoff = time.time() - (days * 24 * 3600)
        recent_calls = [r for r in self.history if r.timestamp >= cutoff]

        if not recent_calls:
            return LLMUsageSummary(
                period_start=cutoff,
                period_end=time.time(),
            )

        # Calculate totals
        total_calls = len(recent_calls)
        total_input = sum(r.tokens_in for r in recent_calls)
        total_output = sum(r.tokens_out for r in recent_calls)
        total_cost = sum(r.cost_usd for r in recent_calls)

        # By provider
        by_provider: dict[str, dict] = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0})
        for r in recent_calls:
            by_provider[r.provider]["calls"] += 1
            by_provider[r.provider]["tokens"] += r.tokens_in + r.tokens_out
            by_provider[r.provider]["cost"] += r.cost_usd

        # By model
        by_model: dict[str, dict] = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0})
        for r in recent_calls:
            by_model[r.model]["calls"] += 1
            by_model[r.model]["tokens"] += r.tokens_in + r.tokens_out
            by_model[r.model]["cost"] += r.cost_usd

        # By tenant
        by_tenant: dict[str, float] = defaultdict(float)
        for r in recent_calls:
            if r.tenant_id:
                by_tenant[r.tenant_id] += r.cost_usd

        # Latency
        latencies = [r.duration_seconds * 1000 for r in recent_calls if not r.cached]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0

        # Cache hit rate
        cached_count = sum(1 for r in recent_calls if r.cached)
        cache_rate = cached_count / len(recent_calls) if recent_calls else 0

        # Success rate
        success_count = sum(1 for r in recent_calls if r.success)
        success_rate = success_count / len(recent_calls) if recent_calls else 1.0

        return LLMUsageSummary(
            period_start=cutoff,
            period_end=time.time(),
            total_calls=total_calls,
            total_tokens={"input": total_input, "output": total_output},
            total_cost_usd=total_cost,
            by_provider=dict(by_provider),
            by_model=dict(by_model),
            by_tenant=dict(by_tenant),
            avg_latency_ms=avg_latency,
            cache_hit_rate=cache_rate,
            success_rate=success_rate,
        )

    def get_top_expensive_calls(self, n: int = 10) -> list[LLMCallRecord]:
        """Get most expensive recent calls.

        Args:
            n: Number of calls to return.

        Returns:
            List of most expensive calls.
        """
        return sorted(self.history, key=lambda r: r.cost_usd, reverse=True)[:n]

    def check_cost_alerts(self, daily_budget: float = 500.0) -> list[dict[str, Any]]:
        """Check for cost-based alerts.

        Args:
            daily_budget: Daily budget in USD.

        Returns:
            List of alerts.
        """
        alerts = []
        summary = self.get_daily_summary(days=1)

        if summary.total_cost_usd > daily_budget:
            alerts.append(
                {
                    "type": "budget_exceeded",
                    "message": f"Daily LLM cost ${summary.total_cost_usd:.2f} exceeds budget ${daily_budget:.2f}",
                    "severity": "warning",
                    "cost": summary.total_cost_usd,
                    "budget": daily_budget,
                }
            )

        # Check for unusual spike
        yesterday = self.get_daily_summary(days=2)
        if yesterday.total_cost_usd > 0:
            ratio = summary.total_cost_usd / (yesterday.total_cost_usd / 2)  # Compare to avg
            if ratio > 2.0:
                alerts.append(
                    {
                        "type": "cost_spike",
                        "message": f"Cost spike detected: {ratio:.1f}x normal",
                        "severity": "warning",
                        "ratio": ratio,
                    }
                )

        return alerts


def track_llm(provider: str, model: str, tenant_id: str | None = None):
    """Decorator to track LLM calls.

    Args:
        provider: Provider name.
        model: Model name.
        tenant_id: Tenant identifier.

    Returns:
        Decorator function.
    """

    def decorator(func: Callable) -> Callable:
        tracker = LLMTracker()

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start

                # Try to extract token counts from result
                tokens_in = getattr(result, "tokens_in", 0)
                tokens_out = getattr(result, "tokens_out", 0)

                tracker.track_call(
                    provider=provider,
                    model=model,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    duration=duration,
                    tenant_id=tenant_id,
                    success=True,
                )

                return result
            except Exception as e:
                duration = time.time() - start
                tracker.track_call(
                    provider=provider,
                    model=model,
                    tokens_in=0,
                    tokens_out=0,
                    duration=duration,
                    tenant_id=tenant_id,
                    success=False,
                    error=str(e),
                )
                raise

        return async_wrapper

    return decorator
