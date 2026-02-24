# Solstein: Complete Implementation Plan
## From Broken to Production-Ready in 9 Phases

> **For Claude:** REQUIRED SUB-SKILL: Use `code-quality/subagent-driven-development` to implement this plan task-by-task.  
> **Plan Date**: February 20, 2026  
> **Scope**: All Tier 1-3 fixes + complete feature implementation  
> **Estimated Duration**: 40-50 hours (8-10 work days)

---

## 🎯 GOAL

Transform Solstein from "beautiful documentation, broken implementation" to "production-ready system with functioning agents, tested scoring logic, and proper error handling."

---

## 📋 IMPLEMENTATION PHASES

### PHASE 0: Foundation Setup (Already Complete ✅)
- [x] Fixed empty exception handlers
- [x] Fixed agent success logic
- [x] Removed temporalio dependency
- [x] Fixed critical imports
- **Status**: Ready for Phase 1

---

## PHASE 1: Retry Logic + Circuit Breaker (CRITICAL)

### Goal
Implement resilient API calling pattern so agents handle rate limits, timeouts, and transient failures gracefully.

### Files
- Create: `src/solstein/agents/resilience.py` (retry + circuit breaker)
- Create: `tests/unit/test_resilience.py` (comprehensive tests)
- Modify: `src/solstein/agents/github_agent.py` (use resilience layer)
- Modify: `src/solstein/agents/companies_house_agent.py` (use resilience layer)
- Modify: `src/solstein/agents/web_search_agent.py` (use resilience layer)
- Modify: `tests/test_agents/test_single_company.py` (test retry scenarios)

### Architecture

```python
# Resilience pattern:
# 1. Exponential backoff: 1s, 2s, 4s, 8s, 16s (max 5 retries)
# 2. Circuit breaker: After 5 failures, stop trying for 60s
# 3. Fallback: Return partial results instead of zero results
# 4. Logging: Every retry attempt logged with context
```

### TASK 1.1: Create RetryConfig and ExponentialBackoff

**Files to create:**
- `src/solstein/agents/resilience.py`

**Test file:**
- `tests/unit/test_resilience.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_resilience.py
import pytest
from solstein.agents.resilience import ExponentialBackoff, RetryConfig

def test_exponential_backoff_calculates_delays():
    config = RetryConfig(max_attempts=5, base_delay=1.0, max_delay=30.0)
    backoff = ExponentialBackoff(config)
    
    delays = [backoff.get_delay(attempt) for attempt in range(5)]
    
    # Should be approximately: 1, 2, 4, 8, 16
    assert delays[0] == pytest.approx(1.0, abs=0.1)
    assert delays[1] == pytest.approx(2.0, abs=0.1)
    assert delays[2] == pytest.approx(4.0, abs=0.1)
    assert delays[3] == pytest.approx(8.0, abs=0.1)
    assert delays[4] == pytest.approx(16.0, abs=0.1)

def test_exponential_backoff_respects_max_delay():
    config = RetryConfig(max_attempts=10, base_delay=1.0, max_delay=10.0)
    backoff = ExponentialBackoff(config)
    
    # After max_delay is reached, it should stay at max_delay
    for attempt in range(5, 10):
        assert backoff.get_delay(attempt) <= 10.0

def test_retry_config_validation():
    # Should reject invalid configs
    with pytest.raises(ValueError):
        RetryConfig(max_attempts=0)
    
    with pytest.raises(ValueError):
        RetryConfig(base_delay=-1)
```

**Step 2: Run test to verify it fails**

```bash
cd /home/ai-whisperers/solstein
source .venv/bin/activate
pytest tests/unit/test_resilience.py::test_exponential_backoff_calculates_delays -v
```

**Expected output**: `FAILED - ModuleNotFoundError: No module named 'solstein.agents.resilience'`

**Step 3: Implement RetryConfig and ExponentialBackoff**

```python
# src/solstein/agents/resilience.py
"""
Resilience patterns for API calls: retry, circuit breaker, fallback.
"""

import asyncio
from dataclasses import dataclass
from typing import Optional
from loguru import logger


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    
    max_attempts: int = 5  # Number of retry attempts
    base_delay: float = 1.0  # Initial delay in seconds
    max_delay: float = 30.0  # Maximum delay in seconds
    exponential_base: float = 2.0  # Exponential backoff multiplier
    jitter: bool = True  # Add randomness to prevent thundering herd
    
    def __post_init__(self):
        """Validate configuration."""
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.base_delay < 0:
            raise ValueError("base_delay must be >= 0")
        if self.max_delay < self.base_delay:
            raise ValueError("max_delay must be >= base_delay")


class ExponentialBackoff:
    """Calculates exponential backoff with optional jitter."""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number (0-indexed).
        
        Formula: min(base_delay * (exponential_base ** attempt), max_delay)
        """
        delay = self.config.base_delay * (
            self.config.exponential_base ** attempt
        )
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            import random
            # Add ±10% jitter to prevent thundering herd
            jitter_factor = 1 + random.uniform(-0.1, 0.1)
            delay *= jitter_factor
        
        return delay


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern."""
    
    failure_threshold: int = 5  # Failures before opening circuit
    success_threshold: int = 2  # Successes before closing circuit
    timeout: int = 60  # Seconds before attempting recovery
    half_open_max_calls: int = 1  # Max calls in half-open state


class CircuitBreaker:
    """
    Implements circuit breaker pattern: Open → HalfOpen → Closed.
    
    Prevents cascading failures by stopping calls when service is down.
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failures = 0
        self.successes = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open
    
    def record_success(self):
        """Record successful call."""
        self.failures = 0
        
        if self.state == "half_open":
            self.successes += 1
            if self.successes >= self.config.success_threshold:
                self.state = "closed"
                self.successes = 0
                logger.info("Circuit breaker: CLOSED (service recovered)")
    
    def record_failure(self):
        """Record failed call."""
        import time
        self.last_failure_time = time.time()
        self.failures += 1
        
        if self.failures >= self.config.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Circuit breaker: OPEN after {self.failures} failures"
            )
    
    def can_execute(self) -> bool:
        """Check if call can be attempted."""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            import time
            if time.time() - self.last_failure_time > self.config.timeout:
                self.state = "half_open"
                self.successes = 0
                logger.info("Circuit breaker: HALF_OPEN (attempting recovery)")
                return True
            return False
        
        if self.state == "half_open":
            return True
        
        return False


async def call_with_retry(
    func,
    *args,
    retry_config: Optional[RetryConfig] = None,
    circuit_breaker: Optional[CircuitBreaker] = None,
    **kwargs
):
    """
    Call function with retry logic and circuit breaker pattern.
    
    Args:
        func: Async function to call
        retry_config: Retry configuration (default sensible values)
        circuit_breaker: Circuit breaker instance (optional)
        *args, **kwargs: Arguments for func
    
    Returns:
        Result of func
    
    Raises:
        Exception: If all retries exhausted or circuit is open
    """
    if retry_config is None:
        retry_config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(retry_config.max_attempts):
        if circuit_breaker and not circuit_breaker.can_execute():
            logger.warning(f"Circuit breaker OPEN: {func.__name__}")
            raise RuntimeError(f"Circuit breaker open for {func.__name__}")
        
        try:
            result = await func(*args, **kwargs)
            if circuit_breaker:
                circuit_breaker.record_success()
            return result
        except Exception as e:
            last_exception = e
            
            if circuit_breaker:
                circuit_breaker.record_failure()
            
            if attempt < retry_config.max_attempts - 1:
                backoff = ExponentialBackoff(retry_config)
                delay = backoff.get_delay(attempt)
                logger.warning(
                    f"Attempt {attempt + 1}/{retry_config.max_attempts} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"All {retry_config.max_attempts} attempts failed: {e}"
                )
    
    if last_exception:
        raise last_exception


# Sensible defaults for different APIs
GITHUB_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    base_delay=1.0,
    max_delay=30.0,
)

COMPANIES_HOUSE_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=2.0,
    max_delay=20.0,
)

WEB_SEARCH_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=0.5,
    max_delay=10.0,
)
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_resilience.py -v
```

**Expected**: All tests PASS

**Step 5: Commit**

```bash
git add src/solstein/agents/resilience.py tests/unit/test_resilience.py
git commit -m "feat: add exponential backoff and circuit breaker for API resilience"
```

---

### TASK 1.2: Integrate Retry Logic Into GitHub Agent

**Files to modify:**
- `src/solstein/agents/github_agent.py`

**Step 1: Update GitHubAgent to use resilience layer**

```python
# Modify src/solstein/agents/github_agent.py

from ..agents.resilience import (
    call_with_retry, 
    GITHUB_RETRY_CONFIG, 
    CircuitBreaker, 
    CircuitBreakerConfig
)

class GitHubAgent(BaseDataGatheringAgent):
    def __init__(self, github_token: str | None = None):
        super().__init__("GitHubAgent", DataSourceType.GITHUB)
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.api_base = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Solstein-AI",
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
        
        # Add circuit breaker for GitHub API
        self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig())
    
    async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
        """Gather GitHub data with resilience patterns."""
        start_time = datetime.now(UTC)
        result = AgentTaskResult(
            agent_name=self.agent_name,
            source_type=self.source_type,
            success=False,
        )

        try:
            self.log_info(f"Starting GitHub research for {company_name}")

            github_org = context.get("known_github_org")
            if not github_org:
                # Use resilience layer for org search
                try:
                    github_org = await call_with_retry(
                        self._search_github_org_async,
                        company_name,
                        retry_config=GITHUB_RETRY_CONFIG,
                        circuit_breaker=self.circuit_breaker,
                    )
                except Exception as e:
                    self.log_warning(f"GitHub org search failed: {e}")
                    result.error_message = f"GitHub org search exhausted retries: {e}"
                    result.execution_time_seconds = (
                        datetime.now(UTC) - start_time
                    ).total_seconds()
                    return result

                if not github_org:
                    self.log_warning(f"No GitHub org found for {company_name}")
                    result.coverage_gaps.append("GitHub organization not found")
                    result.success = False
                    result.error_message = "No GitHub organization found"
                    result.execution_time_seconds = (
                        datetime.now(UTC) - start_time
                    ).total_seconds()
                    return result

            # Use resilience layer for repo fetching
            try:
                repos = await call_with_retry(
                    self._fetch_org_repos_async,
                    github_org,
                    retry_config=GITHUB_RETRY_CONFIG,
                    circuit_breaker=self.circuit_breaker,
                )
            except Exception as e:
                self.log_warning(f"GitHub repo fetch failed: {e}")
                result.error_message = f"GitHub repo fetch exhausted retries: {e}"
                result.execution_time_seconds = (
                    datetime.now(UTC) - start_time
                ).total_seconds()
                return result

            if not repos:
                self.log_warning(f"No repos found in {github_org}")
                result.coverage_gaps.append("No public repositories available")
                result.success = False
                result.error_message = f"No repositories found in {github_org}"
                result.execution_time_seconds = (
                    datetime.now(UTC) - start_time
                ).total_seconds()
                return result

            primary_repos = sorted(
                repos, key=lambda r: r.get("stargazers_count", 0), reverse=True
            )[:5]
            self.log_info(f"Analyzing {len(primary_repos)} repos for {company_name}")

            for repo in primary_repos:
                raw_source = self._create_raw_source(
                    raw_content=repo,
                    source_name=f"GitHub: {repo.get('full_name', 'unknown')}",
                    url=repo.get("html_url"),
                    confidence=0.95,
                    extraction_method="github_api",
                    metadata={
                        "repo_name": repo.get("name"),
                        "stars": repo.get("stargazers_count", 0),
                        "language": repo.get("language"),
                    },
                )
                result.raw_sources.append(raw_source)

            # Extract facts from repos (existing logic)
            tech_stack = self._extract_tech_stack(primary_repos)
            result.extracted_facts.append(
                self._create_fact(
                    fact_type="tech_stack",
                    value=tech_stack,
                    confidence=0.90,
                    sources_used=[
                        f"GitHub: {repo.get('full_name')}" for repo in primary_repos
                    ],
                )
            )

            result.success = len(result.raw_sources) > 0
            self.log_info(
                f"Successfully gathered {len(result.raw_sources)} GitHub sources"
            )

        except Exception as e:
            self.log_error(f"Error gathering GitHub data: {e}")
            result.error_message = str(e)
            result.success = False

        finally:
            result.execution_time_seconds = (
                datetime.now(UTC) - start_time
            ).total_seconds()

        return result

    # Refactor to async versions
    async def _search_github_org_async(self, company_name: str) -> str | None:
        """Search for company's GitHub organization (async)."""
        return await asyncio.to_thread(self._search_github_org, company_name)

    async def _fetch_org_repos_async(self, org_name: str) -> list[dict]:
        """Fetch repos from GitHub org (async)."""
        return await asyncio.to_thread(self._fetch_org_repos, org_name)
```

**Step 2: Add tests for retry scenarios**

```python
# Add to tests/test_agents/test_single_company.py

@pytest.mark.asyncio
async def test_github_agent_retries_on_timeout():
    """Verify GitHub agent retries on timeout."""
    agent = GitHubAgent(github_token="test-token")
    
    # Mock requests to fail first, then succeed
    attempt_count = 0
    
    async def mock_search(*args, **kwargs):
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 2:
            raise asyncio.TimeoutError("Network timeout")
        return "company-org"
    
    agent._search_github_org_async = mock_search
    
    result = await agent.gather("TestCorp", {})
    
    # Should have retried (attempt_count = 2)
    assert attempt_count == 2
    # Result depends on the mock repos data
```

**Step 3: Run tests**

```bash
pytest tests/test_agents/test_single_company.py -v -k github
```

**Step 4: Commit**

```bash
git add src/solstein/agents/github_agent.py tests/test_agents/test_single_company.py
git commit -m "feat: add retry logic and circuit breaker to GitHub agent"
```

---

### TASK 1.3: Integrate Retry Logic Into Other Agents

Repeat the same pattern for:
- `src/solstein/agents/companies_house_agent.py`
- `src/solstein/agents/web_search_agent.py`

**Step**: Update both agents with same resilience pattern (use COMPANIES_HOUSE_RETRY_CONFIG and WEB_SEARCH_RETRY_CONFIG respectively)

**Commit**:
```bash
git add src/solstein/agents/companies_house_agent.py src/solstein/agents/web_search_agent.py
git commit -m "feat: add retry logic and circuit breaker to all agents"
```

---

## PHASE 2: Refactor Scoring Logic (CRITICAL)

### Goal
Break 614-line `GrowthScorer` god class into 3 focused scorer classes with 80%+ test coverage.

### Files
- Modify: `src/solstein/analytics/scoring.py` (refactor into 3 classes)
- Create: `tests/unit/test_growth_scoring.py` (80+ tests)
- Create: `tests/unit/test_financial_scoring.py` (comprehensive tests)
- Create: `tests/unit/test_competitive_scoring.py` (comprehensive tests)

### Architecture

**Before:**
```
GrowthScorer (614 lines)
  ├─ _calculate_growth_score (76 lines)
  ├─ _calculate_financial_health_score (86 lines)
  ├─ _calculate_competitive_position_score (69 lines)
  └─ ... 10 more big methods
```

**After:**
```
GrowthScorer (100 lines)
  └─ Composes 3 focused scorers

FinancialHealthScorer (80-100 lines)
  ├─ Revenue analysis
  ├─ Margin analysis
  ├─ Growth trajectory
  └─ Efficiency metrics

GrowthMomentumScorer (80-100 lines)
  ├─ YoY growth rate
  ├─ Compound growth
  ├─ Market expansion
  └─ New initiatives

CompetitivePositionScorer (80-100 lines)
  ├─ Tech stack depth
  ├─ Engineering maturity
  ├─ Market share trends
  └─ Competitive advantages
```

### TASK 2.1: Create FinancialHealthScorer

**Step 1: Write comprehensive tests first (TDD)**

```python
# tests/unit/test_financial_scoring.py
import pytest
from solstein.domain.models import Company, FinancialMetrics
from solstein.analytics.scoring import FinancialHealthScorer


class TestFinancialHealthScorer:
    """Financial health scoring tests."""
    
    @pytest.fixture
    def scorer(self):
        return FinancialHealthScorer()
    
    def test_calculates_score_zero_to_ten(self, scorer):
        """Score should always be 0-10."""
        company = Company(
            id="test",
            name="Test Co",
            industry="Tech",
            financials=FinancialMetrics(
                revenue=100.0,
                growth_rate=0.20,
                ebitda_margin=0.25,
            ),
        )
        
        score = scorer.score(company)
        assert 0 <= score <= 10
    
    def test_high_revenue_high_margin_scores_high(self, scorer):
        """High revenue + high margin → high score."""
        company = Company(
            id="test",
            name="Healthy Co",
            industry="Tech",
            financials=FinancialMetrics(
                revenue=500.0,  # Large
                growth_rate=0.15,
                ebitda_margin=0.40,  # Excellent
            ),
        )
        
        score = scorer.score(company)
        assert score >= 7.0
    
    def test_low_revenue_scores_low(self, scorer):
        """Low revenue → low score."""
        company = Company(
            id="test",
            name="Small Co",
            industry="Tech",
            financials=FinancialMetrics(
                revenue=5.0,  # Tiny
                growth_rate=0.50,
                ebitda_margin=0.30,
            ),
        )
        
        score = scorer.score(company)
        assert score <= 5.0
    
    def test_handles_missing_data(self, scorer):
        """Should handle missing financial data gracefully."""
        company = Company(
            id="test",
            name="Sparse Co",
            industry="Tech",
            financials=FinancialMetrics(
                revenue=None,
                growth_rate=None,
                ebitda_margin=None,
            ),
        )
        
        score = scorer.score(company)
        assert 0 <= score <= 10  # Doesn't crash
    
    def test_revenue_component(self, scorer):
        """Revenue analysis component."""
        assert scorer._score_revenue(1000.0) > scorer._score_revenue(100.0)
    
    def test_margin_component(self, scorer):
        """Margin analysis component."""
        assert scorer._score_margin(0.40) > scorer._score_margin(0.10)
    
    def test_growth_component(self, scorer):
        """Growth analysis component."""
        assert scorer._score_growth(0.50) > scorer._score_growth(0.05)
    
    def test_explains_scoring(self, scorer):
        """Scorer should explain its reasoning."""
        company = Company(
            id="test",
            name="Test Co",
            industry="Tech",
            financials=FinancialMetrics(
                revenue=200.0,
                growth_rate=0.15,
                ebitda_margin=0.25,
            ),
        )
        
        score, explanation = scorer.score_with_explanation(company)
        
        assert isinstance(score, float)
        assert isinstance(explanation, dict)
        assert "revenue_score" in explanation
        assert "margin_score" in explanation
        assert "growth_score" in explanation
```

**Step 2: Implement FinancialHealthScorer**

```python
# In src/solstein/analytics/scoring.py

class FinancialHealthScorer:
    """
    Scores company financial health on 0-10 scale.
    
    Factors:
      - Revenue scale (1-3 points)
      - EBITDA margin (1-3 points)
      - Growth trajectory (1-3 points)
      - Efficiency trends (1-point bonus)
    """
    
    def score(self, company: Company) -> float:
        """Calculate financial health score (0-10)."""
        score, _ = self.score_with_explanation(company)
        return score
    
    def score_with_explanation(self, company: Company) -> tuple[float, dict]:
        """Calculate score and explain reasoning."""
        score = 0.0
        explanation = {}
        
        # Component 1: Revenue (0-3 points)
        revenue_score = self._score_revenue(company.financials.revenue)
        score += revenue_score
        explanation["revenue_score"] = {
            "value": revenue_score,
            "input": company.financials.revenue,
            "reasoning": "Scale of revenue indicates financial stability"
        }
        
        # Component 2: EBITDA Margin (0-3 points)
        margin_score = self._score_margin(company.financials.ebitda_margin)
        score += margin_score
        explanation["margin_score"] = {
            "value": margin_score,
            "input": company.financials.ebitda_margin,
            "reasoning": "Margin efficiency shows operational leverage"
        }
        
        # Component 3: Growth (0-3 points)
        growth_score = self._score_growth(company.financials.growth_rate)
        score += growth_score
        explanation["growth_score"] = {
            "value": growth_score,
            "input": company.financials.growth_rate,
            "reasoning": "Growth trajectory indicates market traction"
        }
        
        # Component 4: Efficiency bonus (0-1 point)
        efficiency_bonus = self._score_efficiency_trend(company.financials)
        score += efficiency_bonus
        explanation["efficiency_bonus"] = {
            "value": efficiency_bonus,
            "reasoning": "Improving margins suggest operational discipline"
        }
        
        # Ensure 0-10 bounds
        final_score = max(0.0, min(10.0, score))
        explanation["final_score"] = final_score
        
        return final_score, explanation
    
    def _score_revenue(self, revenue: float | None) -> float:
        """Score revenue (0-3 points)."""
        if revenue is None or revenue == 0:
            return 0.0
        
        # Log scale: $1M = 1 pt, $10M = 2 pts, $100M = 3 pts
        import math
        points = max(0.0, min(3.0, math.log10(revenue)))
        return points
    
    def _score_margin(self, margin: float | None) -> float:
        """Score EBITDA margin (0-3 points)."""
        if margin is None or margin < 0:
            return 0.0
        
        # Linear scale: 0% = 0 pts, 50% = 3 pts, >50% = 3 pts
        return max(0.0, min(3.0, margin * 6.0))
    
    def _score_growth(self, growth_rate: float | None) -> float:
        """Score growth rate (0-3 points)."""
        if growth_rate is None:
            return 1.0  # Neutral
        
        # 0% = 0, 10% = 1.5, 30% = 3, >30% = 3
        if growth_rate < 0:
            return 0.0  # Declining
        elif growth_rate < 0.10:
            return growth_rate * 10 * 1.5  # 0-1.5
        elif growth_rate < 0.30:
            return 1.5 + ((growth_rate - 0.10) / 0.20) * 1.5  # 1.5-3
        else:
            return 3.0
    
    def _score_efficiency_trend(self, financials: FinancialMetrics) -> float:
        """Bonus point for improving margins."""
        # TODO: Compare to prior year when we have time-series data
        # For now: small bonus if margin > 0.20
        if financials.ebitda_margin and financials.ebitda_margin > 0.20:
            return 0.5
        return 0.0
```

**Step 3: Run tests**

```bash
pytest tests/unit/test_financial_scoring.py -v
```

**Expected**: All tests PASS (20+ tests)

**Step 4: Commit**

```bash
git add src/solstein/analytics/scoring.py tests/unit/test_financial_scoring.py
git commit -m "refactor: extract FinancialHealthScorer with 80%+ test coverage"
```

---

### TASK 2.2: Create GrowthMomentumScorer

Repeat same pattern:
- Write 20+ TDD tests
- Implement focused scorer
- Add explanation methods
- Test edge cases

**Key components:**
- YoY growth calculation
- Compound annual growth rate (CAGR)
- Market expansion signals
- New product momentum

---

### TASK 2.3: Create CompetitivePositionScorer

**Key components:**
- Tech stack depth analysis
- Engineering maturity assessment
- Market share trend analysis
- Competitive advantage signals

---

### TASK 2.4: Refactor GrowthScorer to Compose

```python
class GrowthScorer:
    """
    Composes financial, momentum, and competitive scorers.
    
    Total score: 0-10 (equal weight to each component)
      - Financial health: 0-10 (weighted 40%)
      - Growth momentum: 0-10 (weighted 40%)
      - Competitive position: 0-10 (weighted 20%)
    """
    
    def __init__(self):
        self.financial_scorer = FinancialHealthScorer()
        self.momentum_scorer = GrowthMomentumScorer()
        self.competitive_scorer = CompetitivePositionScorer()
    
    def calculate_scores(self, company: Company) -> Company:
        """Calculate all scores."""
        financial, fin_explain = self.financial_scorer.score_with_explanation(company)
        momentum, mom_explain = self.momentum_scorer.score_with_explanation(company)
        competitive, comp_explain = self.competitive_scorer.score_with_explanation(company)
        
        # Weighted average
        composite = (
            financial * 0.40 +
            momentum * 0.40 +
            competitive * 0.20
        )
        
        company.growth_score = composite
        company.scoring_breakdown = {
            "financial_health": financial,
            "growth_momentum": momentum,
            "competitive_position": competitive,
            "financial_details": fin_explain,
            "momentum_details": mom_explain,
            "competitive_details": comp_explain,
        }
        
        return company
```

---

## PHASE 3: Configuration Validation at Startup

### Goal
Ensure API keys are configured before system starts, preventing silent failures at runtime.

### Files
- Modify: `src/solstein/config.py` (add validation)
- Modify: `src/solstein/api/main.py` (call validation on startup)
- Create: `tests/unit/test_config_validation.py` (test validation)

### Implementation

```python
# Add to src/solstein/config.py

def validate_required_configs():
    """Validate that all required configs are present."""
    settings = get_settings()
    
    required = {
        "github_token": settings.github_token,
        "companies_house_api_key": settings.companies_house_api_key,
        "google_search_key": settings.google_search_key,
    }
    
    missing = [k for k, v in required.items() if not v]
    
    if missing:
        raise ValueError(
            f"Missing required configuration: {', '.join(missing)}. "
            f"Set environment variables or .env file."
        )
    
    logger.info("✓ All required configurations validated")

# In src/solstein/api/main.py
@app.on_event("startup")
async def startup_validation():
    """Validate configuration on startup."""
    try:
        validate_required_configs()
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        # In development, log warning; in production, raise
        if os.getenv("ENVIRONMENT") == "production":
            raise
```

---

## PHASE 4: Database Persistence for Drill-Down Service

### Goal
Replace in-memory storage with PostgreSQL persistence.

### Files
- Modify: `src/solstein/api/services/drill_down_service.py` (use SQLAlchemy)
- Create: `src/solstein/core/database.py` (SQLAlchemy setup)
- Create: `migrations/` (Alembic migrations)
- Modify: `requirements.txt` (add sqlalchemy, psycopg2)

### Implementation (High-level)

```python
# src/solstein/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# In drill_down_service.py
class DrillDownService:
    def __init__(self):
        self.session = async_session
    
    async def store_audit_trail(self, trail: CompanyAnalysisAuditTrail):
        """Store audit trail in PostgreSQL."""
        async with self.session() as session:
            db_trail = AuditTrailModel(**trail.dict())
            session.add(db_trail)
            await session.commit()
```

---

## PHASE 5-9 (Medium Priority)

These would continue with:
- **PHASE 5**: Signal extraction (50+ signals)
- **PHASE 6**: Monitoring + alerting
- **PHASE 7**: Remaining agents (LinkedIn, SEC, Patents, News, Jobs, Trends, Website)
- **PHASE 8**: Integration tests
- **PHASE 9**: Production hardening

*(Due to token limits, I'm providing phases 1-4 in detail. Phases 5-9 would follow the same pattern)*

---

## 📊 SUMMARY

| Phase | Priority | Effort | Impact | Status |
|-------|----------|--------|--------|--------|
| 0 | CRITICAL | 2h | Enable Phase 1-3 | ✅ DONE |
| 1 | CRITICAL | 8h | Resilient APIs | 🔄 TODO |
| 2 | CRITICAL | 12h | Testable scoring | 🔄 TODO |
| 3 | CRITICAL | 4h | Production safety | 🔄 TODO |
| 4 | CRITICAL | 6h | Persistent data | 🔄 TODO |
| 5 | MEDIUM | 8h | 50+ signals | 🔄 TODO |
| 6 | MEDIUM | 6h | Monitoring | 🔄 TODO |
| 7 | MEDIUM | 20h | Phase 1 agents | 🔄 TODO |
| 8 | MEDIUM | 10h | Integration tests | 🔄 TODO |
| 9 | MEDIUM | 6h | Hardening | 🔄 TODO |
| **TOTAL** | — | **80h** | **Production-ready** | **🔄 IN PROGRESS** |

---

## ✅ EXECUTION INSTRUCTIONS

**This plan is ready for implementation. Two execution options:**

### **Option 1: Subagent-Driven (Recommended)**
- I dispatch fresh subagent per phase
- Code review between phases  
- Fast iteration with quality gates

### **Option 2: Execute Yourself in New Session**
- Use `code-quality/executing-plans` skill
- Batch tasks as you go
- Checkpoints provided after each phase

**Which approach would you like?**

