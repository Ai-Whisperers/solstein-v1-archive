# STORY-124: Delete Old Adapter Versions After Parity

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | High |
| **Epic** | EPIC-032: Complete Unified Adapter Migration |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-121 (news parity), STORY-122 (funding parity), STORY-123 (website parity) |

---

## The Audit Verdict

> Old adapters (news.py, funding.py, website.py, linkedin.py, patents.py, web_search_news.py) still exist alongside unified versions.

---

## Problem Statement

The codebase has 12 adapter files where 6 would suffice. Old and unified versions coexist without any indication of which is canonical. Developers don't know which to use. Bug fixes applied to one don't apply to the other. The "unified" migration was never completed because the old files were never deleted. This is technical debt that compounds with every change.

The coexistence of old and unified adapters is not a neutral state. It is an actively harmful one. Every developer who encounters both `news.py` and `news_unified.py` must spend time determining which is the correct version to use, modify, or test against. The answer is not obvious from the filenames. The answer requires reading both files, understanding the inheritance hierarchy, and making a judgment call. This is time that should be spent on product work. It is instead spent on archaeology.

The maintenance burden is asymmetric and invisible. When a bug is found in the news adapter, the fix is applied to whichever file the developer happens to be looking at. If they fix `news.py`, the bug remains in `news_unified.py`. If they fix `news_unified.py`, the bug remains in `news.py`. Neither version has a comment pointing to the other. Neither has a deprecation notice. The developer who applies the fix believes the bug is resolved. It is not. The next developer to use the other version will encounter it again and wonder why it wasn't fixed.

The situation with `linkedin.py`, `patents.py`, and `web_search_news.py` is particularly concerning because these adapters were not covered by STORY-121, 122, or 123. Their unified counterparts may have their own functional regressions that have not yet been audited. This story must include a parity verification step for these three adapters before deletion, not just a mechanical file removal.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | 12 adapter files where 6 would suffice; every change requires checking both versions |
| **Developer Experience** | Onboarding requires archaeology to determine canonical adapter versions; no documentation guides the choice |
| **Reliability** | Bug fixes applied to one version silently leave the other version broken |
| **Codebase Clarity** | Import paths are ambiguous; `from data.news import X` and `from data.news_unified import X` coexist |

---

## Affected Files

| File | Issue |
|------|-------|
| `data/news.py` | Old version — to be deleted after STORY-121 confirms `news_unified.py` parity |
| `data/funding.py` | Old version — to be deleted after STORY-122 confirms `funding_unified.py` parity |
| `data/website.py` | Old version — to be deleted after STORY-123 confirms `website_unified.py` parity |
| `data/linkedin.py` | Old version — parity with `linkedin_unified.py` must be verified before deletion |
| `data/patents.py` | Old version — parity with `patents_unified.py` must be verified before deletion |
| `data/web_search_news.py` | Old version — parity with `web_search_news_unified.py` must be verified before deletion |
| All files importing old adapters | Import paths must be updated to unified versions |

---

## Architectural Requirements

- STORY-121, STORY-122, and STORY-123 must be completed and accepted before this story begins
- `linkedin.py`, `patents.py`, and `web_search_news.py` must each undergo a parity audit against their unified counterparts before deletion — this audit is in scope for this story
- Any functional gaps found in `linkedin_unified.py`, `patents_unified.py`, or `web_search_news_unified.py` during the parity audit must be documented as new stories before the old files are deleted (do not delete without parity)
- All import statements across the codebase referencing old adapter filenames must be updated to reference unified versions
- Import aliases that obscure the adapter version (e.g., `from data.news import NewsAdapter as NewsAdapter`) must be removed in favor of direct unified imports
- A grep verification step must confirm zero references to old adapter filenames in `src/` before the story is closed
- A developer-facing migration guide must be added to `docs/` documenting the adapter consolidation, the canonical interface for each adapter, and the rationale for the `BaseRefreshConnector` pattern
- The migration guide must include a table mapping old adapter names to their unified replacements

---

## Acceptance Criteria

- [ ] `data/news.py` does not exist in the repository
- [ ] `data/funding.py` does not exist in the repository
- [ ] `data/website.py` does not exist in the repository
- [ ] `data/linkedin.py` does not exist in the repository (after parity verified)
- [ ] `data/patents.py` does not exist in the repository (after parity verified)
- [ ] `data/web_search_news.py` does not exist in the repository (after parity verified)
- [ ] `grep -r "from data.news import\|from data.funding import\|from data.website import\|from data.linkedin import\|from data.patents import\|from data.web_search_news import" src/` returns empty
- [ ] All adapter-related tests pass against unified versions only
- [ ] Migration guide added to `docs/adapters/migration-guide.md`
- [ ] Migration guide includes mapping table from old to unified adapter names
- [ ] No import aliases that obscure adapter version remain in the codebase

---

## Definition of Done

- **Tests Required**: After all deletions, run the full test suite and verify zero failures attributable to missing adapter imports. Run `find src -name "*.py" | xargs grep -l "news\.py\|funding\.py\|website\.py\|linkedin\.py\|patents\.py\|web_search_news\.py"` and verify the command returns no results. For `linkedin.py`, `patents.py`, and `web_search_news.py`, document the parity audit results (pass or fail with specific gaps identified) before proceeding with deletion.
- **Documentation Required**: `docs/adapters/migration-guide.md` covering: (1) the rationale for the `BaseRefreshConnector` pattern, (2) a mapping table from old to unified adapter names, (3) the canonical import path for each unified adapter, (4) a note on what was restored in STORY-121, 122, and 123 for developers who need historical context.
- **Code Review Gate**: Reviewer must run the grep verification command and confirm empty output. Reviewer must verify the migration guide is present and complete. Reviewer must confirm that the parity audit for `linkedin.py`, `patents.py`, and `web_search_news.py` is documented — either as "parity confirmed, deleted" or "gaps found, new stories created."

---

## Notes

This story has a hard dependency on STORY-121, STORY-122, and STORY-123. Do not begin deletion work until all three are accepted. The order matters: restore parity first, delete second. Reversing this order removes the reference implementation before the unified version is verified, which is how the original migration created this problem in the first place.

The parity audit for `linkedin.py`, `patents.py`, and `web_search_news.py` is the highest-risk part of this story. These adapters were not covered by the initial audit that produced STORY-121, 122, and 123. They may have their own functional regressions. If the audit finds gaps, new stories must be created and completed before deletion. The temptation to delete and "fix it later" must be resisted. "Fix it later" is how this epic came to exist.

The migration guide is not optional documentation. It is the artifact that prevents this situation from recurring. The next developer who joins the team and sees `BaseRefreshConnector` in the codebase needs to understand why it exists, what it replaced, and how to use it correctly. Without the guide, the institutional knowledge lives only in git history and the memories of whoever was present for the migration. That is not sufficient.

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
