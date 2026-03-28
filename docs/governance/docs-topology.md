# Documentation Topology and Canonical Source-of-Truth

> **Status**: Active governance document
> **Owner**: Platform Team
> **Last Reviewed**: 2026-03-28
> **Review Cadence**: Quarterly or after any structural reorganisation
> **Epic**: EPIC-063 (STORY-230)
> **Superseded By**: N/A

---

## Purpose

This document defines the canonical structure of all documentation in the Solstein repository, establishes document class boundaries, and specifies ownership per directory. It is the authoritative reference for where documentation lives, who is responsible for it, and how new documentation should be placed.

---

## Top-Level Documentation Roots

The repository has two top-level documentation roots. Each has a distinct mandate and canonical ownership:

| Root | Canonical Purpose | Non-Canonical Mirror | Governance Owner |
|------|------------------|----------------------|-----------------|
| `docs/` | Human-authored developer, operator, and architectural reference documentation | `docs/active/backlog/` mirrors `backlog/EPICS/` (drift exists — see STORY-231) | Platform Team |
| `backlog/` | Planning artifacts: epics, stories, and the work queue | N/A | Product / Platform Team |

**Decision rule**: If a document is referenced by code, CI, or an external tool — it lives in `docs/`. If a document tracks a delivery commitment (epic, story, queue) — it lives in `backlog/`.

---

## Document Classes

Every document in the repository belongs to exactly one class. Class determines review cadence and edit authority.

| Class | Tag | Description | Edit Authority | Review Cadence |
|-------|-----|-------------|---------------|----------------|
| `maintained` | `<!-- class: maintained -->` | Human-authored reference docs that must stay current | Any engineer with PR approval | Quarterly |
| `generated` | `<!-- class: generated -->` | Machine-generated from source of truth (AST, schemas, registry) | CI only — human edits are overwritten | On every generation run |
| `template` | `<!-- class: template -->` | Boilerplate scaffolding for new docs (story templates, ADR templates) | Platform Team lead | On process change |
| `archived` | `<!-- class: archived -->` | Retired documents kept for historical context — not updated | Read-only — requires governance sign-off to unarchive | Never (frozen) |

---

## Directory Topology Map

### `docs/` — Developer and Operator Reference

```
docs/
├── governance/          [maintained] Documentation governance docs (this file, ownership matrix)
├── standards/           [maintained] Engineering standards (exception handling, async HTTP)
├── architecture/        [maintained] System architecture, ADRs, data flow
├── adr/                 [maintained] Architecture Decision Records (numbered sequence)
├── api/                 [maintained] API reference and OpenAPI supplements
├── developers/          [maintained] Developer how-to guides (contributing, async patterns)
├── guides/              [maintained] Operator and user guides (getting-started, retry-logic)
├── runbooks/            [maintained] Incident and operational runbooks
├── security/            [maintained] Security policies and incident response
├── observability/       [maintained] Metrics, tracing, log format docs
├── deployment/          [maintained] Deployment and environment docs
├── migrations/          [maintained] Database migration notes
├── operations/          [maintained] Day-2 operations docs
├── reference/           [maintained + generated] API references; generated/ subdir is CI-owned
├── audit/               [generated] CI-generated audit reports and quality snapshots
├── diagrams/            [maintained] Architecture diagrams (source files)
├── data/                [maintained] Data model and field lineage docs
├── exports/             [maintained] Export format specifications
├── examples/            [maintained] Code examples (curl, Python, JavaScript)
├── adapters/            [maintained] Per-adapter integration docs
├── active/              [DEPRECATED MIRROR] See STORY-231 — do not add new docs here
│   ├── backlog/         [mirror of backlog/EPICS/ — drift exists — retirement planned]
│   ├── epics/           [mirror — retirement planned]
│   └── programs/        [mirror — retirement planned]
├── archive/             [archived] Retired documents — read-only
│   ├── legacy-root/     Historical root-level docs moved during EPIC-043
│   ├── audits/          Historical audit snapshots
│   ├── epics/           Superseded epic planning docs
│   └── analysis/        Historical analysis reports
├── agent-cycles/        [archived] Per-session agent run logs — read-only historical record
├── sessions/            [archived] Session context backups — read-only
├── continuation/        [archived] Agent continuation context — read-only
├── analysis/            [maintained] Ongoing analysis reports and session summaries
├── strategy/            [maintained] Strategic direction and business context
├── communications/      [maintained] Stakeholder communications and updates
├── internal/            [maintained] Internal team notes not for external audiences
├── phases/              [archived] Phase evolution docs (Phases 1-13) — historical record
├── LORE/                [archived] Project origin and decision lore
├── PITCH/               [maintained] Investor and stakeholder pitch materials
└── assets/              [maintained] Static assets (images, CSS, JS for doc site)
```

### `backlog/` — Planning Artifacts

```
backlog/
├── EPICS/               [maintained] One directory per epic; CANONICAL for all epic/story files
│   └── EPIC-NNN-slug/
│       ├── README.md    Epic specification
│       └── STORIES/     Individual story files
└── EPIC_RECONCILIATION.md  [maintained] Reconciliation audit snapshot
```

---

## Ownership Matrix

| Directory | Primary Owner | Secondary Owner | Edit Policy |
|-----------|--------------|-----------------|-------------|
| `docs/governance/` | Platform Team Lead | Any engineer (PR required) | PR with governance review |
| `docs/standards/` | Platform Team Lead | Eng leads | PR with at least one eng lead approval |
| `docs/architecture/` | Senior Architect | Platform Team | PR with architect approval |
| `docs/adr/` | Senior Architect | Platform Team | PR required; ADR must follow numbering |
| `docs/api/` | API owner | Backend Team | PR with backend review |
| `docs/developers/` | Platform Team | Any engineer | PR required |
| `docs/guides/` | Platform Team | Any engineer | PR required |
| `docs/runbooks/` | DevOps / On-call lead | Platform Team | PR required |
| `docs/security/` | Security lead | Platform Team | PR with security review |
| `docs/observability/` | Platform Team | DevOps | PR required |
| `docs/reference/generated/` | CI system | Platform Team (config only) | No human edits — CI regenerates |
| `docs/audit/generated/` | CI system | Platform Team (config only) | No human edits — CI regenerates |
| `docs/archive/` | Platform Team Lead | None | Read-only; require governance approval to unarchive |
| `docs/agent-cycles/` | Autonomous agent system | Platform Team | Read-only; written by agent worker |
| `docs/active/` | DEPRECATED | Platform Team | No new docs; retirement tracked in STORY-231 |
| `backlog/EPICS/` | Product + Platform Team | Any engineer | PR required; stories must follow template |

---

## New Document Creation Rules

When adding a new document, follow this decision tree:

1. **Is it tracking a delivery commitment (epic or story)?**
   → Place in `backlog/EPICS/EPIC-NNN-slug/` (or `STORIES/` subdir).

2. **Is it a machine-generated artifact (AST audit, schema registry, API reference)?**
   → Place in `docs/reference/generated/` or `docs/audit/generated/`.
   → Add the generation script to CI; do not commit by hand.

3. **Is it an architectural decision?**
   → Place in `docs/adr/` using the numbered ADR format.

4. **Is it a developer how-to or engineering standard?**
   → Place in `docs/developers/` (how-to) or `docs/standards/` (standard).

5. **Is it operational guidance for running or deploying the system?**
   → Place in `docs/runbooks/` (incident/ops) or `docs/deployment/` (deploy steps).

6. **Is it reference documentation for an external integration or API?**
   → Place in `docs/api/` or `docs/adapters/`.

7. **Is it retired / historical but must be preserved?**
   → Move to `docs/archive/` with `archived` class tag in front matter.

8. **None of the above?**
   → Default to `docs/` root with a descriptive filename.
   → Add an entry to `docs/DOCUMENTATION_INDEX.md`.

### Placement Examples

| Scenario | Canonical Path |
|----------|---------------|
| New engineering standard for database transactions | `docs/standards/database-transactions.md` |
| ADR for switching from Redis to Valkey | `docs/adr/0042-switch-redis-to-valkey.md` |
| Runbook for Celery queue drain | `docs/runbooks/celery-queue-drain.md` |
| Generated API schema registry | `docs/reference/generated/api-schema-registry.md` |
| Epic for new feature | `backlog/EPICS/EPIC-067-new-feature/README.md` |
| Historical analysis from Feb 2026 | `docs/archive/analysis/analysis-2026-02.md` |

---

## Class-to-Review-Cadence Mapping

| Class | Review Cadence | Trigger | Owner Action |
|-------|---------------|---------|-------------|
| `maintained` | Quarterly | Calendar; or when referenced system changes | Owner reviews, updates, or marks stale |
| `generated` | On every CI run | Automated | CI fails if staleness detected (STORY-244) |
| `template` | On process change | PR introducing new workflow | Platform Team Lead approval |
| `archived` | Never | N/A | Only unarchive via governance review |

---

## Governance Handoff

The following related concerns are delegated to downstream stories:

| Concern | Delegated To | Story |
|---------|-------------|-------|
| Resolving the `docs/active/backlog/` mirror | EPIC-063 | STORY-231 |
| Normalising epic directory naming anomalies | EPIC-063 | STORY-232 |
| Front matter archival metadata policy | EPIC-063 | STORY-233 |
| CI enforcement of doc lifecycle rules | EPIC-065 | STORY-238, STORY-239 |
| Docs review checklist and change control | EPIC-065 | STORY-240 |
| Generated doc freshness enforcement | EPIC-065 | STORY-244 |
