# Task 4 Learnings — Async Jobs & Drill-Down Endpoints

## Patterns Discovered
- Async jobs use Celery with graceful fallback (503 if unavailable)
- Job status: SUBMITTED → PENDING → RUNNING → SUCCESS/FAILED
- Celery internally uses "FAILURE" but API maps to "FAILED"
- All drill-down endpoints derive from CompanyAnalysisAuditTrail domain model
- DrillDownService uses shared in-memory dict when no DB (non-persistent mode)
- All drill-down endpoints are GET-only, read from audit trail
- `/fact/{fact_type}` requires `value` as a query param (not just fact_type)
- Contradictions detected via `contradiction_detected` attribute on facts

## Code Reference Points
- async_jobs.py: 277 lines, 4 endpoints, prefix="/async"
- drill_down.py: 226 lines, 10 endpoints, prefix="/drill-down"
- drill_down_service.py: 173 lines, methods map 1:1 to endpoints
- CompanyAnalysisAuditTrail: domain/models.py line 580
