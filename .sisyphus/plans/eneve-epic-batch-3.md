# ENEVE Pipeline — Epic Batch 3: Critical Bug Fix Round

## TL;DR

> **Quick Summary**: Three independent audit agents identified 23 confirmed bugs across the scoring pipeline, field mapper, synthetic data generator, and architecture. This plan fixes them all in three parallel waves, then validates with a full pipeline re-run.
>
> **Deliverables**:
> - Fixed field mapper (growth_rate, profit_margin, funding_raised unit bugs)
> - Fixed synthetic data generator (duplicates, AI score inconsistency, tier/revenue mismatches)
> - Fixed scoring engine (saas_maturity, tech_stack, dead code removal)
> - Fixed error handling and code quality across the codebase
> - Integrated FinancialSanityValidator into pipeline
> - Clean re-run of 197-company pipeline with verified score distribution
>
> **Estimated Effort**: Large
> **Parallel Execution**: YES — 3 waves
> **Critical Path**: EPIC-011 (field format) → EPIC-012 (employees) → EPIC-019 (validator integration) → EPIC-020 (re-run)

---

## Context

### Original Request
"Run the project for a random company and critic the results and findings all the flows all the logs all the things we are doing and help us find and detail all issues inconsistencies problems etc"

### Audit Summary (3 agents, 2026-03-01)

Three background explore agents ran parallel deep audits of:
1. **Scoring pipeline data flow + field mapping bugs** → 13 confirmed bugs
2. **Synthetic data quality + scoring realism** → 10 confirmed bugs
3. **Code quality, error handling, architecture** → 8 confirmed bugs

**Total: 23 unique confirmed bugs.**

### Confirmed Bug Inventory

| # | Severity | Bug | Epic |
|---|----------|-----|------|
| 1 | 🔴 CRITICAL | `growth_rate` format mismatch: JSON=percent(35), scorer expects decimal(0.05) → slow-growth penalties NEVER trigger | EPIC-011 |
| 2 | 🔴 CRITICAL | `profit_margin` format mismatch: JSON=percent(30), scorer expects decimal → ALL companies get max profitability bonus | EPIC-011 |
| 3 | 🔴 CRITICAL | `funding_raised` unit mismatch: JSON=raw EUR(1,905,663), scorer treats as millions → 381,132× ratio inflation | EPIC-011 |
| 4 | 🔴 CRITICAL | Employee data 100% NULL in scored output — operating efficiency score never applies | EPIC-012 |
| 5 | 🔴 CRITICAL | 10 duplicate company names (LinkPower×2, SmartHub×2, etc.) — breaks competitive overlap analysis | EPIC-014 |
| 6 | 🔴 CRITICAL | AI maturity vs AI score contradictory in 46 companies (23%) — Low maturity + score 8.5, Strong maturity + score 3.1 | EPIC-014 |
| 7 | 🟠 HIGH | `saas_maturity` hardcoded to 5 — all companies get identical SaaS bonus regardless of actual value | EPIC-013 |
| 8 | 🟠 HIGH | `tech_stack` always empty list — tech diversity bonus NEVER triggers for any company | EPIC-013 |
| 9 | 🟠 HIGH | Tier/revenue mismatch: 33 companies assigned wrong tier (tier set before revenue generated) | EPIC-014 |
| 10 | 🟠 HIGH | Original 3 companies (Eneve, Test Co 2, Test Co 3) have tier=null → tier_adj=0.0 in scoring | EPIC-014 |
| 11 | 🟠 HIGH | ~270 lines of dead duplicate code in scoring.py (_calculate_growth_score, _calculate_financial_health_score, _calculate_competitive_position_score — never called) | EPIC-015 |
| 12 | 🟠 HIGH | `run_eneve_199.py` imports from `excel` not `excel_improved` — may use old exporter | EPIC-015 |
| 13 | 🟠 HIGH | Hardcoded absolute path: `sys.path.insert(0, '/home/ai-whisperers/solstein/src')` | EPIC-016 |
| 14 | 🟠 HIGH | No try-except around `open(input_path)` — unfriendly crash if file missing | EPIC-016 |
| 15 | 🟠 HIGH | Bare `except Exception: return financials` in `_merge_facts_into_financials` (both scorers) — silently swallows all errors | EPIC-016 |
| 16 | 🟠 HIGH | Division-by-zero: `revenue/employees`, `funding/revenue` — no guards | EPIC-016 |
| 17 | 🟡 MEDIUM | `ai_score` and `ai_maturity_score` from JSON never mapped to Company model | EPIC-017 |
| 18 | 🟡 MEDIUM | `revenue_timeline` not mapped — historical revenue data completely lost | EPIC-017 |
| 19 | 🟡 MEDIUM | Funding config thresholds too high (€50M high, €10M med) for actual data (most <€5M) | EPIC-013 |
| 20 | 🟡 MEDIUM | SWOT `growth_rate > 20` comparison wrong unit (decimal field, percent threshold) | EPIC-018 |
| 21 | 🟡 MEDIUM | MarketAnalyzer `avg_growth > 15` unit unclear — percent comparison on decimal field? | EPIC-018 |
| 22 | 🟡 MEDIUM | `FinancialSanityValidator` created but never integrated into pipeline | EPIC-019 |
| 23 | 🟡 MEDIUM | Generic company names ('DataBase', 'DigitalAnalytics') — not energy-sector specific | EPIC-014 |

---

## Work Objectives

### Core Objective
Fix all 23 confirmed bugs from the audit round, restore scoring integrity, and produce a clean full pipeline re-run with verified results.

### Concrete Deliverables
- `scripts/run_eneve_199.py` — field mapper fixed, path fix, error handling, ExcelExporter import fixed
- `scripts/generate_synthetic_companies.py` — duplicates fixed, AI consistency enforced, tier assigned after revenue
- `src/solstein/analytics/scorers/growth_momentum.py` — growth_rate/profit_margin decimal thresholds confirmed correct
- `src/solstein/analytics/scorers/financial_health.py` — profit_margin decimal thresholds confirmed
- `src/solstein/analytics/scoring.py` — dead code removed (~270 lines)
- `src/solstein/analytics/scorers/competitive_position.py` — saas_maturity + tech_stack mapping fixed
- `src/solstein/core/scoring_config.py` — funding thresholds lowered
- `src/solstein/domain/models.py` — fields for ai_score, revenue_timeline populated
- `src/solstein/validation/financial_sanity.py` — integrated into pipeline
- `data/input/competitor_data_199.json` — regenerated clean data
- Final pipeline run: score distribution 15-20% Phoenix, 60-75% Salt, 10-25% Lead

### Must NOT Have (Guardrails)
- NO changes to Phoenix/Salt/Lead thresholds (PHOENIX_SCORE_THRESHOLD=8.1 stays)
- NO new composite score weights (0.4/0.3/0.3 stays)
- NO adding new fields to JSON that don't already exist in generator
- NO removing the `ConfidenceLevel.SYNTHETIC` or `data_source_type` added in batch 2
- NO touching the Excel schema unless ExcelExporter import fix requires it
- NO introducing new external dependencies

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: Tests-after (verify each fix with targeted test)
- **Framework**: pytest

### QA Policy
Every EPIC that touches scoring logic MUST produce a verifiable score change via full pipeline re-run.
Evidence saved to `.sisyphus/evidence/epic-{N}-{scenario}.txt`.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — 4 parallel, independent):
├── EPIC-011: Fix field mapper format bugs (BLOCKING - most impactful)
├── EPIC-014: Fix synthetic data generator quality
├── EPIC-015: Remove dead code + fix imports
└── EPIC-016: Fix error handling + division-by-zero + hardcoded path

Wave 2 (After Wave 1 — 4 parallel):
├── EPIC-012: Fix employee data pipeline (depends: EPIC-011 for correct field mapping)
├── EPIC-013: Fix saas_maturity + tech_stack + funding thresholds (depends: EPIC-011)
├── EPIC-017: Map missing JSON fields (depends: EPIC-011 format fixes)
└── EPIC-018: Fix SWOT/MarketAnalyzer unit comparisons (depends: EPIC-011 decimal format)

Wave 3 (After Wave 2 — 2 parallel):
├── EPIC-019: Integrate FinancialSanityValidator (depends: EPIC-011, EPIC-012)
└── EPIC-014b: Regenerate synthetic data with generator fixes (depends: EPIC-014)

Wave Final (After ALL):
└── EPIC-020: Full pipeline re-run + validate score distribution + write critique report
```

### Agent Dispatch Summary

- **Wave 1**: 4 tasks → `quick` (EPIC-015, EPIC-016), `unspecified-high` (EPIC-011, EPIC-014)
- **Wave 2**: 4 tasks → `unspecified-high` (EPIC-012, EPIC-013, EPIC-017, EPIC-018)
- **Wave 3**: 2 tasks → `unspecified-high` (EPIC-019), `quick` (EPIC-014b)
- **Final**: 1 task → `deep` (EPIC-020)

---

## TODOs

---

## Final Verification Wave

- [ ] F1. **Pipeline Compliance Audit** — `oracle`
  Run full pipeline. Verify: score distribution 15-20% Phoenix / 60-75% Salt / 10-25% Lead. Check no null employees in output. Check no duplicate companies. Check profit_margin stored as decimal (<1.0) for all companies. Check funding_raised stored as millions (<1000) for all companies.
  Output: `Distribution [PASS/FAIL] | Employees [PASS/FAIL] | Duplicates [PASS/FAIL] | Formats [PASS/FAIL] | VERDICT`

- [ ] F2. **Score Integrity Check** — `deep`
  Pick 5 companies spanning Lead/Salt/Phoenix. For each: manually trace growth_factor = growth_rate/20, profit_margin adjustment, funding cushion ratio. Verify no impossible values (funding ratio > 10, growth_factor > 4, etc.). Confirm slow-growth penalty triggers for companies with 0-5% growth.
  Output: `Manual trace [5/5 correct] | No impossible values [PASS/FAIL] | Penalties trigger [PASS/FAIL] | VERDICT`

- [ ] F3. **Code Quality Check** — `unspecified-high`
  Run `grep -n "_calculate_growth_score\|_calculate_financial_health_score\|_calculate_competitive_position_score" src/solstein/analytics/scoring.py` → must return 0 results. Run `grep -n "sys.path.insert" scripts/run_eneve_199.py` → must return 0. Run `grep -rn "except Exception:" src/solstein/analytics/scorers/` → must return 0. Run `pytest tests/ -q` → capture pass/fail.
  Output: `Dead code [CLEAN] | Hardcoded path [CLEAN] | Bare excepts [CLEAN] | Tests [N pass/N fail] | VERDICT`

---

## Commit Strategy

- EPIC-011: `fix: normalize growth_rate and profit_margin to decimal in field mapper`
- EPIC-012: `fix: restore employee data flow through pipeline`
- EPIC-013: `fix: map saas_maturity and tech_stack from JSON, lower funding thresholds`
- EPIC-014: `fix: deduplicate company names, fix AI score consistency and tier assignment`
- EPIC-015: `refactor: remove 270 lines of dead code from scoring.py, fix excel import`
- EPIC-016: `fix: add error handling, division-by-zero guards, remove hardcoded path`
- EPIC-017: `feat: map ai_score and revenue_timeline fields from JSON`
- EPIC-018: `fix: normalize growth_rate comparisons in SWOT and MarketAnalyzer`
- EPIC-019: `feat: integrate FinancialSanityValidator into main pipeline`
- EPIC-020: `data: regenerate synthetic companies and re-run pipeline`

---

## Success Criteria

### Verification Commands
```bash
# Score distribution must be in target ranges
python scripts/run_eneve_199.py 2>&1 | grep -E "Phoenix|Salt|Lead"
# Expected: Phoenix ~15-20%, Salt ~60-75%, Lead ~10-25%

# No null employees
python -c "import json; d=json.load(open('data/output/exports/eneve_full_199_scored.json')); nulls=sum(1 for c in d['companies'] if not c.get('employees')); print(f'Null employees: {nulls}')"
# Expected: Null employees: 0

# No duplicate names
python -c "import json; d=json.load(open('data/input/competitor_data_199.json')); names=[c['name'] for c in d]; print(f'Dupes: {len(names)-len(set(names))}')"
# Expected: Dupes: 0

# Profit margin decimal format
python -c "import json; d=json.load(open('data/output/exports/eneve_full_199_scored.json')); bad=sum(1 for c in d['companies'] if c.get('profit_margin',0)>1); print(f'Percent-format margins: {bad}')"
# Expected: Percent-format margins: 0

# Dead code gone
grep -c "_calculate_growth_score\|_calculate_financial_health" src/solstein/analytics/scoring.py
# Expected: 0
```

### Final Checklist
- [ ] All 23 bugs from audit fixed
- [ ] No null employees in scored output
- [ ] No duplicate company names in input
- [ ] growth_rate stored as decimal (0.25 not 25) in Company model
- [ ] profit_margin stored as decimal (<1.0) in Company model
- [ ] funding_raised stored in millions (<1000) in Company model
- [ ] Dead code removed from scoring.py
- [ ] Score distribution within target bands
- [ ] pytest passes with no regressions
