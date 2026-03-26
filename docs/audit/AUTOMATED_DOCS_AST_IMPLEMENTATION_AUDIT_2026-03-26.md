# Automated Docs And AST Implementation Audit

## Purpose

This audit records the repository mandate to fully implement automated docs generation and structural AST enforcement as first-class engineering infrastructure.

It exists because the master audit already exposed large-scale correctness and drift debt, and the repo needs durable machine-readable navigation surfaces instead of repeated manual re-reading.

## Source Of Truth Preservation

- The master audit at `docs/audit/18-03-2026_MASTER_AUDIT.md` remains untouched.
- Current source line count: `7548`
- The complete issue list is now re-indexed mechanically in `docs/audit/generated/MASTER_AUDIT_ISSUE_INDEX.md` and `docs/audit/generated/MASTER_AUDIT_ISSUE_INDEX.json`.
- The generated index is derived from the master audit headings and issue tables. It is not a hand-maintained shadow ledger.

## What Was Implemented In This Pass

1. Added generated-doc scripts under `scripts/docs/` for:
   - AST rule catalog generation
   - master audit issue index generation
   - full generated-doc orchestration
   - freshness checking
2. Added repository-managed git hooks under `.githooks/`:
   - `pre-commit` regenerates and stages committed generated docs
   - `pre-push` blocks stale generated artifacts from being pushed
3. Added Make targets:
   - `docs-generate`
   - `docs-generated-check`
   - `hooks-install`
4. Added generated artifacts:
   - `docs/reference/generated/AST_RULE_CATALOG.md`
   - `docs/reference/generated/AST_RULE_CATALOG.json`
   - `docs/audit/generated/MASTER_AUDIT_ISSUE_INDEX.md`
   - `docs/audit/generated/MASTER_AUDIT_ISSUE_INDEX.json`

## Why This Matters

The generated audit index gives future agents a token-cheap, deduplicated way to inspect the full issue inventory without opening the entire 7,548-line master audit every time.

The AST rule catalog gives a compact view of what structural debt classes are already guarded and which audit issues motivated those rules.

The hooks make generated docs freshness a repository behavior, not a manual habit.

## Still Pending

This is only the foundation. The following work remains and is now explicitly backlog-tracked:

- widen generated docs from the current indexes into pipeline boundary registries, schema inventories, and connector contract surfaces
- expand AST rules beyond the first narrow issue-class protections
- make more of `src/solstein` package-addressable so `Griffe`/`mkdocstrings` can generate broader tokenless API reference coverage
- keep the generated issue index reconciled with live fix-verification audits, not only the historical source audit

## Backlog Tracking

Canonical backlog epic:

- `backlog/EPICS/EPIC-065-documentation-lifecycle-automation-ci-enforcement/README.md`

New stories added for this rollout:

- `STORY-242` Generate AST rule catalog and guardrail registry
- `STORY-243` Generate master audit issue index and keep it current
- `STORY-244` Enforce generated docs freshness through git hooks and CI
- `STORY-245` Expand package-addressable generated API docs and schema registries

## Next Task Guidance

The next implementation task should not start from prose-first docs work.

It should widen machine-derived artifacts in this order:

1. schema ownership map
2. pipeline boundary registry
3. connector contract surface map
4. broader API reference coverage after package cleanup
