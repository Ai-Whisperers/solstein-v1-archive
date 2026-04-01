# UTC Timezone Policy

STORY-120: All datetimes in the Solstein codebase must be timezone-aware UTC.

## Rules

1. **Always use `datetime.now(tz=timezone.utc)`** -- never bare `datetime.now()`.
2. **Never use `datetime.utcnow()`** -- it is deprecated and returns a naive datetime.
3. **Convert external datetimes to UTC at ingestion boundaries** (adapter layer).
4. **PostgreSQL columns use `TIMESTAMP WITH TIME ZONE`** for all datetime fields.

## Canonical Utilities

Use `shared/datetime_utils.py` for all datetime operations:

```python
from solstein.shared.datetime_utils import utc_now, to_utc, parse_iso_to_utc

# Get current time
now = utc_now()

# Convert a naive datetime (assumed UTC)
aware = to_utc(naive_dt)

# Parse an ISO string to UTC
dt = parse_iso_to_utc("2026-03-15T12:00:00+05:00")  # -> 07:00 UTC
```

## Enforcement

- **AST-based CI test**: `test_utc_timezone_policy_story_120.py` scans all source files for bare `datetime.now()` and `datetime.utcnow()` calls.
- **Ruff rules**: DTZ001-DTZ007 can be enabled in `pyproject.toml` for additional static analysis.

## Why UTC Everywhere

Solstein scrapes data from sources in multiple timezones (SEC EDGAR in US/Eastern, Companies House in UK/London, GitHub in UTC). Naive datetimes from different timezone contexts produce incorrect comparisons, wrong freshness calculations, and broken conflict resolution.
