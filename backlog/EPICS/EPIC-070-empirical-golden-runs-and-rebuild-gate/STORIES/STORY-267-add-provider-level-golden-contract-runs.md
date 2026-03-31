# STORY-267: Add Provider-Level Golden Contract Runs

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-070 Empirical Golden Runs and Rebuild Gate |
| **Created** | 2026-03-31 |
| **Risk** | Medium |

---

## Problem Statement

The repo has many provider adapters but no small, trustworthy set of representative contract runs that prove the active provider surfaces still return the fields and failure semantics the runtime expects.

## Acceptance Criteria

- [ ] At least two representative providers have golden contract runs.
- [ ] Golden runs validate both success and degraded/failure semantics.
- [ ] Golden artifacts are stored and diffable.
- [ ] The selected providers cover materially different surfaces.

## Tasks

- [ ] Choose representative providers for the canonical runtime.
- [ ] Define their contract assertions.
- [ ] Add artifact storage and regression comparison.
