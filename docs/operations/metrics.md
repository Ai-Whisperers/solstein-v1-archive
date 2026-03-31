# Prometheus Metrics Catalogue

**STORY-051** | EPIC-014 Observability & Telemetry

## Scrape Endpoint

| Property | Value |
|----------|-------|
| Path | `/metrics/prometheus` |
| Method | `GET` |
| Auth | None (unauthenticated by design) |
| Content-Type | `application/openmetrics-text` |
| Rate-limited | No (excluded) |

Access should be restricted at the network level (e.g., only reachable from the monitoring VPC).

## HTTP Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | method, endpoint, status_code | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | method, endpoint | Request latency (buckets: 10ms-10s) |
| `http_requests_in_progress` | Gauge | method, endpoint | In-flight requests |
| `http_response_size_bytes` | Histogram | endpoint | Response payload size |

## LLM Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `llm_tokens_total` | Counter | provider, model, token_type | Tokens consumed (input/output) |
| `llm_cost_dollars_total` | Counter | provider, model | Estimated cost in USD |
| `llm_request_duration_seconds` | Histogram | provider, model | LLM call latency |

## Database Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `db_queries_total` | Counter | operation, table | Total queries |
| `db_query_duration_seconds` | Histogram | operation | Query latency |
| `db_pool_connections` | Gauge | state | Pool connections (in_use, idle, overflow) |
| `db_pool_wait_duration_seconds` | Histogram | — | Time waiting for a connection |

## Pipeline / Business Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `research_runs_total` | Counter | status | Research pipeline runs |
| `pipeline_stage_duration_seconds` | Histogram | stage | Per-stage latency |
| `companies_enriched_total` | Counter | source, classification | Companies enriched |
| `companies_total` | Gauge | classification, tier | Companies in database |
| `reports_generated_total` | Counter | format | Reports generated |
| `data_quality_score` | Histogram | — | Quality score distribution (0-1) |

## Application Info

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `solstein_app_info` | Info | version, environment | Build metadata |

## Configuration

The endpoint is served by `prometheus_client.generate_latest()` and requires the `prometheus-client>=0.20` dependency declared in `pyproject.toml`.

### Prometheus scrape config

```yaml
scrape_configs:
  - job_name: solstein
    scrape_interval: 15s
    metrics_path: /metrics/prometheus
    static_configs:
      - targets: ["solstein-api:8000"]
```

### Grafana

Import the standard Prometheus data source pointing at your Prometheus instance. The metric names follow Prometheus naming conventions (snake_case, `_total` for counters, `_seconds` for durations) and are compatible with standard Grafana dashboards.

## Naming Conventions

All metrics follow Prometheus best practices:

- snake_case names
- Counters end with `_total`
- Duration histograms end with `_seconds`
- Size histograms end with `_bytes`
- No metric-name collisions with the default `python_` / `process_` metrics
