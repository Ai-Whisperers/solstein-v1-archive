# STORY-226: Implement Domain-Aware Fetch Policy Matrix and Retry Strategy

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-062 Scraping Resilience and Field Evidence Ledger |
| **Created** | 2026-03-11 |
| **Risk** | Medium |
| **Assigned** | - |

---

## Audit Verdict

`ContentExtractorAgent._fetch_page()` currently uses a universal fetch pattern (direct then reader fallback), but lacks policy differentiation by domain class, failure mode, or content type.

---

## Problem Statement

One-size fetch strategy increases retries on low-value domains and misses opportunities to apply optimal pathing for known blocked or JS-heavy sources.

---

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Higher chance of unusable content in extraction pipeline |
| **Performance** | Wasted retries and slower per-company runtime |
| **Maintainability** | Hard to tune behavior for recurring domain failure patterns |

---

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|------------------|
| `src/solstein/research/ai_research_orchestrator.py` | Modify | Introduce domain policy matrix and failure routing |
| `tests/unit/research/test_fetch_policy.py` | Create | Domain policy and retry behavior tests |
| `docs/research/AI_RESEARCH_IMPROVEMENTS.md` | Modify | Document fetch policy classes |

---

## Dependencies

### Hard Dependencies (Must Complete First)
- None

### Soft Dependencies (Preferred Order)
- STORY-227 (extraction contract consumes fetch metadata)

---

## Architectural Requirements

- **REQ-1**: Fetch path must be selected by domain policy and content-type expectations.
- **REQ-2**: Retry/backoff must be bounded and reason-coded.
- **REQ-3**: Fetch result must include strategy used, attempts, and terminal failure reason.
- **REQ-4**: Policy table must be externally configurable and versioned.

---

## Acceptance Criteria

- [ ] Fetch policy matrix implemented with at least: default, blocked-prone, js-heavy, document-heavy classes.
- [ ] Every fetch attempt records strategy and outcome metadata.
- [ ] Blocked-page fallback success rate improves against baseline set.
- [ ] No infinite retry path exists under any policy.
- [ ] Unit tests verify strategy selection and retry cap behavior.

---

## Definition of Done

### Tests Required
- [ ] Policy routing tests by domain class
- [ ] Retry cap tests for transient and permanent errors

### Documentation Required
- [ ] Policy schema and default class mapping documented

### Code Review Gate
- [ ] Reviewer confirms fallback logic is deterministic and bounded
- [ ] Reviewer confirms terminal errors are structured and actionable

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Wrong default policy class | Medium | Medium | Add safe default with telemetry-driven reclassification |
| Policy sprawl | Low | Medium | Keep small fixed class set and explicit ownership |

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-03-11 | @opencode | Created |
