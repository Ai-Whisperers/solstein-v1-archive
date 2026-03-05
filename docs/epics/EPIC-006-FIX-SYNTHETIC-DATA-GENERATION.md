# EPIC-006: Fix Synthetic Data Generation

## Status: 🟡 HIGH
## Priority: P1 - Major Impact
## Effort: 5 story points
## Sprint: Required for realistic test data

---

## Problem Statement

The synthetic data generator has **multiple bugs** that produce unrealistic and inconsistent data. The generated data is used for 196/199 companies, making these bugs critical for data quality.

### Current Broken State
```python
# Line 198 - Classification bug
growth_rate = 0.25  # 25% stored as decimal
"classification": "Phoenix" if growth_rate > 30 else "Salt" if growth_rate > 10 else "Lead"
# 0.25 > 30 is False, 0.25 > 10 is False → ALL classified as "Lead"

# Line 188 - Website URL bug
"website": f"https://{self.generate_company_name().lower()}.com"
# Calls generate_company_name() AGAIN → different name than company!

# Line 110 - 50% empty connector probability
if random.random() < 0.5:
    return connectors  # Half have NO data sources
```

### Additional Issues
- **38 duplicate company names** from limited namespace
- **Templated descriptions** - 56 companies use identical pattern
- **No random seed** - data not reproducible
- **Unrealistic EBITDA margins** - range too narrow

### Impact
- **196/199 companies are synthetic** (98.5% of dataset)
- **ALL synthetic companies classified as "Lead"** (wrong)
- **Website URLs don't match company names**
- **Half of companies have no data sources**
- **38 duplicate names** cause ID collisions

---

## Success Criteria

- [ ] Classification uses correct decimal comparison (0.25 > 0.30)
- [ ] Website URLs match company names
- [ ] Unique company names (no duplicates)
- [ ] Realistic description variety (not templated)
- [ ] Reproducible with random seed
- [ ] All companies have at least 2 data sources
- [ ] EBITDA margins in realistic range (10-40%)

---

## Technical Analysis

### Root Causes
1. **Classification logic** compares decimal growth to percentage thresholds
2. **Website generation** calls name generator twice
3. **Name space too small** - 23 prefixes × 18 suffixes = 414 max
4. **No deduplication** - doesn't check for existing names
5. **No random seed** - different output each run

### Affected Files
- `scripts/generate_synthetic_companies.py` (main issue)
- `tests/fixtures/synthetic/competitor_data_199.json` (output)

---

## Stories

### Story 6.1: Fix Classification Logic
**Priority:** P0 | **Effort:** 1 point

**Description:**
Fix the classification comparison to use decimal values instead of percentages.

**Acceptance Criteria:**
- [ ] Compare growth_rate (0.25) against 0.30 (not 30)
- [ ] Phoenix: growth > 30% (0.30)
- [ ] Salt: growth > 10% (0.10)
- [ ] Lead: growth ≤ 10% (0.10)
- [ ] Regenerate data and verify distribution

**Implementation:**
```python
# OLD (buggy):
"classification": "Phoenix" if growth_rate > 30 else "Salt" if growth_rate > 10 else "Lead",

# NEW (fixed):
growth_decimal = growth_rate / 100  # Convert percentage to decimal
if growth_decimal > 0.30:
    classification = "Phoenix"
elif growth_decimal > 0.10:
    classification = "Salt"
else:
    classification = "Lead"
```

---

### Story 6.2: Fix Website URL Generation
**Priority:** P0 | **Effort:** 1 point

**Description:**
Fix website URL generation to use the company name, not generate a new one.

**Acceptance Criteria:**
- [ ] Website URL uses same name as company
- [ ] No spaces in domain name
- [ ] Handle special characters (., -, etc.)
- [ ] Verify all URLs match company names

**Implementation:**
```python
# OLD (buggy):
"website": f"https://{self.generate_company_name().lower().replace(' ', '')}.com"

# NEW (fixed):
company_name = self.generate_company_name()
website = f"https://{company_name.lower().replace(' ', '').replace('-', '')}.com"
# Use company_name for the rest of the company data
```

---

### Story 6.3: Eliminate Duplicate Company Names
**Priority:** P0 | **Effort:** 2 points

**Description:**
Fix name generation to ensure all 196 synthetic companies have unique names.

**Acceptance Criteria:**
- [ ] Track generated names to prevent duplicates
- [ ] Expand name space if needed (more prefixes/suffixes)
- [ ] Add numeric suffix for collisions (e.g., "PowerFlow-2")
- [ ] Verify 196 unique names in output
- [ ] No company IDs collide

**Implementation:**
```python
def __init__(self, count: int = 196):
    self.generated_names = set()
    self.count = count
    # Expand name space
    self.prefixes = [...]  # Add more prefixes
    self.suffixes = [...]  # Add more suffixes
    self.connectors = [...]  # Add more connectors

def generate_company_name(self) -> str:
    """Generate unique company name."""
    max_attempts = 1000
    for _ in range(max_attempts):
        name = self._generate_name_attempt()
        if name not in self.generated_names:
            self.generated_names.add(name)
            return name

    # Fallback: add numeric suffix
    base_name = self._generate_name_attempt()
    counter = 2
    while f"{base_name}-{counter}" in self.generated_names:
        counter += 1
    unique_name = f"{base_name}-{counter}"
    self.generated_names.add(unique_name)
    return unique_name
```

---

### Story 6.4: Improve Description Variety
**Priority:** P1 | **Effort:** 2 points

**Description:**
Generate more varied and realistic company descriptions instead of rigid templates.

**Acceptance Criteria:**
- [ ] Create description templates with variations
- [ ] Include company-specific details (founded year, employees, etc.)
- [ ] Vary sentence structure and vocabulary
- [ ] No more than 5% identical descriptions
- [ ] Descriptions sound natural and professional

**Implementation:**
```python
DESCRIPTION_TEMPLATES = [
    "{name} is a {industry} company founded in {year} with {employees} employees. They specialize in {specialty} and have achieved {growth}% YoY growth.",
    "Founded in {year}, {name} operates in the {industry} sector. With {employees} team members, they focus on {specialty} and maintain {margin}% EBITDA margins.",
    "{name} delivers {specialty} solutions to the {industry} market. Established in {year}, the company has grown to {employees} employees with {revenue}M in revenue.",
    # Add 10+ more templates
]

def generate_description(self, company_data: dict) -> str:
    """Generate varied company description."""
    template = random.choice(self.DESCRIPTION_TEMPLATES)
    return template.format(
        name=company_data["company_name"],
        industry=company_data["industry"],
        year=company_data["founded_year"],
        employees=company_data["employees"],
        specialty=random.choice(self.SPECIALTIES),
        growth=company_data["revenue"]["timeline"][0]["yoy_growth_pct"],
        margin=company_data["profitability"]["ebitda_margin_pct"],
        revenue=company_data["revenue"]["timeline"][0]["eur_millions"],
    )
```

---

### Story 6.5: Add Random Seed for Reproducibility
**Priority:** P1 | **Effort:** 1 point

**Description:**
Add configurable random seed for reproducible data generation.

**Acceptance Criteria:**
- [ ] Accept seed parameter in constructor
- [ ] Use seed for all random operations
- [ ] Same seed produces identical output
- [ ] Document default seed in code
- [ ] Allow seed=None for random generation

**Implementation:**
```python
def __init__(self, count: int = 196, seed: int = 42):
    self.count = count
    self.seed = seed
    if seed is not None:
        random.seed(seed)
    self.generated_names = set()
    # ... rest of initialization

# Usage
python scripts/generate_synthetic_companies.py --seed 42
```

---

### Story 6.6: Fix Connector Probability
**Priority:** P1 | **Effort:** 1 point

**Description:**
Fix the 50% empty connector probability so all companies have data sources.

**Acceptance Criteria:**
- [ ] Remove or reduce empty connector probability
- [ ] Ensure all companies have 2-5 data sources
- [ ] Distribution: 2 sources (20%), 3 sources (40%), 4 sources (30%), 5 sources (10%)

**Implementation:**
```python
# OLD (buggy):
if random.random() < 0.5:
    return connectors  # 50% chance of NO connectors

# NEW (fixed):
# Always assign connectors, but vary the count
num_connectors = random.choices(
    [2, 3, 4, 5],
    weights=[20, 40, 30, 10]
)[0]
connectors = random.sample(available_connectors, num_connectors)
```

---

## Dependencies

- Story 6.1 and 6.2 are critical - fix bugs
- Story 6.3 required for data integrity
- Stories 6.4-6.6 are improvements (P1)

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| New data breaks existing tests | Medium | Update tests with new data |
| Unique name generation too slow | Low | Optimize algorithm, add caching |
| Description variety still limited | Low | Add more templates over time |

## Definition of Done

- [ ] All synthetic companies have correct classification
- [ ] Website URLs match company names
- [ ] 196 unique company names (no duplicates)
- [ ] Description variety > 95% unique
- [ ] Reproducible with random seed
- [ ] All companies have 2-5 data sources
- [ ] Data passes quality validation
