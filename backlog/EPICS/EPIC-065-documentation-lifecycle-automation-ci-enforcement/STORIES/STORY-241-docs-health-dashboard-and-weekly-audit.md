# STORY-241: Publish Docs Health Dashboard and Weekly Audit Automation

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P2 - Medium |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-065 Documentation Lifecycle Automation and CI Enforcement |
| **Created** | 2026-03-11 |
| **Risk** | Low |

---

## Problem Statement

Documentation quality status is not centrally visible, making regressions hard to detect early.

## Acceptance Criteria

- [ ] Dashboard defines core metrics (broken links, stale docs, placeholders, unresolved drift).
- [ ] Metrics are generated automatically from repository scans.
- [ ] Dashboard consumes the canonical metrics artifact from STORY-236 as its source data.
- [ ] Weekly scheduled audit job publishes trend report.
- [ ] Dashboard links to remediation stories for any red metric.

## Definition of Done

- [ ] Dashboard is published in docs and updated automatically.
- [ ] Weekly job run history is observable and retained.
