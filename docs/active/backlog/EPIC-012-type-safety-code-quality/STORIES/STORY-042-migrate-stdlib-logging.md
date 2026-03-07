# STORY-042: Migrate All Modules from stdlib logging to loguru

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | MEDIUM |
| Epic | [EPIC-012: Type Safety & Code Quality](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict
> At least 10 files import Python's stdlib `logging` module (`import logging` or `logging.getLogger(...)`) instead of the project-standard `loguru`. Structured log fields added via loguru's `bind()` pattern are absent in stdlib-using modules. Log queries in production will return incomplete results for any event originating in these modules.

## Problem Statement
Mixed logging backends produce inconsistent log output. loguru log entries include structured fields (correlation IDs, user context, timing). stdlib `logging` entries do not. A structured log query for `request_id=abc123` will miss events from any module using stdlib. This is not a style preference — it is a data completeness issue in the observability pipeline.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Observability** | Structured log queries return incomplete results — events from stdlib-logging modules are invisible to field-based queries |
| **Debugging** | Incidents spanning stdlib-logging modules lack the context present in loguru modules — correlation IDs, timing, and structured data are absent |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| All files containing `import logging` | Modify | Run `grep -rn "import logging" src/solstein/` for the definitive list. Minimum 10 files. |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: Every module must use loguru for all logging — `from loguru import logger`
- **REQ-2**: No `import logging`, `logging.getLogger()`, or stdlib `Logger` type may appear in any module
- **REQ-3**: Log call sites must be updated to use loguru's bound context pattern where structured fields are available
- **REQ-4**: The migration must not change the log level or message text of any existing log call — this is a backend swap, not a log content change

## Acceptance Criteria
- [ ] `grep -rn "import logging" src/` returns zero results
- [ ] `grep -rn "logging.getLogger" src/` returns zero results
- [ ] All log output uses consistent loguru format
- [ ] No log message text or level was changed during the migration

## Definition of Done

**Tests Required:**
- [ ] Grep confirming absence of stdlib logging imports across entire `src/` tree
- [ ] Integration test: log output from migrated modules includes structured fields when bound context is present

**Documentation Required:**
- [ ] Contributing guide updated to specify loguru as the only permitted logging library

**Code Review Gate:**
- [ ] Reviewer confirms no stdlib logging imports remain
- [ ] Reviewer confirms log levels and message text are preserved

## Notes
This story has no dependencies and can be started immediately. It is a prerequisite for STORY-049 (correlation IDs), which requires a consistent logging backend to propagate request context. The migration is mechanical — each file requires replacing `import logging` with `from loguru import logger` and updating call sites from `self.logger.info(...)` to `logger.info(...)`. The risk is low but the surface area is broad.
