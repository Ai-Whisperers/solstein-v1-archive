# STORY-208: Add checkpoint persistence and resume command

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Size** | L (2-3 days) |
| **Epic** | [EPIC-054](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | High |

## Problem Statement
Any transient failure forces full rerun, wasting time and causing inconsistent partial outputs.

## Affected Files
- `src/solstein/research/pipeline_async.py`
- `src/solstein/data/web_research_pipeline.py`
- `src/solstein/research/pipeline.py`

## Architectural Requirements
- Persist checkpoint payload with stage id and state hash.
- Resume command restores checkpoint and continues safely.

## Acceptance Criteria
- Interrupted run can be resumed from latest valid checkpoint.
- Duplicate stage writes are prevented on resume.
- Resume path is integration-tested on forced-failure scenario.

## Definition of Done
- Recovery playbook documented.
