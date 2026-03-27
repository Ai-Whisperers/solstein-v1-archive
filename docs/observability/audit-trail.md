# Data Access Audit Trail

**STORY-086** | EPIC-014 Observability & Telemetry

## Overview

Every authenticated request to a data-returning endpoint generates an append-only audit record. This satisfies compliance requirements for PE/VC intelligence platforms where data access must be fully auditable.

## How It Works

The `AuditMiddleware` is a Starlette middleware that fires **after** the response is generated (so the status code is available) and **after** the `TenantMiddleware` has set `tenant_id` on `request.state`.

Middleware ordering in `main.py`:

```
AuditMiddleware  (added first, executes last = after tenant is set)
TenantMiddleware (added second, executes first = sets tenant_id)
```

## Audit Record Schema

Table: `data_access_audit`

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment primary key |
| tenant_id | String(255) | Tenant from API key |
| user_id | String(255) | Authenticated user ID |
| method | String(10) | HTTP method (GET, POST, etc.) |
| endpoint | String(500) | Request path |
| resource_id | String(255) | Extracted resource ID (if applicable) |
| timestamp | DateTime (TZ) | UTC timestamp |
| status_code | Integer | HTTP response status |
| client_ip | String(45) | Client IP (supports IPv6) |
| user_agent | Text | User-Agent header |

Indexes: `(tenant_id, timestamp)`, `(user_id, timestamp)`, `(endpoint, timestamp)`.

## Excluded Endpoints

The following paths are excluded from auditing (no meaningful user identity):

- `/health`, `/healthz`, `/ready` -- infrastructure probes
- `/metrics`, `/metrics/prometheus` -- monitoring
- `/docs`, `/openapi.json`, `/redoc` -- documentation
- `/auth/*` -- authentication (user not yet identified)
- `/admin/profiling` -- internal profiling

## Security Properties

1. **Append-only**: The model has no `delete()` method. Application code cannot `DELETE` from `data_access_audit`. Cleanup must use a designated admin procedure.

2. **Resilient**: Audit write failures never fail the original request. Failures are logged via `logger.error` for separate alerting.

3. **Complete**: Every authenticated request is audited via middleware, not per-endpoint opt-in. No developer can accidentally skip auditing.

## Retention Policy

Audit records should be retained for a minimum of **7 years** to satisfy financial regulatory requirements. Implement a scheduled cleanup job (with admin authorization) for records older than the retention period. Do not implement automatic deletion without explicit approval.

## Querying Audit Records

```sql
-- Who accessed company data in the last 24 hours?
SELECT tenant_id, user_id, endpoint, timestamp, status_code
FROM data_access_audit
WHERE endpoint LIKE '/api/v1/companies%'
  AND timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- All access by a specific user
SELECT *
FROM data_access_audit
WHERE user_id = 'user-123'
ORDER BY timestamp DESC
LIMIT 100;
```
