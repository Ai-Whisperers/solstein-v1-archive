# STORY-183: Fix Market Overview Classification Counters

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | S (< half a day) |
| **Epic** | EPIC-048 Report Generation Quality |
| **Created** | 2026-03-01 |
| **Risk** | Low — counter logic fix |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED BUG** — verified by live execution on 2026-03-01.

```markdown
<!-- market_overview.md -->
## Market Summary
- Total Companies Analyzed: 3
- Phoenix Tier: 0
- Salt Tier: 0
- Lead Tier: 0
```

Eneve is classified as `Phoenix` (confirmed: `classification: Phoenix` in output), yet the market overview shows `Phoenix Tier: 0`. The counters are never incremented.

---

## Problem Statement

The `MarketReportGenerator` (or `market.py`) generates the market overview. It iterates over companies but fails to increment the classification counters. Possible causes:
1. Counters initialized but never incremented in the loop
2. Classification string mismatch (e.g., checking `"Phoenix"` but value is `"Phoenix "` with trailing space)
3. Case sensitivity issue (`"phoenix"` vs `"Phoenix"`)
4. Counters incremented after the summary is printed

This makes the market overview useless — it always shows zero for all tiers regardless of actual classifications.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Business Accuracy | 🟠 High — market-level KPIs are completely wrong |
| User Trust | 🟠 High — obvious contradiction (Phoenix company shown, Phoenix count 0) |
| Report Quality | 🟠 High — entire market overview section is invalid |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/exporters/markdown/market.py` | `generate_market_overview()` | Fix counter logic |
| `tests/unit/test_market_report.py` | New or existing | Test counter accuracy |

---

## Dependencies

- **Hard**: None
- **Soft**: STORY-173 (threat_level fix) — related classification logic
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: The market overview must count companies by their `classification` attribute after scoring.

**REQ-2**: Counter logic must be case-insensitive (treat `"Phoenix"`, `"PHOENIX"`, `"phoenix"` as same).

**REQ-3**: The fix must handle all three classifications: Phoenix, Salt, Lead.

**REQ-4**: If a company has `classification = None`, it should not be counted (or counted as "Uncategorized").

---

## Acceptance Criteria

- [ ] With Eneve (Phoenix), Test Company 2, Test Company 3 in data: `Phoenix Tier: 1`
- [ ] If all 3 companies are Salt: `Salt Tier: 3`
- [ ] If classifications are mixed: counters reflect actual distribution
- [ ] Case-insensitive: `"PHOENIX"` in data counts as Phoenix
- [ ] Unit test: `test_market_classification_counters` with mocked companies

---

## Implementation Note

```python
# market.py — fix
from collections import Counter

def generate_market_overview(self, companies):
    classifications = [c.classification for c in companies if c.classification]
    counts = Counter(c.lower() for c in classifications)
    
    return f"""
## Market Summary
- Total Companies Analyzed: {len(companies)}
- Phoenix Tier: {counts.get('phoenix', 0)}
- Salt Tier: {counts.get('salt', 0)}
- Lead Tier: {counts.get('lead', 0)}
"""
```

---

## Definition of Done

- [ ] Market overview shows correct classification counts
- [ ] Manual run: Eneve shows `Phoenix Tier: 1`
- [ ] Unit test added

---

## Change Log

| Date | Author | Note |
|------|--------|
| 2026-03-01 | Analysis Run | Confirmed via market_overview.md showing all zeros |

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
