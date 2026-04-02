"""Provider fallback chain with circuit breaker integration.

STORY-075: Orchestrates multi-provider failover with circuit breaking
and template fallback. Provider order is configurable via settings.

Usage::

    from solstein.llm.fallback import FallbackChain

    chain = FallbackChain(settings)
    result = await chain.execute(query_fn)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from loguru import logger

from ..agents.resilience import CircuitBreaker
from ..config import Settings

# ---------------------------------------------------------------------------
# Template fallback (last resort when all providers fail)
# ---------------------------------------------------------------------------

TEMPLATE_FALLBACK_RESPONSE: dict[str, Any] = {
    "generated_by": "template_fallback",
    "content": (
        "Unable to generate AI analysis at this time. All LLM providers are "
        "currently unavailable. This is a placeholder response. Please retry "
        "when provider connectivity is restored."
    ),
    "company_name": None,
    "analysis": "Analysis unavailable — all LLM providers failed.",
    "confidence": 0.0,
    "metadata": {
        "fallback": True,
        "reason": "all_providers_exhausted",
    },
}


@dataclass
class FallbackDecision:
    """Record of a fallback decision for logging and diagnostics."""

    provider: str
    action: str  # "attempted", "skipped_circuit_open", "skipped_no_client", "failed"
    reason: str
    latency_s: float = 0.0
    error: str | None = None


@dataclass
class FallbackResult:
    """Result of a fallback chain execution."""

    result: str | None
    provider_used: str | None
    is_template_fallback: bool
    decisions: list[FallbackDecision] = field(default_factory=list)
    template_response: dict[str, Any] | None = None


class FallbackChain:
    """Multi-provider fallback with circuit breaker integration.

    Provider order is read from Settings.llm_provider_order (configurable
    via LLM_PROVIDER_ORDER env var). Circuit breakers are per-provider.
    When all providers fail, returns a structured template fallback.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        if settings is None:
            from ..config import get_settings

            settings = get_settings()
        self._settings = settings
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        self._init_circuit_breakers()

    def _init_circuit_breakers(self) -> None:
        """Create a circuit breaker for each configured provider."""
        if not self._settings.llm_circuit_breaker_enabled:
            return
        cb_config = self._settings.circuit_breaker
        for provider in self._settings.llm_provider_order:
            self._circuit_breakers[provider] = CircuitBreaker(
                failure_threshold=cb_config.failure_threshold,
                recovery_timeout=cb_config.recovery_timeout,
                name=f"llm-{provider}",
            )

    def get_provider_order(self, preferred: str | None = None) -> list[str]:
        """Return the provider order, optionally with a preferred provider first."""
        order = list(self._settings.llm_provider_order)
        if preferred and preferred in order:
            order.remove(preferred)
            order.insert(0, preferred)
        elif preferred:
            order.insert(0, preferred)
        return order

    def get_circuit_breaker(self, provider: str) -> CircuitBreaker | None:
        """Get the circuit breaker for a provider."""
        return self._circuit_breakers.get(provider)

    async def execute(
        self,
        query_fn: Any,
        preferred_provider: str | None = None,
        max_retries: int = 2,
    ) -> FallbackResult:
        """Execute query with fallback chain.

        Args:
            query_fn: Async callable(provider) -> result string.
            preferred_provider: Optional preferred provider.
            max_retries: Max retries per provider.

        Returns:
            FallbackResult with result or template fallback.
        """
        providers = self.get_provider_order(preferred_provider)
        decisions: list[FallbackDecision] = []

        for provider in providers:
            # Check circuit breaker
            cb = self._circuit_breakers.get(provider)
            if cb and not cb.can_execute():
                decision = FallbackDecision(
                    provider=provider,
                    action="skipped_circuit_open",
                    reason=f"Circuit breaker OPEN (failures={cb.failure_count})",
                )
                decisions.append(decision)
                logger.warning(
                    f"[FallbackChain] Skipping {provider}: circuit breaker OPEN "
                    f"(failures={cb.failure_count}, state={cb.get_state()})"
                )
                continue

            # Attempt the provider with retries
            for attempt in range(max_retries + 1):
                start = time.monotonic()
                try:
                    result = await query_fn(provider)
                    elapsed = time.monotonic() - start

                    if cb:
                        cb.record_success()

                    decisions.append(
                        FallbackDecision(
                            provider=provider,
                            action="attempted",
                            reason="success",
                            latency_s=elapsed,
                        )
                    )
                    logger.info(f"[FallbackChain] {provider} succeeded (attempt={attempt + 1}, latency={elapsed:.2f}s)")
                    return FallbackResult(
                        result=result,
                        provider_used=provider,
                        is_template_fallback=False,
                        decisions=decisions,
                    )

                except Exception as exc:  # noqa: BLE001
                    elapsed = time.monotonic() - start
                    error_type = type(exc).__name__
                    decisions.append(
                        FallbackDecision(
                            provider=provider,
                            action="failed",
                            reason=f"{error_type}: {exc}",
                            latency_s=elapsed,
                            error=str(exc),
                        )
                    )
                    logger.warning(
                        f"[FallbackChain] {provider} failed "
                        f"(attempt={attempt + 1}/{max_retries + 1}, "
                        f"error={error_type}: {exc})"
                    )

                    if attempt == max_retries:
                        if cb:
                            cb.record_failure()
                        break

        # All providers exhausted — template fallback
        logger.error(f"[FallbackChain] All {len(providers)} providers failed. Returning template fallback.")
        decisions.append(
            FallbackDecision(
                provider="template_fallback",
                action="attempted",
                reason="all_providers_exhausted",
            )
        )
        return FallbackResult(
            result=None,
            provider_used=None,
            is_template_fallback=True,
            decisions=decisions,
            template_response=TEMPLATE_FALLBACK_RESPONSE.copy(),
        )
