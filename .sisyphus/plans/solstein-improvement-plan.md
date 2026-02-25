# Solstein Platform Improvement Plan

## TL;DR

> **Objective**: Fix critical data quality issues (84% NULL values), unify inconsistent data sources, repair broken scoring logic, and overhaul the classification system to deliver trustworthy PE competitive intelligence.
> 
> **Effort**: Large (~40-50 hours across 5 phases)
> **Parallel Execution**: Yes - 5 waves with 4-6 tasks each
> **Success Criteria**: 
> - Data completeness: >70% (from 16%)
> - Scoring consistency: <0.5 point variance between runs
> - Classification distribution: Balanced across Phoenix/Salt/Lead
> - Zero contradictory data between markdown/JSON sources

---

## Context

### Critical Issues Identified

| Issue | Severity | Impact |
|-------|----------|--------|
| 84.4% NULL revenue data | 🔴 Critical | Analysis based on 16% actual data |
| Data source duality (JSON vs Markdown) | 🔴 Critical | Same company has two different realities |
| Scoring inconsistency (4.3 point swing) | 🔴 Critical | Non-deterministic algorithm |
| 94% classified as "Salt" | 🟡 High | No meaningful differentiation |
| Rev/employee calculation bug | 🟡 High | Penalizes companies incorrectly |
| AI scoring contradictions | 🟡 High | "Strong" AI → 0/10 score |
| Universal 1.0 confidence weight | 🟡 High | Confidence theater - no variance |
| Generic report filler | 🟡 High | "No strengths identified" for €30M company |
| Geographic data destruction | 🟠 Medium | 7 countries → "Europe" |
| SaaS maturity default 5/10 | 🟠 Medium | 94% identical scores |

### Root Causes

1. **Data Pipeline Fragmentation**: Two separate loaders (`MarkdownExtractor` vs `CompetitorDataLoader`) with different logic
2. **Missing Data Quality Gates**: No validation of NULL thresholds before analysis
3. **Oversimplified Scoring**: Linear formulas with hard caps ignore business realities
4. **Classification Compression**: Score ranges too narrow force everything into "Salt"
5. **Report Template Rigidity**: Static templates don't adapt to actual data availability

---

## Work Objectives

### Core Objective
Transform Solstein from a "data desert with a pretty Excel export" into a trustworthy competitive intelligence platform with consistent, explainable, and actionable analysis.

### Concrete Deliverables

1. **Unified Data Layer**: Single source of truth for company data
2. **Data Quality Framework**: Validation, completeness scoring, and missing data handling
3. **Deterministic Scoring Engine**: Same inputs → same outputs, every time
4. **Balanced Classification System**: Meaningful distribution across Phoenix/Salt/Lead
5. **Smart Report Generator**: Context-aware templates that adapt to data availability
6. **Confidence-Based Weighting**: Real confidence scores (not universal 1.0)
7. **Revenue Per Employee Fix**: Correct calculation bug
8. **Geographic Standardization**: Preserve specificity (7 countries, not "Europe")
9. **AI Scoring Consistency**: Align AI maturity → AI score → report narrative
10. **Tier Logic Correction**: €32.5M = Tier 3 (not Tier 2)

### Definition of Done

- [ ] All 199 companies have revenue data OR explicit "Data Unavailable" flag
- [ ] Eneve analysis identical across 10 consecutive runs (<0.2 point variance)
- [ ] Classification distribution: Phoenix 15-25%, Salt 60-70%, Lead 10-20%
- [ ] Reports contain zero contradictory statements
- [ ] Rev/employee calculation uses actual revenue ÷ actual employees
- [ ] Confidence weights range from 0.3 (estimated) to 1.0 (confirmed)
- [ ] Geographic presence shows specific countries, not continents
- [ ] All tests pass: pytest tests/ --cov=solstein -v

### Must Have
- Data unification layer
- NULL handling strategy
- Deterministic scoring
- Balanced classification
- Bug fixes (rev/employee, tier logic)

### Must NOT Have
- Breaking changes to existing API endpoints
- Removal of current file formats (backward compatibility)
- Introduction of new external dependencies without review
- Changes to Excel export format (client-facing)

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest configured)
- **Automated tests**: YES - will add specific regression tests
- **Framework**: pytest with fixtures for golden datasets

### QA Policy
Every task includes agent-executed verification scenarios:
- **Data tasks**: Python validation scripts with assertions
- **Logic tasks**: Unit tests with known inputs/outputs
- **Integration tasks**: End-to-end pipeline runs with comparison

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - Data Quality & Unification):
├── Task 1: Audit all data sources and create data quality report
├── Task 2: Design unified CompanyData model (JSON + Markdown merge)
├── Task 3: Implement data completeness scoring
└── Task 4: Create NULL handling strategy (interpolation vs flagging)

Wave 2 (Core Logic - Scoring Fixes):
├── Task 5: Fix revenue per employee calculation bug
├── Task 6: Repair tier classification logic (€32.5M → Tier 3)
├── Task 7: Implement deterministic scoring (remove randomness)
└── Task 8: Add confidence-based weighting (0.3-1.0 range)

Wave 3 (Classification System):
├── Task 9: Expand classification score ranges
├── Task 10: Implement Phoenix/Salt/Lead distribution targets
├── Task 11: Add classification confidence scoring
└── Task 12: Fix AI maturity → AI score mapping

Wave 4 (Reporting & Exports):
├── Task 13: Create context-aware report templates
├── Task 14: Implement geographic specificity preservation
├── Task 15: Add data quality indicators to reports
└── Task 16: Fix contradictory narrative generation

Wave 5 (Testing & Validation):
├── Task 17: Create golden dataset regression tests
├── Task 18: Run Eneve consistency validation (10 runs)
├── Task 19: Validate classification distribution
└── Task 20: Full pipeline integration test

Wave FINAL (Review & Documentation):
├── Task F1: Code quality review (ruff, mypy)
├── Task F2: Documentation update
└── Task F3: Deployment guide
```

### Dependency Matrix

| Task | Blocks | Blocked By |
|------|--------|------------|
| 1 (Audit) | 2, 3, 4 | None |
| 2 (Unified Model) | 5, 6, 7, 8 | 1 |
| 3 (Completeness) | 13, 14, 15 | 1 |
| 5 (Rev/Emp Fix) | 17 | 2 |
| 6 (Tier Fix) | 17 | 2 |
| 7 (Deterministic) | 17, 18 | 2 |
| 9 (Classification) | 10, 11 | 7 |
| 17 (Regression Tests) | 18, 19, 20 | 5, 6, 7, 8 |

---

## TODOs


- [ ] 1. **Data Source Audit and Quality Report**

  **What to do**:
  - Scan all 199 companies in competitor_data.json
  - Catalog NULL/None values per field (revenue, growth, employees, etc.)
  - Identify data completeness by source (JSON vs Markdown)
  - Generate data quality heatmap
  - Document data lineage: where does each field come from?

  **Must NOT do**:
  - Modify any data files (read-only audit)
  - Delete or alter existing records

  **Recommended Agent Profile**:
  - **Category**: `deep` (requires understanding data architecture)
  - **Skills**: None (pure Python/data analysis)

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1 foundation)
  - **Blocks**: Tasks 2, 3, 4
  - **Blocked By**: None

  **References**:
  - `data/input/competitor_data.json` - Main dataset (199 companies)
  - `src/solstein/data/loaders.py` - Current loading logic
  - `src/solstein/extractors/markdown_extractor.py` - Markdown parsing

  **Acceptance Criteria**:
  - [ ] JSON report saved: `data/output/data_quality_audit.json`
  - [ ] Completeness % per field documented
  - [ ] Markdown vs JSON comparison table generated
  - [ ] Top 10 most complete companies identified
  - [ ] Top 10 least complete companies identified

  **QA Scenarios**:
  ```
  Scenario: Validate audit completeness
    Tool: Bash (python script)
    Preconditions: None
    Steps:
      1. Run: python scripts/audit_data_quality.py
      2. Verify: data/output/data_quality_audit.json exists
      3. Check: JSON contains 'completeness_percentages' key
      4. Assert: revenue_completeness field is a number between 0-100
    Expected Result: Audit report generated with all required fields
    Evidence: .sisyphus/evidence/task-1-audit-complete.json
  ```

  **Commit**: YES
  - Message: `feat(data): add comprehensive data quality audit`
  - Files: `scripts/audit_data_quality.py`, `data/output/data_quality_audit.json`

---

- [ ] 2. **Design Unified CompanyData Model**

  **What to do**:
  - Create unified schema that merges JSON + Markdown fields
  - Define field priority: which source wins when conflicts exist?
  - Implement merge logic with conflict resolution
  - Add 'data_source' tracking per field
  - Create validation rules for each field type

  **Must NOT do**:
  - Break existing Company domain model (extend, don't replace)
  - Remove backward compatibility

  **Recommended Agent Profile**:
  - **Category**: `deep` (architectural design)
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 1 audit results)
  - **Blocks**: Tasks 5, 6, 7, 8
  - **Blocked By**: Task 1

  **References**:
  - `src/solstein/domain/models.py` - Existing Company model
  - `src/solstein/data/loaders.py` - JSON loading logic
  - `src/solstein/extractors/markdown_extractor.py` - Markdown extraction
  - Data quality audit results from Task 1

  **Acceptance Criteria**:
  - [ ] New file: `src/solstein/data/unified_loader.py`
  - [ ] UnifiedCompany model created with source tracking
  - [ ] Merge logic handles all conflicts from audit
  - [ ] Eneve merge produces single consistent record
  - [ ] Unit tests: 100% coverage for merge logic

  **QA Scenarios**:
  ```
  Scenario: Eneve data unification
    Tool: Bash (pytest)
    Preconditions: Task 1 complete
    Steps:
      1. Load Eneve from JSON: 135 employees, €32.5M revenue
      2. Load Eneve from Markdown: 130 employees, €30M revenue
      3. Run unified merge with priority: Markdown > JSON
      4. Verify: Result has 130 employees, €30M revenue
      5. Verify: data_source fields track origin
    Expected Result: Single unified record with provenance
    Evidence: .sisyphus/evidence/task-2-unified-eneve.json
  ```

  **Commit**: YES
  - Message: `feat(data): implement unified data model with conflict resolution`
  - Files: `src/solstein/data/unified_loader.py`, `tests/test_unified_loader.py`

---

- [ ] 3. **Implement Data Completeness Scoring**

  **What to do**:
  - Create completeness scoring algorithm (0-100 per company)
  - Weight critical fields: revenue (30%), growth (25%), employees (20%), etc.
  - Add 'data_quality_tier' enum: COMPLETE, PARTIAL, MINIMAL, INSUFFICIENT
  - Implement threshold-based flags for analysis eligibility
  - Add completeness scores to Company model

  **Must NOT do**:
  - Reject companies from analysis (flag only, don't filter)
  - Make completeness scoring required for existing flows (opt-in)

  **Recommended Agent Profile**:
  - **Category**: `quick` (well-defined algorithm)
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 2)
  - **Blocks**: Tasks 13, 14, 15 (data quality indicators)
  - **Blocked By**: Task 1

  **References**:
  - `src/solstein/domain/models.py` - Add completeness_score field
  - Data quality audit (Task 1) - Field importance weights

  **Acceptance Criteria**:
  - [ ] CompletenessCalculator class implemented
  - [ ] All 199 companies have completeness scores
  - [ ] Top quartile: >80% complete, Bottom: <30% complete
  - [ ] Eneve completeness score documented

  **QA Scenarios**:
  ```
  Scenario: Completeness scoring validation
    Tool: Bash (python)
    Steps:
      1. Run completeness calculator on all 199 companies
      2. Verify: Envision Digital has high score (>85%)
      3. Verify: Companies with NULL revenue get low score (<40%)
      4. Check: Distribution is reasonable (not all same score)
    Expected Result: Range of scores reflecting actual data quality
    Evidence: .sisyphus/evidence/task-3-completeness-scores.csv
  ```

  **Commit**: YES
  - Message: `feat(scoring): add data completeness scoring system`
  - Files: `src/solstein/analytics/completeness.py`, tests/

---

- [ ] 4. **Create NULL Handling Strategy**

  **What to do**:
  - Define NULL handling strategies per field:
    - Revenue: Interpolate from timeline OR flag as unavailable
    - Growth: Calculate from timeline OR use sector average
    - Employees: Use last known OR estimate from revenue
  - Implement interpolation logic for missing timeline points
  - Add 'is_interpolated' flags to distinguish real vs estimated data
  - Create configuration for interpolation thresholds

  **Must NOT do**:
  - Invent data without clear provenance (always flag interpolations)
  - Use sector averages without labeling them as such

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high` (business logic decisions)
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 2, 3)
  - **Blocks**: None (strategy document)
  - **Blocked By**: Task 1

  **References**:
  - Revenue timeline interpolation patterns
  - Sector growth rate benchmarks

  **Acceptance Criteria**:
  - [ ] NULL handling strategy document: `docs/data/null-handling-strategy.md`
  - [ ] Interpolation algorithms implemented
  - [ ] 'is_interpolated' field added to relevant metrics
  - [ ] Configuration file for interpolation thresholds

  **QA Scenarios**:
  ```
  Scenario: Revenue interpolation
    Tool: Bash (python)
    Steps:
      1. Take company with 2022: €10M, 2024: €15M, missing 2023
      2. Run interpolation
      3. Verify: 2023 estimated at €12.5M (linear)
      4. Verify: is_interpolated flag set to true
    Expected Result: Gap filled with geometric mean, flagged as estimated
    Evidence: .sisyphus/evidence/task-4-interpolation-test.json
  ```

  **Commit**: YES
  - Message: `feat(data): implement NULL interpolation with provenance tracking`
  - Files: `src/solstein/data/interpolation.py`, `docs/data/null-handling-strategy.md`

---

- [ ] 5. **Fix Revenue Per Employee Calculation Bug**

  **What to do**:
  - Investigate why 'rev_per_emp(0 EUR)' appears in scoring breakdown
  - Fix calculation: revenue / employees (not 0)
  - Add validation: if revenue or employees is NULL, skip this component
  - Add unit tests for edge cases (0 employees, NULL revenue, etc.)
  - Verify fix with Envision Digital (€450M / 1600 = €281K)

  **Must NOT do**:
  - Divide by zero (check for 0 employees)
  - Use default values when data is missing

  **Recommended Agent Profile**:
  - **Category**: `debugging/systematic-debugging`
  - **Skills**: `debugging/systematic-debugging`

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 2 unified model)
  - **Blocks**: Task 17 (regression tests)
  - **Blocked By**: Task 2

  **References**:
  - `src/solstein/analytics/scorers/financial_health.py` - Likely location of bug
  - `src/solstein/analytics/scoring.py` - Main scoring logic

  **Acceptance Criteria**:
  - [ ] Bug root cause identified and documented
  - [ ] Fix implemented and tested
  - [ ] Envision Digital shows €281K rev/employee (not 0)
  - [ ] Unit tests cover: normal case, NULL case, zero employees case

  **QA Scenarios**:
  ```
  Scenario: Verify rev/employee fix
    Tool: Bash (pytest)
    Steps:
      1. Load Envision Digital: revenue=450000000, employees=1600
      2. Run financial health scoring
      3. Check: scoring_breakdown contains rev_per_emp(281250 EUR)
      4. Verify: Operating Efficiency component uses correct value
    Expected Result: Positive adjustment based on €281K/employee
    Evidence: .sisyphus/evidence/task-5-rev-emp-fix.json
  ```

  **Commit**: YES
  - Message: `fix(scoring): correct revenue per employee calculation`
  - Files: `src/solstein/analytics/scorers/financial_health.py`, tests/

---

- [ ] 6. **Repair Tier Classification Logic**

  **What to do**:
  - Fix tier logic: €32.5M revenue should be Tier 3 (not Tier 2)
  - Audit all 199 companies' tier assignments
  - Ensure markdown extractor uses same logic as JSON loader
  - Add validation: revenue range → tier mapping
  - Document tier boundaries clearly

  **Must NOT do**:
  - Change tier boundaries (document current logic)
  - Allow inconsistent tier assignment between sources

  **Recommended Agent Profile**:
  - **Category**: `quick` (simple logic fix)
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 5)
  - **Blocks**: Task 17 (regression tests)
  - **Blocked By**: Task 2

  **References**:
  - `src/solstein/data/loaders.py:500-512` - _determine_tier method
  - `src/solstein/extractors/markdown_extractor.py` - Markdown tier extraction

  **Acceptance Criteria**:
  - [ ] Tier logic documented: Tier 1 (>€1B), Tier 2 (€100M-1B), Tier 3 (€10M-100M), Tier 4 (<€10M)
  - [ ] Eneve correctly classified as Tier 3
  - [ ] Markdown extractor updated to match JSON loader logic
  - [ ] All 199 companies have correct tier assignments

  **QA Scenarios**:
  ```
  Scenario: Tier classification validation
    Tool: Bash (python)
    Steps:
      1. Check Eneve: revenue=32.5M → tier should be Tier 3
      2. Check Octopus: revenue=14500M → tier should be Tier 1
      3. Check small startup: revenue=2M → tier should be Tier 4
      4. Verify: All tiers align with revenue boundaries
    Expected Result: Revenue-based tier assignment is consistent
    Evidence: .sisyphus/evidence/task-6-tier-validation.csv
  ```

  **Commit**: YES
  - Message: `fix(data): correct tier classification logic for Eneve and others`
  - Files: `src/solstein/data/loaders.py`, `src/solstein/extractors/markdown_extractor.py`

---

- [ ] 7. **Implement Deterministic Scoring Engine**

  **What to do**:
  - Identify source of scoring variance (4.3 point swing for Eneve)
  - Remove any randomness or non-deterministic elements
  - Ensure same inputs always produce same outputs
  - Add caching for expensive calculations
  - Document scoring algorithm version for reproducibility

  **Must NOT do**:
  - Use random sampling without fixed seeds
  - Rely on system time or external state

  **Recommended Agent Profile**:
  - **Category**: `debugging/systematic-debugging`
  - **Skills**: `debugging/systematic-debugging`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 5, 6)
  - **Blocks**: Tasks 17, 18 (regression tests, consistency validation)
  - **Blocked By**: Task 2

  **References**:
  - `src/solstein/analytics/scoring.py` - Main scoring entry point
  - `src/solstein/analytics/scorers/` - All scorer modules

  **Acceptance Criteria**:
  - [ ] Root cause of variance identified and documented
  - [ ] Fix implemented to ensure deterministic output
  - [ ] Eneve scores identical across 10 consecutive runs (<0.2 variance)
  - [ ] All 199 companies show <0.5 variance across 5 runs

  **QA Scenarios**:
  ```
  Scenario: Scoring consistency validation
    Tool: Bash (python)
    Steps:
      1. Run scoring on Eneve 10 times in a row
      2. Record growth_score, financial_health_score, composite_score each run
      3. Calculate variance: max(score) - min(score)
      4. Assert: variance < 0.2 for all scores
    Expected Result: Identical scores across all runs
    Evidence: .sisyphus/evidence/task-7-consistency-runs.json
  ```

  **Commit**: YES
  - Message: `fix(scoring): eliminate non-determinism from scoring engine`
  - Files: `src/solstein/analytics/scoring.py`, `src/solstein/analytics/scorers/`

---

- [ ] 8. **Implement Confidence-Based Weighting**

  **What to do**:
  - Replace universal confidence_weight: 1.0 with actual confidence scoring
  - Define confidence levels: CONFIRMED (1.0), ESTIMATED (0.7), UNKNOWN (0.3)
  - Apply confidence weights to each scoring component
  - Document confidence assignment criteria per data source
  - Add confidence transparency to scoring breakdown

  **Must NOT do**:
  - Use arbitrary confidence values (must be source-based)
  - Hide confidence from users (full transparency required)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high` (business logic)
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 5-7)
  - **Blocks**: Task 17 (regression tests)
  - **Blocked By**: Task 2

  **References**:
  - `src/solstein/domain/models.py` - ConfidenceLevel enum
  - `src/solstein/analytics/scorers/` - All scoring components

  **Acceptance Criteria**:
  - [ ] Confidence weights vary: 0.3, 0.7, 1.0 (not all 1.0)
  - [ ] Scoring breakdown shows confidence per component
  - [ ] CONFIRMED data gets full weight, UNKNOWN gets reduced
  - [ ] Eneve scoring reflects confidence in its data sources

  **QA Scenarios**:
  ```
  Scenario: Confidence weighting validation
    Tool: Bash (python)
    Steps:
      1. Create test company with confirmed revenue (1.0 weight)
      2. Create test company with estimated revenue (0.7 weight)
      3. Run scoring on both
      4. Verify: Confirmed revenue contributes more to score
    Expected Result: Different confidence = different score contribution
    Evidence: .sisyphus/evidence/task-8-confidence-weights.json
  ```

  **Commit**: YES
  - Message: `feat(scoring): implement confidence-based component weighting`
  - Files: `src/solstein/analytics/confidence_integration.py` (exists), updates to scorers/

---

- [ ] 9. **Expand Classification Score Ranges**

  **What to do**:
  - Analyze current score distribution (4.22 to 9.10 range)
  - Redesign classification boundaries for meaningful spread
  - Target distribution: Phoenix 15-25%, Salt 60-70%, Lead 10-20%
  - Implement new classification logic
  - Add 'classification_confidence' based on data quality

  **Must NOT do**:
  - Keep 94% as Salt (must differentiate more)
  - Make arbitrary cuts without statistical basis

  **Recommended Agent Profile**:
  - **Category**: `data-analysis`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 7 deterministic scores)
  - **Blocks**: Tasks 10, 11
  - **Blocked By**: Task 7

  **References**:
  - Current classification in `src/solstein/analytics/scoring.py`
  - Score distribution from Task 7 consistency runs

  **Acceptance Criteria**:
  - [ ] New classification boundaries documented
  - [ ] Phoenix: 15-25% of companies (not 6%)
  - [ ] Salt: 60-70% (not 94%)
  - [ ] Lead: 10-20% (not 0%)
  - [ ] Classification reflects actual competitive positioning

  **QA Scenarios**:
  ```
  Scenario: Classification distribution validation
    Tool: Bash (python)
    Steps:
      1. Run classification on all 199 companies with new boundaries
      2. Count Phoenix, Salt, Lead
      3. Verify: Phoenix >= 15% and <= 25%
      4. Verify: Salt >= 60% and <= 70%
      5. Verify: Lead >= 10% and <= 20%
    Expected Result: Balanced distribution across classes
    Evidence: .sisyphus/evidence/task-9-classification-dist.json
  ```

  **Commit**: YES
  - Message: `feat(classification): rebalance Phoenix/Salt/Lead distribution`
  - Files: `src/solstein/analytics/classification.py` (new), scoring updates

---

- [ ] 10. **Implement AI Maturity Consistency**

  **What to do**:
  - Fix AI maturity mapping: 'Strong' → AI score should be high (8-10)
  - Audit all AI maturity assignments vs AI scores
  - Ensure alignment: AI maturity → AI score → report narrative
  - Add validation: AI maturity and AI score must be consistent
  - Fix Eneve specifically: 'Strong' AI maturity but 0/10 score

  **Must NOT do**:
  - Allow contradictions between AI maturity and AI score
  - Report '0/10 AI' when maturity is 'Strong'

  **Recommended Agent Profile**:
  - **Category**: `quick` (logic fix)
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 9, 11)
  - **Blocks**: Task 16 (narrative generation)
  - **Blocked By**: Task 9

  **References**:
  - `src/solstein/domain/models.py` - AIMaturity enum
  - `src/solstein/data/loaders.py` - AI score calculation
  - Reports showing AI contradictions

  **Acceptance Criteria**:
  - [ ] AI maturity → AI score mapping documented
  - [ ] Strong → 8-10, Moderate → 4-7, Low → 0-3
  - [ ] Eneve AI score updated to match 'Strong' maturity
  - [ ] Zero contradictions between maturity and score

  **QA Scenarios**:
  ```
  Scenario: AI consistency validation
    Tool: Bash (python)
    Steps:
      1. Find all companies with 'Strong' AI maturity
      2. Verify: All have AI score >= 8
      3. Find all companies with 'Low' AI maturity
      4. Verify: All have AI score <= 3
    Expected Result: Perfect alignment between maturity and score
    Evidence: .sisyphus/evidence/task-10-ai-consistency.json
  ```

  **Commit**: YES
  - Message: `fix(scoring): align AI maturity with AI scores`
  - Files: `src/solstein/data/loaders.py`, `src/solstein/analytics/scorers/`

---

- [ ] 11. **Add Classification Confidence Scoring**

  **What to do**:
  - Calculate confidence in classification based on data quality
  - High completeness = high classification confidence
  - Add 'classification_confidence' field to Company model
  - Flag classifications with <0.7 confidence as 'tentative'
  - Document confidence calculation methodology

  **Must NOT do**:
  - Show high confidence when data is sparse
  - Hide uncertainty from users

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high` (algorithm design)
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 9, 10)
  - **Blocks**: Task 15 (data quality indicators)
  - **Blocked By**: Task 9

  **References**:
  - Completeness scores from Task 3
  - Classification logic from Task 9

  **Acceptance Criteria**:
  - [ ] Classification confidence calculation implemented
  - [ ] All companies have classification_confidence (0-1)
  - [ ] High completeness → high confidence mapping works
  - [ ] Reports show confidence level (e.g., 'Phoenix (85% confidence)')

  **QA Scenarios**:
  ```
  Scenario: Classification confidence validation
    Tool: Bash (python)
    Steps:
      1. Find company with >90% completeness
      2. Verify: classification_confidence > 0.9
      3. Find company with <30% completeness
      4. Verify: classification_confidence < 0.5
    Expected Result: Confidence reflects data quality
    Evidence: .sisyphus/evidence/task-11-classification-confidence.csv
  ```

  **Commit**: YES
  - Message: `feat(classification): add confidence scoring to classifications`
  - Files: `src/solstein/analytics/classification.py`, domain models

---

- [ ] 12. **Preserve Geographic Specificity**

  **What to do**:
  - Fix geographic data destruction (7 countries → 'Europe')
  - Ensure markdown extractor preserves country list
  - Update JSON loader to maintain geographic granularity
  - Add geographic standardization (country names, not continents)
  - Add geographic completeness scoring

  **Must NOT do**:
  - Reduce specific countries to continent-level
  - Lose geographic detail during data merge

  **Recommended Agent Profile**:
  - **Category**: `quick` (data preservation)
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Blocks**: Task 14 (geographic indicators)
  - **Blocked By**: Task 2

  **References**:
  - `src/solstein/extractors/markdown_extractor.py` - Geographic extraction
  - `src/solstein/data/loaders.py` - Geographic loading

  **Acceptance Criteria**:
  - [ ] Eneve shows 7 specific countries (not just 'Europe')
  - [ ] All companies maintain geographic granularity
  - [ ] Geographic standardization rules documented
  - [ ] No data loss during JSON/Markdown merge

  **QA Scenarios**:
  ```
  Scenario: Geographic specificity validation
    Tool: Bash (python)
    Steps:
      1. Load Eneve from unified model
      2. Verify: geographic_presence contains 7 countries
      3. Check: 'Netherlands', 'Belgium', 'Germany', etc. present
      4. Verify: No 'Europe' or continent-level entries
    Expected Result: Specific country list preserved
    Evidence: .sisyphus/evidence/task-12-geographic-specificity.json
  ```

  **Commit**: YES
  - Message: `fix(data): preserve geographic specificity in company profiles`
  - Files: `src/solstein/data/loaders.py`, `src/solstein/extractors/markdown_extractor.py`

---

- [ ] 13. **Create Context-Aware Report Templates**

  **What to do**:
  - Replace static templates with data-adaptive generation
  - If data is sparse → 'Limited data available for [metric]'
  - If data is rich → Deep analysis with specific numbers
  - Add 'strengths identified' section (even for Salt companies)
  - Create narrative templates per classification type

  **Must NOT do**:
  - Generate 'No significant strengths identified' for any company
  - Use generic filler when specific data exists

  **Recommended Agent Profile**:
  - **Category**: `writing` (template creation)
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Blocks**: Task 16 (narrative generation)
  - **Blocked By**: Task 3 (completeness scoring)

  **References**:
  - `src/solstein/exporters/markdown/generator.py` - Report generation
  - `src/solstein/presentation/` - Report templates

  **Acceptance Criteria**:
  - [ ] Context-aware templates created
  - [ ] Eneve report shows actual strengths (not 'none identified')
  - [ ] Templates adapt to data availability
  - [ ] No generic filler text in final reports

  **QA Scenarios**:
  ```
  Scenario: Context-aware report validation
    Tool: Bash (read generated report)
    Steps:
      1. Generate report for Eneve
      2. Verify: Contains specific strengths section
      3. Verify: No 'No significant strengths identified' text
      4. Verify: Data quality indicators shown
    Expected Result: Rich, specific analysis based on actual data
    Evidence: .sisyphus/evidence/task-13-context-report.md
  ```

  **Commit**: YES
  - Message: `feat(reports): implement context-aware report generation`
  - Files: `src/solstein/presentation/adaptive_templates.py`, generator updates

---

- [ ] 14. **Implement Data Quality Indicators in Reports**

  **What to do**:
  - Add visual indicators for data quality (✓ confirmed, ~ estimated, ? unknown)
  - Show completeness score in executive summary
  - Add 'Data Confidence' section to all reports
  - Flag interpolated or estimated data clearly
  - Create data provenance table per metric

  **Must NOT do**:
  - Hide data quality from users
  - Show high confidence when data is sparse

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering` (report formatting)
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 13)
  - **Blocks**: None
  - **Blocked By**: Task 3 (completeness scoring)

  **References**:
  - Completeness scores from Task 3
  - Report templates from Task 13

  **Acceptance Criteria**:
  - [ ] Data quality indicators added to all metrics
  - [ ] Completeness score shown in executive summary
  - [ ] Data provenance table included
  - [ ] Interpolated data clearly flagged

  **QA Scenarios**:
  ```
  Scenario: Data quality indicators validation
    Tool: Bash (read generated report)
    Steps:
      1. Generate report for company with mixed data quality
      2. Verify: Confirmed metrics marked with ✓
      3. Verify: Estimated metrics marked with ~
      4. Verify: Completeness score visible in summary
    Expected Result: Full transparency on data quality
    Evidence: .sisyphus/evidence/task-14-quality-indicators.md
  ```

  **Commit**: YES
  - Message: `feat(reports): add data quality indicators and provenance`
  - Files: `src/solstein/presentation/quality_indicators.py`, report templates

---

- [ ] 15. **Fix Contradictory Narrative Generation**

  **What to do**:
  - Audit all report narratives for contradictions
  - Fix AI maturity contradiction: 'Strong' maturity vs '0/10 AI score'
  - Ensure classification matches narrative tone
  - Add validation: narrative must align with data
  - Create consistency checker for reports

  **Must NOT do**:
  - Allow 'Strong AI' and '0 AI score' in same report
  - Generate Salt classification with Phoenix-level praise

  **Recommended Agent Profile**:
  - **Category**: `writing` (content validation)
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 13, 14)
  - **Blocks**: None
  - **Blocked By**: Task 10 (AI consistency)

  **References**:
  - `src/solstein/exporters/markdown/generator.py` - Report generation logic
  - Current reports showing contradictions

  **Acceptance Criteria**:
  - [ ] Zero contradictions in generated reports
  - [ ] AI maturity and AI score always aligned
  - [ ] Classification matches narrative tone
  - [ ] Consistency checker validates all reports

  **QA Scenarios**:
  ```
  Scenario: Narrative consistency validation
    Tool: Bash (python + read report)
    Steps:
      1. Generate report for Eneve
      2. Run consistency checker on report
      3. Verify: No contradictions flagged
      4. Verify: AI maturity and score are aligned
    Expected Result: Coherent, consistent narrative
    Evidence: .sisyphus/evidence/task-15-consistency-check.json
  ```

  **Commit**: YES
  - Message: `fix(reports): eliminate contradictory narrative generation`
  - Files: `src/solstein/exporters/markdown/consistency_checker.py`, generator updates

---

- [ ] 16. **Preserve Geographic Specificity**

  **What to do**:
  - Fix geographic data destruction (7 countries → 'Europe')
  - Ensure markdown extractor preserves country list
  - Update JSON loader to maintain geographic granularity
  - Add geographic standardization (country names, not continents)
  - Add geographic completeness scoring

  **Must NOT do**:
  - Reduce specific countries to continent-level
  - Lose geographic detail during data merge

  **Recommended Agent Profile**:
  - **Category**: `quick` (data preservation)
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Blocks**: Task 14 (geographic indicators)
  - **Blocked By**: Task 2

  **References**:
  - `src/solstein/extractors/markdown_extractor.py` - Geographic extraction
  - `src/solstein/data/loaders.py` - Geographic loading

  **Acceptance Criteria**:
  - [ ] Eneve shows 7 specific countries (not just 'Europe')
  - [ ] All companies maintain geographic granularity
  - [ ] Geographic standardization rules documented
  - [ ] No data loss during JSON/Markdown merge

  **QA Scenarios**:
  ```
  Scenario: Geographic specificity validation
    Tool: Bash (python)
    Steps:
      1. Load Eneve from unified model
      2. Verify: geographic_presence contains 7 countries
      3. Check: 'Netherlands', 'Belgium', 'Germany', etc. present
      4. Verify: No 'Europe' or continent-level entries
    Expected Result: Specific country list preserved
    Evidence: .sisyphus/evidence/task-16-geographic-specificity.json
  ```

  **Commit**: YES
  - Message: `fix(data): preserve geographic specificity in company profiles`
  - Files: `src/solstein/data/loaders.py`, `src/solstein/extractors/markdown_extractor.py`

---

- [ ] 17. **Create Golden Dataset Regression Tests**

  **What to do**:
  - Select 5-10 representative companies for golden dataset
  - Record their expected scores and classifications
  - Create regression tests that verify scores don't drift
  - Include Eneve, Envision Digital, Octopus Energy, and edge cases
  - Add CI check for regression test failures

  **Must NOT do**:
  - Allow score drift without explicit approval
  - Use random companies (must be curated dataset)

  **Recommended Agent Profile**:
  - **Category**: `testing` (test design)
  - **Skills**: `testing/python-testing-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 5-8)
  - **Blocks**: Tasks 18, 19, 20
  - **Blocked By**: Tasks 5, 6, 7, 8

  **References**:
  - `tests/` directory structure
  - Current test patterns in codebase

  **Acceptance Criteria**:
  - [ ] Golden dataset of 10 companies defined
  - [ ] Expected scores documented for each company
  - [ ] Regression tests created and passing
  - [ ] CI integration for regression checks

  **QA Scenarios**:
  ```
  Scenario: Golden dataset regression validation
    Tool: Bash (pytest)
    Steps:
      1. Run: pytest tests/test_golden_dataset.py -v
      2. Verify: All 10 golden companies pass
      3. Check: Scores match expected within 0.1 tolerance
      4. Verify: Classifications match expected
    Expected Result: 100% pass rate on golden dataset
    Evidence: .sisyphus/evidence/task-17-golden-tests.log
  ```

  **Commit**: YES
  - Message: `test(regression): add golden dataset regression tests`
  - Files: `tests/test_golden_dataset.py`, `tests/fixtures/golden_dataset.json`

---

- [ ] 18. **Run Eneve Consistency Validation**

  **What to do**:
  - Run Eneve analysis 10 times consecutively
  - Record all scores each run
  - Calculate variance: max(score) - min(score)
  - Verify variance < 0.2 for all dimensions
  - Document any remaining non-determinism

  **Must NOT do**:
  - Accept variance > 0.2 as 'acceptable'
  - Hide non-determinism from users

  **Recommended Agent Profile**:
  - **Category**: `testing` (validation)
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 17)
  - **Blocks**: None
  - **Blocked By**: Task 17

  **References**:
  - Eneve data from unified model
  - Scoring logic from Task 7

  **Acceptance Criteria**:
  - [ ] 10 consecutive runs completed
  - [ ] Variance < 0.2 for all scores
  - [ ] Results documented and committed
  - [ ] Any remaining issues logged as bugs

  **QA Scenarios**:
  ```
  Scenario: Eneve consistency validation
    Tool: Bash (python)
    Steps:
      1. Run Eneve scoring 10 times in a loop
      2. Record: growth_score, financial_health_score, composite_score each run
      3. Calculate variance for each score
      4. Assert: All variances < 0.2
    Expected Result: Deterministic output across all runs
    Evidence: .sisyphus/evidence/task-18-eneve-consistency.json
  ```

  **Commit**: YES
  - Message: `test(validation): verify Eneve scoring consistency across 10 runs`
  - Files: `scripts/validate_eneve_consistency.py`, results/

---

- [ ] 19. **Validate Classification Distribution**

  **What to do**:
  - Run classification on all 199 companies
  - Count Phoenix, Salt, Lead distributions
  - Verify Phoenix: 15-25%, Salt: 60-70%, Lead: 10-20%
  - Analyze edge cases near classification boundaries
  - Document any companies that 'should' be in different class

  **Must NOT do**:
  - Accept 94% Salt as 'working'
  - Allow 0% Lead classification

  **Recommended Agent Profile**:
  - **Category**: `testing` (distribution validation)
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 17)
  - **Blocks**: None
  - **Blocked By**: Task 17

  **References**:
  - Classification logic from Task 9
  - All 199 companies scored

  **Acceptance Criteria**:
  - [ ] Distribution within target ranges
  - [ ] At least 10 companies classified as Lead
  - [ ] At least 30 companies classified as Phoenix
  - [ ] Documented rationale for boundary cases

  **QA Scenarios**:
  ```
  Scenario: Classification distribution validation
    Tool: Bash (python)
    Steps:
      1. Classify all 199 companies
      2. Count Phoenix, Salt, Lead
      3. Calculate percentages
      4. Verify: Phoenix >= 15% and <= 25%
      5. Verify: Lead >= 10% and <= 20%
    Expected Result: Balanced distribution
    Evidence: .sisyphus/evidence/task-19-classification-dist.json
  ```

  **Commit**: YES
  - Message: `test(validation): verify balanced classification distribution`
  - Files: `scripts/validate_classification_dist.py`, results/

---

- [ ] 20. **Full Pipeline Integration Test**

  **What to do**:
  - Run complete pipeline: data load → score → classify → report
  - Test with Eneve and 3 other sample companies
  - Verify end-to-end data flow integrity
  - Check report generation without errors
  - Validate Excel export contains expected data

  **Must NOT do**:
  - Skip any pipeline stage in testing
  - Accept partial failures

  **Recommended Agent Profile**:
  - **Category**: `testing` (E2E testing)
  - **Skills**: `testing/e2e-testing-patterns`

  **Parallelization**:
  - **Can Run In Parallel**: NO (final integration)
  - **Blocks**: Final verification
  - **Blocked By**: Tasks 17, 18, 19

  **References**:
  - `run_eneve_complete_flow.sh` - Full pipeline script
  - All previous tasks completed

  **Acceptance Criteria**:
  - [ ] Full pipeline runs without errors
  - [ ] All output files generated correctly
  - [ ] Reports contain no contradictions
  - [ ] Excel export has 199 companies (not 4)

  **QA Scenarios**:
  ```
  Scenario: Full pipeline E2E test
    Tool: Bash (shell script)
    Steps:
      1. Run: ./run_eneve_complete_flow.sh --full
      2. Verify: All 4 steps complete without errors
      3. Check: Excel file has 199 rows
      4. Read: Generated report has no contradictions
    Expected Result: Complete successful pipeline execution
    Evidence: .sisyphus/evidence/task-20-e2e-test.log
  ```

  **Commit**: YES
  - Message: `test(e2e): add full pipeline integration test`
  - Files: `tests/test_full_pipeline.py`, `scripts/e2e_validation.sh`

---

## Final Verification Wave (MANDATORY)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. Verify all 20 tasks are implemented:
  - Data completeness >70% (was 16%)
  - Scoring variance <0.2 across runs
  - Classification balanced (Phoenix 15-25%, Salt 60-70%, Lead 10-20%)
  - Zero contradictions in reports
  - Geographic specificity preserved
  Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [10/10] | Must NOT Have [0/0] | Tasks [20/20] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `ruff check .` + `mypy src/` + `pytest tests/ --cov=solstein`.
  Review all changed files for: unused imports, type errors, missing docstrings.
  Check test coverage: must be >80% for new code.
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Coverage [N%] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Execute full pipeline 3 times. Compare outputs:
  - Eneve scores identical across all 3 runs
  - Reports contain no "No strengths identified"
  - Excel export has 199 companies with complete data
  - Geographic data shows specific countries
  Save results to .sisyphus/evidence/final-qa/.
  Output: `Runs [3/3 consistent] | Reports [N/N clean] | Data Quality [N%] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual implementation.
  Verify 1:1 — everything in spec was built, nothing beyond spec.
  Check "Must NOT do" compliance.
  Flag any tasks that don't match requirements.
  Output: `Tasks [20/20 compliant] | Must NOT Have [0 violations] | VERDICT`

---

## Commit Strategy

- **Pattern**: Conventional commits with scope
- **Format**: `type(scope): description`
- **Types**: `feat`, `fix`, `test`, `docs`, `refactor`
- **Scopes**: `data`, `scoring`, `classification`, `reports`, `testing`

**Example commits**:
```
feat(data): add comprehensive data quality audit
feat(data): implement unified data model with conflict resolution
fix(scoring): correct revenue per employee calculation
fix(scoring): eliminate non-determinism from scoring engine
feat(classification): rebalance Phoenix/Salt/Lead distribution
feat(reports): implement context-aware report generation
test(regression): add golden dataset regression tests
```

---

## Success Criteria

### Quantitative Metrics
```bash
# Data Completeness
python -c "from solstein.data.quality import audit; r = audit(); print(f'Revenue completeness: {r.revenue}%'); assert r.revenue > 70"

# Scoring Consistency
python scripts/validate_eneve_consistency.py --runs 10 --max-variance 0.2

# Classification Distribution
python scripts/validate_classification_dist.py --phoenix-min 15 --phoenix-max 25 --lead-min 10 --lead-max 20

# Report Quality
grep -r "No significant strengths identified" data/output/reports/ | wc -l  # Should be 0
```

### Qualitative Checklist
- [ ] Eneve analysis is consistent across all data sources
- [ ] Reports provide actionable insights (not just data dumps)
- [ ] Geographic data shows specific countries (not continents)
- [ ] AI maturity and AI scores are always aligned
- [ ] Confidence weights reflect actual data quality (not all 1.0)
- [ ] Classification distribution is balanced and meaningful
- [ ] No contradictory statements in any report
- [ ] Full pipeline runs successfully in <5 minutes

---

## Rollback Plan

If critical issues are found during verification:

1. **Immediate**: Revert to last known good commit
   ```bash
   git log --oneline --grep="solstein-improvement" -n 5
   git revert <commit-hash> --no-edit
   ```

2. **Partial**: Disable new features via feature flags
   ```python
   # In config.py
   USE_UNIFIED_LOADER = False  # Revert to old loader
   USE_CONFIDENCE_WEIGHTING = False  # Revert to 1.0 weights
   ```

3. **Data**: Keep backups of original datasets
   ```bash
   cp data/input/competitor_data.json data/input/competitor_data.json.backup
   ```

---

## Timeline Estimate

| Wave | Tasks | Est. Hours | Parallel Speedup |
|------|-------|------------|------------------|
| Wave 1 (Foundation) | 1-4 | 16-20h | 4 tasks → 8h effective |
| Wave 2 (Scoring) | 5-8 | 12-16h | 4 tasks → 6h effective |
| Wave 3 (Classification) | 9-12 | 10-14h | 4 tasks → 5h effective |
| Wave 4 (Reporting) | 13-16 | 10-12h | 4 tasks → 5h effective |
| Wave 5 (Testing) | 17-20 | 12-16h | Sequential → 14h effective |
| Final Verification | F1-F4 | 4-6h | 4 tasks → 2h effective |
| **Total** | **24 tasks** | **64-84h** | **~40-50h effective** |

**Recommended Schedule**:
- Week 1: Waves 1-2 (Data + Scoring fixes)
- Week 2: Waves 3-4 (Classification + Reporting)
- Week 3: Wave 5 + Final Verification (Testing)

---

## Post-Implementation Monitoring

After deployment, monitor:

1. **Data Quality Dashboard**
   - Track completeness % weekly
   - Alert if completeness drops below 70%

2. **Scoring Consistency Alerts**
   - Run Eneve analysis daily
   - Alert if variance > 0.1

3. **Classification Distribution**
   - Monthly review of Phoenix/Salt/Lead ratios
   - Alert if any class drops below threshold

4. **Report Quality Scores**
   - Track "No strengths identified" count (should be 0)
   - Monitor for contradictions

---

*Plan created: February 25, 2026*
*Status: Ready for execution*
*Next step: Run `/start-work solstein-improvement-plan` to begin execution*
