# EPIC-014: Improve Performance and Scalability

## Status: 🟡 HIGH
## Priority: P1 - Major Impact
## Effort: 5 story points
## Sprint: Required for production scale

---

## Problem Statement

The system has **performance bottlenecks** that will prevent scaling to larger datasets.

### Current Issues
```python
# Synchronous processing
for company in companies:  # 199 companies
    score = scorer.calculate(company)  # Sequential
    enrich(company)  # Sequential API calls

# No caching
# Each run re-fetches all data
# Excel generation is slow
```

### Impact
- **Slow processing** - 199 companies takes minutes
- **API rate limits** hit quickly
- **No caching** - redundant work
- **Memory issues** with large datasets

---

## Success Criteria

- [ ] Process 1000 companies in < 5 minutes
- [ ] API calls cached for 24 hours
- [ ] Parallel processing for independent operations
- [ ] Memory usage < 1GB for 1000 companies
- [ ] Progress reporting for long operations

---

## Technical Analysis

### Bottlenecks
1. **Sequential scoring** - companies processed one by one
2. **Synchronous API calls** - enrichment blocks
3. **No caching** - repeated data fetching
4. **Memory inefficient** - all data loaded at once

### Affected Files
- `scripts/run_eneve_199.py`
- `src/solstein/analytics/scoring.py`
- `src/solstein/data/enrichment.py`

---

## Stories

### Story 14.1: Implement Parallel Processing
**Priority:** P1 | **Effort:** 2 points

**Description:**
Add parallel processing for independent operations.

**Acceptance Criteria:**
- [ ] Score companies in parallel
- [ ] Enrich companies in parallel
- [ ] Limit concurrency to avoid rate limits
- [ ] Progress bar for long operations
- [ ] Error isolation - one failure doesn't stop others

**Implementation:**
```python
import asyncio
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

class ParallelProcessor:
    """Process companies in parallel."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
    
    async def score_companies_parallel(
        self,
        companies: list[Company],
        scorer: GrowthScorer
    ) -> list[Company]:
        """Score companies in parallel with progress bar."""
        
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def score_with_limit(company: Company) -> Company:
            async with semaphore:
                return await asyncio.to_thread(scorer.calculate_scores, company)
        
        # Process with progress bar
        tasks = [score_with_limit(c) for c in companies]
        
        scored = []
        for task in tqdm.as_completed(tasks, total=len(companies), desc="Scoring"):
            try:
                result = await task
                scored.append(result)
            except Exception as e:
                logger.error(f"Scoring failed: {e}")
        
        return scored
    
    async def enrich_companies_parallel(
        self,
        companies: list[dict],
        enricher: EnrichmentPipeline
    ) -> list[dict]:
        """Enrich companies in parallel."""
        
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def enrich_with_limit(company: dict) -> dict:
            async with semaphore:
                result = await enricher.enrich(company)
                return {**company, **result}
        
        tasks = [enrich_with_limit(c) for c in companies]
        
        enriched = []
        for task in tqdm.as_completed(tasks, total=len(companies), desc="Enriching"):
            try:
                result = await task
                enriched.append(result)
            except Exception as e:
                logger.error(f"Enrichment failed: {e}")
                enriched.append(company)  # Keep original on failure
        
        return enriched

# Usage
processor = ParallelProcessor(max_workers=4)
scored = await processor.score_companies_parallel(companies, scorer)
```

---

### Story 14.2: Implement Caching Layer
**Priority:** P1 | **Effort:** 2 points

**Description:**
Add caching for expensive operations.

**Acceptance Criteria:**
- [ ] Cache enrichment results
- [ ] Cache scoring results
- [ ] Cache API responses
- [ ] TTL of 24 hours for volatile data
- [ ] TTL of 7 days for stable data
- [ ] Cache invalidation mechanism

**Implementation:**
```python
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Any
import redis

class CacheManager:
    """Manage caching for expensive operations."""
    
    def __init__(self, redis_url: str = None):
        if redis_url:
            self.cache = redis.from_url(redis_url)
        else:
            # Fallback to in-memory cache
            self.cache = {}
    
    def _make_key(self, prefix: str, data: dict) -> str:
        """Create cache key from data."""
        data_str = json.dumps(data, sort_keys=True)
        hash_val = hashlib.md5(data_str.encode()).hexdigest()
        return f"{prefix}:{hash_val}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if isinstance(self.cache, dict):
            entry = self.cache.get(key)
            if entry and entry['expires'] > datetime.now():
                return entry['value']
            return None
        else:
            value = self.cache.get(key)
            return json.loads(value) if value else None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl_hours: int = 24
    ):
        """Set value in cache."""
        if isinstance(self.cache, dict):
            self.cache[key] = {
                'value': value,
                'expires': datetime.now() + timedelta(hours=ttl_hours)
            }
        else:
            self.cache.setex(
                key,
                timedelta(hours=ttl_hours),
                json.dumps(value)
            )
    
    async def get_or_compute(
        self,
        key: str,
        compute_func: callable,
        ttl_hours: int = 24
    ) -> Any:
        """Get from cache or compute and cache."""
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        result = await compute_func()
        await self.set(key, result, ttl_hours)
        return result

# Usage with enrichment
class CachedEnricher:
    def __init__(self, enricher: EnrichmentPipeline, cache: CacheManager):
        self.enricher = enricher
        self.cache = cache
    
    async def enrich(self, company: dict) -> dict:
        """Enrich with caching."""
        cache_key = self.cache._make_key('enrich', company)
        
        return await self.cache.get_or_compute(
            cache_key,
            lambda: self.enricher.enrich(company),
            ttl_hours=24
        )
```

---

### Story 14.3: Optimize Memory Usage
**Priority:** P1 | **Effort:** 1 point

**Description:**
Optimize memory usage for large datasets.

**Acceptance Criteria:**
- [ ] Stream data instead of loading all at once
- [ ] Use generators for large collections
- [ ] Clear intermediate results
- [ ] Monitor memory usage
- [ ] Stay under 1GB for 1000 companies

**Implementation:**
```python
from typing import Iterator, Generator
import psutil
import os

class MemoryOptimizedProcessor:
    """Process companies with memory optimization."""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.process = psutil.Process(os.getpid())
    
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024
    
    def stream_companies(
        self,
        file_path: str
    ) -> Generator[dict, None, None]:
        """Stream companies from file instead of loading all."""
        import json
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            for company in data['competitors']:
                yield company
    
    def process_in_batches(
        self,
        companies: list[Company],
        processor: callable
    ) -> Iterator[list[Company]]:
        """Process companies in batches to limit memory."""
        for i in range(0, len(companies), self.batch_size):
            batch = companies[i:i + self.batch_size]
            processed = [processor(c) for c in batch]
            
            # Log memory usage
            mem_mb = self.get_memory_usage_mb()
            logger.info(f"Batch {i//self.batch_size + 1}: {mem_mb:.1f} MB")
            
            yield processed
            
            # Clear batch to free memory
            del batch
            del processed

# Usage
processor = MemoryOptimizedProcessor(batch_size=50)

# Stream instead of load all
for company in processor.stream_companies('data.json'):
    process_company(company)

# Process in batches
for batch in processor.process_in_batches(companies, score_company):
    save_batch(batch)
```

---

## Dependencies

- Stories 14.1, 14.2, and 14.3 can be done in parallel

## Definition of Done

- [ ] Parallel processing implemented
- [ ] Caching layer working
- [ ] Memory optimized
- [ ] Performance benchmarks show improvement
- [ ] Can process 1000 companies in < 5 minutes
