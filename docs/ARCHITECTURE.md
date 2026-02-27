# Solstein Architecture Documentation

## System Overview

Solstein is an AI-powered competitive intelligence platform designed for PE/VC professionals. It analyzes market data, company financials, competitive positioning, and generates strategic insights.

## Architecture Principles

1. **Database-First**: All data stored in PostgreSQL with proper constraints
2. **Async-First**: All I/O operations use async/await pattern
3. **Repository Pattern**: Unified repository layer for data access
4. **Type Safety**: Full type hints throughout codebase
5. **Test Coverage**: Comprehensive test suite for reliability

## System Components

### 1. Database Layer

**PostgreSQL 14+** with the following characteristics:

- **21 Tables** organized by domain
- **40+ Indexes** for query optimization
- **20+ Foreign Keys** for referential integrity
- **50+ Constraints** for data quality
- **ACID Compliance** for transaction safety

#### Table Categories

**Core Entities** (001-006 migrations):
- `companies` - Company profiles
- `research_runs` - Research execution tracking
- `facts` - Extracted factual data
- `signals` - Detected market signals
- `contradictions` - Fact contradictions
- `source_document_snapshots` - Source documentation

**Scoring & Analysis** (007 migration):
- `scoring_records` - Company scoring data
- `signal_records` - Signal generation records

**Enrichment** (008 migration):
- `company_enrichment_queue` - Pending enrichments
- `enrichment_results` - Enrichment outcomes
- `enrichment_cache` - Cached enrichment data
- `enrichment_audit` - Enrichment audit trail

**Monitoring** (009-010 migrations):
- `market_snapshots` - Market data snapshots
- `audit_trails` - Audit logging
- `outbox_records` - Event outbox

### 2. Repository Layer

**Unified Async Repository Pattern**

All repositories follow the same async pattern:

```python
class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: str) -> Optional[CompanyRecord]:
        result = await self.session.execute(
            select(CompanyRecord).where(CompanyRecord.id == id)
        )
        return result.scalar_one_or_none()
```

**Key Repositories**:

- `CompanyRepository` - Company CRUD operations
- `FactRepository` - Fact management with confidence tracking
- `SignalRepository` - Signal detection and tracking
- `ScoringRepository` - Score calculation storage

### 3. Service Layer

**Business Logic Services**:

- `DrillDownService` - Data drill-down operations
- `EnrichmentService` - Data enrichment processing
- `ScoringService` - Company scoring algorithms
- `SignalService` - Signal detection and analysis

All services accept `AsyncSession` instead of `DatabaseManager`:

```python
class DrillDownService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.company_repo = CompanyRepository(session)
```

### 4. API Layer

**FastAPI Application**:

- RESTful endpoints for all resources
- Async request handling
- Pydantic models for validation
- Automatic API documentation

**Endpoint Categories**:

- `/companies` - Company management
- `/research-runs` - Research execution
- `/facts` - Fact extraction
- `/signals` - Signal detection
- `/health` - Health checks

### 5. Infrastructure Layer

**Database Manager**:

```python
class DatabaseManager:
    """Manages async database connections."""
    
    async def get_session(self) -> AsyncSession:
        """Get database session."""
        async with self.session_factory() as session:
            yield session
```

**Connection Pooling**:
- Pool size: 5 connections
- Max overflow: 10 connections
- Connection timeout: 30 seconds

## Data Flow

### Research Execution Flow

```
1. Client → POST /research-runs
2. API → Create ResearchRunRecord
3. Service → Execute research workflow
4. Workers → Store facts in facts table
5. Workers → Store signals in signals table
6. API → Return run status
```

### Data Enrichment Flow

```
1. Schedule → Add to enrichment_queue
2. Worker → Process enrichment job
3. Worker → Store result in enrichment_results
4. Worker → Update cache in enrichment_cache
5. Worker → Log to enrichment_audit
```

### Signal Detection Flow

```
1. Fact created → Trigger signal analysis
2. SignalService → Analyze patterns
3. SignalRepository → Store signals
4. Outbox → Publish signal event
5. Clients → Receive notifications
```

## Design Patterns

### Repository Pattern

All data access goes through repositories:

```python
# Good
company = await company_repo.get_by_id(company_id)

# Avoid
result = await session.execute(
    select(CompanyRecord).where(...)
)
```

### Unit of Work

Transactions managed at service level:

```python
async with session.begin():
    company = await company_repo.create(...)
    fact = await fact_repo.create(company_id=company.id, ...)
    # Both committed together or rolled back
```

### Dependency Injection

Services receive dependencies via constructor:

```python
def __init__(self, session: AsyncSession):
    self.session = session
    self.company_repo = CompanyRepository(session)
```

## Performance Optimizations

### Database Optimizations

1. **Composite Indexes** for common query patterns
2. **Partial Indexes** for filtered queries
3. **Covering Indexes** for join operations
4. **Connection Pooling** for concurrent access

### Query Optimizations

1. **Eager Loading** for related data
2. **Pagination** for large result sets
3. **Batch Operations** for bulk inserts
4. **Async Operations** for I/O efficiency

### Caching Strategy

1. **Application Cache** for frequently accessed data
2. **Database Cache** for query results
3. **Enrichment Cache** for external data

## Security Considerations

1. **SQL Injection Prevention** - Parameterized queries only
2. **Connection Security** - SSL/TLS for database connections
3. **Input Validation** - Pydantic models for all inputs
4. **Audit Logging** - All changes logged to audit_trails

## Monitoring

1. **Performance Metrics** - Tracked via performance_baseline.py
2. **Database Metrics** - Query performance, connection usage
3. **Error Tracking** - Exception logging and alerting
4. **Audit Trails** - All data changes logged

## Testing Strategy

1. **Unit Tests** - Business logic isolation
2. **Integration Tests** - Database interactions
3. **API Tests** - Endpoint verification
4. **Performance Tests** - Load and stress testing
5. **Migration Tests** - Data integrity verification

## Deployment Architecture

### Production Setup

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  FastAPI    │────▶│ PostgreSQL  │
│             │     │   Server    │     │  Primary    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Workers   │
                    │  (Temporal) │
                    └─────────────┘
```

### Scaling Considerations

1. **Read Replicas** for query scaling
2. **Connection Pooling** for concurrent access
3. **Caching Layer** for frequently accessed data
4. **Worker Scaling** for background processing

## Migration from JSON to PostgreSQL

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed migration instructions.

## Future Enhancements

1. **Read Replicas** for scaling reads
2. **Redis Cache** for hot data
3. **GraphQL API** for flexible queries
4. **Real-time Subscriptions** via WebSockets
5. **Machine Learning** for signal prediction

---

**Last Updated**: 2024
**Version**: 2.0 (PostgreSQL Migration)
