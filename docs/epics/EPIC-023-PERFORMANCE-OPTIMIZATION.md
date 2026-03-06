# Epic: Performance Optimization & Profiling (EPIC-023)

## Overview
Implement comprehensive performance profiling, optimization, and monitoring to ensure Solstein operates efficiently under load. Identify and eliminate bottlenecks in database queries, JSON serialization, and computational intensive operations.

## Background
Current codebase shows signs of performance issues:
- Synchronous I/O in research pipeline blocks the event loop
- JSON serialization of large objects creates memory pressure
- No performance benchmarks or profiling data exists
- Database query performance untested
- Caching strategy inconsistent

## Goals
- [ ] Achieve <100ms average API response time
- [ ] Reduce memory usage by 40% for large datasets
- [ ] Implement comprehensive performance monitoring
- [ ] Optimize database query performance
- [ ] Establish performance regression testing

## Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| API Response Time | Unknown | <100ms p95 |
| Research Pipeline | Minutes | <30 seconds |
| Memory Usage (1000 companies) | Unknown | <2GB |
| Database Query Time | Unknown | <50ms average |
| JSON Serialization | Blocking | Async streaming |

---

## Stories

### Story 1: Implement Performance Profiling Infrastructure
**Points:** 5
**Priority:** P0

Create comprehensive profiling infrastructure to identify bottlenecks.

**Tasks:**
- [ ] Set up `py-spy` for CPU profiling
- [ ] Integrate `memray` for memory profiling
- [ ] Create `@profile` decorator for function-level profiling
- [ ] Implement timing middleware for API endpoints
- [ ] Create profiling dashboard

**Acceptance Criteria:**
```python
# Usage example
from solstein.monitoring.profiler import profile

@profile(name="enrich_company", report=True)
async def enrich_company(company_id: str):
    # Function is automatically profiled
    pass

# Results logged and viewable in dashboard
```

**Definition of Done:**
- [ ] Profiler can be enabled via environment variable
- [ ] Results export to JSON/HTML
- [ ] No performance overhead when disabled
- [ ] Documentation complete

---

### Story 2: Database Query Optimization
**Points:** 8
**Priority:** P0

Analyze and optimize all database queries.

**Tasks:**
- [ ] Enable SQL query logging
- [ ] Identify N+1 query problems
- [ ] Add missing database indexes
- [ ] Optimize slow queries (target: <50ms)
- [ ] Implement query result caching
- [ ] Add database connection pooling

**Acceptance Criteria:**
```python
# Before optimization (N+1 problem)
for company in companies:
    await db.fetch(company.metrics)  # N queries

# After optimization (single query)
companies_with_metrics = await db.fetch(
    "SELECT c.*, m.* FROM companies c JOIN metrics m ON c.id = m.company_id"
)
```

**Metrics:**
- Query time reduced by 50%
- Zero N+1 queries
- Connection pool utilization <80%

**Definition of Done:**
- [ ] All queries <50ms average
- [ ] Query plan analysis documented
- [ ] Indexes created and verified
- [ ] Caching implemented for hot queries

---

### Story 3: Async JSON Serialization
**Points:** 5
**Priority:** P0

Replace blocking JSON serialization with async streaming.

**Current Issue:**
```python
# Blocking operation
scored_payload = [company.model_dump(mode="json") for company in scored]
# Blocks event loop for large datasets
```

**Solution:**
```python
# Async streaming
async def serialize_companies(companies):
    for company in companies:
        yield await asyncio.to_thread(company.model_dump, mode="json")
        await asyncio.sleep(0)  # Yield control
```

**Tasks:**
- [ ] Audit all JSON serialization points
- [ ] Implement async JSON encoder
- [ ] Add streaming JSON response support
- [ ] Benchmark before/after

**Acceptance Criteria:**
- [ ] No blocking JSON operations in async context
- [ ] Streaming works for >1000 objects
- [ ] Memory usage reduced by 50%

---

### Story 4: Implement Multi-Level Caching Strategy
**Points:** 8
**Priority:** P0

Implement comprehensive caching at multiple layers.

**Cache Layers:**
1. **L1 - In-Memory:** LRU cache for hot data
2. **L2 - Redis:** Shared cache across workers
3. **L3 - CDN:** Static exports and reports

**Tasks:**
- [ ] Implement `@cached` decorator with TTL
- [ ] Add Redis cache backend
- [ ] Cache database query results
- [ ] Cache enrichment API responses
- [ ] Cache computed scores
- [ ] Add cache invalidation strategy

**Acceptance Criteria:**
```python
from solstein.infrastructure.cache import cached

@cached(ttl=300, backend="redis")  # 5 minute cache
async def get_company_score(company_id: str) -> Score:
    return await calculate_score(company_id)

@cached(ttl=3600, backend="memory")  # 1 hour memory cache
async def get_market_data(market: str) -> MarketData:
    return await fetch_market_data(market)
```

**Metrics:**
- Cache hit rate >70%
- Response time reduced by 60%
- Database load reduced by 50%

---

### Story 5: Optimize Research Pipeline Performance
**Points:** 13
**Priority:** P0

Convert synchronous research pipeline to fully async.

**Current:**
```python
def run_market_intelligence(...):
    # Synchronous blocking operations
    candidates = discover_companies(...)  # Blocks
    companies = [enrich_company(c) for c in candidates]  # Sequential
```

**Target:**
```python
async def run_market_intelligence(...):
    # Fully async with concurrency
    candidates = await discover_companies_async(...)
    companies = await asyncio.gather(*[
        enrich_company_async(c) for c in candidates
    ])
```

**Tasks:**
- [ ] Convert discovery to async
- [ ] Convert enrichment to async
- [ ] Add concurrency limits (semaphores)
- [ ] Implement pipeline stage parallelization
- [ ] Add progress tracking

**Acceptance Criteria:**
- [ ] Pipeline completes in <30 seconds (vs minutes)
- [ ] Memory usage <2GB
- [ ] CPU utilization optimized
- [ ] Can process 100 companies concurrently

---

### Story 6: Implement Performance Regression Testing
**Points:** 5
**Priority:** P1

Prevent performance regressions through automated testing.

**Tasks:**
- [ ] Create performance benchmark suite
- [ ] Add API latency tests
- [ ] Add memory usage tests
- [ ] Add throughput tests
- [ ] Integrate into CI/CD

**Acceptance Criteria:**
```python
# tests/performance/test_api_latency.py
async def test_company_endpoint_latency():
    start = time.time()
    response = await client.get("/api/companies/123")
    elapsed = time.time() - start
    assert elapsed < 0.1  # 100ms max
    assert response.status_code == 200
```

**CI Integration:**
```yaml
- name: Performance Tests
  run: |
    pytest tests/performance/ --benchmark-only
    # Fail if 10% slower than baseline
```

---

### Story 7: Optimize LLM API Usage
**Points:** 5
**Priority:** P1

Reduce LLM API costs and latency through optimization.

**Tasks:**
- [ ] Implement request batching
- [ ] Add prompt caching
- [ ] Optimize prompt templates (reduce tokens)
- [ ] Implement model tiering (cheap for simple tasks)
- [ ] Add token usage monitoring

**Cost Optimization:**
```python
# Model tiering
TIER_MAPPING = {
    "summarization": "gpt-3.5-turbo",  # Cheap
    "analysis": "gpt-4",               # Expensive but accurate
    "classification": "gpt-3.5-turbo", # Cheap
}
```

**Metrics:**
- LLM costs reduced by 40%
- Average response time <2 seconds
- Token usage optimized

---

### Story 8: Memory Optimization
**Points:** 5
**Priority:** P1

Reduce memory footprint for large operations.

**Tasks:**
- [ ] Implement streaming for large datasets
- [ ] Use generators instead of lists where possible
- [ ] Add memory usage monitoring
- [ ] Optimize data structures
- [ ] Add memory limits and warnings

**Example:**
```python
# Before: loads all into memory
companies = await load_all_companies()  # 1000 objects

# After: streaming
async for company in load_companies_streaming():
    await process(company)  # One at a time
```

---

## Technical Implementation

### Tools & Libraries
- **Profiling:** py-spy, memray, pyinstrument
- **Benchmarking:** pytest-benchmark
- **Caching:** redis-py, cachetools
- **Monitoring:** prometheus_client, grafana

### Infrastructure
```python
# solstein/monitoring/performance.py
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'api_latency': Histogram('api_latency_seconds'),
            'db_query_time': Histogram('db_query_seconds'),
            'memory_usage': Gauge('memory_bytes'),
            'cache_hit_rate': Gauge('cache_hit_rate'),
        }
```

---

## Performance Budgets

| Component | Target | Alert Threshold |
|-----------|--------|-----------------|
| API Response (p95) | <100ms | >200ms |
| Database Query (avg) | <50ms | >100ms |
| Research Pipeline | <30s | >60s |
| Memory (1000 companies) | <2GB | >4GB |
| Cache Hit Rate | >70% | <50% |

---

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Optimization breaks functionality | High | Comprehensive tests |
| Premature optimization | Medium | Profile first, optimize second |
| Cache inconsistency | Medium | Proper invalidation |
| Memory leaks | High | Memory profiling |

---

## Definition of Done
- [ ] All performance targets met
- [ ] Profiling infrastructure operational
- [ ] Performance tests in CI/CD
- [ ] Documentation complete
- [ ] Team trained on performance best practices

## Estimated Effort
- **Total Points:** 54
- **Duration:** 8-10 weeks
- **Team:** 1 senior developer

## Dependencies
- EPIC-020 (God functions) - Optimize after cleanup
- EPIC-014 (Performance) - Builds on existing work

---

*Created: 2026-03-06*  
*Target Release: Q3 2026*
