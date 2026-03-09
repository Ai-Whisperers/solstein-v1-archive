from solstein.data_sources.quality import ReliabilityMonitor


def test_reliability_monitor_tracks_uptime_and_error_rate() -> None:
    monitor = ReliabilityMonitor()
    monitor.record_request(latency_ms=120, success=True)
    monitor.record_request(latency_ms=180, success=True)
    monitor.record_request(latency_ms=240, success=False)

    metrics = monitor.snapshot()

    assert metrics.total_requests == 3
    assert metrics.successful_requests == 2
    assert metrics.uptime_ratio == 0.6667
    assert metrics.error_rate == 0.3333


def test_reliability_monitor_tracks_timeouts_retries_and_percentiles() -> None:
    monitor = ReliabilityMonitor()
    monitor.record_request(latency_ms=50, success=True)
    monitor.record_request(latency_ms=100, success=False, timed_out=True, retried=True)
    monitor.record_request(latency_ms=300, success=True, retried=True)
    monitor.record_request(latency_ms=500, success=True)

    metrics = monitor.snapshot()

    assert metrics.timeout_count == 1
    assert metrics.retry_count == 2
    assert metrics.p95_latency_ms >= metrics.avg_latency_ms
    assert metrics.p99_latency_ms >= metrics.p95_latency_ms
    assert 0.0 <= metrics.reliability_score <= 1.0


def test_reliability_monitor_zero_requests_defaults_to_healthy() -> None:
    monitor = ReliabilityMonitor()

    metrics = monitor.snapshot()

    assert metrics.total_requests == 0
    assert metrics.uptime_ratio == 1.0
    assert metrics.error_rate == 0.0
    assert metrics.reliability_score == 1.0
