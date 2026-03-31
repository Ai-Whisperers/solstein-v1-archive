# STORY-268: Add Full-Market Golden Run with Artifact Diffing

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

The legacy pipeline can only be trusted if one representative market run is executable as a regression artifact set: discovered candidates, extracted company payloads, stage reports, scores, and export outputs. Today those artifacts exist ad hoc but are not used as a controlled golden run.

## Acceptance Criteria

- [ ] One representative market run is defined as the golden legacy runtime benchmark.
- [ ] Run artifacts are stored and diffable by stage.
- [ ] The gate fails on silent field loss, missing artifacts, or placeholder outputs.
- [ ] The golden run is reproducible from documented commands and fixtures.

## Tasks

- [ ] Choose the benchmark market/company set.
- [ ] Capture canonical stage artifacts.
- [ ] Add artifact diffing and failure thresholds.
