# EPIC-065: Documentation Lifecycle Automation and CI Enforcement

> **Priority**: P1 - High
> **Stories**: 8 (STORY-238 through STORY-245)
> **Effort**: L (3-4 weeks)
> **Dependencies**: EPIC-063 (Documentation Topology and Source-of-Truth Governance), EPIC-064 (Markdown Integrity and Registry Correctness)
> **Status**: 🟡 In Progress

---

## Problem

Documentation quality checks are mostly manual and regressions reappear after ad-hoc cleanup.
There is no consistent lifecycle enforcement from authoring through archival.

---

## Scope

| Category | Action |
|---|---|
| CI Quality Gates | Add markdown lint/link/token checks with policy controls |
| Lifecycle Management | Enforce review cadence and stale-doc detection |
| Authoring Workflow | Standardize PR templates and docs review checklist |
| Observability | Publish docs-quality metrics and trend reporting |
| Generated Artifacts | Generate machine-readable audit and AST indexes |
| Freshness Enforcement | Block stale generated docs locally and in CI |
| Tokenless Navigation | Expand generated schema, boundary, and API reference surfaces |

---

## Stories

| Story | Title | Priority | Size | Status |
|---|---|---|---|---|
| STORY-238 | Implement CI docs quality gates (links, tokens, front matter) | P1 | M | 🔴 Open |
| STORY-239 | Add stale-doc detection and ownership alert workflow | P1 | M | 🔴 Open |
| STORY-240 | Introduce docs review checklist and change-control workflow | P2 | M | 🔴 Open |
| STORY-241 | Publish docs health dashboard and weekly audit automation | P2 | M | 🔴 Open |
| STORY-242 | Generate AST rule catalog and guardrail registry | P1 | M | 🟡 In Progress |
| STORY-243 | Generate master audit issue index and keep it current | P1 | M | 🟡 In Progress |
| STORY-244 | Enforce generated docs freshness through git hooks and CI | P1 | S | 🟡 In Progress |
| STORY-245 | Expand generated API docs and schema registries | P1 | L | 🔴 Open |

---

## Architectural Requirements

- **REQ-1**: Docs quality gates must run in CI and fail on policy violations.
- **REQ-2**: Each maintained doc must have owner and review timestamp metadata per class policy from STORY-233.
- **REQ-3**: Stale-doc detection must be deterministic and explainable.
- **REQ-4**: Dashboard metrics must be generated, not hand-edited.
- **REQ-5**: Docs health dashboards must consume the canonical metrics artifact defined by STORY-236.
- **REQ-6**: Generated structural docs must be derived from source code or source audit inputs, not manually duplicated.
- **REQ-7**: Generated artifacts must have local freshness enforcement before commit and push.
- **REQ-8**: The master audit must remain preserved as source history while generated indexes provide cheaper access paths.

---

## Success Criteria

- CI blocks merges for high-severity docs quality violations.
- Maintained docs have ownership and review metadata coverage above 95%.
- Weekly stale-doc report is generated automatically.
- Docs quality trends are visible in a single dashboard.
- Generated audit and AST indexes are committed and refreshed automatically.
- Repo hooks and CI prevent stale generated docs from being pushed.
