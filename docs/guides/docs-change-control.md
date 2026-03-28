> **Status**: Active
> **Owner**: docs-team
> **Last Reviewed**: 2026-03-28
> **Superseded By**: N/A
> **Review Cadence**: Quarterly

# Documentation Change-Control Workflow

This guide defines the review requirements and checklist for pull requests that modify
documentation. It applies to all changes under `docs/`, `backlog/`, `.claude/rules/`, and
any other canonical documentation paths.

The source-of-truth policy established in STORY-230 and the mirror-cutover policy from
STORY-231 are explicitly referenced and enforced by this workflow.

---

## Quick Reference: Required Reviewers by Doc Class

| Doc Class | Path Pattern | Required Reviewers | Major Change Impact Summary? |
|---|---|---|---|
| Governance | `docs/governance/` | docs-team + 1 senior engineer | Yes |
| Standards | `docs/standards/` | docs-team + 1 senior engineer | Yes |
| Architecture | `docs/architecture/` | platform-team + tech-lead | Yes |
| API Reference | `docs/api/` | backend-team | Yes (breaking changes) |
| Audit | `docs/audit/` | docs-team | No |
| Developer Guides | `docs/guides/`, `docs/developers/` | Any engineer | No |
| Backlog / Epics | `backlog/`, `docs/active/` | product-team | No |
| Generated | `docs/reference/generated/`, `docs/audit/generated/` | Automated (CI only) | N/A |

For governance, standards, and architecture docs: a **major change impact summary** must be
included in the PR body (see template below).

---

## Docs PR Checklist

Copy this checklist into your PR body when your PR touches documentation files.

```markdown
### Docs Change-Control Checklist

#### Topology and Structure
- [ ] File paths follow the canonical structure (see docs/guides/documentation-style-guide.md)
- [ ] No duplicate docs created — checked for existing coverage in the affected area
- [ ] If a doc is moved or renamed: old path has a redirect or deprecation notice
- [ ] If a doc is deleted: all inbound links updated or removed

#### Link Integrity
- [ ] All internal links are relative and point to existing files
- [ ] No links to `example.com` or placeholder URLs
- [ ] External links open in the context they are cited (reference checked)

#### Metadata (governance and standards docs only)
- [ ] Blockquote front-matter present: Status, Owner, Last Reviewed, Superseded By
- [ ] Review Cadence set (recommended)
- [ ] `Last Reviewed` updated to today's date

#### Content Quality
- [ ] No unfilled template variables (`{{ ... }}` that are not intentional)
- [ ] No `PLACEHOLDER`, bare `TODO:`, or `FIXME:` tokens
- [ ] Language is clear, present-tense, and audience-appropriate

#### CI Gates
- [ ] `make docs-quality-check` passes locally (STORY-238)
- [ ] `make docs-generated-check` passes if any generated docs were re-generated
- [ ] No broken links (link-allowlist check passes)

#### Deprecation and Rollback
- [ ] If replacing an existing doc: old doc marked deprecated with a pointer to the new one
- [ ] If removing a policy: downstream references updated or a migration note added
- [ ] Rollback plan: what happens if this doc change needs to be reverted?

#### Source-of-Truth Compliance (STORY-230)
- [ ] This doc lives in its designated canonical location (not a mirror or copy)
- [ ] If this is a mirror path: the canonical source has been updated first

#### Major Change Impact Summary (required for governance, standards, and architecture docs)
<!--
Fill in if your PR touches docs/governance/, docs/standards/, or docs/architecture/.
-->
**What is changing?**
> ...

**Why is this change needed?**
> ...

**Who is affected?**
> ...

**Rollback / deprecation path:**
> ...
```

---

## Change-Control Decision Tree

```
Does the PR touch docs/governance/ or docs/standards/?
├── YES → Required: docs-team + 1 senior engineer review
│         Required: Major Change Impact Summary in PR body
│         Required: blockquote metadata updated (Last Reviewed to today)
│
├── Does it touch docs/architecture/ or docs/api/?
│   ├── YES → Required: platform-team or backend-team review
│   │         Required: Major Change Impact Summary if breaking
│   │
│   └── Does it touch docs/guides/, docs/developers/, or backlog/?
│       ├── YES → Any engineer reviewer is sufficient
│       │
│       └── Does it touch docs/reference/generated/ or docs/audit/generated/?
│           ├── YES → These files must only be changed by the CI generator scripts.
│           │         If you are hand-editing them: stop and update the generator instead.
│           │
│           └── Other path → Follow the style guide and use any engineer reviewer.
```

---

## Rollback and Deprecation Expectations

**Doc deprecation**: When a document is superseded, do not delete it immediately.

1. Add a deprecation notice at the top:
   ```markdown
   > **⚠️ Deprecated**: This document has been superseded by [New Document](../new-doc.md).
   > It will be removed on or after YYYY-MM-DD.
   ```
2. Update the `Superseded By` front-matter key to point to the new document.
3. Update inbound links to the new canonical location.
4. Remove the deprecated doc no sooner than one sprint after the deprecation notice.

**Rollback**: Documentation-only changes can be reverted by reverting the relevant commit.
If the doc change was bundled with a code change, create a follow-up doc-only PR to revert
the documentation while leaving the code in place.

---

## Source-of-Truth and Mirror Policy

Per STORY-230: every document has a single canonical location. Do not maintain duplicate
copies across `docs/` and `backlog/`. If both exist for a file, the `docs/` path is canonical.

Per STORY-231: when a mirror is cut over (the `backlog/` copy retired in favour of `docs/`),
the PR must include a redirect or deprecation notice at the mirror path so inbound links
do not break silently.

---

## Pilot PR Reference

The first PR to use this workflow end-to-end is PR #193 (STORY-238), which introduced the
docs quality gate and its associated allowlist. It demonstrates: docs topology compliance,
metadata-free (not a governance doc), CI gate verification, and the impact-summary form
(not required for that doc class but provided voluntarily).
