# Prometheus Metrics Catalogue

> STORY-051: Prometheus Metrics Endpoints

## Endpoint

**URL**: `GET /metrics/prometheus`

**Authentication**: None (deliberately unauthenticated per Prometheus scraping conventions).

**Security Note**: This endpoint is unauthenticated by design. Access should be
restricted at the network level (e.g., firewall rules, security groups, or
Kubernetes NetworkPolicy) so that only the monitoring infrastructure can reach it.

**Content-Type**: `text/plain; version=0.0.4; charset=utf-8` (Prometheus text exposition format)

## HTTP Request Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | `method`, `endpoint`, `status_code` | Total HTTP requests processed |
| `http_request_duration_seconds` | Histogram | `method`, `endpoint` | Request latency distribution |
| `http_requests_in_progress` | Gauge | `method`, `endpoint` | Currently active requests |
| `http_response_size_bytes` | Histogram | `endpoint` | Response payload size distribution |

## LLM Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `llm_tokens_total` | Counter | `provider`, `model`, `token_type` | Tokens consumed (input/output) |
| `llm_cost_dollars_total` | Counter | `provider`, `model` | Estimated LLM cost in USD |
| `llm_request_duration_seconds` | Histogram | `provider`, `model` | LLM call latency distribution |
| `llm_provider_available` | Gauge | `provider` | Provider availability (1=up, 0=down) |
| `llm_cache_hit_rate` | Gauge | `provider` | LLM response cache hit rate |

## Database Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `db_queries_total` | Counter | `operation`, `table` | Total database queries executed |
| `db_query_duration_seconds` | Histogram | `operation` | Query latency distribution |
| `db_pool_connections` | Gauge | `state` | Connection pool state (in_use, idle, overflow) |
| `db_pool_wait_duration_seconds` | Histogram | | Time waiting for a connection from the pool |

## Business Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `companies_enriched_total` | Counter | `source`, `classification` | Companies enriched |
| `reports_generated_total` | Counter | `format` | Reports generated |
| `research_runs_total` | Counter | `status` | Research pipeline runs |
| `pipeline_stage_duration_seconds` | Histogram | `stage` | Pipeline stage execution time |
| `companies_total` | Gauge | `classification`, `tier` | Companies in database |
| `data_quality_score` | Histogram | | Data quality score distribution |

## System Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `active_connections` | Gauge | `type` | Active connections by type |
| `memory_usage_bytes` | Gauge | `type` | Memory usage (rss, vms) |
| `cpu_usage_percent` | Gauge | | CPU usage percentage |
| `solstein_app_info` | Info | `version`, `environment` | Application version and environment |

## Prometheus Scrape Configuration

```yaml
scrape_configs:
  - job_name: 'solstein-api'
    scrape_interval: 15s
    metrics_path: '/metrics/prometheus'
    static_configs:
      - targets: ['localhost:8000']
```

## Grafana Dashboard

Use the metrics above to build dashboards. Recommended panels:

- **Request Rate**: `rate(http_requests_total[5m])` grouped by endpoint
- **Error Rate**: `rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m])`
- **P95 Latency**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- **LLM Cost**: `increase(llm_cost_dollars_total[1h])`
- **DB Pool Saturation**: `db_pool_connections{state="in_use"} / (db_pool_connections{state="in_use"} + db_pool_connections{state="idle"})`
