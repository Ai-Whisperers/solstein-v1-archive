# Solstein Autonomous Work Queue

> Ordered by milestone, then epic, then story priority. The autonomous worker picks the first READY story top-to-bottom.

| Last Updated | 2026-03-26 | Updated By | Initial setup |

## Status Key

| Status | Meaning |
|--------|---------|
| READY | Available for the worker to pick up |
| VERIFY | Needs verification pass before marking DONE or READY |
| IN_PROGRESS | Currently being worked on |
| DONE | Completed, PR merged |
| BLOCKED | Dependencies not met |
| SKIP | Superseded or not applicable |

---

## Phase 0: Reconciliation (First Run Only)

The first worker run MUST do a verification pass before starting implementation work:

1. Read `backlog/EPIC_RECONCILIATION.md` (March 9 snapshot)
2. For each P0 epic (EPIC-002, 003, 004), verify actual code state matches claims
3. Update this queue with accurate statuses
4. Then proceed to pick up the first READY story

---

## M1: Safe Foundation

### EPIC-002: Configuration Integrity (P0) — Claimed Complete, VERIFY

| # | Story | Title | Status | Notes |
|---|-------|-------|--------|-------|
| 1 | STORY-006 | Fix Duplicate Class Body Definitions in config.py | DONE | Verified 2026-03-26: AST scan confirms no duplicate fields in any class |
| 2 | STORY-007 | Remove All Hardcoded Credentials | DONE | Verified 2026-03-26: No postgres:postgres or change-me-in-production defaults found |
| 3 | STORY-008 | Mandatory Startup Validation for All API Keys | DONE | Verified 2026-03-26: check_configuration() covers DB, JWT, GitHub, optional keys, LLM summary |

### EPIC-036: Configuration Consolidation (P2)

| # | Story | Title | Status | Notes |
|---|-------|-------|--------|-------|
| 4 | STORY-137 | Centralize All Environment Variables in config.py | DONE | PR #80 merged (content in develop) |
| 5 | STORY-138 | Replace Hardcoded Paths with Config-Driven Paths | DONE | PR #81 merged |
| 6 | STORY-139 | Centralize Timeouts and Magic Numbers | READY | |
| 7 | STORY-140 | Fix .env.example with All Required Variables | READY | |

### EPIC-037: Dead Code Elimination Phase 2 (P2)

| # | Story | Title | Status | Notes |
|---|-------|-------|--------|-------|
| 8 | STORY-141 | Delete Disconnected Refresh Router | READY | |
| 9 | STORY-142 | Delete Orphaned worker_tasks_v2.py | READY | |
| 10 | STORY-143 | Audit and Delete Orphaned Data Layer Files | READY | |
| 11 | STORY-144 | Create Dead Code Detection CI Job | READY | |

### EPIC-043: Repository Cleanup & Organization (P2)

| # | Story | Title | Status | Notes |
|---|-------|-------|--------|-------|
| 12 | STORY-165 | Archive Historical Professionalization Documents | READY | |
| 13 | STORY-166 | Consolidate Setup Documentation | READY | |
| 14 | STORY-167 | Organize Strategic Documents | READY | |
| 15 | STORY-168 | Create Repository Organization Standards | READY | |

---

## M2: Secure Identity

### EPIC-020: Supabase Auth Migration (P1) — BLOCKED on M1 completion

| # | Story | Title | Status | Notes |
|---|-------|-------|--------|-------|
| 16 | STORY-067 | Migrate Authentication to Supabase Auth | BLOCKED | Depends on EPIC-002 completion |
| 17 | STORY-068 | Remove Auth Bypass and Wire Supabase JWT Middleware | BLOCKED | |
| 18 | STORY-069 | Error Handling and Input Sanitization | BLOCKED | |
| 19 | STORY-070 | Fix SSRF Vulnerability in Web and Website Agents | BLOCKED | |

### EPIC-019: Multi-Tenancy & Data Isolation (P1) — BLOCKED on EPIC-020

| # | Story | Title | Status | Notes |
|---|-------|-------|--------|-------|
| 20 | STORY-063 | Define Tenant Model and Domain Object Scoping | BLOCKED | Depends on EPIC-020 |
| 21 | STORY-064 | Implement Supabase RLS for All Tables | BLOCKED | |
| 22 | STORY-065 | Add Tenant-Scoped API Key Management | BLOCKED | |
| 23 | STORY-066 | Enforce Tenant Isolation in Research Jobs | BLOCKED | |

---

## Critical Path P0s (New — Added After Last Audit)

### EPIC-045: CLI Runtime Correctness (P0)

| # | Story | Title | Status | Notes |
|---|-------|-------|--------|-------|
| 24 | — | See EPIC-045 README for stories | READY | 4 stories, check epic dir |

### EPIC-046: Scoring Engine Correctness (P0)

| # | Story | Title | Status | Notes |
|---|-------|-------|--------|-------|
| 25 | — | See EPIC-046 README for stories | READY | 4 stories, check epic dir |

### EPIC-052: Provenance, Confidence, Quality Gates (P0)

| # | Story | Title | Status | Notes |
|---|-------|-------|--------|-------|
| 26 | — | See EPIC-052 README for stories | READY | 4 stories |

### EPIC-058: Data Conversion Pipeline Consolidation (P0)

| # | Story | Title | Status | Notes |
|---|-------|-------|--------|-------|
| 27 | — | See EPIC-058 README for stories | READY | 4 stories |

### EPIC-062: Scraping Resilience and Evidence Ledger (P0)

| # | Story | Title | Status | Notes |
|---|-------|-------|--------|-------|
| 28 | — | See EPIC-062 README for stories | READY | 4 stories |

### EPIC-064: Markdown Integrity and Registry Correctness (P0)

| # | Story | Title | Status | Notes |
|---|-------|-------|--------|-------|
| 29 | — | See EPIC-064 README for stories | READY | 4 stories |

---

## M3-M6: Remaining Milestones

Worker should complete M1, M2, and Critical P0s before advancing to these.
See `backlog/README.md` for the full milestone roadmap.

---

## Orchestrator Log

Worker and checker append timestamped entries here:

<!-- Entries below this line -->

### [2026-03-26] Worker Run — STORY-138 Complete
- **Story implemented**: STORY-138 — Replace Hardcoded /home/ Paths with Config-Driven Resolution
- **PR created**: #81 targeting develop
- **Branch**: feature/STORY-138-config-driven-paths
- **Techniques**: `Path(__file__).resolve()` in all Python scripts; `BASH_SOURCE[0]` in all shell scripts; systemd `.template` files + `install-service.sh`; `STATE_DIR` env var for temp/counter dirs
- **New CI guard**: `scripts/ci/check_hardcoded_paths.py` — scans src/, bin/, scripts/ for /home/ paths; returns non-zero on violations
- **Tests added**: 10 unit tests in `tests/unit/test_story138_paths.py` (regression guard runs real project scan)
- **Incidental fixes**: bare excepts, lazy imports, split 138-line `validate_field_mapping` and 145-line `run_eneve_199.main`; removed circular import in `field_mapping_audit`
- **Quality gates**: all pre-commit hooks pass

### [2026-03-26 19:39] Work Checker Run
- **PRs merged**: 0 — worker lock active (worktrees in use: work/free-source-real-data-hardening, merge/free-source-real-data-hardening), skipped merge step
- **PRs rebased**: 0 (skipped — worker lock active)
- **Open PRs**: 6 remaining (PR#79 deps-bump, PR#75 websockets, PR#74 pytz, PR#72 cachetools, PR#71 protobuf, PR#68 audit) — all target master, not develop
- **Queue**: M1: 0/15 DONE. 3 VERIFY, 12 READY. M2: 8 BLOCKED. P0 new epics: 6 READY (EPIC-045, 046, 052, 058, 062, 064).
- **Dependencies unblocked**: None — M1 not yet complete, EPIC-020 and EPIC-019 remain BLOCKED correctly
- **Actions taken**: Pruned 5 stale remote tracking branches (closed dependabot PRs #70, 73, 76, 77, 78); deleted remote feat/phase-1-quality-improvements (PR#1 merged); local branch cleanup skipped (worktrees active)

### [2026-03-27 09:35] Work Checker Run
- **PRs merged**: 7 total — #81 (STORY-138), #68 (audit), #79 (deps-bump), #75 (websockets), #74 (pytz), #72 (cachetools), #71 (protobuf)
- **PRs rebased**: 1 successful (#80 STORY-137, clean rebase — branch already in develop, PR closed, branch deleted)
- **Open PRs**: 0 remaining
- **Queue**: M1: 5/15 DONE (EPIC-002: 3, EPIC-036: 2). 10 READY. M2: 8 BLOCKED. P0 new: 6 epics READY.
- **Dependencies unblocked**: None — M1 not yet complete
- **Branch hygiene**: Deleted 9 remote branches (2 feature, 5 dependabot auto-deleted, 1 orphaned 'update', 1 STORY-137). Pruned stale refs. 2 local branches cleaned.
- **Actions taken**: Fixed 6 PRs targeting master to develop; merged all; updated QUEUE.md notes
