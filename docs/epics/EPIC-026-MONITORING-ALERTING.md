# Epic: Monitoring & Alerting System (EPIC-026)

## Overview
Build a comprehensive monitoring and alerting system to ensure Solstein operates reliably in production. Monitor application health, business metrics, performance indicators, and infrastructure resources with intelligent alerting to reduce MTTR (Mean Time To Recovery).

## Background
Current monitoring gaps:
- No centralized application monitoring
- Limited visibility into business metrics
- Reactive rather than proactive alerting
- No SLA monitoring
- Limited LLM usage/cost tracking
- No error trend analysis

## Goals
- [ ] 99.9% uptime monitoring with alerting
- [ ] Real-time business metrics dashboard
- [ ] Intelligent alerting (reducing false positives)
- [ ] LLM usage and cost tracking
- [ ] Automated incident response
- [ ] SLA compliance monitoring

## Success Metrics
| Metric | Target |
|--------|--------|
| Uptime | 99.9% |
| MTTR | <15 minutes |
| Alert Fatigue | <2 false positives/day |
| Dashboard Refresh | Real-time (<5s) |
| Cost Visibility | 100% of LLM spend |

---

## Stories

### Story 1: Application Performance Monitoring (APM)
**Points:** 8
**Priority:** P0

Implement distributed tracing and APM.

**Components:**

**1. Request Tracing:**
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

tracer = trace.get_tracer(__name__)

@router.get("/companies/{company_id}")
async def get_company(company_id: str):
    with tracer.start_as_current_span("get_company") as span:
        span.set_attribute("company.id", company_id)
        
        with tracer.start_span("fetch_from_db"):
            company = await db.fetch(company_id)
        
        with tracer.start_span("enrich_data"):
            enriched = await enrich(company)
        
        return enriched
```

**2. Metrics Collection:**
```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
requests_total = Counter('http_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'Request duration', ['endpoint'])
requests_in_progress = Gauge('http_requests_in_progress', 'Requests in progress')

# Business metrics
companies_enriched = Counter('companies_enriched_total', 'Companies enriched')
reports_generated = Counter('reports_generated_total', 'Reports generated', ['format'])
```

**3. Health Checks:**
```python
@router.get("/health")
async def health_check():
    checks = {
        'database': await check_database(),
        'redis': await check_redis(),
        'llm_providers': await check_llm_providers(),
        'disk': check_disk_space(),
    }
    
    overall = all(c['status'] == 'healthy' for c in checks.values())
    
    return {
        'status': 'healthy' if overall else 'degraded',
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    }
```

**Tools:**
- OpenTelemetry for tracing
- Prometheus for metrics
- Jaeger for trace visualization
- Grafana for dashboards

---

### Story 2: Business Metrics Dashboard
**Points:** 5
**Priority:** P0

Create real-time business metrics dashboard.

**Key Metrics:**

**Company Intelligence:**
- Companies in database (total, by tier, by classification)
- Enrichment success rate
- Average data quality score
- Companies processed per hour

**Research Pipeline:**
- Research runs per day
- Average pipeline duration
- Success/failure rates
- Stage-level metrics (discovery, enrichment, scoring)

**API Usage:**
- Requests per endpoint
- Error rates by endpoint
- Average response time
- Unique API consumers

**Export Activity:**
- Reports generated (by format)
- Export success rate
- Average export time
- Most requested markets

**LLM Usage:**
- Tokens consumed (by provider, by model)
- Cost per request
- Cache hit rate
- Provider availability

**Dashboard Implementation:**
```python
# Grafana dashboard as code
DASHBOARD = {
    "title": "Solstein Business Metrics",
    "panels": [
        {
            "title": "Companies Processed",
            "type": "stat",
            "targets": [{
                "expr": "sum(increase(companies_enriched_total[1h]))"
            }]
        },
        {
            "title": "API Response Time",
            "type": "graph",
            "targets": [{
                "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
            }]
        },
        # ... more panels
    ]
}
```

---

### Story 3: Intelligent Alerting System
**Points:** 8
**Priority:** P0

Create smart alerting to reduce false positives.

**Alerting Rules:**

**Critical Alerts (Page immediately):**
```yaml
- alert: ServiceDown
  expr: up{job="solstein-api"} == 0
  for: 1m
  severity: critical
  
- alert: DatabaseConnectionFailed
  expr: db_connection_errors_total > 10
  for: 2m
  severity: critical
  
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
  for: 2m
  severity: critical
```

**Warning Alerts (Notify, page if persists):**
```yaml
- alert: HighLatency
  expr: histogram_quantile(0.95, http_request_duration_seconds) > 0.5
  for: 5m
  severity: warning
  
- alert: LowCacheHitRate
  expr: cache_hit_rate < 0.5
  for: 10m
  severity: warning
```

**Smart Grouping:**
```python
# Group related alerts
alert_groups = {
    'database': ['DatabaseConnectionFailed', 'SlowQuery', 'PoolExhaustion'],
    'api': ['HighErrorRate', 'HighLatency', 'RateLimitExceeded'],
    'llm': ['ProviderUnavailable', 'HighCost', 'LowSuccessRate']
}

# If multiple database alerts fire, send one grouped notification
```

**Alert Channels:**
- **Critical:** PagerDuty + Slack + Email
- **Warning:** Slack + Email
- **Info:** Slack only

**Runbook Links:**
```yaml
annotations:
  runbook_url: "https://wiki.solstein.ai/runbooks/database-connection-failed"
  dashboard_url: "https://grafana.solstein.ai/d/database"
```

---

### Story 4: LLM Usage & Cost Monitoring
**Points:** 5
**Priority:** P0

Track and optimize LLM spending.

**Metrics:**
```python
from prometheus_client import Counter, Histogram, Gauge

# Token usage by provider/model
llm_tokens_total = Counter(
    'llm_tokens_total',
    'Tokens consumed',
    ['provider', 'model', 'token_type']  # token_type: input/output
)

# Cost tracking
llm_cost_dollars = Counter(
    'llm_cost_dollars_total',
    'Estimated cost in USD',
    ['provider', 'model']
)

# Request latency
llm_request_duration = Histogram(
    'llm_request_duration_seconds',
    'LLM request duration',
    ['provider', 'model']
)

# Provider health
llm_provider_available = Gauge(
    'llm_provider_available',
    'Provider availability (1=up, 0=down)',
    ['provider']
)
```

**Cost Attribution:**
```python
@trace_llm_call
async def llm_call(prompt: str, model: str, tenant_id: str = None):
    """Track LLM usage with attribution."""
    start = time.time()
    
    response = await provider.call(prompt, model)
    
    duration = time.time() - start
    tokens_in = count_tokens(prompt)
    tokens_out = count_tokens(response)
    cost = calculate_cost(model, tokens_in, tokens_out)
    
    # Record metrics
    llm_tokens_total.labels(
        provider=provider.name,
        model=model,
        token_type='input'
    ).inc(tokens_in)
    
    llm_tokens_total.labels(
        provider=provider.name,
        model=model,
        token_type='output'
    ).inc(tokens_out)
    
    llm_cost_dollars.labels(
        provider=provider.name,
        model=model
    ).inc(cost)
    
    # Log for attribution
    logger.info("LLM call", 
        tenant_id=tenant_id,
        cost=cost,
        tokens=tokens_in + tokens_out,
        model=model
    )
    
    return response
```

**Cost Alerts:**
```yaml
- alert: HighDailyLLMCost
  expr: increase(llm_cost_dollars_total[1d]) > 500
  for: 0m
  severity: warning
  annotations:
    summary: "Daily LLM cost exceeds $500"
    
- alert: UnexpectedCostSpike
  expr: |
    (
      increase(llm_cost_dollars_total[1h]) 
      > 
      2 * increase(llm_cost_dollars_total[1h] offset 1d)
    )
  for: 15m
  severity: warning
```

**Cost Dashboard:**
- Daily spend by provider
- Cost per request (trending)
- Cost by tenant (for billing)
- Model cost comparison
- Budget vs actual

---

### Story 5: SLA Monitoring & Compliance
**Points:** 5
**Priority:** P1

Monitor and report SLA compliance.

**SLA Definitions:**
```yaml
slas:
  availability:
    target: 99.9%  # <44min downtime/month
    measurement: up{job="solstein-api"}
    
  latency:
    target: 95% of requests < 200ms
    measurement: http_request_duration_seconds
    
  error_rate:
    target: < 0.1% 5xx errors
    measurement: rate(http_requests_total{status=~"5.."}[5m])
```

**SLA Reporting:**
```python
async def generate_sla_report(start: datetime, end: datetime) -> SLAReport:
    """Generate SLA compliance report."""
    
    # Availability
    uptime = await calculate_uptime(start, end)
    availability_sla = uptime >= 0.999
    
    # Latency
    latency_95 = await get_p95_latency(start, end)
    latency_sla = latency_95 < 0.2
    
    # Error rate
    error_rate = await calculate_error_rate(start, end)
    error_sla = error_rate < 0.001
    
    return SLAReport(
        period=f"{start} to {end}",
        availability={
            'actual': uptime,
            'target': 0.999,
            'compliant': availability_sla
        },
        latency={
            'actual': latency_95,
            'target': 0.2,
            'compliant': latency_sla
        },
        error_rate={
            'actual': error_rate,
            'target': 0.001,
            'compliant': error_sla
        }
    )
```

**Monthly SLA Report:**
- Automatically generated
- Sent to stakeholders
- Published on status page
- Trend analysis

---

### Story 6: Error Tracking & Analysis
**Points:** 5
**Priority:** P1

Implement comprehensive error tracking.

**Integration with Sentry:**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn="https://xxx@o0.ingest.sentry.io/0",
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
)
```

**Error Classification:**
```python
class ErrorClassifier:
    def classify(self, error: Exception) -> ErrorCategory:
        if isinstance(error, DatabaseError):
            return ErrorCategory.DATABASE
        elif isinstance(error, LLMError):
            return ErrorCategory.LLM_PROVIDER
        elif isinstance(error, ValidationError):
            return ErrorCategory.VALIDATION
        else:
            return ErrorCategory.UNKNOWN
```

**Error Trends:**
- New errors introduced
- Fixed errors
- Error frequency trends
- Most problematic endpoints

---

### Story 7: Automated Incident Response
**Points:** 8
**Priority:** P2

Automate common incident responses.

**Auto-Remediation Rules:**

**1. Restart Stuck Workers:**
```yaml
- alert: WorkerStuck
  expr: time() - worker_last_heartbeat > 300
  for: 1m
  actions:
    - type: restart_worker
      target: "{{ $labels.worker_id }}"
```

**2. Scale Up on Load:**
```yaml
- alert: HighLoad
  expr: cpu_usage > 80%
  for: 5m
  actions:
    - type: scale_up
      replicas: +2
      max_replicas: 10
```

**3. Failover LLM Provider:**
```yaml
- alert: LLMProviderDown
  expr: llm_provider_available{provider="openai"} == 0
  for: 2m
  actions:
    - type: switch_provider
      from: openai
      to: anthropic
```

**Incident Runbooks:**
```markdown
# Database Connection Failed

## Symptoms
- `DatabaseConnectionFailed` alert firing
- API returning 500 errors
- Health check failing

## Resolution Steps
1. Check RDS status in AWS console
2. Verify security group rules
3. Check connection pool usage
4. If pool exhausted: Restart application
5. If RDS down: Failover to read replica

## Escalation
If not resolved in 15 minutes, escalate to: on-call DBA
```

---

### Story 8: Log Aggregation & Analysis
**Points:** 5
**Priority:** P2

Centralized logging with search and analysis.

**Structured Logging:**
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "company_enriched",
    company_id="eneve",
    enrichment_sources=["linkedin", "crunchbase"],
    duration_ms=2500,
    quality_score=0.85
)
```

**Log Shipping:**
- Filebeat -> Logstash -> Elasticsearch
- Or: Direct to cloud (CloudWatch, Stackdriver)

**Log Analysis:**
- Kibana/ Grafana Loki for search
- Pattern detection
- Anomaly detection
- Correlation with metrics

---

## Infrastructure

### Monitoring Stack
```yaml
# docker-compose.monitoring.yml
version: '3'
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
      
  jaeger:
    image: jaegertracing/all-in-one
    ports:
      - "16686:16686"
      
  alertmanager:
    image: prom/alertmanager
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
```

### Dashboards
1. **Overview:** System health, key metrics
2. **API Performance:** Endpoints, latency, errors
3. **Business Metrics:** Companies, research, exports
4. **LLM Usage:** Costs, tokens, providers
5. **Infrastructure:** CPU, memory, disk, network
6. **Database:** Queries, connections, locks

---

## Definition of Done
- [ ] All services monitored
- [ ] Dashboards operational
- [ ] Alerting configured
- [ ] Runbooks documented
- [ ] Team trained
- [ ] On-call rotation established

## Estimated Effort
- **Total Points:** 54
- **Duration:** 8-10 weeks
- **Team:** 1 DevOps + 1 developer

## Dependencies
- EPIC-018 (Observability) - Builds on existing work
- EPIC-023 (Performance) - Metrics integration

---

*Created: 2026-03-06*  
*Target Release: Q3 2026*
