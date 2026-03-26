# EPIC-065: Documentation Lifecycle Automation and CI Enforcement

> **Priority**: P1 - High
> **Status**: 🟡 In Progress
> **Canonical Backlog**: `backlog/EPICS/EPIC-065-documentation-lifecycle-automation-ci-enforcement/`

---

## Active Focus

This active backlog mirror tracks the repo mandate to make generated documentation and AST guardrails a default engineering surface rather than a manual follow-up activity.

## Current Rollout

- Generated AST rule catalog committed under `docs/reference/generated/`
- Generated master audit issue index committed under `docs/audit/generated/`
- Repository git hooks configured to refresh and check generated docs
- Further expansion still pending for schema registries, pipeline boundaries, and broader package-addressable API docs

## Story Queue

- STORY-242 Generate AST rule catalog and guardrail registry
- STORY-243 Generate master audit issue index and keep it current
- STORY-244 Enforce generated docs freshness through git hooks and CI
- STORY-245 Expand generated API docs and schema registries

See the canonical epic and story files for acceptance criteria and delivery tracking.
