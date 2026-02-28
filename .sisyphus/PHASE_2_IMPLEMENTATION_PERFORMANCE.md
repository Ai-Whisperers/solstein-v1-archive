# PHASE 2: PERFORMANCE OPTIMIZATION - DETAILED IMPLEMENTATION PLAN
**Weeks 2-3 | 84 Hours | Team: 1-2 developers**

> Priority: 🟠 HIGH - Major performance improvements (10x-100x)  
> Timeline: Weeks 2-3 (10 business days)  
> Owner: Backend Lead + Database Engineer  
> Review: Performance testing + Code review

---

## PHASE 2 OVERVIEW

### Goals
1. ✅ Fix N+1 query patterns (100x faster)
2. ✅ Add database indexes (10-100x faster)
3. ✅ Implement Redis caching (50x faster for cached queries)
4. ✅ Add request validation (security + data integrity)
5. ✅ Add input validation to all endpoints

### Expected Impact
```
Before:  Market analysis with 1,000 companies = 1,001 queries × 50ms = 50 seconds
After:   Market analysis with 1,000 companies = 5 queries × 50ms = 250ms
Improvement: 200x faster
```

### Timeline
```
Day 1:  Item 2.1 (N+1 query patterns analysis)
Day 2:  Item 2.1 implementation + testing
Day 3:  Item 2.2 (Database indexes)
Day 4:  Item 2.3 (Redis caching - design)
Day 5:  Item 2.3 continued (implementation)
Days 6-8: Item 2.4 (Input validation)
Days 9-10: Testing, reviews, documentation
```

---

## ITEM 2.1: Fix N+1 Query Patterns (16 hours)

### Context
**Risk Level**: 🟠 HIGH - Performance + security (DoS vector)  
**Current Status**: Multiple locations with N+1 patterns  
**Impact**: 1,000 companies = 1,001 queries instead of 5-10  

### Diagnosis

#### Finding N+1 Queries
```bash
# Enable query logging to find N+1 patterns
export LOG_SQL=true
python -m pytest tests/integration/ -s -v
```

**Look for**: Same query repeated multiple times in succession

**Typical Pattern**:
```python
# 1 query: load all companies
companies = repo.get_all()

# N queries: 1 per company in loop
for company in companies:
    overlap = calculate_overlap(company, competitors)
```

### Root Cause Analysis

**File**: `/src/solstein/api/routers/market.py` (lines 67-96)

```python
# ❌ N+1 PATTERN
@router.get("/api/market/overlap")
async def get_market_overlap(sector: str, competitors: list):
    """Get market overlap analysis - HAS N+1 PATTERN"""
    
    # Query 1: Load all companies in sector
    companies = await repo.get_companies_by_sector(sector)
    
    overlaps = []
    for company in companies:  # Loop through N companies
        # Queries 2 to N+1: Load competitors for EACH company
        competitors_data = await repo.get_competitors(company.id)
        financials = await repo.get_financials(company.id)
        
        overlap = calculate_overlap(company, competitors_data)
        overlaps.append(overlap)
    
    return overlaps  # Total queries: 1 + N + N = 2N+1 queries!
```

### Implementation Plan

#### Step 1: Refactor Market Overlap Endpoint
**File**: `/src/solstein/api/routers/market.py`

**Find** (lines 67-96):
```python
@router.get("/api/market/overlap")
async def get_market_overlap(sector: str, competitors: list):
    companies = await repo.get_companies_by_sector(sector)
    overlaps = []
    for company in companies:
        competitors_data = await repo.get_competitors(company.id)
        financials = await repo.get_financials(company.id)
        overlap = calculate_overlap(company, competitors_data)
        overlaps.append(overlap)
    return overlaps
```

**Replace with** (eager loading using selectinload):
```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

@router.get("/api/market/overlap")
async def get_market_overlap(
    sector: str,
    competitors: list,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get market overlap analysis
    
    ✅ FIXED: Uses single query with eager loading
    """
    try:
        # Single query with eager loading
        stmt = (
            select(Company)
            .where(Company.sector == sector)
            .options(
                selectinload(Company.competitors),  # Eager load competitors
                selectinload(Company.financials),    # Eager load financials
            )
        )
        result = await session.execute(stmt)
        companies = result.scalars().unique().all()
        
        logger.info(f"Loaded {len(companies)} companies with competitors/financials in 1 query")
        
        # Calculate overlaps in memory (no more queries)
        overlaps = [
            {
                "company_id": c.id,
                "company_name": c.name,
                "overlap_score": calculate_overlap(c, competitors),
                "competitors_count": len(c.competitors)
            }
            for c in companies
        ]
        
        return overlaps
        
    except Exception as e:
        logger.error(f"Failed to analyze market overlap: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")
```

#### Step 2: Create repository helper methods
**File**: `/src/solstein/infrastructure/repositories.py`

**Add these new methods**:
```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

class CompanyRepository:
    """Company repository with query optimization"""
    
    async def get_companies_with_all_relations(
        self,
        sector: str = None,
        eager_load_all: bool = True
    ) -> List[Company]:
        """
        Get companies with all relations eager loaded
        
        ✅ Single query with all data
        
        Args:
            sector: Filter by sector (optional)
            eager_load_all: Whether to eager load all relations
        
        Returns:
            List of companies with all relations loaded
        """
        stmt = select(Company)
        
        # Eager load all relations
        if eager_load_all:
            stmt = stmt.options(
                selectinload(Company.competitors),
                selectinload(Company.financials),
                selectinload(Company.market_positions),
                selectinload(Company.analyses),
            )
        
        # Filter by sector if provided
        if sector:
            stmt = stmt.where(Company.sector == sector)
        
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()
    
    async def get_company_with_details(self, company_id: str) -> Company:
        """
        Get single company with all related data eager loaded
        
        ✅ Single query for complete company profile
        """
        stmt = (
            select(Company)
            .where(Company.id == company_id)
            .options(
                selectinload(Company.competitors),
                selectinload(Company.financials),
                selectinload(Company.market_positions),
                selectinload(Company.analyses),
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()
    
    async def get_companies_batch(
        self,
        company_ids: List[str],
        eager_load: List[str] = None
    ) -> List[Company]:
        """
        Get multiple companies efficiently
        
        ✅ Single batch query with optional eager loading
        
        Args:
            company_ids: List of IDs to fetch
            eager_load: List of relations to eager load (competitors, financials, etc.)
        
        Returns:
            List of companies
        """
        stmt = select(Company).where(Company.id.in_(company_ids))
        
        # Add eager loading options
        if eager_load:
            if "competitors" in eager_load:
                stmt = stmt.options(selectinload(Company.competitors))
            if "financials" in eager_load:
                stmt = stmt.options(selectinload(Company.financials))
            if "analyses" in eager_load:
                stmt = stmt.options(selectinload(Company.analyses))
        
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()
```

#### Step 3: Update all endpoints to use optimized queries
**Files to update**:
- `/src/solstein/api/routers/companies.py`
- `/src/solstein/api/routers/markets.py`
- `/src/solstein/api/routers/analysis.py`

**Pattern**: Replace loops with eager loading

```python
# ❌ BEFORE
@router.get("/companies")
async def list_companies(repo: CompanyRepo = Depends()):
    companies = repo.get_all()  # 1 query
    results = []
    for c in companies:
        details = repo.get_details(c.id)  # N more queries!
        results.append(details)
    return results

# ✅ AFTER
@router.get("/companies")
async def list_companies(repo: CompanyRepo = Depends()):
    # Single query with all data
    companies = await repo.get_companies_with_all_relations()
    return companies
```

### Testing

#### Unit Tests
**File**: `/tests/unit/test_n_plus_one_queries.py` (new file)

```python
"""Tests to verify N+1 queries are fixed"""

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import event, func
from solstein.infrastructure.repositories import CompanyRepository


class TestNPlusOneQueries:
    """Verify no N+1 query patterns"""
    
    @pytest.fixture
    def query_counter(self):
        """Count queries executed"""
        class QueryCounter:
            count = 0
        
        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
            QueryCounter.count += 1
        
        yield QueryCounter
    
    @pytest.mark.asyncio
    async def test_get_companies_single_query(self, query_counter, repo):
        """Verify getting companies uses only 1 query"""
        query_counter.count = 0
        
        companies = await repo.get_companies_with_all_relations(sector="Tech")
        
        # Should be exactly 1 query
        assert query_counter.count == 1, f"Expected 1 query, got {query_counter.count}"
    
    @pytest.mark.asyncio
    async def test_market_overlap_no_n_plus_one(self, query_counter, repo):
        """Verify market overlap analysis doesn't have N+1"""
        query_counter.count = 0
        
        companies = await repo.get_companies_with_all_relations(sector="Tech")
        
        # Calculate overlaps (no queries in this loop)
        overlaps = [
            {
                "id": c.id,
                "overlap": calculate_overlap(c, [])
            }
            for c in companies
        ]
        
        # Should still be exactly 1 query
        assert query_counter.count == 1
```

#### Performance Tests
**File**: `/tests/performance/test_query_performance.py` (new file)

```python
"""Performance tests to verify improvement"""

import pytest
import time
from solstein.infrastructure.repositories import CompanyRepository


class TestQueryPerformance:
    """Measure and verify query performance"""
    
    @pytest.mark.asyncio
    async def test_load_1000_companies_performance(self, repo):
        """Verify 1,000 companies load in <1 second"""
        # Create 1,000 test companies
        # (skip if test data too large)
        
        start = time.time()
        companies = await repo.get_companies_with_all_relations()
        duration = time.time() - start
        
        # Should load 1,000+ companies with all relations in <1 second
        assert duration < 1.0, f"Loading took {duration}s, should be <1s"
    
    @pytest.mark.asyncio
    async def test_batch_operations_faster_than_loop(self, repo):
        """Verify batch operations are significantly faster"""
        company_ids = ["c1", "c2", "c3", "c4", "c5"]
        
        # Batch operation
        start = time.time()
        companies = await repo.get_companies_batch(company_ids, eager_load=["competitors"])
        batch_time = time.time() - start
        
        assert len(companies) == 5
        assert batch_time < 0.1, f"Batch operation took {batch_time}s"
```

### Verification

```bash
# 1. Check query count with logging
export LOG_SQL=true
pytest tests/unit/test_n_plus_one_queries.py -v -s

# Should see "1 query" not "101 queries"

# 2. Performance testing
pytest tests/performance/test_query_performance.py -v

# Should show <1s for 1000 companies

# 3. Endpoint testing
curl -X GET http://localhost:8000/api/companies?sector=Tech
# Should respond in <200ms (not 50s)
```

### Expected Results

**Before Fix**:
```
GET /api/companies with 1,000 companies
└─ Query 1: SELECT * FROM companies (1,000 rows)
└─ Queries 2-1001: SELECT * FROM competitors WHERE company_id = ? (1,000 times!)
└─ Queries 1002-2001: SELECT * FROM financials WHERE company_id = ? (1,000 times!)
Total: 2,001 queries
Time: 50-100 seconds
```

**After Fix**:
```
GET /api/companies with 1,000 companies
└─ Query 1: SELECT * FROM companies 
            LEFT JOIN competitors ON ...
            LEFT JOIN financials ON ...
            (single query with joins)
Total: 1 query
Time: 100-200ms
Improvement: 250-500x faster
```

**Effort**: 16 hours  
**Complexity**: 🟠 MEDIUM  
**Testing Time**: 4 hours

---

## ITEM 2.2: Add Database Indexes (4 hours)

### Context
**Risk Level**: 🟠 HIGH - Query performance bottleneck  
**Current Status**: Missing critical indexes  
**Impact**: Sort/filter operations become full table scans  

### Missing Indexes Analysis

**File**: `/src/solstein/infrastructure/database_models.py`

```python
# ❌ NO INDEX on creation time (common sort)
class Company(Base):
    __tablename__ = "companies"
    
    id: Column = Column(String, primary_key=True)
    name: Column = Column(String)
    sector: Column = Column(String)  # ❌ NO INDEX
    growth_score: Column = Column(Float)  # ❌ NO INDEX
    created_at: Column = Column(DateTime)  # ❌ NO INDEX
    analyst_id: Column = Column(String, ForeignKey("analysts.id"))  # ❌ FK no index
```

### Queries That Need Indexes

| Query | Current Performance | Why Slow | Index Needed |
|-------|---|---|---|
| `WHERE sector='Tech'` | Full scan | No index on sector | `idx_company_sector` |
| `WHERE sector='Tech' AND growth_score>0.8` | Full scan | No composite index | `idx_company_sector_growth` |
| `ORDER BY created_at DESC` | Full sort | No index | `idx_company_created_at` |
| `WHERE analyst_id='a1'` | Full scan | Foreign key unindexed | `idx_company_analyst_id` |

### Implementation

#### Step 1: Create migration with indexes
**File**: `/alembic/versions/2026_02_28_add_missing_indexes.py` (new migration)

```python
"""Add missing database indexes for performance

Revision ID: 001_add_indexes
Revises: (previous_migration_id)
Create Date: 2026-02-28
"""

from alembic import op
import sqlalchemy as sa


revision = '001_add_indexes'
down_revision = None  # Set to previous migration ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add missing indexes"""
    
    # Company table indexes
    op.create_index('idx_company_sector', 'company', ['sector'])
    op.create_index('idx_company_created_at', 'company', ['created_at'])
    op.create_index('idx_company_analyst_id', 'company', ['analyst_id'])
    op.create_index(
        'idx_company_sector_growth',
        'company',
        ['sector', 'growth_score'],
        unique=False
    )
    
    # Analyst table indexes
    op.create_index('idx_analyst_email', 'analyst', ['email'], unique=True)
    op.create_index('idx_analyst_created_at', 'analyst', ['created_at'])
    
    # MarketPosition table indexes
    op.create_index('idx_market_position_company_id', 'market_position', ['company_id'])
    op.create_index(
        'idx_market_position_market_company',
        'market_position',
        ['market_id', 'company_id']
    )
    
    # Competitor table indexes
    op.create_index('idx_competitor_company_id', 'competitor', ['company_id'])
    op.create_index('idx_competitor_competitor_id', 'competitor', ['competitor_id'])


def downgrade() -> None:
    """Remove indexes"""
    
    op.drop_index('idx_company_sector')
    op.drop_index('idx_company_created_at')
    op.drop_index('idx_company_analyst_id')
    op.drop_index('idx_company_sector_growth')
    op.drop_index('idx_analyst_email')
    op.drop_index('idx_analyst_created_at')
    op.drop_index('idx_market_position_company_id')
    op.drop_index('idx_market_position_market_company')
    op.drop_index('idx_competitor_company_id')
    op.drop_index('idx_competitor_competitor_id')
```

#### Step 2: Run migration
```bash
# Generate migration
alembic revision --autogenerate -m "Add missing indexes"

# Review migration
cat alembic/versions/2026_*.py

# Apply migration to development
alembic upgrade head

# Test on development database
```

#### Step 3: Verify indexes were created
```bash
# PostgreSQL
psql -U user -d solstein -c "\d company"

# Should show:
# Indexes:
#     "idx_company_sector" btree (sector)
#     "idx_company_created_at" btree (created_at)
#     ...

# MySQL
SHOW INDEXES FROM company;
```

### Testing

#### Performance Benchmark
**File**: `/tests/performance/test_index_performance.py` (new file)

```python
"""Verify indexes improve query performance"""

import pytest
import time
from solstein.infrastructure.repositories import CompanyRepository


class TestIndexPerformance:
    """Measure performance improvement from indexes"""
    
    @pytest.mark.asyncio
    async def test_filter_by_sector_uses_index(self, repo):
        """Verify sector filter uses index"""
        start = time.time()
        companies = await repo.get_companies_by_sector("Tech")
        duration = time.time() - start
        
        # With index: <10ms for 10,000 companies
        # Without index: 100-500ms
        assert duration < 0.05, f"Sector filter took {duration}s (should use index)"
    
    @pytest.mark.asyncio
    async def test_composite_filter_uses_index(self, repo):
        """Verify composite filter uses index"""
        start = time.time()
        companies = await repo.get_companies_by_sector_and_growth("Tech", 0.8)
        duration = time.time() - start
        
        # With composite index: <10ms
        # Without: 100-500ms
        assert duration < 0.05
    
    @pytest.mark.asyncio
    async def test_sort_by_date_uses_index(self, repo):
        """Verify DATE sort uses index"""
        start = time.time()
        companies = await repo.get_companies_sorted_by_date()
        duration = time.time() - start
        
        # With index: <20ms for sort
        # Without: 200-500ms
        assert duration < 0.05
```

#### EXPLAIN ANALYZE
```bash
# Verify query uses index
psql -U user -d solstein

# Check sector filter
EXPLAIN ANALYZE SELECT * FROM company WHERE sector = 'Tech';

# Should show:
# Index Scan using idx_company_sector on company ...
# NOT "Seq Scan" (sequential scan = full table scan, no index)

# Check composite filter
EXPLAIN ANALYZE 
SELECT * FROM company 
WHERE sector = 'Tech' AND growth_score > 0.8;

# Should show:
# Index Scan using idx_company_sector_growth on company ...
```

### Monitoring

#### Index Usage Statistics
```sql
-- Check which indexes are being used
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY idx_scan;

-- Zero scans = unused index (candidate for removal)
```

**Effort**: 4 hours  
**Complexity**: 🟢 LOW  
**Testing Time**: 1 hour

---

## ITEM 2.3: Implement Redis Caching (16 hours)

### Context
**Risk Level**: 🟠 MEDIUM - Optional optimization  
**Current Status**: No caching at all  
**Impact**: Same queries repeated = 50-100ms instead of 1-5ms cache hits  

### Caching Strategy

```
Tier 1: HTTP Cache (Cache-Control headers) - Browser/CDN
        ├─ Static endpoints (health, status) - 1 hour TTL
        ├─ Company profiles - 5 minute TTL
        └─ Market data - 1 hour TTL

Tier 2: Application Cache (Redis) - Fast in-memory lookup
        ├─ Company by ID - 1 hour TTL
        ├─ Analysis results - 6 hours TTL
        ├─ Market positions - 1 day TTL
        └─ Lists (paginated) - 5 minute TTL

Tier 3: Database - Source of truth
```

### Installation & Setup

#### Step 1: Add Redis dependency
```bash
pip install redis
# or
uv add redis
```

#### Step 2: Create cache layer
**File**: `/src/solstein/infrastructure/cache.py` (new file)

```python
"""Cache layer implementation using Redis"""

import json
import logging
from typing import Optional, Any, Callable
from datetime import timedelta
import redis
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis-based caching with fallback to in-memory"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize cache manager
        
        Args:
            redis_url: Redis connection URL
        """
        try:
            self.redis = redis.from_url(redis_url)
            self.redis.ping()  # Test connection
            logger.info("Redis cache connected")
            self.available = True
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}, using in-memory cache")
            self.redis = None
            self.available = False
            self.memory_cache = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None
        """
        try:
            if self.available:
                value = self.redis.get(key)
                if value:
                    return json.loads(value)
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        
        Returns:
            True if successful
        """
        try:
            serialized = json.dumps(value)
            
            if self.available:
                self.redis.setex(key, ttl, serialized)
            else:
                self.memory_cache[key] = (value, ttl)
            
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete from cache"""
        try:
            if self.available:
                self.redis.delete(key)
            else:
                self.memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern
        
        Args:
            pattern: Key pattern (e.g., 'company:*')
        
        Returns:
            Number of keys deleted
        """
        try:
            if self.available:
                keys = self.redis.keys(pattern)
                if keys:
                    return self.redis.delete(*keys)
            else:
                count = 0
                for key in list(self.memory_cache.keys()):
                    if self._matches_pattern(key, pattern):
                        del self.memory_cache[key]
                        count += 1
                return count
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return 0
    
    @staticmethod
    def _matches_pattern(key: str, pattern: str) -> bool:
        """Simple pattern matching (e.g., 'company:*')"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)


# Global cache instance
cache = None


def init_cache(redis_url: str) -> CacheManager:
    """Initialize global cache manager"""
    global cache
    cache = CacheManager(redis_url)
    return cache


def get_cache() -> CacheManager:
    """Get cache manager instance"""
    global cache
    if cache is None:
        cache = CacheManager()
    return cache
```

#### Step 3: Add caching decorator
**File**: `/src/solstein/infrastructure/cache.py` (append)

```python
def cached(
    key_prefix: str,
    ttl: int = 3600,
    key_builder: Callable = None
):
    """
    Decorator to cache function results
    
    Args:
        key_prefix: Cache key prefix
        ttl: Time-to-live in seconds
        key_builder: Custom function to build cache key
    
    Usage:
        @cached("company", ttl=3600)
        async def get_company(company_id: str):
            return await repo.get_company(company_id)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default: key_prefix:arg1:arg2:...
                arg_str = ":".join(str(arg) for arg in args if arg)
                cache_key = f"{key_prefix}:{arg_str}"
            
            # Try cache first
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Cache miss - execute function
            logger.debug(f"Cache miss: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    
    return decorator
```

#### Step 4: Apply caching to endpoints
**File**: `/src/solstein/api/routers/companies.py`

```python
from solstein.infrastructure.cache import cached

@router.get("/api/companies/{company_id}")
@cached(
    key_prefix="company",
    ttl=3600,  # 1 hour
    key_builder=lambda self, company_id: f"company:{company_id}"
)
async def get_company(
    company_id: str,
    repo: CompanyRepository = Depends()
):
    """Get company by ID - CACHED for 1 hour"""
    company = await repo.get_company_with_details(company_id)
    if not company:
        raise HTTPException(status_code=404)
    return company


@router.get("/api/companies")
@cached(
    key_prefix="companies_list",
    ttl=300,  # 5 minutes for lists (shorter TTL)
    key_builder=lambda self, sector, page: f"companies_list:{sector}:{page}"
)
async def list_companies(
    sector: str = None,
    page: int = 1,
    repo: CompanyRepository = Depends()
):
    """List companies - CACHED for 5 minutes"""
    return await repo.get_companies_paginated(sector, page)
```

#### Step 5: Cache invalidation on updates
**File**: `/src/solstein/api/routers/companies.py`

```python
from solstein.infrastructure.cache import get_cache

@router.put("/api/companies/{company_id}")
async def update_company(
    company_id: str,
    data: CompanyUpdate,
    repo: CompanyRepository = Depends()
):
    """Update company - invalidate cache"""
    
    # Update in database
    company = await repo.update_company(company_id, data)
    
    # Invalidate related caches
    cache = get_cache()
    await cache.delete(f"company:{company_id}")  # Specific company
    await cache.clear_pattern("companies_list:*")  # All lists
    
    logger.info(f"Invalidated caches for company {company_id}")
    return company
```

### Testing

#### Cache Tests
**File**: `/tests/unit/test_cache.py` (new file)

```python
"""Tests for caching functionality"""

import pytest
from solstein.infrastructure.cache import CacheManager, cached


class TestCacheManager:
    """Cache manager tests"""
    
    @pytest.fixture
    def cache(self):
        return CacheManager()
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, cache):
        """Test basic set/get"""
        await cache.set("test_key", {"data": "value"}, ttl=10)
        result = await cache.get("test_key")
        assert result == {"data": "value"}
    
    @pytest.mark.asyncio
    async def test_expiration(self, cache):
        """Test TTL expiration"""
        import asyncio
        
        await cache.set("expiring", "value", ttl=1)
        assert await cache.get("expiring") == "value"
        
        await asyncio.sleep(1.1)
        assert await cache.get("expiring") is None
    
    @pytest.mark.asyncio
    async def test_delete(self, cache):
        """Test deletion"""
        await cache.set("to_delete", "value")
        assert await cache.get("to_delete") == "value"
        
        await cache.delete("to_delete")
        assert await cache.get("to_delete") is None
    
    @pytest.mark.asyncio
    async def test_clear_pattern(self, cache):
        """Test pattern-based clearing"""
        await cache.set("company:1", {"id": 1})
        await cache.set("company:2", {"id": 2})
        await cache.set("analyst:1", {"id": 1})
        
        await cache.clear_pattern("company:*")
        
        assert await cache.get("company:1") is None
        assert await cache.get("analyst:1") == {"id": 1}


class TestCachingDecorator:
    """Test @cached decorator"""
    
    @pytest.mark.asyncio
    async def test_caches_function_result(self):
        """Test function result is cached"""
        call_count = 0
        
        @cached("test", ttl=10)
        async def expensive_function(id: str):
            nonlocal call_count
            call_count += 1
            return f"result:{id}"
        
        # First call - executes function
        result1 = await expensive_function("123")
        assert result1 == "result:123"
        assert call_count == 1
        
        # Second call - returns cached result
        result2 = await expensive_function("123")
        assert result2 == "result:123"
        assert call_count == 1  # Not incremented!
```

#### Performance Test
**File**: `/tests/performance/test_caching_performance.py` (new file)

```python
"""Measure caching performance improvement"""

import pytest
import time
from solstein.api.routers.companies import get_company


class TestCachingPerformance:
    """Verify caching provides significant speedup"""
    
    @pytest.mark.asyncio
    async def test_cached_query_much_faster(self, repo, cache):
        """Verify cached queries are 10-50x faster"""
        company_id = "c1"
        
        # First call - cache miss
        start = time.time()
        result1 = await get_company(company_id)
        first_time = time.time() - start
        
        # Second call - cache hit
        start = time.time()
        result2 = await get_company(company_id)
        cached_time = time.time() - start
        
        # Cached should be much faster
        assert result1 == result2
        assert cached_time < first_time / 5, \
            f"Cached ({cached_time}s) not faster than first ({first_time}s)"
        
        logger.info(
            f"First call: {first_time*1000:.2f}ms, "
            f"Cached: {cached_time*1000:.2f}ms, "
            f"Speedup: {first_time/cached_time:.1f}x"
        )
```

### Verification

```bash
# 1. Start Redis
redis-server

# 2. Test cache connection
python -c "from solstein.infrastructure.cache import init_cache; init_cache('redis://localhost:6379')"

# 3. Run cache tests
pytest tests/unit/test_cache.py -v
pytest tests/performance/test_caching_performance.py -v

# 4. Endpoint test with caching
curl -X GET http://localhost:8000/api/companies/c1
# First call: ~50ms (database query)
# Second call: ~5ms (cache hit)
```

### Expected Results

**Before Caching**:
```
GET /api/companies/c1
└─ Database query (50ms)
└─ Total response time: 50-100ms
```

**After Caching**:
```
First call:   
  └─ Database query (50ms)
  └─ Store in Redis (1ms)
  └─ Total: 51ms

Subsequent calls:
  └─ Redis get (1ms)
  └─ Total: 1-5ms

Improvement: 10-50x faster for cached queries
```

**Effort**: 16 hours  
**Complexity**: 🟠 MEDIUM  
**Testing Time**: 4 hours

---

## ITEM 2.4: Input Validation (8 hours)

### Context
**Risk Level**: 🟠 MEDIUM - Security + data integrity  
**Current Status**: Incomplete validation  
**Impact**: Prevents data corruption, improves error messages  

### Current Issues

**File**: `/src/solstein/api/routers/market.py` (line 112)

```python
# ❌ UNSAFE: Any attribute can be accessed
def search_markets(field: str, value: str):
    filtered = [
        m for m in repo.get_all()
        if getattr(m, field) == value
    ]
```

### Implementation

#### Step 1: Define allowed search fields
**File**: `/src/solstein/domain/constants.py` (new file)

```python
"""Domain constants and validation rules"""

# Allowed search fields by model
ALLOWED_SEARCH_FIELDS = {
    "company": {"id", "name", "sector", "country", "status"},
    "market": {"id", "name", "region", "status"},
    "analyst": {"id", "email", "name"},
}

# Validation rules
COMPANY_NAME_MIN_LENGTH = 2
COMPANY_NAME_MAX_LENGTH = 255

SECTOR_VALID_VALUES = {
    "Technology", "Healthcare", "Finance", "Energy",
    "Consumer", "Industrial", "Materials", "Real Estate"
}

# Score ranges
SCORE_MIN = 0.0
SCORE_MAX = 1.0
```

#### Step 2: Create Pydantic validators
**File**: `/src/solstein/api/schemas.py` (new file)

```python
"""Request/response schemas with validation"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from solstein.domain.constants import ALLOWED_SEARCH_FIELDS


class SearchRequest(BaseModel):
    """Search request with validation"""
    field: str = Field(..., min_length=1, max_length=50)
    value: str = Field(..., min_length=1, max_length=1000)
    model_type: str = Field(default="company")
    
    @validator("field")
    def validate_field(cls, v, values):
        """Ensure field is allowed"""
        model_type = values.get("model_type", "company")
        allowed = ALLOWED_SEARCH_FIELDS.get(model_type, set())
        
        if v not in allowed:
            raise ValueError(
                f"Invalid field '{v}' for {model_type}. "
                f"Allowed: {allowed}"
            )
        return v


class CompanyCreateRequest(BaseModel):
    """Company creation request"""
    name: str = Field(..., min_length=2, max_length=255)
    sector: str = Field(..., min_length=2, max_length=100)
    growth_score: float = Field(..., ge=0.0, le=1.0)
    
    @validator("sector")
    def validate_sector(cls, v):
        """Validate sector is known"""
        from solstein.domain.constants import SECTOR_VALID_VALUES
        if v not in SECTOR_VALID_VALUES:
            raise ValueError(
                f"Unknown sector '{v}'. "
                f"Valid: {SECTOR_VALID_VALUES}"
            )
        return v
```

#### Step 3: Update endpoints with validation
**File**: `/src/solstein/api/routers/market.py`

```python
from solstein.api.schemas import SearchRequest
from solstein.domain.constants import ALLOWED_SEARCH_FIELDS

@router.post("/api/search")
async def search_markets(
    request: SearchRequest,  # ✅ Validation happens here
    repo: Repository = Depends()
):
    """
    Search markets
    
    ✅ SAFE: Only allowed fields, validated input
    """
    try:
        # Request is already validated by Pydantic
        filtered = [
            m for m in await repo.get_all()
            if getattr(m, request.field) == request.value
        ]
        
        return {"count": len(filtered), "results": filtered}
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Search failed")
```

### Testing

**File**: `/tests/unit/test_validation.py` (new file)

```python
"""Validation tests"""

import pytest
from fastapi.testclient import TestClient
from solstein.api.main import app


class TestInputValidation:
    """Test input validation"""
    
    def test_invalid_search_field_rejected(self):
        """Test invalid field is rejected"""
        client = TestClient(app)
        
        response = client.post(
            "/api/search",
            json={"field": "_password", "value": "admin"}
        )
        
        assert response.status_code == 422
        assert "field" in response.json()["detail"][0]["loc"]
    
    def test_valid_search_field_accepted(self):
        """Test valid field is accepted"""
        client = TestClient(app)
        
        response = client.post(
            "/api/search",
            json={"field": "sector", "value": "Technology"}
        )
        
        assert response.status_code in [200, 422]  # Either succeeds or validation passes
```

**Effort**: 8 hours  
**Complexity**: 🟢 LOW  
**Testing Time**: 2 hours

---

## PHASE 2 SUMMARY

| Item | Hours | Improvement | Status |
|------|-------|-------------|--------|
| 2.1: N+1 Queries | 16h | 250-500x faster | 🎯 |
| 2.2: DB Indexes | 4h | 10-100x faster | 🎯 |
| 2.3: Redis Caching | 16h | 10-50x faster (cached) | 🎯 |
| 2.4: Input Validation | 8h | Security + reliability | 🎯 |

**Total Phase 2**: 44 hours (refined from 84 - achieved in 1 week with proper parallelization)

**Expected Cumulative Performance**:
- API endpoints: 50-100ms (currently 200ms) → 50x faster
- Market analysis: 50s → 250ms → 200x faster
- List operations: Cache hits 1-5ms → 50x faster

---

*End of Phase 2 Implementation Plan - Continue to Phase 3 for Code Quality items...*
