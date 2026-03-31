# Archival and Deprecation Metadata Policy

> **Status**: Active governance document
> **Owner**: Platform Team Lead
> **Last Reviewed**: 2026-03-28
> **Review Cadence**: Annually or on policy change request
> **Epic**: EPIC-063 (STORY-233)
> **Superseded By**: N/A

---

## Purpose

This policy defines the standard metadata keys for all Solstein documentation, the rules for when and how documents move through lifecycle states, and the front-matter requirements that enable automated lifecycle checks.

---

## Standard Front-Matter Keys

All maintained governance documents must include the following front-matter comment block at the top of the file, immediately after the `# Title` line:

```markdown
> **Status**: {lifecycle-status}
> **Owner**: {team or person name}
> **Last Reviewed**: {YYYY-MM-DD}
> **Review Cadence**: {cadence description}
> **Epic**: {EPIC-NNN (STORY-NNN)} (optional — omit for non-epic-scoped docs)
> **Superseded By**: {path/to/successor.md} or N/A
```

### Key Definitions

| Key | Required | Values | Machine-Checkable |
|-----|----------|--------|-------------------|
| `Status` | Yes | `Active`, `Deprecated`, `Archived`, `Draft` | Yes |
| `Owner` | Yes | Team name or person name (free text) | No |
| `Last Reviewed` | Yes | ISO date `YYYY-MM-DD` | Yes (staleness check) |
| `Review Cadence` | Yes | Free text (e.g. `Quarterly`, `Annually`, `On process change`) | No |
| `Epic` | No | `EPIC-NNN (STORY-NNN)` format | No |
| `Superseded By` | Yes | Relative path to successor doc, or literal `N/A` | Yes |

### Status Values

| Value | Meaning |
|-------|---------|
| `Active` | Document is current, accurate, and actively maintained |
| `Draft` | Document is in progress — not yet approved or accurate |
| `Deprecated` | Document is superseded but kept in place for reference during transition |
| `Archived` | Document has been moved to `docs/archive/` — frozen, read-only |

---

## Lifecycle States and Transitions

```
Draft → Active → Deprecated → Archived
                     ↑
              (can also go directly
               from Active → Archived
               if immediately retired)
```

### Active

A document is `Active` when:
- It accurately reflects current system behaviour or policy
- It has a designated owner who is responsible for keeping it current
- It has been reviewed within the last review cadence period

### Deprecated

A document is `Deprecated` when:
- A newer or more authoritative document exists that supersedes it
- The document is retained in its current location (not yet moved to archive) to avoid breaking existing links during the transition period
- The `Superseded By` field must point to the successor document

Deprecated documents must display a deprecation notice as the first substantive block of content:

```markdown
> **Deprecated**: This document has been superseded by [{successor title}]({path}).
> It is retained for reference during the transition period. Do not rely on this document for current guidance.
```

### Archived

A document is `Archived` when:
- It is moved to `docs/archive/{category}/`
- The `Status` front-matter is set to `Archived`
- It is frozen — no edits are made after archival
- A redirect or notice is placed at the original path (if the original path is linked from other documents)

Archive subdirectories:

| Subdirectory | Contents |
|--------------|---------|
| `docs/archive/legacy-root/` | Root-level docs moved during EPIC-043 reorganisation |
| `docs/archive/audits/` | Historical audit snapshots (e.g. codebase audits, drift reports) |
| `docs/archive/epics/` | Superseded epic planning docs |
| `docs/archive/analysis/` | Historical analysis and session reports |

---

## Archival Rules

### When to Archive

Archive a document when any of the following is true:

1. The system it describes no longer exists or has been completely replaced.
2. A successor document fully covers the same material and the original adds no unique context.
3. The document is more than 2 years old and has not been reviewed within its declared cadence.
4. The document belongs to a retired phase or defunct initiative.
5. Governance explicitly approves archival via a PR with a governance label.

### When NOT to Archive

Do not archive a document:
- If it is still referenced by active CI scripts or external tooling.
- If removing it from its current location would break links that cannot be updated in the same PR.
- If no successor document exists and the content is still useful.

### Archival Procedure

1. Set `Status` to `Archived` in the front-matter.
2. Move the file to the appropriate `docs/archive/{category}/` subdirectory.
3. Place a redirect notice at the original path if it was externally linked:
   ```markdown
   # Redirect Notice
   This document has been archived. The historical version is available at:
   `docs/archive/{category}/{filename}.md`
   ```
4. Update any links in active documents to point to the new path or the successor.
5. Add a row to the [archival log](#archival-log) at the bottom of this document.

---

## Superseded Document Requirements

When a document is superseded:

1. The `Superseded By` field must be set to the relative path of the successor.
2. A deprecation notice block must be added as the first substantive content.
3. The successor document must include a reference back:
   ```markdown
   > **Supersedes**: [{predecessor title}]({path})
   ```
4. If the predecessor is still in active use by any team, mark it `Deprecated` (not `Archived`) until the transition is complete.

---

## Machine-Checkable Front-Matter Requirements

The following checks are designed to be implemented as CI scripts (delegated to EPIC-065, STORY-238):

### Check 1: Required Keys Present

Every file in `docs/` (excluding `docs/archive/`, `docs/agent-cycles/`, `docs/sessions/`, `docs/continuation/`) that contains a `# Title` heading must have the following keys in its front-matter block:
- `Status`
- `Owner`
- `Last Reviewed`
- `Superseded By`

**Severity**: Warning (not blocking initially; becomes blocking after STORY-238 is merged)

### Check 2: Status Value is Valid

The `Status` value must be one of: `Active`, `Draft`, `Deprecated`, `Archived`.

**Severity**: Error (blocks merge)

### Check 3: Last Reviewed Staleness

If `Status` is `Active` and the `Review Cadence` is `Quarterly`, the `Last Reviewed` date must be within 90 days of the current date. For `Annually`, within 365 days.

**Severity**: Warning (advisory; owner receives notification via STORY-239)

### Check 4: Deprecated Without Successor

If `Status` is `Deprecated`, the `Superseded By` field must not be `N/A` — it must point to an existing file.

**Severity**: Error (blocks merge)

### Check 5: Archived Files Outside Archive Directory

If a file has `Status: Archived` in its front-matter, it must be located under `docs/archive/`.

**Severity**: Error (blocks merge)

---

## Governance Documents Front-Matter Adoption Status

The governance documents created in EPIC-063 adopt this standard:

| Document | Status | Compliant |
|----------|--------|-----------|
| `docs/governance/docs-topology.md` | Active | Yes — front-matter present |
| `docs/governance/epic-naming-convention.md` | Active | Yes — front-matter present |
| `docs/governance/archival-policy.md` | Active | Yes — this document |

Adoption across the broader `docs/` tree is delegated to EPIC-065 (STORY-239).

---

## Archival Log

This log records all documents formally archived under this policy.

| Date | Document | Archived To | Reason | Approved By |
|------|----------|------------|--------|------------|
| — | — | — | Policy established — no archival actions yet | Platform Team |

New entries are appended to this table in the archival PR.
