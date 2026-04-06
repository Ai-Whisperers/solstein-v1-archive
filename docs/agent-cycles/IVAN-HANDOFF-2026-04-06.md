# Ivan Handoff — Hermes Pipeline Improvements
**Date:** 2026-04-06  
**Author:** gesttaltt + Claude Sonnet 4.6  
**Scope:** Full session summary + actionable items for Ivan to improve the Hermes autonomous agent loop today

---

## What This Session Accomplished (Summary Table)

| # | What We Found / Built | Why It Matters for Hermes |
|---|----------------------|--------------------------|
| 1 | **Hermes made 45 commits, delivered 2 lasting stories** (STORY-246, STORY-247). STORY-251 was reversed. The rest was scaffolding, log noise, or CI rebuild. | Volume of commits is not a proxy for value. The agent was busy but not productive. |
| 2 | **No session protocol existed.** Hermes had no mandatory first-read, no story selection rule, no exit checklist. It picked stories by intuition or epic order. | Every failure traces back to this. Discipline cannot be optional for an autonomous agent. |
| 3 | **`planning/QUEUE.md` was 2015 lines long** — mostly Hermes work-checker run logs appended in a loop. The actual queue was buried under hundreds of stale entries. | Hermes was reading its own noise as context. The queue file had become unreadable. |
| 4 | **EPIC-083 had a stale baseline** ("~313 failed") vs actual (3855/291/237). EPIC-084 declared two files safe to delete that have active callers (`cli_research.py:22`, `review.py:168`). | Hermes would have run STORY-340/343 and broken production imports. Wrong facts in story files are directly executable bugs. |
| 5 | **STORY-337 and STORY-374 directly conflict** in scope on the same file. STORY-337 adds an auth bypass; STORY-374 removes one. No coordination warning existed. | If Hermes ran both in any order, one would silently undo the other. |
| 6 | **`AGENTS.md` and `CLAUDE.md` did not exist at project root.** Only a stale `docs/reference/AGENTS.md` from March. | Agent runtimes auto-load root-level files. Without them Hermes starts cold every session with no context unless it chooses to read `.hermes.md` — which it didn't. |
| 7 | **Built `backlog/EXECUTION_ORDER.md`** — 95 stories in strict dependency/priority order across 10 phases, with hard gate criteria and Status column Hermes updates per story. | Removes all ambiguity from "what do I work on." First READY row = next action. No reasoning required. |
| 8 | **Rewrote `.hermes.md`** with 6 hard selection constraints, 9 prohibited actions (each derived from a real prior failure), verified facts table, correct python invocation, and regression floor. | Turns the protocol from a suggestion into a machine-readable ruleset. |
| 9 | **Created `AGENTS.md` + `CLAUDE.md` at root + `.claude/rules/agent-bootstrap.md`** — three auto-loaded files that all enforce the same two mandatory reads before any work. | Context is now injected, not requested. Hermes cannot start a session without receiving it. |
| 10 | **Standardized all 18 epics (EPIC-071–089)** — added Verified Codebase State to 4 epics, corrected wrong assumptions in 2, added DoD checklists, flagged blocked/dangerous stories explicitly. | Story files are the instructions Hermes executes. Errors in them are errors in production. |

---

## Files Created / Modified This Session

### New files
| File | Purpose |
|------|---------|
| `AGENTS.md` | Root-level auto-loaded by OpenCode, Codex, Gemini — enforces first reads |
| `CLAUDE.md` | Root-level auto-loaded by Claude Code — same bootstrap protocol |
| `.claude/rules/agent-bootstrap.md` | Loaded by Claude Code rules engine before every tool call |
| `backlog/EXECUTION_ORDER.md` | Canonical ordered queue — 95 stories, 10 phases, hard gates |
| `docs/agent-cycles/IVAN-HANDOFF-2026-04-06.md` | This file |

### Modified files
| File | What Changed |
|------|-------------|
| `.hermes.md` | Full rewrite — mandatory reads, 6 selection constraints, 9 prohibited actions, verified facts table, regression floor, correct python invocation |
| `backlog/EPICS/EPIC-071–085/README.md` (14 files) | Standardized metadata tables, added DoD checklists, added Verified Codebase State |
| `backlog/EPICS/EPIC-086–089/README.md` (4 files) | Converted blockquote metadata to standard table format |
| `backlog/EPICS/EPIC-083/README.md` | Fixed stale baseline; added STORY-337/374 coordination warning |
| `backlog/EPICS/EPIC-084/README.md` | Corrected wrong "safe to delete" assumptions for STORY-340/343 |
| `backlog/EPICS/EPIC-033/README.md` | Added Verified Codebase State (data_source_type gap, migration test URL) |
| `backlog/EPICS/EPIC-073/README.md` | Added Verified Codebase State (build_default_registry adapter inventory) |
| `backlog/EPICS/EPIC-001/README.md` | Status changed to Superseded by EPIC-020 |
| `docs/agent-cycles/HERMES-IMPROVEMENT-PLAN-2026-04-05.md` | Created in prior session (476 lines, full post-mortem) |

---

## The Hermes Loop — Current Architecture

```
Agent runtime starts
        ↓
[AUTO] Loads AGENTS.md / CLAUDE.md (root)        ← NEW: enforced
[AUTO] Loads .claude/rules/agent-bootstrap.md    ← NEW: enforced
        ↓
Agent reads .hermes.md                           ← NOW MANDATORY (was optional)
Agent reads backlog/EXECUTION_ORDER.md           ← NOW MANDATORY (was optional)
        ↓
Agent picks first READY row in queue             ← NOW DETERMINISTIC (was intuition)
Agent reads story file
Agent runs Before-grep to verify bug exists
        ↓
Implements change
Runs tests (must stay ≥ 3800 passing)
Runs After-grep to verify fix
        ↓
Commits: feat(STORY-NNN): <title>
Updates EXECUTION_ORDER.md Status → DONE
Checks if any BLOCKED rows are now unblocked
        ↓
Session ends — writes work log (REQUIRED, not done yet — see open items)
```

---

## What Is Still Missing — Ivan's Focus Areas for Today

These are the remaining gaps in the Hermes loop that this session did **not** close:

### 1. No session work log enforcement ⚠️ HIGH

**Problem:** `.hermes.md` tells Hermes to write a session log. `docs/work-logs/` directory exists with just a README. Zero logs have ever been written.

**Impact:** When Hermes fails mid-story (crashes, context exhaustion, bad implementation), the next session has no record of partial state. It re-derives everything from scratch and often re-attempts the same failed approach.

**Fix needed:** 
- Add a work log template to `docs/work-logs/TEMPLATE.md`
- Make the exit protocol in `.hermes.md` mandatory with a specific format: `docs/work-logs/YYYY-MM-DD-STORY-NNN.md`
- Consider adding a pre-commit hook that rejects commits lacking a work log entry for the story being committed

**Work log minimum fields:**
```markdown
# Work Log — STORY-NNN
Date: YYYY-MM-DD
Story: <title>
Status: COMPLETE | PARTIAL | ABANDONED
Before-grep result: <output>
After-grep result: <output>
Tests before: X passed / Y failed
Tests after: X passed / Y failed
Blockers encountered: <or "none">
State left for next session: <or "clean">
```

---

### 2. No verification that Hermes actually read the mandatory files ⚠️ HIGH

**Problem:** `AGENTS.md` says "read `.hermes.md` first." There is no mechanism to verify this happened. An agent can silently skip the read and proceed.

**Fix options:**
- **Option A — Session start script:** Create `scripts/hermes-session-start.sh` that cats `.hermes.md` and `EXECUTION_ORDER.md` to stdout, forcing the agent to process them as tool output before doing anything else. If Hermes is invoked via a launcher, inject this as the first tool call.
- **Option B — Commit hook guard:** Add a pre-commit hook that checks whether the commit message contains `STORY-NNN` matching a READY row in `EXECUTION_ORDER.md`. Rejects commits for stories not in the queue or not in READY state.
- **Option C — Queue lock file:** Before starting a story, Hermes must write `backlog/.hermes-lock` containing `{ "story": "STORY-NNN", "session_start": "ISO-timestamp" }`. Pre-commit hook verifies this file exists and matches the story in the commit message.

**Recommendation:** Option C is the most practical — it's a file write that Hermes must do before any code change, and the hook can enforce it without network calls.

---

### 3. `planning/QUEUE.md` is 2015 lines and still referenced ⚠️ MEDIUM

**Problem:** `.hermes.md` (old version) referenced `planning/QUEUE.md`. The new `.hermes.md` references `EXECUTION_ORDER.md`. But the old queue still exists and an agent that reads git history or scans the `planning/` directory will find it and may use it.

**Fix needed:**
- Archive `planning/QUEUE.md` → `planning/QUEUE.archived-2026-04-05.md`
- Add a one-line `planning/QUEUE.md` tombstone: `# ARCHIVED — use backlog/EXECUTION_ORDER.md`
- Add the archive note to `.hermes.md` prohibited files list

---

### 4. EPIC-089 STORY-362 has a staged but uncommitted change ⚠️ MEDIUM

**Problem:** `git status` at session start showed `M backlog/EPICS/EPIC-089-workflow-orchestration-api/STORIES/STORY-362.md` as staged. This was not committed during this session. The change is still in the index.

**Fix needed:** 
```bash
cd /d1/AI\ WHISPERERS/AGENTIC/solstein
git diff --cached backlog/EPICS/EPIC-089-workflow-orchestration-api/STORIES/STORY-362.md
```
Review the staged change and either commit it or reset it. Do not leave staged hunks — they confuse the next agent about the current state.

---

### 5. `docs/reference/AGENTS.md` is stale and conflicts with root `AGENTS.md` ⚠️ LOW

**Problem:** `docs/reference/AGENTS.md` is a 2026-03-01 documentation file about the project architecture. Now that `AGENTS.md` exists at root, agents that scan the repo may find both and get confused about which is authoritative.

**Fix:** Add a note at the top of `docs/reference/AGENTS.md`:
```markdown
> ⚠️ This is project architecture documentation, not the agent protocol.
> For agent instructions see: `AGENTS.md` (project root) and `.hermes.md`
```

---

### 6. No LLM-dependent stories have a fallback verification path ⚠️ LOW

**Problem:** Phases 7–9 in `EXECUTION_ORDER.md` include stories that require deployed infrastructure (PostgreSQL, Redis, LLM API keys). If Hermes reaches these stories in a local-only environment, it has no guidance on what to do — it may attempt the implementation anyway and produce broken code.

**Fix needed:** For each BLOCKED-by-infrastructure story in the queue, add an explicit note:
```
| 62 | STORY-311 | Deploy PostgreSQL 15 | M | READY — ⚠️ requires cloud/docker access; if not available skip to Phase 10 |
```

---

## Verified Codebase Facts — Do Not Re-Derive

These were confirmed by direct file reads on 2026-04-05. Hermes should not re-investigate them.

| Claim | File | Line | Verified |
|-------|------|------|---------|
| `extra="forbid"` on `Company` and `FinancialMetric` | `src/solstein/domain/models.py` | — | 2026-04-03 ✅ |
| `strict_provenance=False` hardcoded | `src/solstein/research/research_dual_write.py` | 424 | 2026-04-05 ✅ |
| `SOLSTEIN_TEST_MODE` default `"mixed"` | `src/solstein/core/test_modes.py` | 16 | 2026-04-05 ✅ |
| `data_source_type` column absent from `CompanyRecord` | `src/solstein/infrastructure/models/company.py` | 77 | 2026-04-05 ✅ |
| `load_competitor_data.py` uses `get_database_url(test=True)` | `src/solstein/migrations/load_competitor_data.py` | 179 | 2026-04-05 ✅ |
| `export.py` gate evaluated but `.passed` never checked | `src/solstein/api/routers/export.py` | 41–47 | 2026-04-05 ✅ |
| `cli_research.py` imports `RealDataLoader` (active caller) | `src/solstein/cli_research.py` | 22, 50, 115, 233 | 2026-04-05 ✅ |
| `review.py` imports from `research.graph.executor` (active caller) | `src/solstein/api/routers/review.py` | 168 | 2026-04-05 ✅ |
| `_retired/` directories have zero callers | `grep -rn "from.*_retired" src/` | — | 2026-04-05 ✅ |
| `build_default_registry()` registers 6–7 adapters | `src/solstein/adapters/registry.py` | 74–132 | 2026-04-05 ✅ |
| Test baseline: 3855 passed / 291 failed / 237 errors | `.venv/bin/python3 -m pytest tests/unit/` | — | 2026-04-05 ✅ |
| All 291 failures are infra-dependent (no local DB/Redis) | — | — | 2026-04-05 ✅ |

---

## Execution Order — Current Phase 0 Queue (Ivan's Reference)

The first 13 stories are the P0 gate. These must all be DONE before any data or feature work.

| # | Story | Title | Size | File to Change |
|---|-------|-------|------|---------------|
| 1 | STORY-376 | Remove leaked test DB files; add `.gitignore` rules | XS | `.gitignore`, `git rm` |
| 2 | STORY-373 | CI lint guard — no `src/` imports from `tests.*` | XS | `scripts/ci/` or `pyproject.toml` |
| 3 | STORY-374 | Fix `test_api_routers_coverage.py` — module-scope → fixtures | S | `tests/unit/test_api_routers_coverage.py` |
| 4 | STORY-375 | Fix `test_load.py` — DB URL env overrides → monkeypatch | S | `tests/performance/test_load.py` |
| 5 | STORY-377 | Add CI guard detecting module-scope mutations | S | `scripts/ci/` |
| 6 | STORY-387 | Fix `pyproject.toml` — remove DeprecationWarning suppression | S | `pyproject.toml` |
| 7 | STORY-371 | Fix test factories — add `data_source_type="synthetic"` default | XS | `tests/factories/` |
| 8 | STORY-372 | Deduplicate test factory modules | S | `tests/factories/` |
| 9 | STORY-382 | Fix `test_modes.py` — default `"mixed"` → `"strict_real"` | S | `src/solstein/core/test_modes.py:16` |
| 10 | STORY-383 | Fix `research_dual_write.py` — remove `strict_provenance=False` | S | `src/solstein/research/research_dual_write.py:424` |
| 11 | STORY-384 | Add `data_source_type` column to `CompanyRecord` + migration | S | `src/solstein/infrastructure/models/company.py` + alembic |
| 12 | STORY-386 | Fix `load_competitor_data.py` — remove `get_database_url(test=True)` | XS | `src/solstein/migrations/load_competitor_data.py:179` |
| 13 | STORY-381 | Fix migration — set `data_source_type` on all `CompanyRecord` objects | XS | `src/solstein/migrations/load_competitor_data.py` |

Gate verification command:
```bash
PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -q \
  --ignore=tests/unit/test_async_boundary_regressions.py \
  --ignore=tests/unit/test_api_routers_coverage.py \
  --no-header 2>&1 | tail -3
```
Target: ≥ 3855 passed (baseline), goal ≥ 3920 after Phase 1.

---

## Ivan's Recommended Action Order Today

1. **Fix STORY-362 staged change** — 5 minutes. Run `git diff --cached` and either commit or reset.
2. **Archive `planning/QUEUE.md`** — 5 minutes. Rename + add tombstone.
3. **Add `docs/work-logs/TEMPLATE.md`** — 15 minutes. Define the mandatory work log format.
4. **Add the lock file protocol** (Option C above) — 1 hour. Pre-commit hook + Hermes instruction to write `backlog/.hermes-lock` before starting a story.
5. **Add tombstone note to `docs/reference/AGENTS.md`** — 2 minutes.
6. **Optionally: launch Hermes against STORY-376** (XS, 30 minutes) to test the new loop end-to-end before committing to a longer session.

---

## Prior Art

- Full Hermes post-mortem: `docs/agent-cycles/HERMES-IMPROVEMENT-PLAN-2026-04-05.md` (476 lines)
- Prior session (2026-03-31): `docs/agent-cycles/2026-03-31/` — Hermes work logs (empty)
- Backlog structural audit: `docs/audit/BACKLOG_STRUCTURAL_AUDIT_2026-04-03.md`
- Execution queue: `backlog/EXECUTION_ORDER.md`
- Agent protocol: `.hermes.md`
