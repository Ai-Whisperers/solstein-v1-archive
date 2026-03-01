# EPIC-010: Fix Company Model and ID Generation

## Status: 🔴 CRITICAL
## Priority: P0 - System Blocking
## Effort: 5 story points
## Sprint: Required for data integrity

---

## Problem Statement

The company ID generation and model structure have **critical flaws** causing data collisions and field access inconsistencies.

### Current Broken State
```python
# In run_eneve_199.py line 68 - ID generation
def convert_json_to_company(data: dict) -> Company:
    return Company(
        id=data.get("company_name", "unknown").lower().replace(" ", "-").replace(".", ""),
        # "SyncEnergy" appears 3 times → 3 companies with ID "syncenergy"
    )

# Field access inconsistency
# Company model has: profit_margin (top level)
# But data stored in: financials.profit_margin (nested)
# Excel export tries: p.profit_margin (None)
# Should be: p.financials.profit_margin
```

### Impact
- **32 duplicate company IDs** causing data collisions
- **Field access patterns inconsistent** throughout codebase
- ** profit_margin and ebitda_margin always None** at Company level
- **Data integrity compromised** - cannot uniquely identify companies

---

## Success Criteria

- [ ] All 199 companies have unique IDs
- [ ] ID generation is deterministic and collision-free
- [ ] Field access patterns standardized
- [ ] Company model fields match actual data structure
- [ ] No more top-level fields that should be nested

---

## Technical Analysis

### Root Causes
1. **Simple name-based ID generation** doesn't handle duplicates
2. **No deduplication logic** in ID generation
3. **Company model has fields** that should be in FinancialMetric
4. **Inconsistent access patterns** - some code uses company.field, other uses company.financials.field

### Affected Files
- `src/solstein/domain/models.py`
- `scripts/run_eneve_199.py`
- `src/solstein/exporters/excel.py`
- `src/solstein/exporters/markdown/company.py`

---

## Stories

### Story 10.1: Implement Unique ID Generation
**Priority:** P0 | **Effort:** 2 points

**Description:**
Fix ID generation to ensure all companies have unique, deterministic IDs.

**Acceptance Criteria:**
- [ ] Track generated IDs to prevent duplicates
- [ ] Add numeric suffix for collisions (e.g., "syncenergy-2")
- [ ] Use slugify for consistent ID format
- [ ] Handle special characters in company names
- [ ] Verify 199 unique IDs in output

**Implementation:**
```python
import hashlib
from slugify import slugify

class CompanyIDGenerator:
    """Generate unique, deterministic company IDs."""
    
    def __init__(self):
        self.generated_ids = set()
    
    def generate_id(self, company_name: str, index: int = None) -> str:
        """Generate unique ID for company.
        
        Args:
            company_name: Name of the company
            index: Optional index for guaranteed uniqueness
        
        Returns:
            Unique company ID
        """
        base_id = slugify(company_name, separator="-")
        
        if base_id not in self.generated_ids:
            self.generated_ids.add(base_id)
            return base_id
        
        # Handle collision with suffix
        if index is not None:
            unique_id = f"{base_id}-{index}"
        else:
            counter = 2
            while f"{base_id}-{counter}" in self.generated_ids:
                counter += 1
            unique_id = f"{base_id}-{counter}"
        
        self.generated_ids.add(unique_id)
        return unique_id

# Usage in run_eneve_199.py
id_generator = CompanyIDGenerator()
for i, company_data in enumerate(companies_raw):
    company_id = id_generator.generate_id(
        company_data.get("company_name", "unknown"),
        index=i
    )
```

---

### Story 10.2: Standardize Field Access Patterns
**Priority:** P0 | **Effort:** 2 points

**Description:**
Audit and standardize field access patterns throughout codebase to use consistent nested structure.

**Acceptance Criteria:**
- [ ] Audit all field access in exporters
- [ ] Move top-level fields to FinancialMetric where appropriate
- [ ] Update all access patterns to use company.financials.field
- [ ] Remove or deprecate top-level aliases
- [ ] Add property accessors for backward compatibility (if needed)

**Implementation:**
```python
# In domain/models.py - standardize structure
class Company(BaseModel):
    """Standardized company model."""
    
    # Identity
    id: str
    name: str
    
    # Financial data - ALL in nested structure
    financials: FinancialMetric
    
    # Remove top-level fields that duplicate financials
    # profit_margin: Optional[float] = None  # REMOVED - use financials.profit_margin
    # ebitda_margin: Optional[float] = None  # REMOVED - use financials.ebitda_margin
    
    # Backward compatibility properties (optional)
    @property
    def profit_margin(self) -> Optional[float]:
        """Backward compatibility - use financials.profit_margin instead."""
        return self.financials.profit_margin if self.financials else None

# Update all exporters
# OLD:
# f"{p.profit_margin:.1f}%"

# NEW:
# f"{p.financials.profit_margin:.1f}%" if p.financials else "N/A"
```

---

### Story 10.3: Add Company Model Validation
**Priority:** P1 | **Effort:** 1 point

**Description:**
Add validation to Company model to ensure data integrity.

**Acceptance Criteria:**
- [ ] Validate ID is unique across dataset
- [ ] Validate required fields are present
- [ ] Validate financials are consistent
- [ ] Add validation errors to output
- [ ] Log validation failures

**Implementation:**
```python
# In domain/models.py
class Company(BaseModel):
    ...
    
    @validator('id')
    def id_must_be_unique(cls, v, values):
        # Note: Actual uniqueness check happens at dataset level
        if not v or v == "unknown":
            raise ValueError("Company ID cannot be empty or 'unknown'")
        return v
    
    @validator('financials')
    def financials_must_be_consistent(cls, v):
        if v:
            # Validate revenue and employees are positive
            if v.revenue is not None and v.revenue < 0:
                raise ValueError("Revenue cannot be negative")
            if v.employees is not None and v.employees < 0:
                raise ValueError("Employees cannot be negative")
        return v

# Dataset-level validation
def validate_company_dataset(companies: list[Company]) -> list[str]:
    """Validate entire company dataset."""
    errors = []
    
    # Check for duplicate IDs
    ids = [c.id for c in companies]
    duplicates = [id for id in set(ids) if ids.count(id) > 1]
    if duplicates:
        errors.append(f"Duplicate company IDs found: {duplicates}")
    
    # Check each company
    for company in companies:
        if not company.name:
            errors.append(f"Company {company.id} has no name")
        if not company.financials:
            errors.append(f"Company {company.id} has no financials")
    
    return errors
```

---

## Dependencies

- Story 10.1 is critical - must be done first
- Story 10.2 should follow immediately
- Story 10.3 can be done in parallel with 10.2

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| ID changes break existing references | High | Migration script, backward compatibility |
| Field access changes break exporters | High | Comprehensive testing |

## Definition of Done

- [ ] All 199 companies have unique IDs
- [ ] Field access patterns standardized
- [ ] Company model validation passing
- [ ] No duplicate IDs in output
- [ ] All exporters working with new structure
