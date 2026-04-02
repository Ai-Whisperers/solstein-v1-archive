# STORY-245: Expand Generated API Docs and Schema Registries

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | L (1-2 weeks) |
| **Epic** | EPIC-065 Documentation Lifecycle Automation and CI Enforcement |
| **Created** | 2026-03-26 |
| **Risk** | High |

---

## Problem Statement

The current automated docs layer only covers a small strict slice. High-risk folders such as `analytics`, `data`, and `domain` still need package cleanup and generated schema/boundary registries before the docs system becomes broadly useful.

## Acceptance Criteria

- [ ] Missing package-addressability blockers are resolved for the targeted modules.
- [ ] A generated schema ownership map is committed and linked from reference docs.
- [ ] A generated pipeline boundary registry is committed and linked from reference docs.
- [ ] A generated connector contract surface index is committed and linked from reference docs.
- [ ] Docs generation remains strict and blocking for the maintained subset while the broader expansion is phased in.

## Definition of Done

- [ ] `PYTHON_API_REFERENCE.md` expands beyond the current strict slice.
- [ ] Generated docs cover the critical business pipeline boundaries.
- [ ] Future agents can answer schema ownership and connector-contract questions without reopening large source areas.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- `planning/QUEUE.md` marks this story `READY` and it is the only active unfinished story in EPIC-065.

### Next Agent Action

- Continue with source-derived generated docs only.
- Expand registries and generated references without backsliding into hand-maintained API prose.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md` and the tokenless-doc direction in `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Keep maintained-doc strictness honest; do not silently expand blocking scope to legacy docs that are still noisy.

### Minimum Verification For Future Agents

- Run `make docs-strict`, `make docs-generated-check`, and `make docs-quality-check`.
- If the generated references change maintained engineering surfaces, finish with `make gate-engineering` or document the exact pre-existing blocker.
