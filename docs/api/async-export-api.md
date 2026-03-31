# Async Export API

**STORY-111** | EPIC-030 Export Pipeline Modernization

## Overview

Exports are generated asynchronously via Celery tasks. The API returns a job ID immediately (202 Accepted) and the export file is generated in the background on the `export` queue. Clients poll for status and receive a download URL when the export completes.

## Endpoints

### POST `/api/v1/exports`

Create a new export job.

**Request Body:**

```json
{
  "format": "excel",
  "company_id": "optional-company-id",
  "industry": "optional-industry-filter"
}
```

**Supported formats:** `excel`, `csv`, `json`, `markdown`, `llm`

**Response (202 Accepted):**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "format": "excel",
  "file_url": null,
  "error_message": null,
  "created_at": null,
  "completed_at": null
}
```

### GET `/api/v1/exports/{job_id}`

Get the status of an export job.

**Response (200 OK) — queued/processing:**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "format": "excel",
  "file_url": null,
  "error_message": null,
  "created_at": "2026-03-27T10:00:00+00:00",
  "completed_at": null
}
```

**Response (200 OK) — completed:**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "format": "excel",
  "file_url": "/data/output/exports/export_all_20260327_100000.xlsx",
  "error_message": null,
  "created_at": "2026-03-27T10:00:00+00:00",
  "completed_at": "2026-03-27T10:00:45+00:00"
}
```

## Architecture

```
Client                    API Server              Celery Worker
  |                           |                       |
  |  POST /api/v1/exports     |                       |
  |-------------------------->|                       |
  |  202 {job_id, queued}     |                       |
  |<--------------------------|                       |
  |                           |  generate_export()    |
  |                           |---------------------->|
  |                           |                       | fetch companies
  |  GET /exports/{job_id}    |                       | run exporter
  |-------------------------->|                       | write file
  |  200 {processing}         |                       |
  |<--------------------------|                       |
  |                           |                       | update DB
  |  GET /exports/{job_id}    |                       |
  |-------------------------->|                       |
  |  200 {completed, url}     |                       |
  |<--------------------------|                       |
```

## Database Schema

Table: `export_jobs`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Job identifier |
| tenant_id | String(255) | Tenant that owns the export |
| company_id | String(255) | Optional company filter |
| format | String(50) | Export format |
| status | String(50) | queued, processing, completed, failed |
| file_url | Text | File path or signed URL when complete |
| error_message | Text | Error details when failed |
| retry_count | Integer | Number of retries attempted |
| created_at | DateTime (TZ) | Job creation timestamp |
| completed_at | DateTime (TZ) | Completion timestamp |

Indexes: `(tenant_id, created_at)`, `(status, created_at)`.

## Celery Configuration

The export task runs on a dedicated `export` queue with higher time limits than the default refresh tasks:

- **Default time limit:** 150 s hard / 120 s soft (covers LLM generation)
- **Queue:** `export`
- **Max retries:** 2 (with 10 s delay between retries)
- **DLQ integration:** Failed exports are persisted to the `failed_tasks` DLQ table

### Running the export worker

```bash
celery -A solstein.celery_config worker --queues=export --concurrency=2
```

## Idempotency

Re-triggering the same `export_job_id` is safe. The Celery task checks the current job status before processing:

- If `completed`: skips (logs warning)
- If `processing`: skips (logs warning)
- If `queued`: proceeds with export

## Error Handling

Export failures follow the EPIC-025 reliability guarantees:

1. Task retries up to 2 times with 10 s backoff
2. After max retries, the job is marked `failed` with an error message
3. The failure is persisted to the PostgreSQL DLQ (STORY-088)
4. Audit failure never fails the original request
