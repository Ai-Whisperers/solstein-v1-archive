# Async Export API

STORY-111: Export file generation is handled asynchronously via Celery tasks.
The HTTP request returns immediately with a job ID; the file is generated in the background.

## Endpoints

### POST /api/v1/exports

Create a new export job. Returns `202 Accepted` with a job ID.

**Request body:**
```json
{
  "format": "excel",
  "filters": {
    "industry": "Technology",
    "tenant_id": "uuid"
  }
}
```

**Response (202):**
```json
{
  "job_id": "uuid",
  "status": "queued"
}
```

### GET /api/v1/exports/{job_id}

Poll export job status. Returns current status and download URL when complete.

**Response (200):**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "file_url": "https://storage.example.com/exports/file.xlsx",
  "expires_at": "2026-04-03T00:00:00Z"
}
```

## Database Schema

The `export_jobs` table tracks all export jobs:

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | String | Owning tenant |
| export_format | String | excel, csv, json, markdown, llm |
| status | String | queued, processing, completed, failed |
| file_url | String | Signed download URL (populated on completion) |
| progress_pct | Integer | 0–100 progress indicator |
| created_at | DateTime | Job creation time |
| completed_at | DateTime | Completion time |
| expires_at | DateTime | URL expiry time |
| error_message | String | Error detail on failure |
