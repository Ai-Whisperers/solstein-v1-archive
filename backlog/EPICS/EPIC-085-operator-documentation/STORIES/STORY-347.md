# STORY-347: Write pipeline operations runbook

| Field | Value |
|-------|-------|
| **Epic** | EPIC-085 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-330 (golden run baseline) |

## Description

Write a pipeline operations runbook at `docs/operations/pipeline-runbook.md` covering: how to trigger a run, how to monitor it, common failure modes and their resolutions, and how to export results.

## Acceptance Criteria

- [ ] Runbook covers: trigger, monitor, debug, export
- [ ] Common failure modes: no data enriched, all scores zero, LLM failures, DB connection errors
- [ ] Each failure mode has: symptom, likely cause, fix command
- [ ] Tested against actual golden run from STORY-330
