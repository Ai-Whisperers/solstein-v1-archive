# Exception Handling Standards

> STORY-132 | EPIC-034: Exception Handling Transparency
> This document is prescriptive. Follow it mechanically. When in doubt, choose the pattern
> that produces more diagnostic information, not less.

## Goal

Exceptions must be **visible**, **actionable**, and **contextual**. A system that hides its
failures is not resilient — it is deceptive. Every exception handler in the Solstein codebase
must satisfy three criteria:

1. **Detected**: the exception is caught at the appropriate granularity.
2. **Logged**: structured context is emitted before any fallback or propagation.
3. **Handled**: a deliberate decision is made — propagate, return structured error, or degrade
   with an explicit reason code.

---

## Decision Tree

Follow this tree for every `try/except` block you write or review:

```
Is the exception expected by design?
├── YES: Is the caller able to recover?
│   ├── YES → Return structured result (Pattern A)
│   └── NO  → Log + re-raise domain exception (Pattern B)
└── NO: Is this a transient failure (network, rate-limit, timeout)?
    ├── YES → Bounded retry with backoff (Pattern C)
    │         After max retries → Pattern B (raise)
    └── NO  → Is fallback behaviour expected by product design?
        ├── YES → Log fallback reason + return degraded result (Pattern D)
        └── NO  → Log + raise (Pattern B)
```

**If you cannot decide which pattern applies, use Pattern B (log and raise).** Raising is
always safer than silently returning None.

---

## Allowed Patterns

### Pattern A: Structured Result

Use when the caller is designed to handle partial failure (e.g., batch processing).

```python
from solstein.core.error_taxonomy import ErrorCategory

def fetch_company_data(company_id: str) -> dict:
    try:
        data = adapter.fetch(company_id)
        return {"success": True, "data": data, "error": None, "error_code": None}
    except ConnectionError as e:
        logger.warning(
            "[DataAdapter] Fetch failed",
            component="data_adapter",
            operation="fetch_company",
            entity_id=company_id,
            error_type=type(e).__name__,
            message=str(e),
        )
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "error_code": "EXTERNAL_SERVICE_ERROR",
        }
```

### Pattern B: Log and Raise

Use when the caller should not silently continue. This is the **default pattern**.

```python
from solstein.core.exceptions import ExternalServiceError

def fetch_financials(company_id: str) -> FinancialData:
    try:
        return sec_edgar.get_filings(company_id)
    except requests.Timeout as e:
        logger.error(
            "[SECEdgar] Timeout fetching filings",
            component="sec_edgar",
            operation="get_filings",
            entity_id=company_id,
            error_type="Timeout",
            message=str(e),
        )
        raise ExternalServiceError(
            f"SEC EDGAR timeout for {company_id}", error_code="TIMEOUT_ERROR"
        ) from e
```

### Pattern C: Bounded Retry

Use for transient failures only. Never retry validation or authentication errors.

```python
import asyncio
from solstein.core.error_taxonomy import is_retryable

MAX_RETRIES = 3
BASE_DELAY = 1.0  # seconds

async def fetch_with_retry(url: str, company_id: str) -> dict:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return await http_client.get(url)
        except (ConnectionError, TimeoutError) as e:
            logger.warning(
                "[HTTPClient] Transient failure, retrying",
                component="http_client",
                operation="fetch",
                entity_id=company_id,
                error_type=type(e).__name__,
                attempt=attempt,
                max_retries=MAX_RETRIES,
            )
            if attempt == MAX_RETRIES:
                raise
            await asyncio.sleep(BASE_DELAY * (2 ** (attempt - 1)))
```

### Pattern D: Explicit Degradation

Use **only** when the product design document specifies fallback behaviour. Log the reason.

```python
def enrich_company(company_id: str) -> Company:
    company = load_base_company(company_id)
    try:
        company.financials = fetch_financials(company_id)
    except ExternalServiceError as e:
        logger.warning(
            "[Enrichment] Primary source failed, using cached data",
            component="enrichment",
            operation="fetch_financials",
            entity_id=company_id,
            error_type=type(e).__name__,
            fallback="cached_data",
            reason_code="PRIMARY_SOURCE_UNAVAILABLE",
        )
        company.financials = load_cached_financials(company_id)
        company.data_freshness["financials"] = "stale"
    return company
```

---

## Forbidden Patterns

These are enforced by ruff rules (BLE001, TRY002, TRY003, TRY301) and AST guardrails.

### F1: Bare except

```python
# FORBIDDEN — catches KeyboardInterrupt, SystemExit
except:
    pass
```

### F2: Broad except with silent return

```python
# FORBIDDEN — error concealment
except Exception:
    return None

except Exception as e:
    return {}  # silent fallback without logging
```

### F3: Broad except for control flow

```python
# FORBIDDEN — using exceptions as branching logic
try:
    value = config["key"]
except Exception:
    value = "default"

# CORRECT — use dict.get() or specific KeyError
value = config.get("key", "default")
```

### F4: Exception swallowing

```python
# FORBIDDEN — error annihilation
except Exception as e:
    pass

except Exception:
    continue
```

### F5: String-only error recording

```python
# FORBIDDEN — loses type, traceback, and structured context
error_log.append(str(exc))

# REQUIRED — preserve structured error information
error_log.append({
    "error_type": type(exc).__name__,
    "message": str(exc),
    "traceback": traceback.format_exc(),
    "context": {"company_id": company_id},
})
```

---

## Required Logging Fields

Every exception log entry **must** include these fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `component` | str | Module or class handling the exception | `"sec_edgar_adapter"` |
| `operation` | str | The operation that failed | `"fetch_filings"` |
| `error_type` | str | Exception class name | `"ConnectionError"` |
| `message` | str | Human-readable error description | `"Connection refused"` |
| `entity_id` | str | Company/run/task ID when applicable | `"company_12345"` |

**Optional but recommended**:

| Field | Type | When to Include |
|-------|------|-----------------|
| `attempt` | int | During retries |
| `max_retries` | int | During retries |
| `trace_id` | str | In request-scoped contexts |
| `http_status` | int | For HTTP-related errors |
| `provider` | str | For external service calls |
| `fallback` | str | When degradation pattern is used |
| `reason_code` | str | When degradation pattern is used |
| `latency_s` | float | For timed operations |

---

## Division Safety

All division operations in scoring and analytics **must** use the `safe_div` utility from
`solstein.core.math_utils` (STORY-131). Raw division on values that may be zero or None is
forbidden in any scoring path.

```python
from solstein.core.math_utils import safe_div

# CORRECT
revenue_per_employee = safe_div(revenue, employees, default=None, label="revenue_per_employee")

# FORBIDDEN
revenue_per_employee = revenue / employees  # ZeroDivisionError if employees == 0
```

The `safe_div` function:
- Returns `default` when denominator is zero, None, or NaN.
- Logs a warning with the `label` when a default is returned.
- Distinguishes "calculated as zero" from "could not be calculated" in the return metadata.

---

## Adapter/LLM Exception Guidance

### Adapters (data fetchers, connectors)

- Convert library-specific exceptions into domain exceptions from `solstein.core.exceptions`.
- Log the original exception with full context before re-raising or returning structured result.
- Never let `requests.ConnectionError`, `aiohttp.ClientError`, or similar transport errors
  propagate raw to callers.
- Tag each adapter error with the adapter name for filtering in log aggregation.

### LLM Client

- Classify exceptions by type: `TimeoutError`, `AuthenticationError` (401),
  `RateLimitError` (429), `ParseError`, `ProviderError` (5xx).
- Emit Prometheus metrics: `llm_requests_total{provider, model, status}`,
  `llm_errors_total{provider, error_type}`.
- Signal failures to the circuit breaker / health checker.
- Hash prompt content (SHA-256 of first 500 chars) for correlation — never log raw prompts.

### Research Pipeline

- Every stage must produce a structured stage result with `success`, `error_code`, and
  `error_details` fields.
- Failed stages must not silently produce empty data; the downstream stage must know that
  upstream failed vs. legitimately returned no data.

---

## Linting Enforcement

The following ruff rules are enabled to catch exception handling violations at lint time:

| Rule | Description | Action |
|------|-------------|--------|
| `BLE001` | Blind except (catches `Exception` without re-raising) | Error |
| `TRY002` | Raise vanilla `Exception` | Warning |
| `TRY003` | Long message in exception constructor | Warning |
| `TRY301` | Raise within `try` block (should be outside) | Warning |
| `E722` | Bare `except` | Error |

These rules are configured in `pyproject.toml` under `[tool.ruff.lint]`.

---

## Code Review Checklist

Every PR review **must** verify:

- [ ] No silent failure paths introduced (`except ... return None` without logging).
- [ ] All exception handlers catch specific types, not bare `Exception`.
- [ ] Structured logging fields present: `component`, `operation`, `entity_id`, `error_type`, `message`.
- [ ] Fallback/degradation behavior is explicit, logged with `reason_code`, and tested.
- [ ] Division operations use `safe_div` (scoring/analytics paths).
- [ ] No `str(exc)` as the sole error record — structured context preserved.
- [ ] Retry logic is bounded with configurable max attempts.
- [ ] Domain exceptions used at module boundaries (not raw library exceptions).

---

## Reference

- Error taxonomy: `src/solstein/core/error_taxonomy.py`
- Math utilities: `src/solstein/core/math_utils.py` (STORY-131)
- Project error handling rules: `.claude/rules/error-handling.md`
- Ruff exception rules: `pyproject.toml` `[tool.ruff.lint]`
