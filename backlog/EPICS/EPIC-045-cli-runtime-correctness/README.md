# EPIC-045: CLI Runtime Correctness

> **Discovered**: 2026-03-01 via live end-to-end run analysis  
> **Priority**: P0 — BLOCKER (4 of 8 CLI commands crash on every invocation)  
> **Stories**: 4 (STORY-169 through STORY-172)  
> **Effort**: M (3–5 days total)

---

## Problem

A live test run of the CLI against `data/input/competitor_data.json` revealed that 4 of 8 CLI commands crash immediately, before doing any useful work. The root cause is a mismatch between the expected JSON format (a flat list `[...]`) and the actual file format (a wrapped object `{"competitors": [...]}`). Additionally, the `generate-llm-report` command crashes with a missing module error because an exporter was renamed without updating the import.

These are not edge cases — they are the primary user-facing commands.

### Affected Commands

| Command | Error | Status |
|---------|-------|--------|
| `score` | `Company(**item) for item in data` → unpacks string keys | ❌ Crashes |
| `analyze-market` | Same JSON iteration bug | ❌ Crashes |
| `compare` | Same JSON iteration bug | ❌ Crashes |
| `export-excel` | Same JSON iteration bug | ❌ Crashes |
| `generate-llm-report` | `ModuleNotFoundError: No module named 'solstein.exporters.report_generator'` | ❌ Crashes |
| `generate-report` | Uses deprecated `CompetitorDataLoader` | ⚠️ Works with warning |
| `generate-all-reports` | Uses deprecated `CompetitorDataLoader` | ⚠️ Works with warning |
| `extract` | Not affected | ✅ Works |

---

## Stories

| Story | Title | Priority | Size |
|-------|-------|----------|------|
| STORY-169 | Fix JSON parsing in score/analyze-market/compare/export-excel | P0 | S |
| STORY-170 | Restore `generate-llm-report` exporter import | P0 | S |
| STORY-171 | Migrate all CLI commands from deprecated `CompetitorDataLoader` | P1 | M |
| STORY-172 | Add structured input validation with actionable error messages | P2 | M |

---

## Definition of Done

- [ ] All 8 CLI commands execute without crashing on `data/input/competitor_data.json`
- [ ] All 8 CLI commands produce correct output for a sample company
- [ ] Unit tests cover JSON parsing for both `[...]` and `{competitors: [...]}` formats
- [ ] No `DeprecationWarning` emitted during normal CLI runs
