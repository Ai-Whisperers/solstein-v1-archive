# Documentation Governance Audit (2026-03-11)

## Scope

- Repository: `solstein`
- Audited trees: `docs/**`, `backlog/**`
- Mode: analysis and planning only (no cleanup execution)

## Verified Findings

| Area | Finding | Evidence |
|---|---|---|
| Markdown volume | Large documentation surface with significant operational overhead | 1454 markdown files total |
| Mirror duplication | Backlog mirrored across two trees | 229 mirrored markdown files between `docs/active/backlog` and `backlog/EPICS` |
| Mirror drift | Mirrored content not fully synchronized | 3 drifted mirrored files (`EPIC-002/003/004` READMEs) |
| Link integrity | Broken relative references across docs/backlog | 140 broken relative links in scoped audit (`docs` + `backlog`) |
| Placeholder debt | Template placeholders leaking into maintained docs | Tokens found: `EPIC-XXX`, `STORY-XXX`, `ADR-XXX`, `FD-XXX`, `TODO:`, `TBD` |
| Registry quality | Backlog dashboard inconsistency in canonical index | Duplicate and conflicting metric rows in `backlog/README.md` |

## Risk Assessment

| Risk | Severity | Why it matters |
|---|---|---|
| Dual source-of-truth for backlog docs | High | Causes silent drift and conflicting decisions |
| Broken links in operational docs | High | Reduces navigability and trust; blocks onboarding |
| Placeholder tokens in active docs | Medium | Signals incomplete governance; harms credibility |
| Inconsistent backlog metrics | Medium | Weakens planning and prioritization reliability |

## Root-Cause Themes

1. Documentation topology lacks a single enforced source-of-truth.
2. Link and placeholder quality checks are not enforced in CI.
3. Documentation lifecycle and archival policies are implicit, not automated.
4. Backlog registry updates are partially manual and prone to drift.

## Planning Output

This audit is executed through three implementation epics:

- `EPIC-063`: Documentation Topology and Source-of-Truth Governance
- `EPIC-064`: Markdown Integrity and Registry Correctness
- `EPIC-065`: Documentation Lifecycle Automation and CI Enforcement

Each epic includes detailed stories with acceptance criteria and definition of done.

## Non-Goals (This Phase)

- No file archival, deletion, or migration performed.
- No broken links fixed yet.
- No placeholders replaced yet.
- No index/dashboard metrics corrected yet.

Execution is intentionally deferred to the new stories.
