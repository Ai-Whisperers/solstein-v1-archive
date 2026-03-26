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
| 1 | STORY-006 | Fix Duplicate Class Body Definitions in config.py | VERIFY | Reconciliation says partial, README says complete |
| 2 | STORY-007 | Remove All Hardcoded Credentials | VERIFY | Check if defaults still exist |
| 3 | STORY-008 | Mandatory Startup Validation for All API Keys | VERIFY | Check startup validation coverage |

### EPIC-036: Configuration Consolidation (P2)

| # | Story | Title | Status | Notes |
|---|-------|-------|--------|-------|
| 4 | STORY-137 | Centralize All Environment Variables in config.py | READY | |
| 5 | STORY-138 | Replace Hardcoded Paths with Config-Driven Paths | READY | |
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
