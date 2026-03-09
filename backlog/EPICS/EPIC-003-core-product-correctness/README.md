# EPIC-003: Core Product Correctness

| Field | Value |
|-------|-------|
| Priority | **P0 — Ship Blocker** |
| Status | 🔶 Partial — STORY-009 Complete |
| Stories | 3 |
| Created | 2026-02-28 |
| Depends On | [EPIC-001: Security Restoration](../EPIC-001-security-restoration/README.md) |

## Context

The scoring and classification system is the platform's core deliverable. PE/VC clients pay for company tier assignments and composite scores. The system that produces those outputs is non-deterministic.

**Three conflicting threshold definitions.** `analytics/scoring.py` classifies a company as "Lead" when its composite score is ≤ 3.9. `analytics/classification.py` uses < 5.5 for the same classification. Router handlers contain their own hardcoded threshold values. The same composite score — say, 4.5 — is classified as "Prospect" by one code path and "Lead" by another. The platform's primary output depends on which function happened to execute. This is not a display difference. It is a correctness failure in the product's core value proposition.

**Duplicate scoring implementations.** `analytics/scoring.py` (688 lines) independently implements `_calculate_growth_score()`, `_calculate_financial_health_score()`, and `_calculate_competitive_position_score()`. These exact functions already exist in `analytics/scorers/`. Additionally, `_merge_facts_into_financials()` and `_confidence_to_level()` are copy-pasted identically into both `analytics/scorers/financial_health.py` and `analytics/scorers/growth_momentum.py`. Any bug fix applied to one copy silently leaves the others unfixed. Any calibration change applied to one implementation silently diverges the others.

**Unnamed magic numbers.** Scoring uses numeric literals throughout: `0.4 / 0.3 / 0.3` (component weights), `7.0` (score ceiling), `3.9` (Lead threshold), `1.0 - (d / 3.0)` (data freshness decay). None are named constants. None have explanatory comments. None have documented business rationale. They exist as numeric literals dispersed across at least three files, and no engineer who did not write the original formulas can confidently modify them.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-009](STORIES/STORY-009-unify-classification-thresholds.md) | Unify Classification Thresholds Across All Files | CRITICAL |
| [STORY-010](STORIES/STORY-010-eliminate-scoring-duplication.md) | Eliminate Scoring Logic Duplication | HIGH |
| [STORY-011](STORIES/STORY-011-name-scoring-constants.md) | Name and Document All Scoring Constants | MEDIUM |

## Definition of Done

## Definition of Done

- [x] A single module is the designated source of truth for all classification threshold values — no other module defines threshold literals
- [ ] Each scoring function is implemented exactly once — `analytics/scoring.py` delegates, it does not re-implement
- [ ] Every numeric literal in scoring logic is replaced with a named constant that has a documented business rationale
- [x] The same input produces the same tier output regardless of which code path executes
- [ ] Component weights are asserted to sum to 1.0 in a test
- [ ] Each scoring function is implemented exactly once — `analytics/scoring.py` delegates, it does not re-implement
- [ ] Every numeric literal in scoring logic is replaced with a named constant that has a documented business rationale
- [ ] The same input produces the same tier output regardless of which code path executes
- [ ] Component weights are asserted to sum to 1.0 in a test

## Ordering Rationale

STORY-009 (thresholds) must complete before STORY-010 (deduplication), which must complete before STORY-011 (naming). Consolidating scoring logic before establishing a single threshold source risks embedding the wrong thresholds into the consolidated implementation. Naming constants before the implementation is consolidated means naming constants that will be deleted.
