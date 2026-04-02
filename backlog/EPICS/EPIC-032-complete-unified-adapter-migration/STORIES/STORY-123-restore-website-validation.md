# STORY-123: Restore Website Adapter Validation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | High |
| **Epic** | EPIC-032: Complete Unified Adapter Migration |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-092 (merge task files) |

---

## The Audit Verdict

> `website.py` has early validation for missing website URL. `website_unified.py` lacks this validation — proceeds to fetch and fails later.

---

## Problem Statement

The old website adapter checked if a company had a website URL before attempting to fetch it. The unified adapter skips this check and tries to fetch anyway, resulting in a failed HTTP request to an empty or malformed URL. This is wasted resources and misleading error messages. A simple guard clause was lost in the migration, and the consequences are disproportionate to the size of the omission.

When a company record has no website URL — which is not uncommon for early-stage companies, subsidiaries, or recently acquired entities — the old adapter returned a clear, early result indicating no website was available. The unified adapter attempts an HTTP request to an empty string or `None`, which produces a connection error that looks like a network failure. Downstream error handling treats this as a transient infrastructure problem and may retry. It is not a transient infrastructure problem. It is a data quality issue that should be identified and reported immediately, not retried three times with backoff.

The missing validation also affects pipeline observability. When the old adapter returned early with a "no website" result, the research pipeline could log this as a data gap and continue. When the unified adapter fails with a connection error, the pipeline may halt or produce an incomplete record without a clear indication of why. The error message "Failed to connect to ''" is not useful. The message "Company has no website URL — skipping fetch" is.

This is the smallest of the three functional regressions in this epic, but it is also the most embarrassing. A guard clause that prevents fetching an empty URL is not sophisticated engineering. It is basic defensive programming. Its absence in the unified adapter suggests the migration was done by copying the structure without reading the logic.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Efficiency** | Wasted HTTP calls to empty or malformed URLs; unnecessary retry attempts for a non-retryable condition |
| **Error Quality** | Cryptic connection errors instead of clear "no website" messages; misleading failure classification |
| **Pipeline Observability** | Data gaps (missing website) are indistinguishable from infrastructure failures in logs |
| **Maintainability** | Two website adapters with different validation behavior; the "official" one is the less defensive one |

---

## Affected Files

| File | Issue |
|------|-------|
| `data/website_unified.py` | Missing early validation for empty/None/malformed website URL; proceeds to HTTP fetch unconditionally |
| `data/website.py` | Reference implementation — contains the guard clause that must be ported; to be deleted after parity |

---

## Architectural Requirements

- Early validation for missing, empty, or `None` website URL must be present in `website_unified.py` before any network call is initiated
- Validation must also cover malformed URLs that would produce a connection error (e.g., URLs without a scheme, URLs that are whitespace-only)
- When validation fails, the adapter must return a structured result indicating no website is available — not raise an exception
- The structured "no website" result must include a reason field distinguishing "URL not provided" from "URL malformed"
- No HTTP request must be made when validation fails — this is the primary behavioral requirement
- The validation result must be logged at INFO level (not WARNING or ERROR — missing website is a data quality note, not a system problem)
- `website.py` must be deleted only after unit tests confirm `website_unified.py` validates correctly
- The public interface of `website_unified.py` must remain backward-compatible with existing callers

---

## Acceptance Criteria

- [ ] `website_unified.py` returns early with a structured result when website URL is `None`
- [ ] `website_unified.py` returns early with a structured result when website URL is an empty string
- [ ] `website_unified.py` returns early with a structured result when website URL is whitespace-only
- [ ] `website_unified.py` returns early with a structured result when website URL lacks a scheme (e.g., `"example.com"` without `https://`)
- [ ] No HTTP request is made in any of the above cases (verifiable via mock assertion)
- [ ] The structured result includes a reason field distinguishing URL-not-provided from URL-malformed
- [ ] Validation result is logged at INFO level, not WARNING or ERROR
- [ ] `website.py` is deleted
- [ ] No import of `website.py` remains anywhere in the codebase

---

## Definition of Done

- **Tests Required**: Unit test that passes a company with `website_url=None` and asserts no HTTP call is made (mock the HTTP client and verify zero calls). Unit test that passes a company with `website_url=""` and asserts the same. Unit test that passes a company with a malformed URL and asserts early return with a structured result. All three tests must verify the returned result contains a reason field.
- **Documentation Required**: Inline comment on the validation block explaining what constitutes an invalid URL for this adapter and why the check must precede any network call.
- **Code Review Gate**: Reviewer must verify that the HTTP client is not instantiated or called when validation fails. Reviewer must confirm the log level is INFO (not WARNING or ERROR) for the validation failure case. Reviewer must verify `website.py` is absent from the repository after merge.

---

## Notes

The severity on this story is High rather than Critical because the failure mode is a connection error rather than a silent data corruption or security issue. The pipeline fails loudly rather than silently. That said, "fails loudly with a misleading error" is not a satisfactory outcome for a production system.

The temptation will be to add a single `if not url: return None` and call it done. This is insufficient. `None` is not a structured result. The caller cannot distinguish "no website available" from "fetch failed" if both return `None`. The return value must carry enough information for the pipeline to log the data gap correctly and continue without treating it as an infrastructure failure.

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
