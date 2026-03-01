# EPIC-013: Fix Data Quality and Validation

## Status: 🔴 CRITICAL
## Priority: P0 - System Blocking
## Effort: 5 story points
## Sprint: Required for reliable data

---

## Problem Statement

The system has **no data validation**, allowing impossible values and inconsistent data to flow through the pipeline.

### Current Broken State
```python
# No validation on input data
company = Company(
    revenue=-5.0,  # Negative revenue allowed!
    employees=-10,  # Negative employees!
    funding_raised=1000000.0,  # $1M funding
    valuation=50000.0,  # $50K valuation (funding > valuation!)
)

# No validation on calculated fields
rev_per_emp = revenue / employees  # Division by zero possible
```

### Impact
- **Impossible values** in dataset (negative revenue, funding > valuation)
- **Runtime errors** from division by zero
- **Incorrect scores** from bad data
- **No data quality feedback** to users

---

## Success Criteria

- [ ] All input data validated before processing
- [ ] Impossible values rejected with clear errors
- [ ] Data quality score calculated for each company
- [ ] Quality issues reported to users
- [ ] Automatic data cleaning where possible

---

## Technical Analysis

### Validation Gaps
1. **No range validation** on numeric fields
2. **No consistency checks** (funding vs valuation)
3. **No required field validation**
4. **No data type validation**
5. **No outlier detection**

### Affected Files
- `src/solstein/domain/models.py`
- `scripts/run_eneve_199.py`
- All data conversion points

---

## Stories

### Story 13.1: Implement Input Data Validation
**Priority:** P0 | **Effort:** 2 points

**Description:**
Add comprehensive validation to input data before conversion.

**Acceptance Criteria:**
- [ ] Validate revenue is non-negative
- [ ] Validate employees is positive integer
- [ ] Validate growth rate is reasonable (-100% to 1000%)
- [ ] Validate funding_raised <= valuation
- [ ] Validate founded_year is reasonable (1800-current)
- [ ] Reject or flag invalid data

**Implementation:**
```python
from pydantic import validator, ValidationError
from typing import Optional

class CompanyValidator:
    """Validate company data."""
    
    VALIDATION_RULES = {
        'revenue': {'min': 0, 'max': 1_000_000},  # €0 to €1B
        'employees': {'min': 1, 'max': 100_000},
        'growth_rate': {'min': -100, 'max': 1000},  # -100% to 1000%
        'founded_year': {'min': 1800, 'max': 2026},
    }
    
    @classmethod
    def validate_company_data(cls, data: dict) -> list[str]:
        """Validate company data and return list of issues."""
        issues = []
        
        # Range validation
        for field, rules in cls.VALIDATION_RULES.items():
            value = data.get(field)
            if value is not None:
                if value < rules['min'] or value > rules['max']:
                    issues.append(
                        f"{field}={value} outside valid range "
                        f"[{rules['min']}, {rules['max']}]"
                    )
        
        # Consistency validation
        funding = data.get('funding_raised')
        valuation = data.get('valuation')
        if funding and valuation and funding > valuation:
            issues.append(
                f"Funding ({funding}) > valuation ({valuation}) - unusual"
            )
        
        # Required fields
        required = ['company_name']
        for field in required:
            if not data.get(field):
                issues.append(f"Required field '{field}' is missing")
        
        return issues
    
    @classmethod
    def clean_company_data(cls, data: dict) -> dict:
        """Clean and normalize company data."""
        cleaned = data.copy()
        
        # Normalize strings
        if 'company_name' in cleaned:
            cleaned['company_name'] = cleaned['company_name'].strip()
        
        # Convert types
        if 'employees' in cleaned and cleaned['employees']:
            cleaned['employees'] = int(cleaned['employees'])
        
        # Remove impossible values
        if 'revenue' in cleaned and cleaned['revenue'] is not None:
            if cleaned['revenue'] < 0:
                cleaned['revenue'] = None  # Flag as missing
        
        return cleaned

# Usage in run_eneve_199.py
from solstein.validation import CompanyValidator

for company_data in companies_raw:
    # Validate
    issues = CompanyValidator.validate_company_data(company_data)
    if issues:
        logger.warning(f"Validation issues for {company_data.get('company_name')}: {issues}")
    
    # Clean
    cleaned_data = CompanyValidator.clean_company_data(company_data)
    
    # Convert
    company = convert_json_to_company(cleaned_data)
```

---

### Story 13.2: Add Data Quality Scoring
**Priority:** P0 | **Effort:** 2 points

**Description:**
Calculate data quality score for each company based on completeness and validity.

**Acceptance Criteria:**
- [ ] Define data quality metrics
- [ ] Calculate completeness score (% of fields present)
- [ ] Calculate confidence score (average of confidence levels)
- [ ] Calculate validity score (no validation errors)
- [ ] Combine into overall data quality score (0-1)
- [ ] Display quality score in output

**Implementation:**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DataQualityMetrics:
    """Data quality metrics for a company."""
    completeness_score: float  # 0-1
    confidence_score: float  # 0-1
    validity_score: float  # 0-1
    overall_score: float  # 0-1
    
    missing_fields: list[str]
    validation_errors: list[str]
    low_confidence_fields: list[str]

class DataQualityScorer:
    """Calculate data quality scores."""
    
    # Fields that should be present for complete data
    REQUIRED_FIELDS = [
        'revenue', 'employees', 'growth_rate',
        'funding_raised', 'valuation'
    ]
    
    # Fields that are nice to have
    OPTIONAL_FIELDS = [
        'description', 'website', 'ai_maturity',
        'geographic_presence'
    ]
    
    def calculate_quality(self, company: Company) -> DataQualityMetrics:
        """Calculate data quality metrics."""
        
        # Completeness
        completeness, missing = self._calculate_completeness(company)
        
        # Confidence
        confidence, low_confidence = self._calculate_confidence(company)
        
        # Validity
        validity, errors = self._calculate_validity(company)
        
        # Overall (weighted average)
        overall = (
            completeness * 0.4 +
            confidence * 0.4 +
            validity * 0.2
        )
        
        return DataQualityMetrics(
            completeness_score=completeness,
            confidence_score=confidence,
            validity_score=validity,
            overall_score=overall,
            missing_fields=missing,
            validation_errors=errors,
            low_confidence_fields=low_confidence
        )
    
    def _calculate_completeness(self, company: Company) -> tuple[float, list[str]]:
        """Calculate completeness score."""
        present = 0
        missing = []
        
        for field in self.REQUIRED_FIELDS:
            value = getattr(company.financials, field, None)
            if value is not None:
                present += 1
            else:
                missing.append(field)
        
        score = present / len(self.REQUIRED_FIELDS)
        return score, missing
    
    def _calculate_confidence(self, company: Company) -> tuple[float, list[str]]:
        """Calculate confidence score."""
        if not company.signal_confidences:
            return 0.0, ['all']
        
        confidences = list(company.signal_confidences.values())
        avg_confidence = sum(confidences) / len(confidences)
        
        low_confidence = [
            field for field, conf in company.signal_confidences.items()
            if conf < 0.5
        ]
        
        return avg_confidence, low_confidence
    
    def _calculate_validity(self, company: Company) -> tuple[float, list[str]]:
        """Calculate validity score."""
        from solstein.validation import CompanyValidator
        
        data = company.model_dump()
        errors = CompanyValidator.validate_company_data(data)
        
        # Score based on number of errors
        if not errors:
            return 1.0, []
        elif len(errors) <= 2:
            return 0.5, errors
        else:
            return 0.0, errors
```

---

### Story 13.3: Add Quality Reporting
**Priority:** P1 | **Effort:** 1 point

**Description:**
Add data quality reporting to identify dataset-wide issues.

**Acceptance Criteria:**
- [ ] Generate quality report for entire dataset
- [ ] Identify companies with poor quality
- [ ] Show quality distribution
- [ ] Recommend data improvements
- [ ] Export quality report

**Implementation:**
```python
class DataQualityReport:
    """Generate data quality reports."""
    
    def generate_report(self, companies: list[Company]) -> dict:
        """Generate quality report for dataset."""
        scorer = DataQualityScorer()
        
        metrics = [scorer.calculate_quality(c) for c in companies]
        
        report = {
            'total_companies': len(companies),
            'average_quality': sum(m.overall_score for m in metrics) / len(metrics),
            'quality_distribution': {
                'high': sum(1 for m in metrics if m.overall_score >= 0.8),
                'medium': sum(1 for m in metrics if 0.5 <= m.overall_score < 0.8),
                'low': sum(1 for m in metrics if m.overall_score < 0.5),
            },
            'common_issues': self._aggregate_issues(metrics),
            'low_quality_companies': [
                {
                    'name': companies[i].name,
                    'quality': m.overall_score,
                    'issues': m.validation_errors + m.missing_fields
                }
                for i, m in enumerate(metrics)
                if m.overall_score < 0.5
            ]
        }
        
        return report
    
    def _aggregate_issues(self, metrics: list[DataQualityMetrics]) -> dict:
        """Aggregate common issues across dataset."""
        from collections import Counter
        
        all_missing = []
        all_errors = []
        
        for m in metrics:
            all_missing.extend(m.missing_fields)
            all_errors.extend(m.validation_errors)
        
        return {
            'most_common_missing': Counter(all_missing).most_common(5),
            'most_common_errors': Counter(all_errors).most_common(5)
        }
```

---

## Dependencies

- Story 13.1 should be done first
- Story 13.2 depends on 13.1
- Story 13.3 can be done in parallel with 13.2

## Definition of Done

- [ ] Input validation in place
- [ ] Data quality scores calculated
- [ ] Quality reports generated
- [ ] Invalid data rejected or flagged
- [ ] Documentation updated
