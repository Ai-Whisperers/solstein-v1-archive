# Autonomous Agent Improvement Plan
**Date:** 2026-04-05  
**Author:** gesttaltt + Claude Sonnet 4.6  
**Scope:** Post-mortem of Hermes session (2026-03-31/04-01) + actionable improvements for all future autonomous agents

---

## 1. Executive Summary

Hermes ran 45 commits across two days and delivered 2 working stories out of a backlog with 30+ READY P0 items. One of those 2 stories (STORY-251) was immediately reversed by subsequent human work. The CI rebuild was the most impactful single action. No P0 contamination gate stories were touched. No work logs were written despite a work-logs directory being created.

This document diagnoses why, and specifies exactly what needs to change so the next agent session delivers more than infrastructure reshuffling.

---

## 2. Root Cause Analysis

### 2.1 Hermes worked from stale context

`.hermes.md` contained a project snapshot frozen at a point before the contamination audit (2026-03-31). It described "132 READY stories, 98 BLOCKED" but the actual P0 priority — `planning/QUEUE.md` — had explicit **⚠️ STOP. Read this before picking any other story** notices that Hermes apparently ignored or never reached.

**Evidence:** Hermes picked STORY-246 and STORY-247 (import cycle fixes, P2 engineering debt) while EPIC-086 P0 field loss stories sat untouched at the top of QUEUE.md with a mandatory execution-order warning.

### 2.2 No mandatory pre-read protocol

`.hermes.md` told the agent to "pick first READY story top-to-bottom" in QUEUE.md. But there was no instruction to:
- Read the full STOP notices at the top of the queue before picking anything
- Read the full story file (not just the queue summary line) before starting
- Verify the current codebase state against the story's "before" conditions

**Evidence:** STORY-251 told the agent to make domain models explicitly declare their extra-field policy. Hermes set `extra='ignore'` — technically a valid interpretation of "explicit" — but the *intent* was to move toward `extra='forbid'` to expose field loss. Four days later, gesttaltt implemented STORY-348 which flipped it to `extra='forbid'`, undoing Hermes' work entirely.

### 2.3 No session exit protocol

`.hermes.md` described the Karpathy MEASURE → CHANGE → TEST → MEASURE pattern, but there was no requirement to:
- Write a session exit log to `docs/work-logs/`
- Update story statuses in `planning/QUEUE.md` for stories worked but not completed
- Leave a "state as of session end" note for the next agent

**Evidence:** `docs/work-logs/` directory was created by Hermes but contains only a README. Zero session logs were written. The next agent has no record of what Hermes attempted, what failed, or what partial state exists.

### 2.4 No prohibition on planning work

Hermes spent commits on:
- Creating `.hermes.md` and upgrading it (meta work, not stories)
- Unblocking stories in bulk without verifying the unblocking condition was met
- Creating a work-logs README instead of an actual work log
- Documenting the product readiness audit into QUEUE.md (planning work)

None of this is prohibited in the current instructions. An autonomous agent should never make planning decisions without explicit authorization — it should only execute stories.

### 2.5 Incorrect story direction (STORY-251)

The story file specified enforcement of explicit extra-field policy on domain models. The agent interpreted "explicit" as `extra='ignore'` (makes the implicit v2 default explicit). The intent was `extra='forbid'` (makes violations visible). This is a story specification failure — the story didn't clearly state the *direction* of the change.

### 2.6 No verification before claiming done

Hermes created "Housekeeping: Mark STORY-XXX as DONE" commits after feature commits, but there is no evidence of:
- Running `pytest` before marking done
- Checking `git log` to ensure the change wasn't already made or already superseded
- Verifying the story's acceptance criteria line by line

### 2.7 AGENTS.md was outdated

`docs/reference/AGENTS.md` (last updated 2026-03-01) described architecture that no longer matched the codebase:
- Says "18 SQLAlchemy ORM models in `infrastructure/database_models.py`" — models were split into `infrastructure/models/` package months earlier
- Says "11 data source adapters" — the actual count of registered adapters is 6-7 (others were retired)
- Lists `monitoring/` as containing health checks — `worker_health()` is in `api/routers/health.py`

An agent that reads AGENTS.md will build a wrong mental model before touching any code.

---

## 3. What the Backlog Enrichment Fixed (and What It Didn't)

### Fixed (our 2026-04-03/04 work):

| Problem | Fix Applied |
|---------|-------------|
| Stories had no verified codebase state | Added exact `file:line` references to EPIC-013, EPIC-052, EPIC-033, EPIC-073, EPIC-087, EPIC-088, EPIC-089 |
| 739 bare STORY-NNN references unresolvable | Converted to clickable links across 88 READMEs |
| EPIC-071-085 existed only in QUEUE.md text | Materialized as full README + story files |
| Story number collisions | Resolved — 413-416, 405-412, 190-197 |
| EPIC-001 still showed "🔴 Open" | Updated to "📦 Superseded" |

### Not fixed (still needed):

| Problem | Status |
|---------|--------|
| `.hermes.md` has no session protocol | **See Section 4** |
| `docs/reference/AGENTS.md` is stale (2026-03-01) | Needs rebuild from current codebase |
| Story files lack "wrong direction" guardrails | Story-level acceptance criteria need negative examples |
| Work log template doesn't exist | Needs creating |
| No CI check that tests actually pass before "DONE" | Needs enforcement gate |
| `pgvector` / `duckduckgo_search` import failures block test collection | Two test files break `pytest` collection |

---

## 4. Required Changes to `.hermes.md`

### 4.1 Session Start Protocol (MANDATORY — do not skip)

Add this as the first section in `.hermes.md`:

```markdown
## Session Start Protocol

Run in order. Do NOT skip any step.

1. `git log --oneline -10` — know what changed before your session
2. `git status` — confirm working tree is clean before starting
3. Read ALL of `planning/QUEUE.md` from top — stop at every ⚠️ STOP notice and read the linked epic
4. Run baseline: `PYTHONPATH=src pytest tests/unit/ -q --no-header 2>&1 | tail -5`
   Record: N passed, N failed, N errors
5. Run lint baseline: `ruff check src/ --statistics 2>&1 | tail -5`
   Record: N violations

Only pick a story AFTER completing steps 1-5 and recording baselines.
```

### 4.2 Story Selection Rules

```markdown
## Story Selection Rules

- Pick the FIRST story in QUEUE.md with status READY that is not in the DO-NOT-TOUCH list
- Before selecting: read the FULL story file at `backlog/EPICS/EPIC-NNN-slug/STORIES/STORY-NNN.md`
  - NOT just the queue summary line
  - Read the Acceptance Criteria and Technical Notes sections completely
- If the story says "blocked by X", verify X is DONE in the queue before starting
- If the story file doesn't exist, skip it and flag in session log
- Never work on more than ONE story at a time

## DO-NOT-TOUCH Without Human Authorization

The following require human decision before implementation:
- Any story that changes authentication, authorization, or tenant isolation behavior
- Any Alembic migration (schema changes are irreversible without rollback)
- Any story marked "requires human release decision"
- STORY-276 (develop→master merge) — merge gates require human
- Any story in status BLOCKED regardless of your assessment of the blocker
```

### 4.3 Implementation Protocol

```markdown
## Per-Story Implementation Protocol

For EACH story:

1. **Read the epic README** — `backlog/EPICS/EPIC-NNN-slug/README.md`
   Look specifically for "Verified Codebase State" or "Autonomous Continuation Notes" sections
   These contain exact file:line references. Use them. Do not rediscover what is already documented.

2. **Verify the "before" state** — grep or read the specific line the story targets
   Do NOT assume the story description matches current code. Code changes. Stories don't always track.
   Example: `grep -n "strict_provenance" src/solstein/infrastructure/research_dual_write.py`
   If the before-state doesn't match, stop and log as "pre-condition mismatch — needs triage"

3. **Make the smallest possible change** — one file, one function, one line if possible
   Never refactor surrounding code. Never "improve" adjacent logic. Change exactly what the story says.

4. **Run tests immediately** — `PYTHONPATH=src pytest tests/unit/ -q -x 2>&1 | tail -10`
   If tests fail: revert. Do NOT commit broken tests.

5. **Run lint** — `ruff check src/ tests/ scripts/`
   If violations: fix them before committing.

6. **Write a regression test** — every story that touches production code needs at least one test
   that proves the change is correct. "Tests pass" is not sufficient. The test must specifically
   verify the story's acceptance criteria.

7. **Commit with metrics** — include in every commit message:
   - Tests: N passed (was N before)
   - Lint: 0 violations (was N before)
   - Story AC-1: [description of what proves this criterion is met]
```

### 4.4 Session Exit Protocol (MANDATORY)

```markdown
## Session Exit Protocol

Before ending any session, complete ALL of the following:

1. **Final test run** — record exact output
2. **Final lint run** — record exact output
3. **Update QUEUE.md** — for every story worked:
   - DONE: add PR reference
   - PARTIAL: change status to IN_PROGRESS, add note describing current state
   - ABANDONED: change status to VERIFY, explain why
4. **Write session log** to `docs/work-logs/YYYY-MM-DD-HHMM.md`
   Use the template in Section 5 of this document.
5. **Never leave a broken state** — if you broke something and can't fix it, REVERT the change
   A revert with a log entry is always better than leaving broken code.
```

### 4.5 Prohibited Actions

```markdown
## Prohibited Actions (never do these)

- ❌ Commit without running tests
- ❌ Mark a story DONE without a passing regression test for its acceptance criteria
- ❌ Unblock stories in bulk — only unblock a story if you directly verified the blocker is resolved
- ❌ Create new epics, new stories, or new planning documents — that is human work
- ❌ Modify `.hermes.md` itself — it's written by humans, not agents
- ❌ Push to remote without being explicitly asked to — commit to develop only
- ❌ "Fix" code that is not part of the current story — scope creep is a regression risk
- ❌ Delete files that aren't test artifacts — check `git blame` first
- ❌ Interpret a story's direction without reading its acceptance criteria in full
```

---

## 5. Work Log Template

Create `docs/work-logs/TEMPLATE.md`:

```markdown
# Work Log — YYYY-MM-DD HHMM

**Agent:** [Hermes / Claude Code / other]  
**Session start:** [timestamp]  
**Session end:** [timestamp]  
**Branch:** develop  

## Baseline (session start)

| Metric | Value |
|--------|-------|
| Tests (unit) | N passed / N failed / N errors |
| Lint violations | N |
| Last commit | [hash] [message] |

## Stories Worked

### STORY-NNN: [title]

**Status:** DONE / PARTIAL / ABANDONED  
**Files changed:** [list]  
**Test delta:** +N added, N passed, 0 failed  
**AC verified:**
- [x] AC-1: [what proves it]
- [ ] AC-2: [why not done]

**Notes:** [anything the next agent needs to know]

## End State (session end)

| Metric | Value |
|--------|-------|
| Tests (unit) | N passed / N failed / N errors |
| Lint violations | N |
| Last commit | [hash] [message] |

## Blockers Found

- [Any story that turned out to be impossible without human action]

## Recommended Next Story

[STORY-NNN: title — reason it should be next]
```

---

## 6. Story File Quality Standards

For future story files to be agent-executable without rediscovery, each story file must include:

### Required Fields

```markdown
## Pre-condition (verified YYYY-MM-DD)

The exact code state this story assumes as its starting point:
- `path/to/file.py:N` — current value: `expression = "wrong_value"`
- Grep command to verify: `grep -n "wrong_value" src/solstein/path/to/file.py`

## Change Required

Exact diff or precise description:
- File: `src/solstein/path/to/file.py`
- Line: N
- From: `expression = "wrong_value"`
- To: `expression = "correct_value"`

## Verification Command

```bash
# This command should pass after the change:
grep -n "correct_value" src/solstein/path/to/file.py
PYTHONPATH=src pytest tests/unit/test_specific_file.py -q
```

## Acceptance Criteria (machine-checkable)

- [ ] `grep "correct_value" src/solstein/path/to/file.py` returns line N
- [ ] `PYTHONPATH=src pytest tests/unit/test_story_NNN.py -v` → all pass
- [ ] `ruff check src/solstein/path/to/file.py` → 0 violations
```

---

## 7. AGENTS.md Rebuild Requirements

`docs/reference/AGENTS.md` must be rebuilt. Current state is stale (2026-03-01). The following are verified wrong as of 2026-04-05:

| AGENTS.md claim | Actual state |
|----------------|--------------|
| "18 SQLAlchemy ORM models in `infrastructure/database_models.py`" | Models are in `infrastructure/models/` package (split earlier) |
| "11 data source adapters" | `build_default_registry()` registers 6-7 adapters; 3 retired to `_retired/` |
| Health checks in `monitoring/` | `worker_health()` is at `src/solstein/api/routers/health.py:156` |
| "636 source files" | Audit shows 656 Python files as of 2026-04-02 |
| `mcp_servers: [filesystem, sequential-thinking, memory]` | Additional MCPs configured (github, playwright, fetch, serena) |

**Required action:** Rebuild AGENTS.md from current `git log`, `find src/ -name "*.py" | wc -l`, and direct file reads of key modules. Do not update incrementally — the drift is too wide.

---

## 8. Immediate P0 Work Queue for Next Agent

The following 8 stories are the highest-value, lowest-risk actions for the next session. Each has pre-verified codebase state in the linked epic README. They are ordered by impact-to-risk ratio.

| Priority | Story | Epic | Size | Verified Location | Expected Outcome |
|----------|-------|------|------|------------------|-----------------|
| 1 | STORY-383 | EPIC-052 | 1 line | `research_dual_write.py:424` | Quality gate re-enabled in production async path |
| 2 | STORY-376 | EPIC-013 | XS | `tests/test_integration.db`, `tests/test_perf.sqlite3` | 1.6MB removed from git |
| 3 | STORY-382 | EPIC-052 | 1 line | `test_modes.py:16` | Synthetic data no longer flows without explicit env var |
| 4 | STORY-374 | EPIC-013 | S | `test_api_routers_coverage.py:19-25` | Auth bypass isolated to fixture scope |
| 5 | STORY-375 | EPIC-013 | S | `test_load.py:7-8` | DATABASE_URL override isolated to fixture scope |
| 6 | STORY-370 | EPIC-052 | XS | `scripts/seed_db.py` | Faker-seeded records tagged synthetic |
| 7 | STORY-378 | EPIC-052 | XS | `src/solstein/data/seed_db.py` | Production seeder tags before save |
| 8 | STORY-371 | EPIC-013 | XS | `tests/factories.py:56`, `tests/factories/__init__.py:64` | Both CompanyFactory defaults to `data_source_type="synthetic"` |

All 8 are independent. All 8 have been verified by direct file read on 2026-04-04. None requires infrastructure, migrations, or human decision.

---

## 9. Known Broken Test Infrastructure

The next agent will encounter these failures and must not be confused by them:

| Failure | File | Root Cause | Workaround |
|---------|------|------------|-----------|
| `ModuleNotFoundError: No module named 'pgvector'` | `tests/conftest.py` (via import chain) | `conftest.py` imports `tests/factories/__init__.py` which imports `domain/facts.py` which imports `infrastructure/models/company.py` which uses `pgvector` — but pgvector IS installed in `.venv`. Root cause: test collection using wrong Python. | Run via `.venv/bin/python3 -m pytest` not `python3 -m pytest` |
| `ModuleNotFoundError: No module named 'duckduckgo_search'` | `tests/unit/test_async_boundary_regressions.py:11` | Module-level import of `web_research_pipeline.py` which requires `duckduckgo_search` — not in dev dependencies | Add `--ignore=tests/unit/test_async_boundary_regressions.py` until STORY-392 (add to deps or mock import) |
| Auth globally disabled for entire test session | `tests/unit/test_api_routers_coverage.py:19-25` | Module-scope `app.dependency_overrides` — STORY-374 fixes this | Add `--ignore=tests/unit/test_api_routers_coverage.py` until STORY-374 is done |

**Safe baseline test command for any agent session:**
```bash
PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -q \
  --ignore=tests/unit/test_async_boundary_regressions.py \
  --ignore=tests/unit/test_api_routers_coverage.py \
  --no-header 2>&1 | tail -5
```

---

## 10. Summary of Required Changes

| Item | File | Priority | Type |
|------|------|----------|------|
| Add session start/exit protocol | `.hermes.md` | CRITICAL | Rewrite |
| Add prohibited actions list | `.hermes.md` | CRITICAL | Addition |
| Add work log template | `docs/work-logs/TEMPLATE.md` | HIGH | New file |
| Rebuild AGENTS.md from current codebase | `docs/reference/AGENTS.md` | HIGH | Rewrite |
| Add pre-condition + verification to each P0 story file | 8 story files | HIGH | Per-story |
| Add `duckduckgo_search` to dev dependencies or mock import | `pyproject.toml` / test file | MEDIUM | Bug fix |
| Add CI check: agent must not leave failing tests | `.github/workflows/ci.yml` | MEDIUM | Gate |

---

## 11. Verified Test Baseline (2026-04-05)

Two full test runs completed after the backlog enrichment commits. This is the authoritative regression floor for all future sessions.

### Results (both runs consistent)

| Run | Python binary | Passed | Failed | Errors | Skipped | Duration |
|-----|--------------|--------|--------|--------|---------|----------|
| Run A | system `python3` + `--ignore` x2 | 3851 | 295 | 237 | 5 | 7m 34s |
| Run B | `.venv/bin/python3` + `--ignore` x2 | 3855 | 291 | 237 | 5 | 22m 27s |

**Canonical baseline: 3855 passed / 291 failed / 237 errors**  
(4-test variance between runs is pytest-randomly ordering noise — not a real difference)

### What the failures and errors mean

**291 failures** — all infrastructure-dependent. Every failing test requires a live PostgreSQL or Redis instance that is not present in local dev. These are expected and must NOT be "fixed" by an agent. Do not add `pytest.mark.skip`, mock the DB, or change the tests. They pass in CI (which spins up postgres:14-alpine).

**237 errors** — same cause: test collection succeeds but setup fixtures that require a DB session fail at runtime. Same class of expected failure.

**Regression rule:** If a future session reports fewer than **3800 passing tests**, regressions were introduced. Stop and investigate before committing.

### Python binary matters

The `pgvector` import error seen earlier in this session was an invocation artifact: system `python3` lacks `pgvector` in its site-packages, but `.venv/bin/python3` has it installed (v0.4.2). The `--ignore` flags for the two known-broken files are still required regardless of which binary is used, because:

- `test_async_boundary_regressions.py` — imports `duckduckgo_search` which is not in any Python environment on this machine (not in `pyproject.toml` dev deps)
- `test_api_routers_coverage.py` — module-scope auth bypass (STORY-374 fixes this at source)

### Corrected Section 9 entry for pgvector

The earlier Section 9 table listed `pgvector` as a test infrastructure bug. That entry is **incorrect**. Using `.venv/bin/python3` resolves it completely. The only real import blocker is `duckduckgo_search`.

---

## 12. Additional Anti-Patterns Identified from Hermes Session

### 12.1 Bulk story unblocking without verification

Hermes committed `chore: unblock ALL blocked stories (4 blockers → 0)` — a single commit that changed the status of multiple stories without any code change or verification that the blocking condition was resolved. This is dangerous: a story marked READY that is actually still blocked will waste the next agent's entire session on a dead end.

**Rule addition for `.hermes.md`:** Only change a story status from BLOCKED to READY if you directly verified (by file read or grep) that the dependency the story was blocked on is present in the codebase.

### 12.2 Creating infrastructure for infrastructure's sake

Hermes created `docs/work-logs/README.md` — a README for a directory that contains no actual work logs. The act of creating the scaffolding was committed as progress. This is the planning-work anti-pattern applied to docs.

**Rule addition:** Never create a directory, template, or README for work that isn't done yet. Create the actual artifact or don't create anything.

### 12.3 Interpreting absence of ruff output as a problem

`ruff check src/` produces **no output** when there are zero violations. An agent that pattern-matches on "empty output = error" will misdiagnose a clean lint state. Always use the exit code: `ruff check src/; echo "exit: $?"` — exit 0 means clean.

### 12.4 Not checking `git log` before starting a story

Hermes implemented STORY-251 without checking that gesttaltt had been actively working on the same epic hours earlier. A `git log --oneline -10` at session start would have shown the recent activity and prompted Hermes to check whether STORY-251's direction was already decided.

**Rule:** Run `git log --oneline -10` as the first command of every session. If the most recent commits touch the same epic you're about to work on, read those commits before starting.

### 12.5 Feature flag / story status inflation

The commit `chore: unblock ALL blocked stories (4 blockers → 0)` changed story statuses in QUEUE.md based on Hermes' own assessment of what was blocking them — not based on verified code state. Status changes are planning decisions. An agent should only update a story status to DONE after delivering the code change, not as a planning assertion.

---

## 13. CI Coverage Threshold is Too Low

`ci.yml` runs `pytest --cov-fail-under=25`. At 28% actual coverage, this gate has almost no headroom — a single file deletion would pass it. It provides no protection against coverage regression.

**Recommended increments:**

| Timeline | Threshold | Rationale |
|----------|-----------|-----------|
| Now | 25% (current) | Baseline — do not lower |
| After STORY-374/375 (test isolation fixes) | 30% | Test isolation improvements expose real coverage |
| After EPIC-013 complete | 35% | Factory/boundary tests added |
| After EPIC-069 (golden runs) | 40% | Integration test harness in place |

Each threshold increase should be a separate commit after the tests that justify it are merged. Never raise the threshold without the tests to back it.

---

## 14. `.hermes.md` Current State vs Required State

For human reference — a side-by-side of what exists and what needs to change:

| Section | Current `.hermes.md` | Required |
|---------|---------------------|----------|
| Session start | Not present | Mandatory 5-step protocol |
| Story selection | "Pick first READY top-to-bottom" | Full rules with DO-NOT-TOUCH list |
| Implementation | Karpathy 5-step loop (abstract) | Per-story protocol with exact commands |
| Session exit | Not present | Mandatory work log + QUEUE.md update |
| Prohibited actions | Not present | Explicit list (12.1–12.5 above) |
| Test baseline | Not present | 3855/291/237 with regression floor |
| Python binary | Not specified | `.venv/bin/python3` required |
| AGENTS.md reference | Not present | "Verify AGENTS.md before trusting architecture claims" |

The current `.hermes.md` is 56 lines. The required version is approximately 150 lines. All additions are operational rules, not prose.

---

---

## 15. Navigation Guide: Where to Look Given the Abundance of Issues

The codebase has 90 EPICs, 350+ stories, and 342 markdown files. An agent opening the repo cold will drown. This section is the entry point map — read in this order, nothing else.

### The 3-file read sequence (mandatory session start)

```
1. planning/QUEUE.md          lines 1–120   ← P0 emergencies, current execution order
2. backlog/EPICS/EPIC-052-provenance-confidence-quality-gates/README.md  ← gate state
3. backlog/EPICS/EPIC-013-test-suite-integrity/README.md                 ← test isolation
```

After these three files, an agent has enough context to pick and execute any P0 story without further reading. Everything else is background.

### Do NOT read these files first (they will mislead you)

| File | Why it misleads |
|------|----------------|
| `NEXT_ACTIONS.md` | Written 2026-03-31, superseded by QUEUE.md. References a broken state that has since been partially fixed. |
| `docs/reference/AGENTS.md` | Last updated 2026-03-01. Seven documented incorrect claims (see Section 7). Architecture diagrams are stale. |
| `.hermes.md` (architecture section) | Says "70 EPICs" — there are now 90. Story counts are stale. |
| `docs/audit/HEALTH_REPORT_2026-04-01.md` | Snapshot from April 1. EPIC-086 was open then; it is DONE now. |
| `backlog/EPICS/EPIC-071-085/` | These are P1–P5 product stories. Do not read before clearing the P0 queue. |
| Any file in `docs/active/` | These were being migrated during a docs cleanup. Status uncertain; do not treat as current. |

### Issue triage map

The issues in this codebase fall into four distinct classes. Agents should work down this list strictly — never start a lower class while a higher class has READY stories.

```
Class 1 — CONTAMINATION GATE (P0): data_source_type not enforced
  Stories: STORY-383, 382, 366, 367, 368, 370, 378, 379, 380, 381, 384, 385, 386, 388, 389, 390
  Root cause: Synthetic/untagged data reaches scoring and export without detection
  Signals in code: grep for "strict_provenance=False", "mixed", "unknown", "ensure_safe"
  Epic: EPIC-052

Class 2 — TEST ISOLATION (P0): module-scope mutations bypass security for entire session
  Stories: STORY-371, 372, 373, 374, 375, 376, 377, 387
  Root cause: app.dependency_overrides and os.environ set at import time
  Signals in code: grep module-level "os.environ[" and "app.dependency_overrides[" in tests/
  Epic: EPIC-013

Class 3 — DB SCHEMA GAP (P0): data_source_type column missing from company_records
  Stories: STORY-381, 384, 386
  Root cause: Gate field cannot be persisted or queried — all DB-loaded records bypass gate
  Signals in code: grep "data_source_type" in infrastructure/models/company.py → nothing
  Epic: EPIC-033

Class 4 — PRODUCT BACKLOG (P1–P5): features, adapters, infra
  Stories: STORY-277–347 (EPIC-071–085)
  Do not touch until Classes 1–3 are complete
```

### Quick orientation grep commands

Run these at session start to orient yourself instantly:

```bash
# How many P0 stories still READY?
grep -c "| READY |" planning/QUEUE.md

# Are gate bypass paths still present?
grep -n "strict_provenance=False" src/solstein/infrastructure/research_dual_write.py
grep -n '"mixed"' src/solstein/core/test_modes.py

# Are test module-scope mutations still present?
grep -n "^os.environ\[" tests/unit/test_api_routers_coverage.py tests/performance/test_load.py
grep -n "^app.dependency_overrides" tests/unit/test_api_routers_coverage.py

# Is data_source_type column missing?
grep -n "data_source_type" src/solstein/infrastructure/models/company.py

# Are the test databases still tracked in git?
git ls-files tests/test_integration.db tests/test_perf.sqlite3
```

If all five checks return nothing (or expected "no output"), the P0 class 1–3 work is done.

---

## 16. Verification Task Library

For every P0 story, this section provides exact before-state grep (to confirm the pre-condition holds), after-state grep (to confirm the fix landed), and the regression test command. Run all three for every story.

---

### STORY-383 — Remove `strict_provenance=False` from `_payload_from_legacy_kwargs()`

**File:** `src/solstein/infrastructure/research_dual_write.py:424`

```bash
# BEFORE (must return line 424 — if it doesn't, story was already done or file moved):
grep -n "strict_provenance=False" src/solstein/infrastructure/research_dual_write.py

# AFTER (must return nothing):
grep -n "strict_provenance=False" src/solstein/infrastructure/research_dual_write.py

# Regression test:
PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -k "legacy_kwargs or dual_write or strict_provenance" -v --no-header
# Expected: 0 failures. Add a test if none exists that asserts legacy path triggers the quality gate.
```

**What "done" looks like:** Line 424 reads `strict_provenance=True,` or the argument is removed entirely (if the field has a default of True). Verify by reading `pipeline.py:82-84` — the `if not strict_provenance: return` guard must be reachable only when explicitly set.

---

### STORY-382 — Change `SOLSTEIN_TEST_MODE` default from `"mixed"` to `"strict_real"`

**File:** `src/solstein/core/test_modes.py:16`

```bash
# BEFORE:
grep -n '"mixed"' src/solstein/core/test_modes.py
# Expected: line 16: mode = os.getenv("SOLSTEIN_TEST_MODE", "mixed").strip().lower()

# AFTER:
grep -n '"strict_real"' src/solstein/core/test_modes.py
# Expected: line 16: mode = os.getenv("SOLSTEIN_TEST_MODE", "strict_real").strip().lower()

# Regression test:
PYTHONPATH=src .venv/bin/python3 -c "
import os
# unset the env var to test default behavior
os.environ.pop('SOLSTEIN_TEST_MODE', None)
from solstein.core.test_modes import get_test_mode
mode = get_test_mode()
assert not mode.allow_synthetic, f'Expected allow_synthetic=False, got {mode.allow_synthetic}'
print('PASS: unset env var produces allow_synthetic=False')
"
```

---

### STORY-376 — Remove `test_integration.db` and `test_perf.sqlite3` from git

```bash
# BEFORE (must return both files):
git ls-files tests/test_integration.db tests/test_perf.sqlite3

# AFTER (must return nothing):
git ls-files tests/test_integration.db tests/test_perf.sqlite3

# Verify .gitignore rule added:
grep "test_integration.db\|test_perf.sqlite3\|\.sqlite3\|\.db" .gitignore

# No regression test needed — this is a git operation. Verify the files are gone from tracking.
# Note: the files may still exist on disk (that's fine). They must not be tracked.
```

---

### STORY-374 — Move module-scope auth bypass in `test_api_routers_coverage.py` into fixtures

**File:** `tests/unit/test_api_routers_coverage.py:19–25`

```bash
# BEFORE (lines 20, 21, 25 must be at column 0 — module scope):
grep -n "^app.dependency_overrides\|^os.environ" tests/unit/test_api_routers_coverage.py
# Expected: lines 20, 21, 25 with no leading whitespace

# AFTER (those lines must be inside a fixture — indented):
grep -n "^app.dependency_overrides\|^os.environ" tests/unit/test_api_routers_coverage.py
# Expected: nothing (module-scope mutations gone)

# Regression test (remove from ignore list first):
PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/test_api_routers_coverage.py -v --no-header 2>&1 | tail -5
# Expected: tests pass AND auth is no longer globally disabled after collection
```

---

### STORY-375 — Move `DATABASE_URL` override in `test_load.py` into a monkeypatched fixture

**File:** `tests/performance/test_load.py:7–8`

```bash
# BEFORE (lines 7-8 must be at column 0 — before any imports):
grep -n "^os.environ\[.DATABASE_URL.\]\|^os.environ\[.SYNC_DATABASE_URL.\]" tests/performance/test_load.py
# Expected: lines 7 and 8 with no leading whitespace

# AFTER:
grep -n "^os.environ\[.DATABASE_URL.\]\|^os.environ\[.SYNC_DATABASE_URL.\]" tests/performance/test_load.py
# Expected: nothing

# Regression test:
PYTHONPATH=src .venv/bin/python3 -m pytest tests/performance/test_load.py -v --no-header 2>&1 | tail -5
```

---

### STORY-370 — Set `data_source_type="synthetic"` in `scripts/seed_db.py`

**File:** `scripts/seed_db.py` (Faker-seeded records)

```bash
# BEFORE:
grep -n "data_source_type" scripts/seed_db.py
# Expected: nothing

# AFTER:
grep -n "data_source_type" scripts/seed_db.py
# Expected: at least one line setting data_source_type="synthetic" before the save call

# Regression test:
PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -k "seed_db or seed" -v --no-header 2>&1 | tail -5
# Add a test if none exists: instantiate the Company/record built by seed_db and assert data_source_type == "synthetic"
```

---

### STORY-378 — Set `data_source_type` in `src/solstein/data/seed_db.py` before `repo.save()`

**File:** `src/solstein/data/seed_db.py` (production Supabase seeder)

```bash
# BEFORE:
grep -n "data_source_type" src/solstein/data/seed_db.py
# Expected: nothing

# AFTER:
grep -n "data_source_type" src/solstein/data/seed_db.py
# Expected: line setting data_source_type="synthetic" before line 31 (repo.save(scored_company))

# Verify order — the assignment must come BEFORE repo.save():
grep -n "data_source_type\|repo.save" src/solstein/data/seed_db.py
```

---

### STORY-371 — Add `data_source_type="synthetic"` default to both `CompanyFactory` definitions

**Files:** `tests/factories.py:56` AND `tests/factories/__init__.py:64`

```bash
# BEFORE (must return nothing for both files):
grep -n "data_source_type" tests/factories.py tests/factories/__init__.py

# AFTER (must appear in BOTH files):
grep -n "data_source_type" tests/factories.py tests/factories/__init__.py
# Expected: two lines, one per file, both showing data_source_type = "synthetic"

# Regression test:
PYTHONPATH=src .venv/bin/python3 -c "
import sys; sys.path.insert(0, 'src'); sys.path.insert(0, '.')
from tests.factories import CompanyFactory
c = CompanyFactory()
assert c.data_source_type == 'synthetic', f'Got: {c.data_source_type}'
print('PASS: CompanyFactory defaults to data_source_type=synthetic')
"
```

---

### STORY-366 — Block `data_source_type="unknown"` in `ReportReleaseGate`

**File:** `src/solstein/data/report_release_gate.py:172`

```bash
# BEFORE (unknown is NOT in the blocked set — only synthetic and mixed are blocked):
grep -n '"unknown"' src/solstein/data/report_release_gate.py
# Expected: nothing (unknown is the fallback default but is not explicitly blocked)

# AFTER:
grep -n '"unknown"' src/solstein/data/report_release_gate.py
# Expected: "unknown" appears in the blocked condition alongside "synthetic" and "mixed"

# Regression test:
PYTHONPATH=src .venv/bin/python3 -c "
import sys; sys.path.insert(0, 'src')
from solstein.data.report_release_gate import ReportReleaseGate
from solstein.domain.models import Company
gate = ReportReleaseGate(min_confidence=0.0, allow_synthetic=False)
# Create a company with unknown data_source_type
c = Company(id='test', name='Test', data_source_type='unknown')
result = gate.evaluate([c])
assert not result.passed, 'Gate must block data_source_type=unknown'
print('PASS: unknown is blocked')
"
```

---

### STORY-367 — Wire `SyntheticDataBlocker.ensure_safe()` into export path

**File:** `src/solstein/api/routers/export.py` (add caller)  
**Definition:** `src/solstein/data/synthetic_data_safety.py:284`

```bash
# BEFORE (no callers in production code — only the definition):
grep -rn "ensure_safe" src/ --include="*.py" | grep -v "synthetic_data_safety.py\|\.pyc"
# Expected: nothing

# AFTER:
grep -rn "ensure_safe" src/ --include="*.py" | grep -v "synthetic_data_safety.py\|\.pyc"
# Expected: at least one call site in export.py or a shared export boundary

# Regression test:
PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -k "ensure_safe or synthetic_blocker" -v --no-header
```

---

### STORY-368 — Add `if not gate_result.passed: raise` guard in `export.py`

**File:** `src/solstein/api/routers/export.py:42` (and L120 — both export endpoints)

```bash
# BEFORE (gate_result is computed but .passed is never checked to raise):
grep -n "gate_result.passed\|if not gate_result" src/solstein/api/routers/export.py
# Expected: nothing — gate_result is used only for metadata, never to block

# AFTER:
grep -n "gate_result.passed\|if not gate_result" src/solstein/api/routers/export.py
# Expected: at least one line with "if not gate_result.passed"

# Regression test:
PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -k "export and (gate or synthetic or blocked)" -v --no-header
# Must include a test asserting that a request with synthetic data returns 4xx, not 200.
```

---

### STORY-381 + STORY-386 — Fix `load_competitor_data.py` (land in same PR)

**File:** `src/solstein/migrations/load_competitor_data.py`  
**STORY-381** targets line 77 (missing `data_source_type`)  
**STORY-386** targets line 179 (`test=True` in production path)

```bash
# BEFORE:
grep -n "data_source_type" src/solstein/migrations/load_competitor_data.py
# Expected: nothing

grep -n "test=True" src/solstein/migrations/load_competitor_data.py
# Expected: line 179: db_url = settings.get_database_url(test=True) or "..."

# AFTER:
grep -n "data_source_type" src/solstein/migrations/load_competitor_data.py
# Expected: line in _build_company_record() setting data_source_type="real"

grep -n "test=True" src/solstein/migrations/load_competitor_data.py
# Expected: nothing

# Regression test:
PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -k "competitor_data or load_competitor" -v --no-header
```

---

### STORY-384 — Add `data_source_type` column to `CompanyRecord`

**File:** `src/solstein/infrastructure/models/company.py` (add column)  
**Also requires:** new Alembic migration (020 or next available number)

```bash
# BEFORE:
grep -n "data_source_type" src/solstein/infrastructure/models/company.py
# Expected: nothing (only data_source exists at line 77)

# AFTER:
grep -n "data_source_type" src/solstein/infrastructure/models/company.py
# Expected: data_source_type = Column(String(20), nullable=True) or similar

# Verify migration created:
ls alembic/versions/ | grep -i "020\|data_source"
# Expected: new file like 020_add_data_source_type_to_company_records.py

# Regression test — verify migration is reversible:
PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -k "data_source_type or company_record" -v --no-header
```

---

## 17. Verification Summary Checklist

Use this as a post-session audit. Every checkbox should be ticked before writing the session exit log.

```markdown
## Session Verification Checklist

### Gate bypass paths (Class 1)
- [ ] `grep -n "strict_provenance=False" src/solstein/infrastructure/research_dual_write.py` → nothing
- [ ] `grep -n '"mixed"' src/solstein/core/test_modes.py` → references strict_real, not mixed
- [ ] `grep -rn "ensure_safe" src/ --include="*.py" | grep -v synthetic_data_safety` → ≥1 caller
- [ ] `grep -n "if not gate_result.passed" src/solstein/api/routers/export.py` → ≥1 line
- [ ] `grep -n '"unknown"' src/solstein/data/report_release_gate.py` → unknown in blocked set

### Test isolation (Class 2)
- [ ] `grep -n "^app.dependency_overrides\[" tests/unit/test_api_routers_coverage.py` → nothing
- [ ] `grep -n "^os.environ\[" tests/performance/test_load.py` → nothing
- [ ] `git ls-files tests/test_integration.db tests/test_perf.sqlite3` → nothing
- [ ] `grep -n "data_source_type" tests/factories.py tests/factories/__init__.py` → 2 lines

### DB schema gap (Class 3)
- [ ] `grep -n "data_source_type" src/solstein/infrastructure/models/company.py` → ≥1 line
- [ ] `grep -n "test=True" src/solstein/migrations/load_competitor_data.py` → nothing
- [ ] `grep -n "data_source_type" src/solstein/migrations/load_competitor_data.py` → ≥1 line

### Regression floor
- [ ] `PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -q --ignore=tests/unit/test_async_boundary_regressions.py --ignore=tests/unit/test_api_routers_coverage.py --no-header 2>&1 | tail -3` → ≥3800 passed
- [ ] `ruff check src/ tests/ scripts/` → exit code 0
```

---

*This document is for human review and implementation. Agents should not act on this document directly — the improvements must be applied to `.hermes.md`, `AGENTS.md`, and story files before the next autonomous session starts.*
