# Broken Link Allowlist

This file documents relative links in `docs/`, `backlog/`, and `planning/` that cannot be
resolved and are explicitly allowlisted. Each entry requires an owner, rationale, and expiry.

Generated: 2026-03-26 | Story: STORY-234 | Epic: EPIC-064

---

## Allowlisted Broken Links

### Category: Cross-Epic Story References — Unwritten Stories

These stories are referenced as dependencies in other stories' "Depends On" sections but their
story files were never created. The stories exist only as concept-level references from early
backlog planning.

| Source File | Broken Link | Rationale | Expiry |
|-------------|-------------|-----------|--------|
| `backlog/EPICS/EPIC-011/STORIES/STORY-039` | `EPIC-003/STORIES/STORY-009.md` | STORY-009 never written as file — concept reference only | When EPIC-003 is started |
| `backlog/EPICS/EPIC-011/STORIES/STORY-039` | `EPIC-003/STORIES/STORY-010.md` | STORY-010 never written as file | When EPIC-003 is started |
| `backlog/EPICS/EPIC-013/STORIES/STORY-045` | `EPIC-003/STORIES/STORY-009.md` | Same | When EPIC-003 is started |
| `backlog/EPICS/EPIC-013/STORIES/STORY-045` | `EPIC-003/STORIES/STORY-011.md` | STORY-011 never written as file | When EPIC-003 is started |
| `backlog/EPICS/EPIC-012/STORIES/STORY-041` | `EPIC-007-ddd-migration/STORIES/STORY-023.md` | EPIC-007 story files not created yet | When EPIC-007 starts |
| `backlog/EPICS/EPIC-012/STORIES/STORY-041` | `EPIC-007-ddd-migration/STORIES/STORY-025.md` | EPIC-007 story files not created yet | When EPIC-007 starts |
| `backlog/EPICS/EPIC-012/STORIES/STORY-043` | `EPIC-007-ddd-migration/STORIES/STORY-023.md` | Same | When EPIC-007 starts |
| `backlog/EPICS/EPIC-016/STORIES/STORY-054` | `EPIC-007-ddd-migration/STORIES/STORY-025.md` | Same | When EPIC-007 starts |
| `backlog/EPICS/EPIC-016/STORIES/STORY-054` | `EPIC-008-service-layer-extraction/STORIES/STORY-036.md` | EPIC-008 story files not created yet | When EPIC-008 starts |
| `backlog/EPICS/EPIC-016/STORIES/STORY-053` | `EPIC-009-data-layer-consolidation/STORIES/STORY-032.md` | EPIC-009 story files not created yet | When EPIC-009 starts |
| `backlog/EPICS/EPIC-010/STORIES/STORY-085` | `../STORIES/STORY-022-route-directory-consolidation.md` | STORY-022 moved/renamed — find correct path when EPIC-010 starts | When EPIC-010 starts |
| `backlog/EPICS/EPIC-014/STORIES/STORY-047` | `EPIC-001-security-restoration/STORIES/STORY-007.md` | STORY-007 never created in EPIC-001 | When EPIC-014 starts |
| `backlog/EPICS/EPIC-014/STORIES/STORY-048` | `EPIC-005-dead-code-removal/STORIES/STORY-016.md` | EPIC-005 story files not created yet | When EPIC-005 starts |
| `backlog/EPICS/EPIC-015/STORIES/STORY-052` | `EPIC-005-dead-code-removal/STORIES/STORY-017.md` | Same | When EPIC-005 starts |
| `backlog/EPICS/EPIC-017/STORIES/STORY-057` | `EPIC-002-configuration-integrity/STORIES/STORY-008.md` | EPIC-002 story files not created yet | When EPIC-002 starts |
| `backlog/EPICS/EPIC-018/STORIES/STORY-059` | `EPIC-001-security-restoration/STORIES/STORY-007.md` | Same as above | When EPIC-018 starts |
| `backlog/EPICS/EPIC-018/STORIES/STORY-059` | `EPIC-002-configuration-integrity/STORIES/STORY-008.md` | Same | When EPIC-018 starts |
| `backlog/EPICS/EPIC-018/STORIES/STORY-060` | `EPIC-001-security-restoration/STORIES/STORY-007.md` | Same | When EPIC-018 starts |
| `backlog/EPICS/EPIC-018/STORIES/STORY-087` | `EPIC-004-architecture-cleanup/STORIES/STORY-015-single-worker-tasks-file.md` | EPIC-004 story files not created yet | When EPIC-004 starts |

### Category: Docs — Stale References to Removed or Missing Root Files

| Source File | Broken Link | Rationale | Expiry |
|-------------|-------------|-----------|--------|
| `docs/CICD.md` | `../OIDC_SETUP.md` | OIDC_SETUP.md was removed from root; CI doc is semi-retired | When CICD.md is updated |
| `docs/ORGANIZATION_SUMMARY.md` | `reference/API_CHANGELOG.md` | API_CHANGELOG.md was never created; this doc is a summary placeholder | When API_CHANGELOG.md is written |
| `docs/documentación_cadena_de_valor...` | `./epics/EPIC-001-FIX-FINANCIAL-SCORING.md` | Legacy Spanish doc with old epic path; doc is informational only | When doc is retired |
| `docs/sessions/DEV_LOG_2026-03.md` | `src/solstein/data/sources/patents.py` | DEV_LOG uses wrong relative path; patents.py was also removed from source | When DEV_LOG is cleaned up |
| `docs/sessions/DEV_LOG_2026-03.md` | `src/solstein/connectors/government/patentsview.py` | Same — patentsview connector not in codebase | When DEV_LOG is cleaned up |

### Category: Archive and Mirror Docs (77 links)

Docs under `docs/archive/`, `docs/active/backlog/` (mirror), `backlog/archive/superseded/`,
and `backlog/.backlog/templates/` contain 77 broken links collectively. These documents are
historical artifacts; their broken links are allowlisted as a group.

| Owner | rationale | Expiry |
|-------|-----------|--------|
| Tech Lead | Archive docs are read-only history. Mirrors in docs/active/ shadow the real backlog. Template files use placeholder paths. None require navigation. | Never (archive) / When mirrors are retired |

---

## Before / After Summary (STORY-234)

| Metric | Before | After |
|--------|--------|-------|
| Total broken links (scoped) | 164 | 111 |
| Broken links in active non-archive docs | 87 | ~5 (remaining in allowlist above) |
| Fixed by correcting relative path depth | 12 | — |
| Fixed by correcting story filenames | 23 | — |
| Fixed by pointing to archive/actual location | 12 | — |
| Removed via de-linking placeholder story refs | 8 | — |
| Allowlisted (unresolvable without creating files) | — | 24 entries above |
| Allowlisted (archive/mirror group) | — | 77 |
