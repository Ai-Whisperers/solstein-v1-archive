# EPIC-051: Data Source Quality Scoring System

|**Status:** 🔴 Not Started  
|**Priority:** MEDIUM (P2)  
|**Story Points:** 21  
|**Sprint Allocation:** 2 sprints  
|**Target Date:** Week 31-32

---

## Problem Statement

Solstein integrates multiple data sources but lacks systematic quality measurement. Different APIs have varying reliability, coverage, and freshness. Without quality scoring, the platform cannot intelligently weight sources, detect degradation, or prioritize improvements.

### Impact
- Low-quality data propagates to scoring engine
- No visibility into source reliability trends
- Cannot compare source effectiveness
- Difficult to identify which sources need attention
- Analysts cannot assess data confidence

---

## Success Criteria

1. ✅ Quality scoring framework operational for all data sources
2. ✅ Four dimensions scored: reliability, freshness, coverage, accuracy
3. ✅ Quality scores influence data weighting in enrichment
4. ✅ Degradation alerts when source quality drops
5. ✅ Quality dashboard showing source health
6. ✅ Historical quality trends tracked

---

## Stories

### Story 51.1: Quality Metrics Framework (8 pts)
**Task:** Design and implement quality scoring framework

**Acceptance Criteria:**
- [ ] Quality dimensions defined: reliability, freshness, coverage, accuracy
- [ ] Scoring algorithms for each dimension
- [ ] Composite quality score calculation
- [ ] Quality score storage in database
- [ ] API for retrieving source quality
- [ ] Documentation of scoring methodology

**Quality Dimensions:**
```python
# src/solstein/data_sources/quality/models.py
@dataclass
class SourceQualityScores:
    """Quality scores for a data source (0.0 - 1.0)."""
    
    # Reliability: API uptime, error rate, response time
    reliability: float
    reliability_factors: dict = field(default_factory=dict)
    # - uptime_percentage: 99.5%
    # - error_rate: 0.1%
    # - avg_response_time_ms: 250
    # - timeout_rate: 0.05%
    
    # Freshness: Data recency, update frequency
    freshness: float
    freshness_factors: dict = field(default_factory=dict)
    # - avg_data_age_hours: 24
    # - update_frequency_hours: 12
    # - staleness_rate: 0.02
    
    # Coverage: Geographic, sector, company stage coverage
    coverage: float
    coverage_factors: dict = field(default_factory=dict)
    # - geography_coverage: 0.8 (80% of target geographies)
    # - sector_coverage: 0.7
    # - company_stage_coverage: 0.9
    # - fill_rate: 0.85 (85% of companies have data)
    
    # Accuracy: Data correctness, validation pass rate
    accuracy: float
    accuracy_factors: dict = field(default_factory=dict)
    # - validation_pass_rate: 0.95
    # - contradiction_rate: 0.03
    # - manual_audit_score: 0.92
    
    # Composite score (weighted average)
    overall: float
    
    # Metadata
    calculated_at: datetime
    sample_size: int
    calculation_period_days: int

class QualityScorer:
    """Calculate quality scores for data sources."""
    
    WEIGHTS = {
        'reliability': 0.35,
        'freshness': 0.25,
        'coverage': 0.25,
        'accuracy': 0.15,
    }
    
    def calculate_overall(self, scores: SourceQualityScores) -> float:
        """Calculate weighted composite score."""
        return sum(
            getattr(scores, dim) * weight
            for dim, weight in self.WEIGHTS.items()
        )
```

---

### Story 51.2: Reliability Monitoring (5 pts)
**Task:** Monitor API reliability metrics

**Acceptance Criteria:**
- [ ] Uptime tracking for all APIs
- [ ] Error rate monitoring and alerting
- [ ] Response time percentiles (p50, p95, p99)
- [ ] Timeout and retry tracking
- [ ] Circuit breaker integration
- [ ] Reliability score calculation

**Implementation:**
```python
# src/solstein/data_sources/quality/reliability_monitor.py
class ReliabilityMonitor:
    """Monitor API reliability metrics."""
    
    def __init__(self, metrics_client: MetricsClient):
        self.metrics = metrics_client
    
    async def record_request(
        self,
        source: str,
        success: bool,
        response_time_ms: float,
        error_type: str | None = None
    ):
        """Record API request outcome."""
        self.metrics.increment(
            'api_requests_total',
            labels={'source': source, 'success': str(success)}
        )
        self.metrics.histogram(
            'api_response_time_ms',
            value=response_time_ms,
            labels={'source': source}
        )
        if error_type:
            self.metrics.increment(
                'api_errors_total',
                labels={'source': source, 'error_type': error_type}
            )
    
    def calculate_reliability_score(
        self,
        source: str,
        period_days: int = 7
    ) -> float:
        """Calculate reliability score from metrics."""
        total = self.metrics.get_count('api_requests_total', source, period_days)
        errors = self.metrics.get_count('api_errors_total', source, period_days)
        
        if total == 0:
            return 0.0
        
        uptime = (total - errors) / total
        avg_response_time = self.metrics.get_avg('api_response_time_ms', source, period_days)
        
        # Score: 50% uptime + 50% response time factor
        response_score = max(0, 1 - (avg_response_time / 1000))  # Penalty > 1s
        return (uptime * 0.5) + (response_score * 0.5)
```

---

### Story 51.3: Freshness & Coverage Tracking (5 pts)
**Task:** Track data freshness and coverage metrics

**Acceptance Criteria:**
- [ ] Data age tracking per company/source
- [ ] Update frequency measurement
- [ ] Geographic coverage calculation
- [ ] Sector coverage calculation
- [ ] Fill rate (completeness) tracking
- [ ] Freshness and coverage score calculation

---

### Story 51.4: Quality-Based Data Weighting (3 pts)
**Task:** Use quality scores to weight data in enrichment

**Acceptance Criteria:**
- [ ] Quality scores influence source weighting
- [ ] Low-quality sources automatically deprioritized
- [ ] Quality degradation triggers source fallback
- [ ] Analysts can override quality weights
- [ ] Quality weighting documented

**Implementation:**
```python
# src/solstein/enrichment/quality_weighted_aggregator.py
class QualityWeightedAggregator:
    """Aggregate data with quality-based weighting."""
    
    def __init__(self, quality_service: QualityService):
        self.quality = quality_service
    
    async def aggregate(
        self,
        company_id: str,
        data_points: list[DataPoint]
    ) -> AggregatedData:
        """Aggregate data weighted by source quality."""
        weighted_data = []
        
        for point in data_points:
            quality = await self.quality.get_score(point.source)
            
            # Skip very low quality sources
            if quality.overall < 0.3:
                logger.warning(f"Skipping low-quality source: {point.source}")
                continue
            
            weighted_data.append({
                'value': point.value,
                'weight': quality.overall,
                'confidence': point.confidence * quality.overall,
            })
        
        return self.calculate_weighted_average(weighted_data)
```

---

## Definition of Done

- [ ] Quality scoring framework implemented
- [ ] All existing data sources have quality scores
- [ ] Reliability monitoring operational
- [ ] Freshness and coverage tracking active
- [ ] Quality-based weighting in enrichment pipeline
- [ ] Quality dashboard showing source health
- [ ] Degradation alerting configured
- [ ] Documentation complete

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scoring accuracy | Medium | Medium | Validation, calibration |
| Performance overhead | Medium | Medium | Async calculation, caching |
| Alert fatigue | Medium | Medium | Tuned thresholds, grouping |

---

## Resources

- **Developers:** 1-2 backend engineers
- **Time:** 2 weeks
- **Dependencies:** EPIC-049 (catalog), existing data sources

---

*Epic created from OpenClaw API list analysis*
