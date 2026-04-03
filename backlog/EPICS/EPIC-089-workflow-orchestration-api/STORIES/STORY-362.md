# STORY-362: Define Workflow API Model and WorkflowRepository Over Existing DB Tables

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | EPIC-089 Workflow Orchestration API |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (rewritten after codebase audit) |
| **Risk** | Low — only adding new code over existing tables |
| **Blocked By** | EPIC-086 (must be DONE first) |

---

## Actual Codebase State (verified 2026-04-03)

**These tables ALREADY EXIST in `src/solstein/infrastructure/models/research.py`:**

`ResearchRunRecord` (line 34):
- Columns: `id` (UUID), `tenant_id` (nullable), `run_id` (String, unique), `market`, `seed_company`, `status`, `strict_provenance`, `min_readiness_score`, `summary` (JSON), `created_at`
- Relationships: `stages` (→ ResearchStageRecord), `artifacts`, `sources`

`ResearchStageRecord` (line 65):
- Columns: `id` (UUID), `run_id` (FK), `stage_name` (String, indexed), `stage_order`, `status`, `metrics` (JSON), `created_at`
- Unique constraint: (run_id, stage_name)

`ResearchJobRecord` (line 281):
- Columns: `id` (UUID), `tenant_id` (NOT NULL), `company_id`, `company_name`, `status` (`queued|running|completed|failed|cancelled`), `progress_pct`, `current_stage`, `error_message`, `job_metadata` (JSON), `created_at`, `started_at`, `completed_at`
- Note: this is the newer, more complete record type — **prefer this for the Workflow API**

**Existing job API:**
- `src/solstein/api/routers/research_jobs.py` — `GET /jobs` and `GET /jobs/{job_id}` already exist and return `ResearchJobResponse`
- `src/solstein/api/routers/jobs.py` — `GET /{workflow_id}` returns HTTP 501

**The gap:** There is no unified `POST /workflows` (to submit) or `GET /workflows/{id}` (to retrieve). The existing `research_jobs` router only reads — no creation endpoint.

---

## Problem Statement

The `GET /jobs/{workflow_id}` route (`src/solstein/api/routers/jobs.py`) returns HTTP 501. A newer and more capable `GET /jobs/{job_id}` exists in `research_jobs.py` but there is no `POST` to create a workflow job, no `Workflow` response model unified across both routers, and no `WorkflowRepository` abstraction.

This story creates the `Workflow` API contract and repository layer.

---

## Acceptance Criteria

- [ ] `WorkflowStatus` StrEnum defined: `queued | running | completed | failed | cancelled`
- [ ] `Workflow` Pydantic response model with: `workflow_id`, `status`, `current_stage`, `progress_pct`, `started_at`, `completed_at`, `output_url`, `error`
- [ ] `WorkflowRepository.get(workflow_id: str) -> Workflow | None` queries `ResearchJobRecord` (preferred) OR `ResearchRunRecord` as fallback
- [ ] The 501 route in `src/solstein/api/routers/jobs.py` is replaced or removed — it must not coexist with a working implementation
- [ ] Unit test: given a mock `ResearchJobRecord` at each status, `WorkflowRepository.get()` returns the correct `WorkflowStatus`
- [ ] `ruff check` at 0 errors

---

## Tasks

- [ ] Read `src/solstein/infrastructure/models/research.py:281` — understand `ResearchJobRecord` columns
- [ ] Read `src/solstein/api/routers/research_jobs.py` — understand the existing response model (`ResearchJobResponse`)
- [ ] Decide whether `Workflow` is a new model or an alias/superset of `ResearchJobResponse`
- [ ] Create `src/solstein/domain/workflow.py` with `WorkflowStatus` StrEnum and `Workflow` Pydantic model
- [ ] Create `src/solstein/infrastructure/workflow_repository.py` with `WorkflowRepository.get()`
- [ ] Map `ResearchJobRecord.status → WorkflowStatus` (they likely use the same strings)
- [ ] Write unit tests

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/infrastructure/models/research.py` | 281 | `ResearchJobRecord` — use this for Workflow state |
| `src/solstein/api/routers/jobs.py` | 25 | Returns HTTP 501 — remove or replace |
| `src/solstein/api/routers/research_jobs.py` | 1 | Existing read-only job API to align with |
| `src/solstein/api/main.py` | 218 | Both routers registered on `/jobs` prefix |
