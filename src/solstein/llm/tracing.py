"""LLM call tracing and observability via Langfuse.

STORY-073: Unified tracing using Langfuse SDK. Every LLM call produces a
trace with token counts, model, provider, and cost estimate. Falls back
gracefully to loguru-only tracing when Langfuse is unavailable (REQ-5).

Usage::

    from solstein.llm.tracing import LLMTracer, TraceRecord, get_tracer

    tracer = get_tracer()
    tracer.record(TraceRecord(
        prompt="Analyse Stripe",
        schema_name="CompanyProfile",
        provider="deepinfra",
        model="meta-llama/Llama-3.3-70B-Instruct",
        attempt=1,
        latency_s=1.23,
        success=True,
    ))
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from loguru import logger

if TYPE_CHECKING:
    from ..config import Settings


@dataclass
class TraceRecord:
    """A single LLM call trace entry."""

    prompt: str
    schema_name: str = "free_form"
    provider: str = ""
    model: str = ""
    attempt: int = 1
    latency_s: float = 0.0
    success: bool = True
    error: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    correlation_id: str | None = None
    tenant_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class LLMTracer:
    """Traces LLM calls to loguru (always) and Langfuse (when configured).

    STORY-073: Langfuse failures are caught and logged at warning level
    but never propagate to callers (REQ-5).
    """

    def __init__(self, settings: Settings | None = None, max_records: int = 1_000) -> None:
        self._records: list[TraceRecord] = []
        self._max_records = max_records
        self._langfuse: Any | None = self._init_langfuse(settings)

    def record(self, trace: TraceRecord) -> None:
        """Record a trace and forward to Langfuse if available."""
        if len(self._records) >= self._max_records:
            self._records.pop(0)
        self._records.append(trace)

        log_fn = logger.debug if trace.success else logger.warning
        log_fn(
            "[LLMTracer] call traced",
            extra={
                "provider": trace.provider,
                "model": trace.model,
                "schema": trace.schema_name,
                "attempt": trace.attempt,
                "latency_s": round(trace.latency_s, 3),
                "success": trace.success,
                "input_tokens": trace.input_tokens,
                "output_tokens": trace.output_tokens,
                "error": trace.error,
            },
        )

        if self._langfuse is not None:
            self._emit_to_langfuse(trace)

    def stats(self) -> dict[str, Any]:
        """Return aggregate statistics over all recorded traces."""
        total = len(self._records)
        if total == 0:
            return {"total": 0, "success": 0, "failure": 0, "avg_latency_s": 0.0}
        successes = sum(1 for r in self._records if r.success)
        latencies = [r.latency_s for r in self._records]
        total_cost = sum(r.cost_usd for r in self._records)
        return {
            "total": total,
            "success": successes,
            "failure": total - successes,
            "avg_latency_s": round(sum(latencies) / len(latencies), 3),
            "max_latency_s": round(max(latencies), 3),
            "total_cost_usd": round(total_cost, 6),
        }

    def clear(self) -> None:
        """Clear the in-memory trace buffer."""
        self._records.clear()

    @property
    def langfuse_enabled(self) -> bool:
        """Whether Langfuse tracing is active."""
        return self._langfuse is not None

    def flush(self) -> None:
        """Flush pending Langfuse events. No-op if Langfuse is not configured."""
        if self._langfuse is not None:
            try:
                self._langfuse.flush()
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"[LLMTracer] Langfuse flush failed: {exc}")

    # ------------------------------------------------------------------
    # Langfuse integration (optional, graceful degradation)
    # ------------------------------------------------------------------

    def _init_langfuse(self, settings: Settings | None) -> Any | None:
        """Return a Langfuse client if credentials are configured."""
        if settings is None:
            return None

        public_key = settings.langfuse_public_key
        secret_key = settings.langfuse_secret_key
        if not (public_key and secret_key):
            return None

        try:
            from langfuse import Langfuse

            client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=settings.langfuse_host,
            )
            logger.info(
                "[LLMTracer] Langfuse tracing enabled",
                extra={"host": settings.langfuse_host},
            )
            return client
        except ImportError:
            logger.warning("[LLMTracer] langfuse package not installed, tracing disabled")
            return None
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"[LLMTracer] Langfuse init failed: {exc}")
            return None

    def _emit_to_langfuse(self, trace: TraceRecord) -> None:
        """Forward a trace to Langfuse. Failures are logged, never raised."""
        try:
            lf_trace = self._langfuse.trace(
                name=f"llm-{trace.schema_name}",
                input=trace.prompt[:500],
                metadata={
                    "provider": trace.provider,
                    "model": trace.model,
                    "attempt": trace.attempt,
                    "correlation_id": trace.correlation_id,
                    "tenant_id": trace.tenant_id,
                    **trace.metadata,
                },
            )
            lf_trace.generation(
                name=f"generation-{trace.provider}",
                model=trace.model,
                input=trace.prompt[:500],
                output="<structured>" if trace.success else trace.error or "",
                usage={
                    "input": trace.input_tokens,
                    "output": trace.output_tokens,
                    "total": trace.input_tokens + trace.output_tokens,
                },
                metadata={
                    "cost_usd": trace.cost_usd,
                    "success": trace.success,
                },
                level="DEFAULT" if trace.success else "ERROR",
                status_message="" if trace.success else (trace.error or ""),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"[LLMTracer] Langfuse trace failed: {exc}")


# Module-level singleton tracer (shared across the process)
_default_tracer: LLMTracer | None = None


def get_tracer(settings: Settings | None = None) -> LLMTracer:
    """Return the process-wide singleton LLMTracer."""
    global _default_tracer
    if _default_tracer is None:
        _default_tracer = LLMTracer(settings=settings)
    return _default_tracer


def reset_tracer() -> None:
    """Reset the singleton tracer (for testing)."""
    global _default_tracer
    _default_tracer = None
