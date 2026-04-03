# STORY-362: Define Workflow Model, States, and Internal Storage Contract

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | M (2 days) |
| **Epic** | EPIC-089 Workflow Orchestration API |
| **Created** | 2026-04-03 |
| **Risk** | Medium — design decision; downstream stories depend on this contract |
| **Blocked By** | EPIC-086 (pipeline must produce correct data first) |

---

## Problem Statement

There is no `Workflow` concept in the domain. The existing `ResearchRunRecord` and `ResearchStageRecord` tables track pipeline execution, but there is no API-facing model, no state machine, and no documented contract for how workflow state maps to HTTP responses. This must be defined before the POST/GET endpoints can be implemented.

## Acceptance Criteria

- [ ] `Workflow` Pydantic model defined with fields: `workflow_id`, `status`, `current_stage`, `progress_pct`, `started_at`, `completed_at`, `output_url`, `error`
- [ ] Workflow states documented as a `WorkflowStatus` StrEnum: `queued | running | completed | failed | cancelled`
- [ ] Mapping documented: `ResearchRunRecord.state` → `WorkflowStatus`
- [ ] `WorkflowRepository` class with `get(workflow_id) -> Workflow | None` implemented
- [ ] Unit test: given a mock `ResearchRunRecord` at each state, `WorkflowRepository.get()` returns the correct `WorkflowStatus`

## Tasks

- [ ] Read `src/solstein/infrastructure/database_models.py` — understand `ResearchRunRecord` and `ResearchStageRecord` fields
- [ ] Define `WorkflowStatus` StrEnum in `src/solstein/domain/models.py` or new `src/solstein/domain/workflow.py`
- [ ] Define `Workflow` Pydantic model
- [ ] Implement `WorkflowRepository.get(workflow_id: str) -> Workflow | None` using existing `ResearchRunRecord`
- [ ] Map pipeline stage names to `progress_pct` (e.g., discovery=10%, gather=30%, scoring=70%, export=100%)
- [ ] Write unit tests for the repository
