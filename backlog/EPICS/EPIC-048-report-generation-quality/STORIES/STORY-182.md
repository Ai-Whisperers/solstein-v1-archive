# STORY-182: Round All Score Outputs to 2 Decimal Places in Reports

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | S (< half a day) |
| **Epic** | EPIC-048 Report Generation Quality |
| **Created** | 2026-03-01 |
| **Risk** | Low — formatting change only |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED BUG** — verified by live execution on 2026-03-01.

```markdown
<!-- competitive-analysis.md for Eneve -->
| Metric | Value |
|--------|-------|
| Competitive Position Score | 7.138888888888889 |
```

The `competitive_position_score` is printed with full Python float precision (17 digits). This is unprofessional and hard to read. The `composite_score` is already rounded to 2 decimals in `scoring.py`, but sub-scores are not.

---

## Problem Statement

Report templates use `{{ company.competitive_position_score }}` directly, which renders the raw float. All scores should be rounded to 2 decimal places for readability:
- `7.138888...` → `7.14`
- `8.366666...` → `8.37`
- `9.75` → `9.75` (already clean)

This affects:
- `growth_score`
- `financial_health_score`
- `competitive_position_score`
- `composite_score` (already rounded, but verify)
- Any signal values that are floats

---

## Impact

| Dimension | Severity |
|-----------|----------|
| User Experience | 🟠 High — unprofessional output erodes trust |
| Report Quality | 🟠 High — hard to read and compare scores |
| Security | ⬜ None |
| Performance | ⬜ None |
| Maintainability | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/exporters/markdown/base.py` | Template filters | Add `|round` filter |
| `src/solstein/exporters/markdown/company.py` | Report templates | Apply rounding |
| `src/solstein/exporters/markdown/market.py` | Report templates | Apply rounding |
| All `.md` template files | Variable interpolations | Add `:0.2f` formatting |

---

## Dependencies

- **Hard**: None
- **Soft**: STORY-181 (path fix) — do both in same PR for clean reports
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: Create a Jinja2 filter `round2` in `base.py` that formats floats to 2 decimal places: `{{ score | round2 }}` → `"7.14"`.

**REQ-2**: Apply the filter to all score variables in all templates:
```jinja2
| Growth Score | {{ company.growth_score | round2 }} |
| Financial Health | {{ company.financial_health_score | round2 }} |
| Competitive Position | {{ company.competitive_position_score | round2 }} |
| Composite | {{ company.composite_score | round2 }} |
```

**REQ-3**: If the template engine is not Jinja2, use Python f-string formatting: `f"{score:.2f}"`.

**REQ-4**: Ensure `None` values are handled gracefully (show "N/A" instead of crashing).

---

## Acceptance Criteria

- [ ] `competitive-analysis.md` shows `7.14` not `7.138888888888889`
- [ ] `financial-growth.md` shows all scores rounded to 2 decimals
- [ ] `market_overview.md` shows average scores rounded to 2 decimals
- [ ] A company with `growth_score = None` shows "N/A" not crash
- [ ] Unit test: `test_scores_rounded_in_reports` verifies 2-decimal formatting

---

## Implementation Note

```python
# base.py — add filter
from jinja2 import Environment

env = Environment()
env.filters['round2'] = lambda x: f"{x:.2f}" if x is not None else "N/A"

# In templates:
# {{ company.growth_score | round2 }}
```

Or if using Python string formatting directly:
```python
# company.py
def format_score(score):
    return f"{score:.2f}" if score is not None else "N/A"

template_data = {
    "growth_score": format_score(company.growth_score),
    # ...
}
```

---

## Definition of Done

- [ ] All score outputs rounded to 2 decimals
- [ ] Manual verification: no `7.138888...` in any generated report
- [ ] Unit test added

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Confirmed via reading competitive-analysis.md output |

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
