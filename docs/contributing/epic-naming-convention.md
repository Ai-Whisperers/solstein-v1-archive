# Epic Directory Naming Convention and Anomaly Registry

> **Status**: Active governance document
> **Owner**: Platform Team
> **Last Reviewed**: 2026-03-28
> **Review Cadence**: On any epic directory rename or creation
> **Epic**: EPIC-063 (STORY-232)
> **Superseded By**: N/A

---

## Canonical Naming Convention

All epic directories under `backlog/EPICS/` must follow this format:

```
EPIC-{NNN}-{slug}
```

Where:

| Segment | Rule | Examples |
|---------|------|---------|
| `EPIC-` | Literal prefix — always uppercase | `EPIC-` |
| `{NNN}` | Zero-padded 3-digit integer matching the epic number | `001`, `010`, `066` |
| `-` | Literal hyphen separator | `-` |
| `{slug}` | Lowercase, hyphen-separated description of the epic content | `api-layer-hardening`, `test-suite-integrity` |

### Slug Rules

- All lowercase, no underscores, no spaces
- Words separated by single hyphens
- No leading or trailing hyphens
- Must be descriptive of the epic's primary concern (not a verb-first action phrase)
- Maximum 50 characters

### Valid Examples

```
EPIC-010-api-layer-hardening
EPIC-035-async-first-external-adapters
EPIC-066-architectural-boundaries-and-cycle-elimination
```

### Invalid Examples

| Path | Violation |
|------|-----------|
| `EPIC-002` | Missing slug |
| `EPIC-032-complete-unified-adapter-migration` | Slug starts with action verb `complete-` that is not descriptive of the domain |
| `EPIC-010_api_layer` | Underscores in slug |
| `epic-010-api` | Non-uppercase prefix |

---

## Story Directory Convention

Story files under `backlog/EPICS/EPIC-NNN-slug/STORIES/` follow:

```
STORY-{NNN}-{slug}.md
```

Same rules as epic slugs apply. The numeric portion is the story number, not the epic number.

---

## Anomaly Registry

All detected path anomalies are listed here with their disposition. Dispositions are:

- **RENAME**: Rename the directory to the canonical name (requires all internal links updated)
- **MERGE**: Merge the duplicate into the canonical directory, then remove the source
- **ARCHIVE**: Move to `docs/archive/` (for docs mirrors), flagged as deprecated
- **KEEP**: Accepted exception — document the rationale
- **MONITOR**: No immediate action; track for future cleanup

### `backlog/EPICS/` Anomalies

| Path | Anomaly | Disposition | Planned Action | Risk |
|------|---------|------------|---------------|------|
| `EPIC-002` | Missing slug — bare epic number only | MERGE | Content is byte-for-byte identical to `EPIC-002-configuration-integrity`. Remove `EPIC-002/` after confirming no remaining links. | Low — no functional differences |
| `EPIC-032-complete-unified-adapter-migration` | Slug prefixed with action verb `complete-` rather than domain noun | MONITOR | Renaming would break any existing links. Defer rename to next structural cleanup cycle. Document here as technical debt. | Medium — risk of link breakage |

### `docs/active/` Anomalies

| Path | Anomaly | Disposition | Planned Action | Risk |
|------|---------|------------|---------------|------|
| `docs/active/backlog/` | Mirror of `backlog/EPICS/` — 229 files, proven drift (3 files) | ARCHIVE | STORY-231 owns the retirement plan for this mirror | High — must coordinate with STORY-231 |
| `docs/active/epics/` | Mirror of epic planning content | ARCHIVE | Coordinated with `docs/active/backlog/` retirement (STORY-231) | High |
| `docs/active/programs/` | Mirror of programs planning content | ARCHIVE | Coordinated with `docs/active/backlog/` retirement (STORY-231) | Medium |

### `docs/` Root Anomalies

| Path | Anomaly | Disposition | Planned Action | Risk |
|------|---------|------------|---------------|------|
| `docs/epics/` | Contains only `SOLSTEIN_ENHANCEMENT_EPICS.md` — not a real epic registry | MERGE | Move file to `docs/archive/epics/` if outdated, or `docs/strategy/` if still current | Low |
| `docs/documentation/` | Redundant subdirectory (docs inside docs) | MONITOR | Review contents; candidate for merge into `docs/standards/` or `docs/governance/` | Low |

---

## Redirect / Reference Strategy for Renamed Paths

When an epic directory is renamed:

1. Add a `REDIRECT.md` file at the old path with a forward reference:
   ```markdown
   # Redirect Notice
   This directory has been renamed. The canonical path is:
   `backlog/EPICS/{new-canonical-name}/`
   ```
2. Run `scripts/ci/check_markdown_links.py` to detect all files that link to the old path.
3. Update all detected links in a single atomic commit.
4. Remove the old directory after all links are updated and the PR is merged.
5. Update this anomaly registry to mark the anomaly as resolved.

---

## Registry Update Process (Naming Validation)

When creating a new epic directory:

1. Verify the name matches `EPIC-{NNN}-{slug}` format using:
   ```bash
   echo "EPIC-067-my-new-epic" | grep -E '^EPIC-[0-9]{3}-[a-z][a-z0-9-]{1,49}$'
   ```
2. Confirm the number does not collide with an existing epic:
   ```bash
   ls backlog/EPICS/ | grep "^EPIC-067"
   ```
3. Add the epic to `planning/QUEUE.md` with READY/BLOCKED status before creating the directory.
4. If an anomaly is introduced intentionally (accepted exception), add it to the **Anomaly Registry** with a `KEEP` disposition and documented rationale.

---

## Immediate Remediation Actions

The following actions are safe to execute now (low risk, no link breakage expected):

### Action 1: Remove `EPIC-002` Duplicate Directory

`EPIC-002` is byte-for-byte identical to `EPIC-002-configuration-integrity`. It should be removed.

Before removal, verify no files link to it:

```bash
grep -r "EPIC-002[^-]" backlog/ docs/ --include="*.md" | grep -v "EPIC-002-configuration-integrity"
```

If the command returns no results, it is safe to delete `backlog/EPICS/EPIC-002/`.

**Status**: Identified — action delegated to next structural cleanup PR.

### Action 2: Document `EPIC-032` Slug Exception

`EPIC-032-complete-unified-adapter-migration` uses an action-verb prefix. The rename is deferred to avoid link breakage. Tracked here as accepted technical debt with `MONITOR` disposition.

---

## Enforcement

New epic path validation is delegated to EPIC-065 (STORY-238: CI Docs Quality Gates). Until CI enforcement is live, manual review during PR is the primary gate.

Reviewers should check new `backlog/EPICS/` directories against this convention before approving PRs.
