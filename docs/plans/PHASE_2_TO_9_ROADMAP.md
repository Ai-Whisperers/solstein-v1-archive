# Solstein Implementation Roadmap: Phases 2-9

**Status**: Phase 1 ✅ COMPLETE | Phases 2-9 ⏳ IN PLANNING  
**Last Updated**: 2026-02-20  
**Total Effort**: ~80 hours remaining

---

## Quick Reference: Progress Summary

| Phase | Title | Status | Effort | Priority |
|-------|-------|--------|--------|----------|
| 1 | Resilience Layer (Retry + Circuit Breaker) | ✅ COMPLETE | 8h | HIGH |
| 2 | Scoring Refactor (Split god class) | 🔄 IN PROGRESS | 12h | HIGH |
| 3 | Configuration Validation | ⏳ PENDING | 4h | HIGH |
| 4 | Database Persistence (PostgreSQL) | ⏳ PENDING | 6h | HIGH |
| 5 | Signal Extraction (50+ rules) | ⏳ PENDING | 8h | MEDIUM |
| 6 | Monitoring + Alerting | ⏳ PENDING | 6h | MEDIUM |
| 7 | Additional Agents (LinkedIn, SEC, Patents) | ⏳ PENDING | 20h | MEDIUM |
| 8 | Integration Tests | ⏳ PENDING | 10h | MEDIUM |
| 9 | Production Hardening | ⏳ PENDING | 6h | MEDIUM |

---

## PHASE 2: Scoring Refactor (12 hours)

### Objective
Split the 614-line `GrowthScorer` god class into 3 focused, independently testable scorer classes with 80%+ test coverage.

### Current State
- **File**: `src/solstein/analytics/scoring.py` (613 lines)
- **Main class**: `GrowthScorer` with 3 scoring methods mixed with market analysis
- **Coverage**: 11% (only 3 signals extracted)
- **Debt**: Tightly coupled logic, hard to test, difficult to extend

### Target State
- 3 focused scorer classes (~90, ~80, ~120 lines each)
- 60+ unit tests with 80%+ coverage
- Clean composition in main `GrowthScorer`
- No API changes for external callers

### Implementation Steps

#### Step 2.1: Create FinancialHealthScorer (3 hours)
**File**: `src/solstein/analytics/scorers/financial_health.py`

```python
class FinancialHealthScorer:
    def __init__(self, config: ScoringSettings | None = None):
        self.config = config or ScoringSettings()
    
    def score(self, financials: FinancialMetric) -> tuple[float, ScoringExplanation]:
        """Score financial health (0-10)."""
        # Extract from original _calculate_financial_health_score (lines 158-244)
        # Components:
        # - Revenue scale (large, medium, small thresholds)
        # - Profitability (margins, penalties for negative)
        # - Employee efficiency (revenue per employee)
        # - Funding cushion (funding/revenue ratio)
```

**Tests** (`tests/unit/test_scorers_financial.py`):
- Happy path: all fields present
- Partial data: missing fields (None checks)
- Edge cases: zero employees, negative margins
- Score capping: ensure 0-10 bounds
- Explanation: verify components populated
- Thresholds: test all boundary conditions

**Checklist**:
- [ ] Extract method logic from lines 158-244
- [ ] Write 20+ unit tests
- [ ] Achieve 90%+ coverage of scorer
- [ ] Verify score range [0, 10]
- [ ] Add docstrings

#### Step 2.2: Create CompetitivePositionScorer (3 hours)
**File**: `src/solstein/analytics/scorers/competitive_position.py`

```python
class CompetitivePositionScorer:
    def score(self, profile: Company) -> tuple[float, ScoringExplanation]:
        """Score competitive position (0-10)."""
        # Extract from original _calculate_competitive_position_score (lines 246-315)
        # Components:
        # - Market tier positioning
        # - AI maturity score
        # - SaaS transformation index
        # - Geographic presence (global vs regional)
        # - Tech stack diversity
```

**Tests** (`tests/unit/test_scorers_competitive.py`):
- Market tier scoring
- AI maturity mapping
- Geographic thresholds
- Tech stack diversity
- Edge cases (empty lists, None values)

**Checklist**:
- [ ] Extract method logic from lines 246-315
- [ ] Require `profile: Company` instead of `financials`
- [ ] Write 20+ unit tests
- [ ] Achieve 90%+ coverage
- [ ] Add docstrings

#### Step 2.3: Refactor GrowthScorer to Compose Three Scorers (3 hours)
**File**: `src/solstein/analytics/scoring.py` (refactor lines 39-78)

```python
class GrowthScorer:
    def __init__(self, config: ScoringSettings | None = None):
        self.config = config or ScoringSettings()
        self.growth_scorer = GrowthMomentumScorer(config)
        self.financial_scorer = FinancialHealthScorer(config)
        self.competitive_scorer = CompetitivePositionScorer(config)
    
    def calculate_scores(self, profile: Company) -> Company:
        """Calculate all scores using composed scorers."""
        # Call three scorers
        growth_score, growth_expl = self.growth_scorer.score(profile.financials)
        financial_score, financial_expl = self.financial_scorer.score(profile.financials)
        competitive_score, competitive_expl = self.competitive_scorer.score(profile)
        
        # Update profile (unchanged API)
        profile.growth_score = growth_score
        profile.financial_health_score = financial_score
        profile.competitive_position_score = competitive_score
        
        # Composite: 40% growth, 30% financial, 30% competitive (unchanged)
        # ...rest unchanged
        return profile
```

**Checklist**:
- [ ] Create imports for three scorers
- [ ] Instantiate scorers in `__init__`
- [ ] Replace method calls with scorer calls
- [ ] Verify all tests still pass (280+)
- [ ] No API changes for external callers

#### Step 2.4: Write Integration Tests (3 hours)
**File**: `tests/unit/test_growth_scorer_integrated.py`

```python
def test_scores_composite_correctly():
    """Test that composite score is weighted correctly."""
    profile = Company(...)
    scorer = GrowthScorer()
    
    result = scorer.calculate_scores(profile)
    
    expected = (result.growth_score * 0.4 +
                result.financial_health_score * 0.3 +
                result.competitive_position_score * 0.3)
    assert pytest.approx(result.composite_score) == expected

def test_classification_correct():
    """Test company classification based on scores."""
    # Rocket: score >= 7.0
    # Dinosaur: score <= 4.0
    # Neutral: 4.0 < score < 7.0
```

### Success Criteria
- ✅ 60+ new scorer tests added (20 per scorer, 20 integration)
- ✅ All 280+ existing tests still pass
- ✅ Coverage: 11% → 80%+ for scorers
- ✅ Each scorer < 100 lines (excluding docstrings)
- ✅ No changes to external API
- ✅ GrowthScorer maintains exact same behavior

---

## PHASE 3: Configuration Validation (4 hours)

### Objective
Add startup validation to fail loudly if required API keys are missing.

### Implementation

**File**: `src/solstein/config.py` - Add validation method

```python
class ScoringSettings:
    def validate(self) -> None:
        """Validate all required configuration at startup."""
        if not self.github_token:
            raise ConfigurationError(
                "GITHUB_TOKEN required but not found. "
                "Set environment variable GITHUB_TOKEN."
            )
        if not self.companies_house_api_key:
            raise ConfigurationError("COMPANIES_HOUSE_API_KEY required")
        if not self.google_api_key:
            logger.warning("GOOGLE_API_KEY not configured, web search disabled")
```

**File**: `src/solstein/api/main.py` - Call on startup

```python
@app.on_event("startup")
async def startup():
    try:
        config = ScoringSettings()
        config.validate()
        logger.info("Configuration validated successfully")
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        raise
```

**Tests**: `tests/unit/test_config_validation.py`
- Missing required keys raises error
- All keys present passes
- Partial keys logs warnings
- Error message is helpful

**Effort**: 4 hours
**Success Criteria**:
- ✅ Startup fails visibly if GitHub token missing
- ✅ Helpful error messages
- ✅ 10+ validation tests
- ✅ API doesn't start with broken config

---

## PHASE 4: Database Persistence (6 hours)

### Objective
Replace in-memory drill-down service with PostgreSQL persistence for audit trails.

### Current State
- `src/solstein/api/services/drill_down_service.py` uses in-memory dict
- No persistence between restarts
- No audit trail for analysis changes

### Target State
- PostgreSQL with SQLAlchemy ORM
- Audit trail of all scoring decisions
- Historical comparisons possible
- Scalable to multiple instances

### Implementation

**File**: `src/solstein/core/database.py` (NEW)

```python
from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ScoringRecord(Base):
    __tablename__ = "scoring_records"
    
    id = Column(String, primary_key=True)
    company_id = Column(String, index=True)
    growth_score = Column(Float)
    financial_score = Column(Float)
    competitive_score = Column(Float)
    composite_score = Column(Float)
    classification = Column(String)
    scoring_breakdown = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

def get_session():
    engine = create_engine(os.getenv("DATABASE_URL"))
    return sessionmaker(bind=engine)()
```

**Alembic Migration**: `alembic/versions/001_create_scoring_table.py`

```python
def upgrade():
    op.create_table('scoring_records',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        # ... other columns
    )
    op.create_index('ix_scoring_records_company_id', 'scoring_records', ['company_id'])

def downgrade():
    op.drop_table('scoring_records')
```

**Update Service**: `src/solstein/api/services/drill_down_service.py`

```python
class DrillDownService:
    def __init__(self):
        self.session = get_session()
    
    def save_scoring(self, record: ScoringRecord) -> None:
        self.session.add(record)
        self.session.commit()
    
    def get_scoring_history(self, company_id: str) -> list[ScoringRecord]:
        return self.session.query(ScoringRecord).filter(
            ScoringRecord.company_id == company_id
        ).order_by(ScoringRecord.created_at.desc()).all()
```

**Tests**: `tests/unit/test_database_persistence.py`
- Save and retrieve scoring
- History queries work
- Timestamps correct
- Migration works

**Effort**: 6 hours
**Success Criteria**:
- ✅ PostgreSQL schema created
- ✅ Alembic migrations working
- ✅ Scoring records persisted
- ✅ 10+ database tests
- ✅ No data loss on restart

---

## PHASE 5: Signal Extraction (8 hours)

### Objective
Implement 50+ signals across all agents (currently only 3).

### Current State
Only 3 signals extracted:
1. GitHub: tech_stack, engineering_velocity, contributor_count
2. Companies House: company_name, headquarters, company_status
3. Web Search: funding_news_signal, hiring_news_signal, product_innovation_signal

### Target: 50+ Signals

**GitHub Agent** (10 signals):
- tech_stack ✓
- engineering_velocity ✓
- contributor_count ✓
- repo_count (number of public repos)
- average_commit_frequency (commits/week)
- ai_ml_adoption (has Python/Rust repos)
- open_source_engagement (stars/forks ratio)
- code_quality_signal (activity consistency)
- microservices_adoption (mono vs poly-repo)
- containerization_signal (Docker presence)

**Companies House Agent** (8 signals):
- company_name ✓
- headquarters ✓
- company_status ✓
- incorporation_date
- employee_count_signal
- annual_revenue_trend
- profit_margin_trend
- funding_rounds_count

**Web Search Agent** (12 signals):
- funding_news_signal ✓
- hiring_news_signal ✓
- product_innovation_signal ✓
- acquisition_signal (M&A news)
- leadership_changes_signal
- market_expansion_signal
- partnership_announcements
- award_recognition_signal
- patent_filing_signal
- regulatory_news_signal
- competitive_positioning
- brand_sentiment

**Additional Future Agents** (20+ signals):
LinkedIn, SEC EDGAR, Patents, News API, Jobs API, Tech Trends, Website

### Implementation Pattern

```python
class SignalExtractor:
    def extract_signals(self, data: dict) -> list[Signal]:
        """Extract 10+ signals from raw data."""
        signals = []
        
        if self._has_ai_languages(data):
            signals.append(Signal(
                name="ai_ml_adoption",
                value=0.8,
                evidence=["Python repo", "Pytorch dependency"],
                confidence=0.85
            ))
        
        # ... 9 more signals
        return signals

# Use in agents
signals = extractor.extract_signals(raw_github_data)
for signal in signals:
    fact = create_fact(
        fact_type=signal.name,
        value=signal.value,
        confidence=signal.confidence,
        sources_used=signal.evidence
    )
    result.extracted_facts.append(fact)
```

### Files to Create/Modify
- `src/solstein/agents/signal_extractors.py` (NEW, 200+ lines)
- `src/solstein/agents/github_agent.py` (update: use extractor)
- `src/solstein/agents/companies_house_agent.py` (update: use extractor)
- `src/solstein/agents/web_search_agent.py` (update: use extractor)
- `tests/unit/test_signal_extraction.py` (30+ tests)

**Effort**: 8 hours
**Success Criteria**:
- ✅ 50+ signals defined
- ✅ All agents extract multiple signals
- ✅ Signals have evidence and confidence
- ✅ 30+ extraction tests

---

## PHASE 6: Monitoring + Alerting (6 hours)

### Objective
Add data quality monitoring and health checks for PE analysts.

### Monitoring Endpoints

**Health Check**: `GET /health/status`
```json
{
  "status": "healthy",
  "timestamp": "2026-02-20T22:00:00Z",
  "agents": {
    "github": {"status": "ok", "last_run": "2026-02-20T21:45:00Z"},
    "companies_house": {"status": "degraded", "last_error": "401 Unauthorized"},
    "web_search": {"status": "ok"}
  },
  "database": {"status": "ok"},
  "cache": {"status": "ok"}
}
```

**Data Quality**: `GET /monitoring/data-quality`
```json
{
  "companies_analyzed": 150,
  "avg_signals_per_company": 8.5,
  "avg_confidence": 0.82,
  "coverage": {
    "financial_data": 92,
    "tech_signals": 87,
    "market_signals": 76
  },
  "alerts": [
    {"level": "warning", "message": "Web search API rate limited"}
  ]
}
```

**API Metrics**: `GET /monitoring/metrics`
- Request latency (p50, p95, p99)
- Error rates by agent
- Retry success rates
- Circuit breaker states

### Implementation Files
- `src/solstein/api/routers/monitoring.py` (NEW, 100 lines)
- `src/solstein/core/metrics.py` (NEW, 80 lines)
- `src/solstein/core/health_checker.py` (NEW, 60 lines)
- `tests/unit/test_monitoring.py` (20+ tests)

**Effort**: 6 hours
**Success Criteria**:
- ✅ Health endpoint returns accurate status
- ✅ Data quality metrics tracked
- ✅ Alerts for degraded services
- ✅ Metrics exportable for PE analysts

---

## PHASE 7: Additional Agents (20 hours)

### Agent 1: LinkedIn Agent (3 hours)
**Signals**: Hiring trends, employee growth, skills mentioned, leadership

**Implementation**:
```python
class LinkedInAgent(BaseDataGatheringAgent):
    def _extract_company_page(self) -> dict:
        """Scrape or API call to LinkedIn company profile"""
    
    def _extract_job_postings(self) -> list[dict]:
        """Count and analyze active job openings"""
    
    def _extract_signals(self) -> list:
        # hiring_velocity, team_growth, skill_gaps, retention
```

### Agent 2: SEC EDGAR Agent (4 hours)
**Signals**: Revenue trend, profitability, growth rate, R&D investment, debt levels

```python
class SECEdgarAgent(BaseDataGatheringAgent):
    def _search_company_ticker(self, name: str) -> str:
        """Find SEC CIK number"""
    
    def _fetch_10k_filings(self) -> list[dict]:
        """Get latest 10-K and 10-Q filings"""
    
    def _parse_financial_data(self) -> FinancialMetric:
        # Extract revenue, net income, R&D spending
```

### Agent 3: Patents Agent (3 hours)
**Signals**: Innovation rate, IP portfolio strength, tech leadership

```python
class PatentsAgent(BaseDataGatheringAgent):
    def _search_patents(self, company: str) -> list[dict]:
        """Search Google Patents or USPTO"""
    
    def _extract_signals(self) -> list:
        # patent_velocity, technology_domains, citation_count
```

### Agents 4-7: News, Jobs, Tech Trends, Website (10 hours)
Similar structure as above

**Total Signals Added**: 50+ (across all new agents)
**Effort**: 20 hours
**Success Criteria**:
- ✅ 7 new agents implemented
- ✅ All agents follow base class pattern
- ✅ Resilience layer integrated
- ✅ 50+ new signals extracted
- ✅ Unit tests for each agent

---

## PHASE 8: Integration Tests (10 hours)

### Test Scenarios

**Retry Scenarios**: `tests/integration/test_agent_retries.py`
```python
def test_github_retries_on_rate_limit():
    """Verify GitHub agent retries after 429"""
    
def test_circuit_breaker_opens_after_threshold():
    """Verify circuit breaker prevents cascading failures"""

def test_exponential_backoff_timing():
    """Verify backoff delays increase correctly"""
```

**Data Completeness**: `tests/integration/test_data_quality.py`
```python
def test_all_agents_return_facts():
    """Verify all agents extract at least some facts"""

def test_scoring_handles_partial_data():
    """Verify scoring works with missing agent data"""
```

**End-to-End**: `tests/integration/test_e2e_workflow.py`
```python
async def test_full_company_analysis():
    """Run analysis on test company, verify all components work"""
    # 1. Gather data from all agents
    # 2. Extract signals
    # 3. Calculate scores
    # 4. Generate explanations
    # 5. Export results
```

**Performance**: `tests/integration/test_performance.py`
```python
def test_single_company_analysis_under_10s():
    """Ensure analysis completes in reasonable time"""

def test_market_analysis_100_companies_under_60s():
    """Batch analysis must be fast"""
```

**Effort**: 10 hours
**Success Criteria**:
- ✅ 40+ integration tests
- ✅ All retry scenarios tested
- ✅ Performance benchmarks met
- ✅ Data quality verified

---

## PHASE 9: Production Hardening (6 hours)

### Graceful Degradation
```python
# If GitHub fails, continue with other agents
# If database unavailable, cache in memory
# If scoring fails, use last cached score
```

**Implementation**:
- `src/solstein/core/failover.py` (NEW, 100 lines)
- Circuit breaker state checking in critical paths
- Fallback scoring algorithms
- Memory cache with TTL

### Health Check Endpoints
- `/health/live` - Is service running?
- `/health/ready` - Is service ready to serve?
- `/health/startup` - Has startup completed?

### Graceful Shutdown
- Drain in-flight requests
- Flush database writes
- Log shutdown reason

### Performance Optimization
- Cache frequently accessed companies
- Batch similar API calls
- Index database queries
- Profile and optimize bottlenecks

**Files**:
- `src/solstein/core/failover.py` (100 lines)
- `src/solstein/core/cache.py` (80 lines)
- Update `src/solstein/api/main.py` with lifecycle hooks
- `tests/unit/test_failover.py` (20+ tests)

**Effort**: 6 hours
**Success Criteria**:
- ✅ Service continues on partial failures
- ✅ Graceful shutdown implemented
- ✅ Performance acceptable under load
- ✅ 20+ hardening tests

---

## Execution Strategy

### Recommended Order
1. **Phase 2** (Scoring) - Foundation for all scoring
2. **Phase 3** (Config) - Must pass before Phase 4
3. **Phase 4** (Database) - Required for persistence
4. **Phase 5** (Signals) - Increases data quality
5. **Phases 6-9** - Parallel optimization phases

### Dependencies Graph
```
Phase 1 ✓
  ↓
Phase 2 (Scoring)
  ↓
Phase 3 (Config) → Phase 4 (Database)
  ↓
Phase 5 (Signals) + Phase 6 (Monitoring)
  ↓
Phase 7 (New Agents)
  ↓
Phase 8 (Integration Tests)
  ↓
Phase 9 (Production Hardening)
```

### Quick-Win Tasks (1-2 hours each)
- Add health endpoint (Phase 6)
- Add logging decorator (Phase 6)
- Implement caching (Phase 9)
- Add API response validation (Phase 3)

### Critical Path (must complete)
1. Phase 2 (Scoring refactor)
2. Phase 3 (Config validation)
3. Phase 4 (Database)
4. Phase 8 (Integration tests)

### Nice-to-Have (can defer)
- Phase 7 (New agents beyond 3)
- Complex Phase 9 optimizations
- Advanced monitoring dashboards

---

## Testing Strategy

**Test Coverage Target**: 80%+ overall
- Unit tests: 60%
- Integration tests: 20%
- E2E tests: 10%

**Test Execution**:
```bash
# Phase 2: Scoring tests
pytest tests/unit/test_scorers_*.py -v --cov

# Phase 3: Config tests
pytest tests/unit/test_config_validation.py -v

# Phase 4: Database tests
pytest tests/unit/test_database_persistence.py -v

# Phase 5: Signal extraction tests
pytest tests/unit/test_signal_extraction.py -v

# Full suite with coverage
pytest tests/ -v --cov=src/solstein
```

---

## Estimated Timeline

| Phase | Effort | Team | Timeline |
|-------|--------|------|----------|
| 1 | 8h | 1 | ✅ DONE |
| 2 | 12h | 1-2 | 3-4 days |
| 3 | 4h | 1 | 1 day |
| 4 | 6h | 1 | 1.5 days |
| 5 | 8h | 2 | 2 days |
| 6 | 6h | 1 | 1.5 days |
| 7 | 20h | 2 | 5 days |
| 8 | 10h | 2 | 2-3 days |
| 9 | 6h | 1 | 1.5 days |
| **TOTAL** | **80h** | **2-3 team** | **~3 weeks** |

---

## Success Metrics

### Code Quality
- [ ] Test coverage 80%+
- [ ] All 300+ tests passing
- [ ] Zero type errors
- [ ] Zero security warnings
- [ ] <5 lines per method average

### Functionality
- [ ] All 50+ signals extracted
- [ ] Scoring works with partial data
- [ ] Agents retry on failures
- [ ] Circuit breaker prevents cascades
- [ ] Graceful degradation works

### Performance
- [ ] Single company analysis: <10s
- [ ] Market analysis (100 cos): <60s
- [ ] API response: <500ms p95
- [ ] Database queries: <100ms

### Operations
- [ ] Startup validation enforced
- [ ] Health checks passing
- [ ] Monitoring alerts working
- [ ] Database persisted
- [ ] Graceful shutdown complete

---

##Next Steps

1. **Review this plan** with team
2. **Prioritize phases** based on business needs
3. **Assign ownership** (2-3 engineers)
4. **Start Phase 2** (scoring refactor)
5. **Weekly syncs** to track progress

Questions? See `/claude/COMPREHENSIVE_DATA_GATHERING_FRAMEWORK.md` for context.
