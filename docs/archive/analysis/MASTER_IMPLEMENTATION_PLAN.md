# MASTER IMPLEMENTATION PLAN: All Pending Epics

> **Status**: Planning Phase
> **Total Epics**: 15 (excluding EPIC-018 which is complete)
> **Total Story Points**: 88
> **Estimated Duration**: 5-6 months
> **Priority**: System Unusable - Must Complete for Production

---

## 🎯 EXECUTIVE SUMMARY

This plan addresses all 15 remaining epics that make the system unusable. The epics are organized into 6 phases based on dependencies and business criticality.

### Critical Path

**Phase 1** (Weeks 1-3): Data Integrity Foundation
**Phase 2** (Weeks 4-6): Core Scoring System
**Phase 3** (Weeks 7-9): Data Pipeline & Export
**Phase 4** (Weeks 10-14): Real Data & Enrichment
**Phase 5** (Weeks 15-18): Data Quality & Cleanup
**Phase 6** (Weeks 19-24): Testing & Production Readiness

---

## 📋 PHASE 1: DATA INTEGRITY FOUNDATION (Weeks 1-3)

### Goal: Fix fundamental data issues that block everything else

---

## EPIC-010: Fix Company Model and IDs
**Priority**: P0 | **Points**: 5 | **Week**: 1

**Problem**: 32 duplicate company IDs, data integrity issues

**Success Criteria**:
- [ ] No duplicate company IDs
- [ ] Unique constraint enforced at database level
- [ ] Migration script for existing data
- [ ] ID generation strategy documented

**Implementation**:
```python
# 1. Add unique constraint to database
# 2. Create migration script to deduplicate
# 3. Fix ID generation logic
# 4. Add validation
```

**Files to Modify**:
- `infrastructure/database_models.py` - Add unique constraint
- `domain/models.py` - Fix ID generation
- Create migration script

**Acceptance Tests**:
```python
def test_no_duplicate_ids():
    ids = [c.id for c in companies]
    assert len(ids) == len(set(ids))
```

---

## EPIC-001: Fix Financial Health Scoring
**Priority**: P0 | **Points**: 8 | **Weeks**: 1-2

**Problem**: ALL companies score 5.5/10 due to unit mismatch

**Root Cause**: Data stores revenue in millions, config expects absolute EUR

**Implementation Steps**:

### Step 1: Fix Unit Mismatch (Day 1-2)
```python
# BEFORE (broken):
revenue_large_threshold = 100_000_000.0  # €100M absolute
revenue = 5.0  # €5M stored as millions (WRONG)
comparison: 5.0 > 100_000_000  # ALWAYS FALSE

# AFTER (fixed):
# Option A: Convert data to absolute values
revenue = company.revenue * 1_000_000  # Convert millions to absolute

# Option B: Convert thresholds to millions
revenue_large_threshold = 100.0  # €100M in millions
```

### Step 2: Fix Funding/Revenue Ratio (Day 3)
```python
# Both must use same units
funding = company.funding_total  # Assume absolute
revenue = company.revenue * 1_000_000  # Convert to absolute
ratio = funding / revenue if revenue > 0 else 0
```

### Step 3: Fix Efficiency Calculation (Day 4)
```python
# Revenue per employee
revenue_absolute = company.revenue * 1_000_000
employees = company.employees
rev_per_emp = revenue_absolute / employees if employees > 0 else 0
```

### Step 4: Update Thresholds (Day 5)
```python
# Config in millions for consistency
REVENUE_THRESHOLDS = {
    "small": 1.0,      # €1M
    "medium": 10.0,    # €10M
    "large": 100.0,    # €100M
}
```

**Files to Modify**:
- `analytics/scorers/financial_health.py` - Fix calculations
- `config/scoring_config.py` - Update thresholds
- `analytics/scoring.py` - Update scoring logic

**Acceptance Tests**:
```python
def test_financial_health_variance():
    scores = [c.financial_health_score for c in companies]
    variance = max(scores) - min(scores)
    assert variance > 2.0, f"Variance is {variance}, expected > 2.0"

def test_revenue_thresholds():
    # Company with €150M revenue should be "large"
    company = Company(revenue=150.0)  # in millions
    assert classify_revenue(company) == "large"
```

---

## 📋 PHASE 2: CORE SCORING SYSTEM (Weeks 4-6)

---

## EPIC-002: Fix Classification System
**Priority**: P0 | **Points**: 5 | **Week**: 4

**Problem**: Lead classification impossible due to backwards tier mapping

**Implementation**:

```python
# Fix tier mapping
TIER_MAPPING = {
    "unicorn": {"min_valuation": 1000},  # $1B
    "late_stage": {"min_valuation": 100, "max_valuation": 1000},
    "growth": {"min_valuation": 10, "max_valuation": 100},
    "early_stage": {"max_valuation": 10},
}

def classify_company(company) -> str:
    """Correct classification logic."""
    valuation = company.valuation or 0

    if valuation >= 1000:
        return "unicorn"
    elif valuation >= 100:
        return "late_stage"
    elif valuation >= 10:
        return "growth"
    else:
        return "early_stage"
```

**Files to Modify**:
- `analytics/classifiers/company_classifier.py`
- `analytics/scoring.py`

**Acceptance Tests**:
```python
def test_classification_rate():
    classified = sum(1 for c in companies if c.tier != "unknown")
    rate = classified / len(companies)
    assert rate >= 0.10, f"Classification rate {rate} < 10%"
```

---

## EPIC-009: Fix Scoring Configuration
**Priority**: P0 | **Points**: 5 | **Weeks**: 5-6

**Problem**: Hardcoded weights, no configuration possible

**Implementation**:

```python
# config/scoring_config.py
from pydantic import BaseSettings

class ScoringConfig(BaseSettings):
    """Configurable scoring weights."""

    # Financial health weights
    revenue_weight: float = 0.30
    growth_weight: float = 0.25
    efficiency_weight: float = 0.25
    funding_cushion_weight: float = 0.20

    # Classification thresholds
    unicorn_threshold: float = 1000.0  # $1B
    late_stage_threshold: float = 100.0
    growth_threshold: float = 10.0

    class Config:
        env_prefix = "SCORING_"

# Usage
config = ScoringConfig()
score = (
    revenue_component * config.revenue_weight +
    growth_component * config.growth_weight +
    ...
)
```

**Files to Modify**:
- `config/scoring_config.py` - Create new
- `analytics/scoring.py` - Use config
- `api/routers/admin.py` - Add config endpoint

---

## 📋 PHASE 3: DATA PIPELINE & EXPORT (Weeks 7-9)

---

## EPIC-004: Fix Data Conversion Pipeline
**Priority**: P0 | **Points**: 8 | **Weeks**: 7-8

**Problem**: 30+ fields lost during JSON to Company conversion (73% loss rate)

**Implementation**:

### Step 1: Audit Current Conversion (Day 1)
```python
# Create field mapping audit
SOURCE_FIELDS = list(raw_company.keys())  # ~41 fields
TARGET_FIELDS = [f.name for f in fields(Company)]  # ~11 fields
LOST_FIELDS = set(SOURCE_FIELDS) - set(TARGET_FIELDS)
print(f"Lost fields: {len(LOST_FIELDS)}")  # 30 fields lost!
```

### Step 2: Map Lost Fields (Day 2-3)
```python
# Add missing fields to Company model
@dataclass
class Company:
    # Existing fields
    id: str
    name: str
    revenue: float
    ...

    # Missing fields to add
    cagr: float = None  # Compound Annual Growth Rate
    enrichment_source_count: int = 0
    confidence_level: str = "unknown"
    # ... add other 27 missing fields
```

### Step 3: Fix Conversion Logic (Day 4-6)
```python
def convert_json_to_company(raw: dict) -> Company:
    """Convert raw JSON to Company with ALL fields preserved."""
    return Company(
        id=raw.get("company_id"),
        name=raw.get("company_name"),
        revenue=raw.get("revenue"),
        cagr=raw.get("cagr"),  # Was lost!
        enrichment_source_count=raw.get("enrichment_source_count", 0),  # Was lost!
        confidence_level=raw.get("confidence_level", "unknown"),  # Was lost!
        # ... map all 41 fields
    )
```

**Files to Modify**:
- `domain/models.py` - Add missing fields
- `data/conversion.py` - Fix conversion logic
- `infrastructure/database_models.py` - Add columns

**Acceptance Tests**:
```python
def test_no_field_loss():
    raw = load_test_company_json()
    company = convert_json_to_company(raw)

    # Check all source fields exist in target
    for field in raw.keys():
        assert hasattr(company, field), f"Field {field} lost!"

    loss_rate = (len(raw) - len([f for f in raw if getattr(company, f)])) / len(raw)
    assert loss_rate < 0.05, f"Field loss rate {loss_rate} > 5%"
```

---

## EPIC-005: Fix Excel Export
**Priority**: P0 | **Points**: 5 | **Week**: 9

**Problem**: profit_margin and ebitda_margin always "N/A"

**Implementation**:

```python
# exporters/excel.py

def calculate_margins(company) -> dict:
    """Calculate profit and EBITDA margins."""
    revenue = company.revenue * 1_000_000  # Convert to absolute

    # Profit margin
    if revenue > 0 and company.profit is not None:
        profit_margin = (company.profit / revenue) * 100
    else:
        profit_margin = None

    # EBITDA margin
    if revenue > 0 and company.ebitda is not None:
        ebitda_margin = (company.ebitda / revenue) * 100
    else:
        ebitda_margin = None

    return {
        "profit_margin": profit_margin,
        "ebitda_margin": ebitda_margin,
    }

def export_to_excel(companies: list[Company]) -> bytes:
    """Export companies to Excel with correct margins."""
    data = []
    for company in companies:
        margins = calculate_margins(company)
        data.append({
            "name": company.name,
            "revenue": company.revenue,
            "profit_margin": margins["profit_margin"],  # Will be calculated
            "ebitda_margin": margins["ebitda_margin"],  # Will be calculated
            # ... other fields
        })

    return create_excel_file(data)
```

**Files to Modify**:
- `exporters/excel.py` - Fix margin calculations
- `exporters/csv.py` - Apply same fix

**Acceptance Tests**:
```python
def test_margins_calculated():
    company = Company(revenue=10.0, profit=1.0, ebitda=2.0)
    margins = calculate_margins(company)

    assert margins["profit_margin"] == 10.0, f"Expected 10%, got {margins['profit_margin']}"
    assert margins["ebitda_margin"] == 20.0, f"Expected 20%, got {margins['ebitda_margin']}"
```

---

## 📋 PHASE 4: REAL DATA & ENRICHMENT (Weeks 10-14)

---

## EPIC-007: Implement Confidence System
**Priority**: P0 | **Points**: 5 | **Week**: 10

**Problem**: Confidence weighting is disabled

**Implementation**:

```python
# analytics/confidence.py

class ConfidenceCalculator:
    """Calculate data confidence scores."""

    def calculate(self, company: Company) -> float:
        """Calculate confidence score 0-1."""
        factors = []

        # Source count factor
        if company.enrichment_source_count >= 3:
            factors.append(1.0)
        elif company.enrichment_source_count >= 1:
            factors.append(0.5)
        else:
            factors.append(0.0)

        # Data freshness factor
        days_since_update = (datetime.now() - company.last_updated).days
        if days_since_update < 30:
            factors.append(1.0)
        elif days_since_update < 90:
            factors.append(0.7)
        else:
            factors.append(0.3)

        # Data completeness factor
        completeness = self._calculate_completeness(company)
        factors.append(completeness)

        return sum(factors) / len(factors)

    def _calculate_completeness(self, company: Company) -> float:
        """Calculate field completeness 0-1."""
        required_fields = ['revenue', 'employees', 'industry', 'headquarters']
        present = sum(1 for f in required_fields if getattr(company, f))
        return present / len(required_fields)

# Apply confidence to scoring
def score_with_confidence(company: Company) -> float:
    """Apply confidence weighting to score."""
    base_score = calculate_base_score(company)
    confidence = ConfidenceCalculator().calculate(company)
    return base_score * confidence
```

**Files to Modify**:
- `analytics/confidence.py` - Create new
- `analytics/scoring.py` - Integrate confidence

---

## EPIC-003: Implement Real Enrichment
**Priority**: P0 | **Points**: 13 | **Weeks**: 11-13

**Problem**: Enrichment is 100% fake (mock data)

**Implementation**:

### Step 1: Set Up API Clients (Week 11)
```python
# data/connectors/crunchbase_connector.py
import httpx

class CrunchbaseConnector:
    """Real Crunchbase API integration."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.crunchbase.com/v4"

    async def enrich_company(self, name: str) -> dict:
        """Fetch real data from Crunchbase."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/entities/organizations/{name}",
                headers={"X-cb-user-key": self.api_key},
                timeout=30.0
            )
            resp.raise_for_status()
            return resp.json()

# Similar for LinkedIn, News APIs
```

### Step 2: Create Enrichment Pipeline (Week 12)
```python
# services/enrichment_service.py

class RealEnrichmentService:
    """Real data enrichment (not mock)."""

    def __init__(self):
        self.connectors = [
            CrunchbaseConnector(settings.CRUNCHBASE_API_KEY),
            LinkedInConnector(settings.LINKEDIN_API_KEY),
            NewsConnector(settings.NEWS_API_KEY),
        ]

    async def enrich(self, company: Company) -> Company:
        """Enrich company with real data from multiple sources."""
        sources_used = 0

        for connector in self.connectors:
            try:
                data = await connector.enrich_company(company.name)
                self._merge_data(company, data)
                sources_used += 1
            except Exception as e:
                logger.warning(f"Enrichment failed for {connector}: {e}")

        company.enrichment_source_count = sources_used
        company.last_enriched = datetime.now()
        return company
```

### Step 3: Replace Mock Enrichment (Week 13)
```python
# BEFORE (fake):
from data.enrichment import mock_enrich
company = mock_enrich(company)  # Returns fake data

# AFTER (real):
from services.enrichment_service import RealEnrichmentService
service = RealEnrichmentService()
company = await service.enrich(company)  # Real API calls
```

**Files to Create/Modify**:
- `data/connectors/crunchbase_connector.py` - New
- `data/connectors/linkedin_connector.py` - New
- `data/connectors/news_connector.py` - New
- `services/enrichment_service.py` - New
- Replace all mock enrichment calls

**Acceptance Tests**:
```python
async def test_real_enrichment():
    company = Company(name="Stripe")
    service = RealEnrichmentService()

    enriched = await service.enrich(company)

    assert enriched.enrichment_source_count > 0
    assert enriched.revenue is not None  # Should have real data
    assert not enriched.is_synthetic
```

---

## EPIC-008: Replace Synthetic with Real Data
**Priority**: P0 | **Points**: 13 | **Week**: 14

**Problem**: 196/199 companies are synthetic (98.5% fake)

**Implementation**:

```python
# scripts/migrate_synthetic_to_real.py

async def migrate_company(company_id: str):
    """Migrate synthetic company to real data."""
    company = await get_company(company_id)

    if not company.is_synthetic:
        return  # Already real

    # Try to find real data
    real_data = await find_real_company_data(company.name)

    if real_data:
        # Update with real data
        company.revenue = real_data.get('revenue')
        company.employees = real_data.get('employees')
        company.industry = real_data.get('industry')
        company.is_synthetic = False
        company.data_source = real_data.get('source')
        await save_company(company)
        return True
    else:
        # Mark as needing manual review
        company.needs_manual_review = True
        await save_company(company)
        return False

async def batch_migrate():
    """Migrate all synthetic companies."""
    synthetic = await get_synthetic_companies()

    migrated = 0
    failed = 0

    for company in synthetic:
        success = await migrate_company(company.id)
        if success:
            migrated += 1
        else:
            failed += 1

    print(f"Migrated: {migrated}, Failed: {failed}, Total: {len(synthetic)}")
```

---

## 📋 PHASE 5: DATA QUALITY & CLEANUP (Weeks 15-18)

---

## EPIC-006: Fix Synthetic Data Generation
**Priority**: P1 | **Points**: 5 | **Week**: 15

**Improve synthetic data quality for companies that can't be enriched**.

---

## EPIC-013: Fix Data Quality and Validation
**Priority**: P0 | **Points**: 5 | **Weeks**: 16-17

**Problem**: No data validation

**Implementation**:

```python
# validation/company_validator.py

class CompanyValidator:
    """Validate company data."""

    def validate(self, company: Company) -> list[str]:
        """Return list of validation errors."""
        errors = []

        # Revenue validation
        if company.revenue < 0:
            errors.append("Revenue cannot be negative")
        if company.revenue > 10000:  # > €10B suspicious
            errors.append("Revenue seems too high (> €10B)")

        # Employee validation
        if company.employees < 0:
            errors.append("Employees cannot be negative")
        if company.employees > 1000000:  # > 1M suspicious
            errors.append("Employee count seems too high (> 1M)")

        # Website validation
        if company.website and not company.website.startswith("http"):
            errors.append("Website must start with http/https")

        return errors

# Apply validation on save
async def save_company(company: Company):
    validator = CompanyValidator()
    errors = validator.validate(company)

    if errors:
        raise ValidationError(f"Invalid company data: {errors}")

    await db.save(company)
```

---

## 📋 PHASE 6: TESTING & PRODUCTION READINESS (Weeks 19-24)

---

## EPIC-012: Implement Testing Strategy
**Priority**: P0 | **Points**: 8 | **Weeks**: 19-20

**Goal**: Increase test coverage from <20% to >80%

**Implementation**:

```python
# Test pyramid structure
tests/
├── unit/                    # Fast, isolated
│   ├── analytics/
│   ├── domain/
│   ├── api/
│   └── exporters/
├── integration/             # Cross-component
│   ├── database/
│   ├── enrichment/
│   └── scoring/
└── e2e/                     # Full workflows
    ├── company_import.py
    ├── enrichment_flow.py
    └── export_flow.py
```

---

## EPIC-014: Performance and Scalability
**Priority**: P1 | **Points**: 5 | **Week**: 21

Already partially done (blocking I/O fixed). Remaining:
- Add caching
- Optimize database queries
- Add connection pooling

---

## EPIC-015: Documentation and Knowledge Transfer
**Priority**: P1 | **Points**: 3 | **Weeks**: 22-23

Create comprehensive documentation:
- API documentation
- Architecture diagrams
- Deployment guide
- Troubleshooting runbook

---

## EPIC-016: Security and Compliance
**Priority**: P1 | **Points**: 5 | **Week**: 24

Partially done (bcrypt, admin auth). Remaining:
- Security audit
- Penetration testing
- Compliance documentation

---

## 📊 IMPLEMENTATION TIMELINE

```
Month 1 (Weeks 1-4):
├── Week 1: EPIC-010 (Company IDs)
├── Week 2: EPIC-001 (Financial Scoring - Part 1)
├── Week 3: EPIC-001 (Financial Scoring - Part 2)
└── Week 4: EPIC-002 (Classification)

Month 2 (Weeks 5-8):
├── Week 5: EPIC-009 (Scoring Config)
├── Week 6: EPIC-009 (Scoring Config) + Buffer
├── Week 7: EPIC-004 (Data Conversion - Part 1)
└── Week 8: EPIC-004 (Data Conversion - Part 2)

Month 3 (Weeks 9-12):
├── Week 9: EPIC-005 (Excel Export)
├── Week 10: EPIC-007 (Confidence System)
├── Week 11: EPIC-003 (Real Enrichment - Part 1)
└── Week 12: EPIC-003 (Real Enrichment - Part 2)

Month 4 (Weeks 13-16):
├── Week 13: EPIC-003 (Real Enrichment - Part 3)
├── Week 14: EPIC-008 (Replace Synthetic Data)
├── Week 15: EPIC-006 (Synthetic Data Quality)
└── Week 16: EPIC-013 (Data Validation)

Month 5 (Weeks 17-20):
├── Week 17: EPIC-013 (Data Validation) + Buffer
├── Week 18: Buffer / Polish
├── Week 19: EPIC-012 (Testing Strategy)
└── Week 20: EPIC-012 (Testing Strategy)

Month 6 (Weeks 21-24):
├── Week 21: EPIC-014 (Performance)
├── Week 22: EPIC-015 (Documentation)
├── Week 23: EPIC-015 (Documentation)
└── Week 24: EPIC-016 (Security) + Final Polish
```

---

## 🎯 SUCCESS METRICS

### Before Fix
- Financial health variance: **0** (all 5.5)
- Lead classification rate: **0%**
- Real data ratio: **1.5%**
- Field loss rate: **73%** (30/41 fields)
- Enrichment authenticity: **0%**
- Test coverage: **<20%**

### After Fix (Target)
- Financial health variance: **> 2.0**
- Lead classification rate: **10-20%**
- Real data ratio: **> 80%**
- Field loss rate: **< 5%**
- Enrichment authenticity: **100%**
- Test coverage: **> 80%**
- System usability: **PRODUCTION READY**

---

## 🚀 NEXT ACTIONS

### Immediate (Today)
1. **Commit all current changes** (EPIC-018)
2. **Create feature branches** for Phase 1 epics
3. **Begin EPIC-010** (Company Model and IDs)

### This Week
1. Complete EPIC-010
2. Begin EPIC-001 (Financial Scoring)
3. Set up API accounts for enrichment (Crunchbase, LinkedIn)

---

**Status**: 📝 Planning Complete | Ready for Implementation
**Total Duration**: 24 weeks (6 months)
**Team Required**: 2-3 backend engineers, 1 data engineer
**Next Step**: Begin Phase 1 implementation

---

*Master Plan Created: 2026-03-05*
*Ready for Implementation*
