# Mirror Drift Report — 2026-03-26

**Story**: STORY-237 — Reconcile Mirrored Drift and Publish Delta Changelog
**Generated**: 2026-03-26
**Owner**: Autonomous worker (EPIC-064)

---

## Mirror Under Analysis

| Mirror | Source | Purpose |
|--------|--------|---------|
| `docs/active/backlog/` | `backlog/EPICS/` | Stale copy of backlog from pre-EPICS-subdirectory restructure |

---

## Drift Inventory

| Category | Count |
|----------|-------|
| Files with identical content in both locations | 0 |
| Files only in mirror (`docs/active/backlog/`) | 236 |
| Files only in source (`backlog/EPICS/`) | 327 |
| Files with content divergence | **0** |

**Key finding**: The mirror and source share **zero overlapping files** by path. The mirror was created
before the backlog was restructured to place stories under `backlog/EPICS/<epic-name>/STORIES/`. The
mirror uses the old flat structure (`docs/active/backlog/EPIC-001-security-restoration/README.md`)
while the source uses `backlog/EPICS/EPIC-001-security-restoration/README.md`.

Since file paths don't overlap, there is no content drift to reconcile — the mirror is simply an
older structural snapshot, not a maintained copy.

---

## Reconciliation Decision

**Decision**: Retire `docs/active/backlog/` mirror.

**Rationale**:
- The mirror was useful when the backlog lived at the root level. After the EPICS/ restructuring,
  the mirror diverged in structure (not content) and became a navigation hazard.
- The mirror accounts for 77 of the 111 remaining broken links in the link audit (STORY-234).
- No feature code or operational docs depend on the `docs/active/backlog/` path.
- The source of truth is `backlog/EPICS/` which is actively maintained.

**Action**: The mirror directory is retained in this commit (destructive deletion requires explicit
human approval per CLAUDE.md). A follow-up task should remove `docs/active/backlog/` and
`docs/active/epics/` once approved.

**Disposition**: `docs/active/backlog/` → retire (do not maintain, schedule deletion)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-03-26 | Drift inventory generated; mirror retirement decision recorded | Autonomous worker |
| 2026-03-26 | Broken links in mirror documented in `docs/link-allowlist.md` (allowlisted as group) | Autonomous worker |

---

## Follow-Up Actions Required

1. **Human approval**: Delete `docs/active/backlog/` and `docs/active/epics/` directories
2. **Update**: Remove `docs/active/` reference from `docs/ORGANIZATION_SUMMARY.md` if present
3. **Verify**: No CI scripts reference `docs/active/backlog/` paths
4. **Update**: `backlog/README.md` if it references the mirror path
