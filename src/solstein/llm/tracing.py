"""LLM call tracing and observability.

Provides a ``LLMTracer`` that records every LLM call with latency, token
estimates, schema name, and success/failure outcome.  Traces are emitted
via loguru (always) and optionally forwarded to Langfuse when the
``LANGFUSE_PUBLIC_KEY`` / ``LANGFUSE_SECRET_KEY`` env vars are set.

Usage::

    from solstein.llm.tracing import LLMTracer, TraceRecord

    tracer = LLMTracer()
    tracer.record(TraceRecord(
        prompt="Analyse Stripe",
        schema_name="CompanyProfile",
        attempt=1,
        latency_s=1.23,
        success=True,
    ))
    stats = tracer.stats()
    # {"total": 1, "success": 1, "failure": 0, "avg_latency_s": 1.23}
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TraceRecord:
    """A single LLM call trace entry.

    Attributes:
        prompt: The prompt sent to the LLM (truncated for storage).
        schema_name: Pydantic schema name (for structured extractions) or
                     ``'free_form'`` for plain text generations.
        attempt: Which retry attempt produced this record (1-based).
        latency_s: Wall-clock time in seconds.
        success: Whether the call resulted in a valid response.
        error: Optional error message when *success* is ``False``.
        metadata: Arbitrary extra key-value pairs (model, token counts, etc.).
    """

    prompt: str
    schema_name: str = "free_form"
    attempt: int = 1
    latency_s: float = 0.0
    success: bool = True
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class LLMTracer:
    """Collects LLM call traces and emits them to loguru (and Langfuse if configured).

    Thread-safe for reading/writing via a plain list (GIL-protected).
    For production workloads with high concurrency, replace with a queue.
    """

    def __init__(self, max_records: int = 1_000) -> None:
        self._records: list[TraceRecord] = []
        self._max_records = max_records
        self._langfuse: Any | None = self._init_langfuse()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record(self, trace: TraceRecord) -> None:
        """Record a trace and forward to Langfuse if available."""
        from loguru import logger

        # Keep a bounded in-memory buffer
        if len(self._records) >= self._max_records:
            self._records.pop(0)
        self._records.append(trace)

        # Always emit to loguru
        log_fn = logger.debug if trace.success else logger.warning
        log_fn(
            "LLM call traced",
            schema=trace.schema_name,
            attempt=trace.attempt,
            latency_s=round(trace.latency_s, 3),
            success=trace.success,
            error=trace.error,
        )

        # Forward to Langfuse if available
        if self._langfuse is not None:
            try:
                self._emit_to_langfuse(trace)
            except Exception as exc:
                logger.warning("Langfuse trace failed", error=str(exc))

    def stats(self) -> dict[str, Any]:
        """Return aggregate statistics over all recorded traces."""
        total = len(self._records)
        if total == 0:
            return {"total": 0, "success": 0, "failure": 0, "avg_latency_s": 0.0}
        successes = sum(1 for r in self._records if r.success)
        latencies = [r.latency_s for r in self._records]
        return {
            "total": total,
            "success": successes,
            "failure": total - successes,
            "avg_latency_s": round(sum(latencies) / len(latencies), 3),
            "max_latency_s": round(max(latencies), 3),
        }

    def clear(self) -> None:
        """Clear the in-memory trace buffer."""
        self._records.clear()

    # ------------------------------------------------------------------
    # Langfuse integration (optional)
    # ------------------------------------------------------------------

    def _init_langfuse(self) -> Any | None:
        """Return a Langfuse client if credentials are configured."""
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        if not (public_key and secret_key):
            return None
        try:
            from langfuse import Langfuse  # type: ignore[import]

            client = Langfuse(public_key=public_key, secret_key=secret_key, host=host)
            from loguru import logger

            logger.info("Langfuse tracing enabled", host=host)
            return client
        except ImportError:
            return None

    def _emit_to_langfuse(self, trace: TraceRecord) -> None:
        """Forward a trace to Langfuse."""
        generation = self._langfuse.generation(
            name=f"llm-{trace.schema_name}",
            input=trace.prompt[:500],  # truncate for cost control
            metadata={
                "attempt": trace.attempt,
                "success": trace.success,
                "error": trace.error,
                **trace.metadata,
            },
            start_time=trace.timestamp,
            end_time=trace.timestamp + trace.latency_s,
        )
        if trace.success:
            generation.end(output="<structured>")
        else:
            generation.end(level="ERROR", status_message=trace.error or "")


# Module-level singleton tracer (shared across the process)
_default_tracer: LLMTracer | None = None


def get_tracer() -> LLMTracer:
    """Return the process-wide singleton LLMTracer."""
    global _default_tracer
    if _default_tracer is None:
        _default_tracer = LLMTracer()
    return _default_tracer
