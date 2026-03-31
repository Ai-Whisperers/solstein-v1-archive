# Mirror Retirement Plan: `docs/active/backlog/` and `docs/active/epics/`

> **Status**: Active governance document
> **Owner**: Platform Team
> **Last Reviewed**: 2026-03-28
> **Review Cadence**: On execution of each migration phase
> **Epic**: EPIC-063 (STORY-231)
> **Superseded By**: N/A

---

## Context and Prior Work

An earlier drift analysis (STORY-237, EPIC-064, [report](../MIRROR_DRIFT_REPORT_2026-03-26.md)) found:

- `docs/active/backlog/` contains **236 files** — an old structural snapshot from before the `backlog/EPICS/` restructuring
- `backlog/EPICS/` contains **309 files** — the canonical, actively maintained backlog
- The two trees share **zero overlapping file paths** (different directory structure)
- The mirror has **zero content drift** relative to what it claims to mirror — it is simply stale in structure
- The mirror accounts for the majority of broken links documented in the link allowlist

The retirement decision is already recorded. This document formalises the migration design, defines cutover controls, and constitutes the dry-run report required by STORY-231 before any destructive action is taken.

---

## Canonical Tree Selection

**Decision: `backlog/EPICS/` is the canonical tree for all epic and story planning artifacts.**

Rationale:

| Factor | `backlog/EPICS/` | `docs/active/backlog/` |
|--------|-----------------|----------------------|
| Actively maintained | Yes — all new epics added here | No — frozen since restructuring |
| Consistent structure | Yes — `EPIC-NNN-slug/STORIES/STORY-NNN-slug.md` | Partial — old flat layout |
| Used by autonomous worker | Yes — QUEUE.md references this path | No |
| CI scripts reference | Yes — link checkers, registry scripts | One legacy reference only |
| Contains newest epics | Yes — EPIC-063 through EPIC-066 | No — missing recent epics |

---

## Non-Canonical Tree Strategy: Retirement

The `docs/active/backlog/`, `docs/active/epics/`, and `docs/active/programs/` mirror directories will be **retired** (deleted) rather than maintained as a generated mirror or kept in sync.

Rationale for retirement over sync:
- The structural divergence (flat vs. nested) makes automated sync non-trivial and error-prone
- The mirror has no active consumers (feature code, CI, documentation) that require it to exist
- Maintaining a stale mirror creates a navigation hazard and a persistent broken-link source

---

## Cutover Control During Transition

Until the mirror is physically deleted, the following controls prevent unintentional edits to the mirror:

1. **No PR approval for edits to `docs/active/`**: PRs that add or modify files in `docs/active/backlog/`, `docs/active/epics/`, or `docs/active/programs/` should be rejected unless the PR also removes those files.

2. **Pre-commit advisory check** (design — delegate to EPIC-065 STORY-238): Warn on any `git add` of a file under `docs/active/` with a message directing to `backlog/EPICS/` as the canonical path.

3. **Deprecation notice in directory README**: A `docs/active/backlog/README.md` (if absent) or an update to the existing one should state clearly that this directory is deprecated and scheduled for deletion.

---

## Dry-Run Report

### Files That Will Be Deleted

| Directory | File Count | Last Modified | Risk |
|-----------|-----------|--------------|------|
| `docs/active/backlog/` | 236 markdown files | Pre-2026-03-11 restructuring | Low — no canonical content |
| `docs/active/epics/` | ~10 markdown files | Pre-2026-03-11 restructuring | Low |
| `docs/active/programs/` | ~5 markdown files | Pre-2026-03-11 restructuring | Low |

### Files That Reference the Mirror (Must Update or Accept Breakage)

The following files contain references to `docs/active/backlog/` or `docs/active/epics/`:

| File | Action Required |
|------|----------------|
| `docs/README.md` | Update any links to point to `backlog/EPICS/` |
| `docs/audit/CODEBASE_AUDIT_2026-03-17.md` | Archived audit — update or accept stale links |
| `docs/audit/PRODUCTION_PATH_ANALYSIS.md` | Update or archive if outdated |
| `docs/audit/PROJECT_STATE_AUDIT_2026-03-27.md` | Update any active links |
| `docs/audit/AGENT_ZERO_FIX_VERIFICATION_BACKLOG.md` | Update or archive |
| `docs/audit/DOCUMENTATION_GOVERNANCE_AUDIT_2026-03-11.md` | Historical — archive or accept stale links |
| `docs/ORGANIZATION_SUMMARY.md` | Update links to canonical paths |
| `docs/active/EPIC_STATUS_DASHBOARD.md` | Move to `docs/` root or archive |
| `docs/EPIC_ANALYSIS_AND_ORGANIZATION_PLAN.md` | Update or archive |
| `docs/MIRROR_DRIFT_REPORT_2026-03-26.md` | Historical record — accept stale links, add notice |
| `scripts/ci/check_root_scripts.py` | Update one hardcoded path reference |

**Total external references**: 13 files — all in `docs/` or `scripts/ci/`

### Non-Destructive Pre-Checks

Before deletion, run these checks to confirm safety:

```bash
# 1. Confirm no Python/shell/CI files reference the mirror paths (except known ones)
grep -r "docs/active/backlog\|docs/active/epics" \
  --include="*.py" --include="*.sh" --include="*.yml" --include="*.yaml" \
  /path/to/solstein | grep -v ".git" | grep -v "scripts/ci/check_root_scripts.py"
# Expected: 0 results (only the known false-positive in check_root_scripts.py)

# 2. Confirm no unique content exists only in the mirror (not in backlog/EPICS/)
# Since paths don't overlap, check for any mirror files that don't exist anywhere in backlog/EPICS/
for f in $(find docs/active/backlog -name "*.md" -printf "%f\n"); do
  if ! find backlog/EPICS -name "$f" | grep -q .; then
    echo "UNIQUE TO MIRROR: $f"
  fi
done
# Expected: may have files (different naming) — review manually for uniqueness

# 3. Confirm git tracks all files (no untracked surprises)
git status docs/active/
# Expected: clean working tree
```

---

## Drift Detection Rule

Drift between the two trees is detected by checking whether any file added to `backlog/EPICS/` in the last 30 days also exists (by filename) in `docs/active/backlog/`. If a file exists in both locations with different content, it is a drift event.

Concrete check (designed for STORY-238 CI implementation):

```bash
# Find filenames that exist in both trees
for f in $(find docs/active/backlog -name "*.md" -printf "%f\n"); do
  canonical=$(find backlog/EPICS -name "$f" 2>/dev/null | head -1)
  if [ -n "$canonical" ]; then
    if ! diff -q "docs/active/backlog/**/$f" "$canonical" > /dev/null 2>&1; then
      echo "DRIFT: $f"
    fi
  fi
done
```

This drift check is delegated to STORY-237 for implementation in CI (EPIC-064 already completed STORY-237 — the check is in the link validation workflow).

---

## Migration Execution Plan

Migration is a three-phase process. Each phase requires a separate PR approved by Platform Team Lead.

### Phase 1: Add Deprecation Notices (Low Risk — Execute Now)

1. Add/update `docs/active/backlog/README.md` with deprecation notice
2. Add/update `docs/active/epics/README.md` with deprecation notice
3. Add/update `docs/active/programs/README.md` with deprecation notice
4. Update `docs/DOCUMENTATION_INDEX.md` to mark `docs/active/` as deprecated

**PR label**: `docs`, `governance`

### Phase 2: Update External References (Medium Risk — After Phase 1 Merged)

1. Update all 13 files listed in the dry-run report above
2. Update the single Python reference in `scripts/ci/check_root_scripts.py`
3. Run `scripts/ci/check_markdown_links.py` to confirm no new broken links introduced

**PR label**: `docs`, `governance`, `cleanup`

### Phase 3: Delete Mirror (Destructive — Requires Explicit Approval)

1. Run all pre-checks above — confirm 0 blocking results
2. Delete `docs/active/backlog/`, `docs/active/epics/`, `docs/active/programs/`
3. Run link check — no new errors should appear (all links already updated in Phase 2)
4. Commit deletion

**PR label**: `docs`, `governance`, `destructive`
**Approval required**: Platform Team Lead + one additional engineer

---

## No Unresolved Design Ambiguity

| Question | Decision |
|----------|---------|
| Which tree is canonical? | `backlog/EPICS/` |
| What happens to `docs/active/`? | Retire (delete) in Phase 3 |
| Generated mirror or one-way sync? | Neither — retire entirely |
| Who can edit the mirror until deletion? | Nobody — no PR approval for mirror edits |
| How is drift detected? | Filename+content check per STORY-237 CI |
| What is the blocking control before deletion? | PR review gate + no-merge-to-mirror policy |
