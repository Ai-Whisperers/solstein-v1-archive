# Solstein — AI-Powered Development Pipeline

**For: Jonathan (and team)**
**Date: April 1, 2026**
**By: Ivan + Hermes Agent (autonomous AI developer)**

---

## TL;DR

We set up an autonomous AI agent (Hermes) that works on Solstein 24/7. It picks up stories from the backlog, implements them, runs tests, and pushes PRs — every 3 hours, around the clock. You'll get Telegram updates with what was done. All you need to do is review PRs and merge them.

---

## What Is Hermes Agent?

Hermes is an open-source autonomous AI agent by [Nous Research](https://nousresearch.com). It runs on our VPS and connects to Telegram for communication. It has:

- **150 skills** (coding, testing, GitHub workflows, debugging, etc.)
- **Persistent memory** across sessions (remembers the project, preferences, past work)
- **Scheduled tasks** that run unattended every 3 hours
- **Access to 200+ AI models** with automatic fallback if one goes down
- **MCP servers** for GitHub integration (issues, PRs, code search)

It's NOT a chatbot wrapper. It actually reads code, writes code, runs tests, creates branches, pushes commits, and creates PRs. Autonomously.

---

## What Was Done to Solstein

### 1. Branch Consolidation

**Problem:** `develop` was 523 commits ahead of `master`, but `master` had a critical fix (`jwt.py`) that develop was missing. 11 feature branches had unmerged work. Total chaos.

**What we did:**
- Cherry-picked the M0 emergency fix (jwt.py, conftest, classification thresholds) from master into develop
- Merged ALL 11 feature branches into develop:
  - STORY-250 through STORY-266 (export schema, boundary schemas, LLM contracts, behavioral tests, runtime freeze, provider scorecard, adapter dedup, etc.)
  - fix-ci-issues branch
- Pushed everything to develop on GitHub

**Result:** `develop` is now the SINGLE source of truth with everything merged. 636 Python source files, 110K lines of code, 333 test files.

### 2. Documentation Cleanup

**Problem:** 1,006 markdown files scattered everywhere. Duplicate backlogs in 3 locations. 417 AI session dump files. Conflicting "source of truth" documents. 62 loose files in docs/ root.

**What we did:**
- **Deleted 680+ garbage files** (4.4MB): session dumps, analysis outputs, duplicate backlogs, stubs, broken files
- **Merged duplicates**: architecture docs, API docs, documentation indexes
- **Relocated 50+ loose files** into proper subdirectories
- **Consolidated 14 tiny directories** into parent directories

**Result:** Clean structure with 13 organized docs/ subdirectories:

```
docs/
├── architecture/    (20 files) — System design, DB schema, ADRs
├── api/             (8 files)  — API reference, export schema
├── guides/          (39 files) — Developer, operator, setup guides
├── operations/      (21 files) — Deploy, monitor, DR, migration
├── research/        (17 files) — AI research, OSINT, web intel
├── reference/       (74 files) — Indexes, module maps, generated
├── audit/           (29 files) — All audit reports
├── archive/         (71 files) — Historical, completed docs
├── contributing/    (12 files) — Code standards, governance
├── PITCH/           (9 files)  — Business docs, case studies
├── LORE/            (4 files)  — Origin story
├── analysis/        (16 files) — Market analysis reports
└── runbooks/        (4 files)  — Operational runbooks
```

### 3. Hermes Agent Context File

Added `.hermes.md` to the repo root. This file is automatically loaded by Hermes when it works on Solstein. It contains:
- Project description and current state
- Architecture overview (canonical pipeline vs frozen graph)
- Work queue location
- The "Autoresearch Protocol" (how Hermes works on the code)
- Key commands and pitfalls

---

## The Autonomous Pipeline

### How It Works

Hermes runs **9 scheduled jobs** that fire every 3 hours:

| Time  | Name           | Focus |
|-------|----------------|-------|
| 00:00 | sol-shift-00   | Structural refactoring (dead code, duplicates, god files) |
| 03:00 | sol-shift-03   | Test engineering (fix failures, add coverage, remove skips) |
| 06:00 | sol-shift-06   | Priority stories (audit hotfixes, P0/P1) |
| 09:00 | sol-shift-09   | Foundation work (httpx migration, data integrity) |
| 12:00 | sol-shift-12   | Data pipeline (field loss, validation, scoring, exports) |
| 15:00 | sol-shift-15   | Blocker clearing (unblock downstream stories) |
| 18:00 | sol-shift-18   | Modern stack (LLM client, agents, observability) |
| 21:00 | sol-shift-21   | Cleanup + overflow (lint, finish work, daily wrap) |
| Sun 8 | sol-weekly-audit | Full codebase health check, gap detection, backlog grooming |

### The Karpathy Autoresearch Pattern

Every shift follows this protocol (inspired by Andrej Karpathy's autoresearch repo):

1. **MEASURE BASELINE** — Run tests, count lint errors, count files before touching anything
2. **PICK WORK** — Take the first READY story from `planning/QUEUE.md`
3. **TIGHT LOOPS** — Make ONE small change → run tests → if green, continue; if red, revert and try different approach
4. **MEASURE AFTER** — Same metrics as step 1, compare
5. **COMMIT ONLY IF GREEN** — Never push failing tests. Include metrics delta in commit message
6. **UPDATE QUEUE** — Mark story as DONE, pick next

GitHub issues are not the execution authority for cron shifts. If you want a local cached view of the live issue tracker, refresh `planning/generated/GITHUB_ISSUE_SNAPSHOT.{json,md}` with `make issues-snapshot`, but continue selecting work from `planning/QUEUE.md`.

### What You'll See

- **Telegram notifications** after each shift with: stories completed, test results, PRs created, blockers found
- **Feature branches** named `feature/STORY-NNN-description` targeting develop
- **PRs on GitHub** with descriptions referencing the story and metrics
- **QUEUE.md updates** showing story status changes

### Your Role

1. **Review PRs** that Hermes creates — check the diff, make sure it makes sense
2. **Merge or request changes** — Hermes will pick up feedback and try again
3. **Prioritize** — if you want specific stories done first, reorder them in `planning/QUEUE.md` (READY stories are picked top-to-bottom)
4. **Ask via Telegram** — message the bot to ask for specific work, check status, or run commands

---

## Current System State

### The Verdict (from the audit)

The system is in CRITICAL state — it works as a demo but not as production software:

| Issue | Impact |
|-------|--------|
| Auth accepts any credentials | Security: zero |
| 70% field loss in data pipeline | Core product broken |
| 7 stub agents return fake data | Intelligence is fake |
| 6 duplicate adapter pairs | Maintenance nightmare |
| Fake health checks (sleep + return True) | Monitoring is useless |
| ~28% test coverage | Regressions everywhere |
| Classification thresholds conflict in 3 files | Non-deterministic output |

### Priority Roadmap

| Priority | Timeline | What | Why |
|----------|----------|------|-----|
| P0 Emergency | Week 1 | jwt.py ✅, conftest ✅, thresholds ✅ | System can't even start |
| P1 Foundation | Weeks 2-4 | httpx migration, dead code, duplicates | Remove technical debt |
| P2 Data Pipeline | Weeks 5-8 | Validation, scoring, exports | Fix the 70% data loss |
| P3 Modern Stack | Weeks 9-16 | Supabase Auth, LLM rewrite, agents | Replace broken systems |
| P4 Business Value | Weeks 17-24 | Dashboard, workers, AI readiness | Actual product features |

### Work Queue Status

- **132 READY** stories waiting for implementation
- **98 BLOCKED** (weekly audit checks if they can be unblocked)
- **27+ DONE** stories completed
- **17 IN_PROGRESS** being worked on

At ~8-16 stories/day throughput, the READY queue should be cleared in ~2 weeks. The weekly audit continuously discovers new gaps and creates new stories, so the pipeline never runs dry.

---

## AI Model Setup

### Cost: $30/month total

| Service | Cost | What It Does |
|---------|------|-------------|
| Anthropic Claude Pro | $20/mo | Primary reasoning engine (Opus for interactive, Sonnet for cron jobs) |
| OpenRouter credits | $10/mo | Access to 200+ models for auxiliary tasks and fallback |
| Ollama local (VPS) | $0 | qwen2.5-coder:7b + llama3.1:8b — free, unlimited, always available |
| HuggingFace | $0 | Qwen3-235B as emergency fallback (free tier) |

### Model Assignment (optimized by task complexity)

| Task | Model | Cost per M tokens | Why |
|------|-------|-------------------|-----|
| Your interactive chat | Claude Opus 4.6 | $15/$75 | Best reasoning |
| Cron jobs (coding) | Claude Sonnet 4 | $3/$15 | Great coder, 5x cheaper than Opus |
| Subagent delegation | Claude Sonnet 4 | $3/$15 | Needs coding ability |
| Vision (screenshots) | Gemini 2.5 Flash | ~$0.05/$0.15 | Best vision:cost ratio |
| Context compression | Gemini 2.5 Flash | ~$0.05/$0.15 | Good at summarization |
| Session search | Gemini 2.5 Flash | ~$0.05/$0.15 | Good at summarization |
| Web extraction | DeepSeek V3 | $0.14/$0.28 | Trivial task, cheapest |
| Skills/approval/MCP/memory | DeepSeek V3 | $0.14/$0.28 | Trivial tasks, cheapest |
| Simple questions (smart routing) | DeepSeek V3 | $0.14/$0.28 | Short turns get cheap model |

### Fallback Chain (4 levels, never goes down)

```
Anthropic (primary) 
  → Claude Sonnet 4 via OpenRouter (rate limit recovery)
    → DeepSeek V3 via OpenRouter (cheap backup)
      → Qwen3-235B via HuggingFace (free emergency)
        → qwen2.5-coder:7b via local Ollama ($0, always available)
```

---

## Infrastructure

### VPS (Hostinger)

- **CPU:** 8-core AMD EPYC 9354P
- **RAM:** 32GB
- **Disk:** 387GB (33% used)
- **GPU:** None (CPU inference only)
- **OS:** Ubuntu
- **Running:** Hermes Agent gateway (systemd), Ollama (local models), 9 cron jobs

### Services Running

| Service | Port | Purpose |
|---------|------|---------|
| Hermes Gateway | (systemd) | Telegram bot, cron scheduler |
| Ollama | 11434 | Local LLM inference |
| GitHub MCP | (stdio) | Issues, PRs, code search |
| Filesystem MCP | (stdio) | Direct file access to /tmp/solstein |

### Laptop GPU Integration (future)

When connected, the laptop can serve larger models via SSH tunnel:

```bash
# On laptop with NVIDIA GPU:
ollama serve
# SSH tunnel to VPS:
ssh -R 11434:localhost:11434 user@vps-ip
# Hermes then uses: /model custom:local:qwen2.5-coder:32b
```

---

## Quick Commands (via Telegram)

| Command | What It Does |
|---------|-------------|
| `/sol` | Start a Solstein work session |
| `/test` | Run the Solstein test suite |
| `/audit` | Full codebase audit (lint, tests, TODOs, gaps) |
| `/pr` | Review open PRs |
| `/queue` | Show work queue status (READY/DONE/BLOCKED counts) |
| `/personality coder` | Switch to "senior Python engineer" mode |
| `/personality reviewer` | Switch to "code reviewer" mode |
| `/model custom:local:qwen2.5-coder:7b` | Switch to free local model |

---

## Key Files

| File | Purpose |
|------|---------|
| `planning/QUEUE.md` | Work queue — stories are picked top-to-bottom |
| `NEXT_ACTIONS.md` | Priority roadmap (P0→P4) |
| `.hermes.md` | Agent context (auto-loaded by Hermes) |
| `backlog/EPICS/` | All 70 EPICs with stories (canonical backlog) |
| `DOCS_CLEANUP_PLAN.md` | Documentation reorganization rationale |
| `src/solstein/analytics/constants.py` | Classification thresholds (SOURCE OF TRUTH) |
| `src/solstein/research/pipeline.py` | CANONICAL research pipeline |
| `src/solstein/research/graph/` | FROZEN — do not modify |

---

## Git Workflow

1. All work targets `develop` branch (NOT master)
2. Feature branches: `feature/STORY-NNN-description`
3. PRs target develop, squash merge
4. Hermes creates branches, commits, pushes, and creates PRs autonomously
5. You review and merge

---

## What Happens Next

1. **Right now:** 9 cron jobs are running 24/7, picking up READY stories
2. **This week:** P0 Emergency items should be fully resolved, P1 Foundation starts
3. **Week 2-4:** httpx migration, dead code elimination, duplicate adapter cleanup
4. **Week 5-8:** Data pipeline fixes (the 70% field loss problem)
5. **Ongoing:** Weekly audit every Sunday creates new stories for gaps found

The system is designed to be self-sustaining. The weekly audit finds new problems, creates stories, and the daily shifts implement them. Your job is to review PRs, adjust priorities, and steer the direction.

---

*Built by [AI Whisperers](https://ai-whisperers.com) — finding the diamonds nobody knew were there.*
