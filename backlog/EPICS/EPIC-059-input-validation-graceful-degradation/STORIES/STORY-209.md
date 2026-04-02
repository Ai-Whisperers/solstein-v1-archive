# STORY-209: Implement Validation Before Scoring

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-059 Input Validation & Graceful Degradation |
| **Created** | 2026-03-01 |
| **Risk** | Medium — validation errors could block scoring; need graceful fallback |
| **Assigned** | — |
| **Depends On** | STORY-206 (Company Validation), STORY-207 (None-Safety) |

---

## Audit Verdict

**CONFIRMED MISSING** — No validation runs before companies reach the scorer. Invalid companies produce invalid scores.

Current flow:
```
Raw JSON → Convert → Score (no validation gate)
                    ↑
                 If data is invalid, no one catches it
```

Desired flow:
```
Raw JSON → Convert → Validate → Score (or warn/skip if invalid)
                                  ↑
                           Catches invalid data
```

---

## Problem Statement

The pipeline lacks a validation gate between conversion and scoring. Invalid companies flow directly to the scorer, producing meaningless scores.

Example: Company with `revenue = None` due to format mismatch:
1. Raw JSON loads
2. Converted to Company (revenue = None due to format issue)
3. Validation should catch this before scoring
4. Currently: Validator exists but is not wired into pipeline
5. Score produced based on incomplete data

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Data Quality Assurance | 🔴 Critical — Invalid data reaches scorer |
| Pipeline Robustness | 🔴 Critical — No safety gate |
| Debuggability | 🟡 Medium — Errors surfaced late |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/data/loaders.py` | Loading pipeline | Add validation after conversion |
| `scripts/run_eneve_199.py` | Pipeline orchestration | Call validation before scoring |
| `src/solstein/analytics/scoring.py` | Scorer invocation | Handle validation errors gracefully |

---

## Dependencies

- **Hard**: STORY-206 (Company Validation), STORY-207 (None-Safety)
- **Blocks**: Nothing; safety improvement

---

## Architectural Requirements

**REQ-1**: After conversion, validate each company before scoring:
```python
for raw_company in companies:
    company = convert_to_domain_company(raw_company)
    
    # Validation happens here
    try:
        validated_company = validate_company(company)
        score = scorer.score(validated_company)
    except ValidationError as e:
        logger.warning(f"Company {company.name}: validation failed: {e}")
        # Handle gracefully (skip, use default score, etc.)
```

**REQ-2**: Validation errors are logged with specific field and reason.

**REQ-3**: Invalid companies can be skipped, scored with warning, or blocked (configurable).

---

## Acceptance Criteria

- [ ] Validation runs after conversion
- [ ] Invalid companies produce warning message (not silent)
- [ ] Scoring only happens for valid companies (or with explicit override)
- [ ] Validation error message shows which field failed and why
- [ ] Integration test: Invalid company → warning logged, skip/score based on config
- [ ] Real data passes validation
- [ ] Manual run: `python scripts/run_eneve_199.py` shows validation results

---

## Definition of Done

- [ ] Validation gate wired into pipeline
- [ ] Invalid companies logged with details
- [ ] Graceful handling (skip vs. score with warning)
- [ ] Integration tests verify behavior
- [ ] Real data passes validation
- [ ] No silent failures

---

## Implementation Notes

### Pipeline Integration

```python
def load_and_score_companies(input_file: str, config: ScoreConfig) -> List[ScoreResult]:
    companies_raw = load_json(input_file)
    companies_domain = [convert_to_domain_company(c) for c in companies_raw]
    
    valid_companies = []
    invalid_companies = []
    
    for company in companies_domain:
        try:
            # Validation happens here
            validated = validate_company(company)
            valid_companies.append(validated)
        except ValidationError as e:
            logger.warning(f"Company {company.name}: {e}")
            if config.strict_mode:
                # Skip invalid companies
                invalid_companies.append((company, e))
            else:
                # Score anyway with warning
                valid_companies.append(company)
    
    scores = [scorer.score(c) for c in valid_companies]
    
    return {
        "scores": scores,
        "invalid_count": len(invalid_companies),
        "invalid_details": invalid_companies
    }
```

### Files to Create/Modify

- `src/solstein/data/loaders.py` - Add validation gate
- `scripts/run_eneve_199.py` - Wire validation into pipeline
- `src/solstein/analytics/scoring.py` - Handle validation errors
- `tests/integration/test_pipeline_validation.py` - Integration tests (NEW)

### Risk Mitigation

- Validation errors could block legitimate data → Add override flag
- Performance impact → Profile with 10K companies
- Existing pipeline might depend on invalid companies → Check before blocking

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | No validation gate between conversion and scoring |

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
