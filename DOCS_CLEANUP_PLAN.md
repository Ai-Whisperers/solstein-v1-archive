# Solstein Documentation Cleanup Plan

**Generated:** 2026-03-31
**Problem:** 1,006 markdown files (9.97 MB) — unmaintainable chaos
**Target:** ~150-200 well-organized files

---

## Critical Findings

### 1. GARBAGE — Delete Immediately (420+ files, 2+ MB)

| Directory | Files | Size | Reason |
|-----------|-------|------|--------|
| `docs/agent-cycles/` | 417 | 1.7MB | AI session dumps with no lasting value. These are ephemeral cycle logs from automated agents — zero business value. |
| `.analysis-output/` | 8 | 468KB | One-time analysis runs, captured in audit docs already. |
| `docs/eneve_analysis_critique_2026-03-01.md` | 1 | 214B | Stub — the real file is in `docs/analysis/` |
| `docs/fantasy-agent-roster.md` | 1 | — | Not a real document |
| `=5.3.0` (root) | 1 | — | Broken file from a bad pip/uv command |

### 2. DUPLICATES — Merge or Delete (60+ files)

| Keep | Delete/Merge | Reason |
|------|-------------|--------|
| `docs/architecture/` dir | `docs/architecture.md` + `docs/ARCHITECTURE.md` | Consolidate into `docs/architecture/overview.md` |
| `docs/api/reference.md` (72KB) | `docs/api.md` (8KB) | api.md is a stub pointing to the real reference |
| `docs/DOCUMENTATION_INDEX.md` (19KB) | `docs/documentation/DOCUMENTATION_INDEX.md` (140B stub) | Keep the big one, delete the stub |
| `backlog/EPICS/` | `docs/active/backlog/` (238 files) | Two parallel backlogs tracking same EPICs |
| `backlog/EPICS/` | `docs/active/epics/` (12 overlapping EPICs) | 12 EPICs exist in BOTH locations |

### 3. MISPLACED — Move to Correct Location (60+ files)

| File(s) | Current | Should Be |
|---------|---------|-----------|
| 62 loose .md files | `docs/` root | Organized into subdirectories |
| `docs/ARCHITECTURE.md` | root of docs | `docs/architecture/overview.md` |
| `docs/API_DOCUMENTATION.md` | root of docs | `docs/api/` |
| `docs/API_PROVIDERS_GUIDE.md` | root of docs | `docs/guides/api-providers.md` |
| `docs/CICD.md` | root of docs | `docs/guides/ci-cd.md` (already exists!) |
| `docs/DATABASE_SCHEMA.md` | root of docs | `docs/architecture/database-schema.md` |
| `docs/DEPLOYMENT_GUIDE.md` | root of docs | `docs/operations/DEPLOYMENT_GUIDE.md` (already exists!) |
| `docs/SECURITY_INCIDENT_RESPONSE.md` | root of docs | `docs/security/incident-response.md` (already exists!) |
| `docs/TROUBLESHOOTING.md` | root of docs | `docs/guides/TROUBLESHOOTING.md` (already exists!) |
| `docs/MIGRATION_GUIDE.md` | root of docs | `docs/operations/MIGRATION_GUIDE.md` (already exists!) |
| `docs/SESSION_*.md` | root of docs | `docs/sessions/` |
| `src/solstein/MODULE_INDEX.md` | src dir | `docs/reference/MODULE_INDEX.md` |
| `src/solstein/TEST_REPORT.md` | src dir | `docs/reference/TEST_REPORT.md` |
| `AUDIT-REPORT.md` | repo root | `docs/audit/AUDIT-REPORT.md` |
| `REPOSITORY_STRUCTURE.md` | repo root | `docs/reference/` |
| `ENEVE_PIPELINE_CRITICAL_ANALYSIS.md` | repo root | `docs/analysis/` |
| `2026-02-27/cycle-004.md` | repo root (!!) | Delete (orphaned) |

### 4. BLOAT — Archive or Compress (800+ files in hidden dirs)

| Directory | Files | Size | Action |
|-----------|-------|------|--------|
| `.antigravity/prompts/` | 191 | 1.5MB | Keep but add to .gitattributes as non-essential |
| `.antigravity/exemplars/` | 40 | 309KB | Same — agent tooling, not project docs |
| `.claude/` | 25 | 420KB | Agent context — not documentation. Add to .gitignore or archive |
| `.cursor/` | 1 | — | IDE rules, fine |
| `.opencode/` | ? | — | Check if needed |

### 5. CONFLICTING "SOURCE OF TRUTH" (the NEXT_ACTIONS.md problem)

These files all claim to be the canonical status tracker:
1. `planning/QUEUE.md` (125KB — massive)
2. `docs/active/ROADMAP.md`
3. `docs/active/EPIC_STATUS_DASHBOARD.md`
4. `backlog/README.md`
5. `NEXT_ACTIONS.md`
6. Various `docs/active/epics/EPIC-0XX` files

**Resolution:** `NEXT_ACTIONS.md` is the authority. Everything else is reference.

---

## Proposed Directory Structure

```
solstein/
├── README.md                    # Project overview
├── NEXT_ACTIONS.md              # Current priorities (canonical)
├── LICENSE
├── docs/
│   ├── index.md                 # MkDocs entry point
│   ├── architecture/            # System design docs
│   │   ├── overview.md          # Merged from architecture.md + ARCHITECTURE.md
│   │   ├── decisions.md         # ADRs
│   │   ├── database-schema.md
│   │   ├── provider-scorecard.md
│   │   └── runtime-depth-ledger.md
│   ├── api/                     # API documentation
│   │   └── reference.md
│   ├── guides/                  # How-to guides
│   │   ├── developer.md
│   │   ├── operator.md
│   │   ├── api-providers.md
│   │   ├── connector-enrichment.md
│   │   ├── ci-cd.md
│   │   ├── troubleshooting.md
│   │   └── ...
│   ├── operations/              # Deployment & ops
│   │   ├── deployment.md
│   │   ├── migration.md
│   │   ├── monitoring.md
│   │   └── disaster-recovery.md
│   ├── research/                # AI research docs
│   │   └── ...
│   ├── audit/                   # Audit reports (keep)
│   │   └── ...
│   ├── PITCH/                   # Business docs (keep)
│   │   └── ...
│   ├── LORE/                    # Origin story (keep)
│   │   └── ...
│   └── reference/               # Generated/reference docs
│       ├── changelog.md
│       ├── glossary.md
│       └── ...
├── backlog/                     # SINGLE source of truth for work tracking
│   ├── EPICS/
│   ├── MILESTONES/
│   └── GUIDELINES/
├── planning/
│   └── QUEUE.md                 # Work queue
└── .agent-tools/                # Renamed from .antigravity/.claude/.cursor
    ├── prompts/
    ├── rules/
    └── templates/
```

---

## Execution Plan

### Phase 1: Delete Garbage (saves 2+ MB, removes 420+ files)
- `rm -rf docs/agent-cycles/`
- `rm -rf .analysis-output/`
- `rm docs/eneve_analysis_critique_2026-03-01.md`
- `rm docs/fantasy-agent-roster.md`
- `rm "=5.3.0"`
- `rm 2026-02-27/cycle-004.md`

### Phase 2: Deduplicate (resolve 60+ file conflicts)
- Merge architecture docs → `docs/architecture/overview.md`
- Delete `docs/api.md` stub (keep `docs/api/reference.md`)
- Delete `docs/documentation/DOCUMENTATION_INDEX.md` stub
- Remove `docs/active/backlog/` (duplicate of `backlog/`)
- Remove `docs/active/epics/` EPIC duplicates

### Phase 3: Relocate Loose Files
- Move 62 loose `docs/*.md` into proper subdirectories
- Move root-level docs into `docs/`
- Move `src/solstein/*.md` into `docs/reference/`

### Phase 4: Consolidate Agent Tooling
- Keep `.antigravity/`, `.claude/`, `.cursor/` as-is (they're agent configs)
- Add README explaining these are agent tool configs, not project docs
