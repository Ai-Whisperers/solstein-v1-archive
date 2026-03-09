from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReliabilityMetrics:
    total_requests: int
    successful_requests: int
    timeout_count: int
    retry_count: int
    uptime_ratio: float
    error_rate: float
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    reliability_score: float


class ReliabilityMonitor:
    def __init__(self) -> None:
        self._latencies: list[float] = []
        self._total_requests = 0
        self._successful_requests = 0
        self._timeout_count = 0
        self._retry_count = 0

    def record_request(
        self, *, latency_ms: float, success: bool, timed_out: bool = False, retried: bool = False
    ) -> None:
        self._total_requests += 1
        if success:
            self._successful_requests += 1
        if timed_out:
            self._timeout_count += 1
        if retried:
            self._retry_count += 1
        self._latencies.append(max(0.0, latency_ms))

    def snapshot(self) -> ReliabilityMetrics:
        total = self._total_requests
        successful = self._successful_requests
        uptime_ratio = (successful / total) if total > 0 else 1.0
        error_rate = (1.0 - uptime_ratio) if total > 0 else 0.0

        avg_latency = _avg(self._latencies)
        p95_latency = _percentile(self._latencies, 95)
        p99_latency = _percentile(self._latencies, 99)

        latency_factor = _latency_factor(avg_latency)
        timeout_penalty = min(0.2, self._timeout_count * 0.01)
        retry_penalty = min(0.15, self._retry_count * 0.005)
        reliability_score = max(
            0.0, min(1.0, uptime_ratio * 0.7 + latency_factor * 0.3 - timeout_penalty - retry_penalty)
        )

        return ReliabilityMetrics(
            total_requests=total,
            successful_requests=successful,
            timeout_count=self._timeout_count,
            retry_count=self._retry_count,
            uptime_ratio=round(uptime_ratio, 4),
            error_rate=round(error_rate, 4),
            avg_latency_ms=round(avg_latency, 4),
            p95_latency_ms=round(p95_latency, 4),
            p99_latency_ms=round(p99_latency, 4),
            reliability_score=round(reliability_score, 4),
        )


def _avg(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _percentile(values: list[float], percentile: int) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    idx = max(0, min(len(sorted_values) - 1, int((percentile / 100) * (len(sorted_values) - 1))))
    return sorted_values[idx]


def _latency_factor(avg_latency_ms: float) -> float:
    if avg_latency_ms <= 200:
        return 1.0
    if avg_latency_ms <= 500:
        return 0.8
    if avg_latency_ms <= 1000:
        return 0.6
    if avg_latency_ms <= 2000:
        return 0.4
    return 0.2
