# EPIC-009: Fix Scoring Configuration Architecture

## Status: 🔴 CRITICAL
## Priority: P0 - System Blocking
## Effort: 5 story points
## Sprint: Required for maintainable scoring

---

## Problem Statement

The scoring system has **hardcoded weights and inconsistent configuration** that makes it impossible to tune or maintain.

### Current Broken State
```python
# In scoring.py line 126 - HARDCODED WEIGHTS
profile.composite_score = round(
    (growth_score * 0.4) + (financial_health_score * 0.3) + (competitive_position_score * 0.3),
    2,
)

# Duplicate classification functions with DIFFERENT thresholds
# scoring.py: classify_company() uses >=7.0, 4.0-6.99, <=3.9
# classification.py: classify_company_balanced() uses >=7.0, >=5.5, <5.5

# Inconsistent margin thresholds
# GrowthScoringConfig: margin_high=20%, margin_med=10%
# FinancialHealthConfig: margin_high=15%, margin_med=5%
```

### Impact
- **Cannot tune scoring weights** without code changes
- **Inconsistent classification** between different functions
- **Same metric (margin) treated differently** in different configs
- **SaaS maturity formula hardcoded** - not configurable

---

## Success Criteria

- [ ] Composite weights configurable via ScoringSettings
- [ ] Single classification function used throughout
- [ ] Consistent thresholds across all config classes
- [ ] SaaS maturity formula configurable
- [ ] All magic numbers replaced with config values
- [ ] Configuration validated at startup

---

## Technical Analysis

### Root Causes
1. **Weights hardcoded** in scoring.py instead of config
2. **Two classification functions** with different logic
3. **Config classes define same metrics** with different thresholds
4. **No configuration validation**

### Affected Files
- `src/solstein/core/scoring_config.py`
- `src/solstein/analytics/scoring.py`
- `src/solstein/analytics/classification.py`
- `src/solstein/analytics/scorers/competitive_position.py`

---

## Stories

### Story 9.1: Consolidate Classification Functions
**Priority:** P0 | **Effort:** 2 points

**Description:**
Eliminate duplicate classification logic and use single function throughout codebase.

**Acceptance Criteria:**
- [ ] Choose ONE classification function (recommend classify_company from scoring.py)
- [ ] Deprecate or remove classify_company_balanced from classification.py
- [ ] Update all call sites to use consolidated function
- [ ] Document classification thresholds
- [ ] Add unit tests for classification function

**Implementation:**
```python
# In classification.py - mark as deprecated
@deprecated("Use solstein.analytics.scoring.classify_company() instead")
def classify_company_balanced(score: float) -> CompanyClassification:
    """DEPRECATED: Use scoring.classify_company() for consistent classification."""
    from solstein.analytics.scoring import classify_company
    return classify_company(score)

# Update all imports and calls throughout codebase
# Search for classify_company_balanced and replace
```

---

### Story 9.2: Make Composite Weights Configurable
**Priority:** P0 | **Effort:** 2 points

**Description:**
Move composite score weights from hardcoded values to configuration.

**Acceptance Criteria:**
- [ ] Add growth_weight, financial_weight, competitive_weight to ScoringSettings
- [ ] Update scoring.py to use config weights
- [ ] Validate weights sum to 1.0
- [ ] Document weight tuning guidelines
- [ ] Add example configurations for different use cases

**Implementation:**
```python
# In core/scoring_config.py
class ScoringSettings(BaseModel):
    """Configurable scoring weights."""
    growth_weight: float = Field(default=0.4, ge=0.0, le=1.0)
    financial_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    competitive_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    
    @validator('growth_weight', 'financial_weight', 'competitive_weight')
    def weights_sum_to_one(cls, v, values):
        total = sum([values.get('growth_weight', 0.4),
                    values.get('financial_weight', 0.3),
                    values.get('competitive_weight', 0.3)])
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        return v

# In analytics/scoring.py
profile.composite_score = round(
    (growth_score * self.config.growth_weight) +
    (financial_health_score * self.config.financial_weight) +
    (competitive_position_score * self.config.competitive_weight),
    2,
)
```

---

### Story 9.3: Harmonize Configuration Thresholds
**Priority:** P1 | **Effort:** 2 points

**Description:**
Ensure consistent thresholds for the same metrics across all configuration classes.

**Acceptance Criteria:**
- [ ] Audit all threshold definitions across configs
- [ ] Choose consistent values for margin thresholds
- [ ] Choose consistent values for efficiency thresholds
- [ ] Document why each threshold was chosen
- [ ] Update all config classes with consistent values

**Implementation:**
```python
# Create shared thresholds module
class MarginThresholds:
    """Shared margin thresholds across all scorers."""
    HIGH = 20.0  # 20% margin
    MEDIUM = 10.0  # 10% margin
    LOW = 5.0  # 5% margin

class EfficiencyThresholds:
    """Shared efficiency thresholds (revenue per employee)."""
    HIGH = 1_000_000  # €1M per employee
    MEDIUM = 500_000  # €500K per employee
    LOW = 100_000  # €100K per employee

# Use in all config classes
from .shared_thresholds import MarginThresholds, EfficiencyThresholds

class GrowthScoringConfig:
    margin_high_threshold: float = MarginThresholds.HIGH
    margin_med_threshold: float = MarginThresholds.MEDIUM
    
class FinancialHealthConfig:
    margin_high_threshold: float = MarginThresholds.HIGH
    margin_med_threshold: float = MarginThresholds.MEDIUM
```

---

### Story 9.4: Make SaaS Maturity Formula Configurable
**Priority:** P1 | **Effort:** 1 point

**Description:**
Extract hardcoded SaaS maturity formula into configuration.

**Acceptance Criteria:**
- [ ] Add saas_maturity_formula to config
- [ ] Support linear and custom formulas
- [ ] Document formula parameters
- [ ] Validate formula produces reasonable outputs

**Implementation:**
```python
# In core/scoring_config.py
class CompetitivePositionConfig:
    """Configuration for competitive position scoring."""
    
    # SaaS maturity scoring
    saas_maturity_max_bonus: float = 2.0
    saas_maturity_formula: str = "linear"  # or "custom"
    
    def calculate_saas_adjustment(self, saas_maturity: int) -> float:
        """Calculate SaaS maturity adjustment."""
        if self.saas_maturity_formula == "linear":
            # Linear: (maturity - 1) / 9 * max_bonus
            return (saas_maturity - 1) / 9 * self.saas_maturity_max_bonus
        elif self.saas_maturity_formula == "custom":
            # Custom formula could be defined here
            pass
        else:
            raise ValueError(f"Unknown formula: {self.saas_maturity_formula}")
```

---

## Dependencies

- Story 9.1 and 9.2 are critical - should be done first
- Story 9.3 can be done in parallel
- Story 9.4 is enhancement (P1)

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Changing weights affects all scores | High | Recalculate baseline, notify users |
| Config validation too strict | Low | Allow flexibility with warnings |

## Definition of Done

- [ ] Single classification function used throughout
- [ ] Composite weights configurable
- [ ] Consistent thresholds across configs
- [ ] SaaS maturity formula configurable
- [ ] Configuration validated at startup
- [ ] Documentation updated
