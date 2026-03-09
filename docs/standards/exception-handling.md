# Exception Handling Standards

## Goal

Exceptions must be visible, actionable, and contextual. Do not hide failures by returning `None` without structured logging.

## Decision Tree

1. **Can the caller recover safely?**
   - Yes: return a structured result with explicit error fields.
   - No: log context and raise a domain-specific exception.
2. **Is the failure transient (network/rate limit)?**
   - Yes: apply bounded retry with backoff and emit retry telemetry.
   - No: fail fast and propagate.
3. **Is fallback behavior expected by product design?**
   - Yes: log fallback reason and include reason code in output.
   - No: do not invent fallback silently.

## Allowed Patterns

- **Propagate with context**
  - Catch specific exception types.
  - Log structured context (`component`, `operation`, `entity_id`, `error_type`).
  - Re-raise typed domain error.
- **Structured result**
  - Return explicit status object (`success`, `error_code`, `message`, `metadata`).
- **Bounded retry**
  - Retry only transient failures.
  - Use finite attempts and deterministic delay policy.

## Forbidden Patterns

- Bare `except:`
- `except Exception: return None` without logging
- Empty catch blocks
- Catching broad exceptions only to suppress and continue silently

## Required Logging Fields

- `component`
- `operation`
- `error_type`
- `message`
- `entity_id` (company/run/task id when applicable)
- `attempt` (for retries)

## Adapter/LLM Guidance

- Adapters must convert transport/library errors into structured domain failures.
- LLM client failures must emit provider/model context and retry classification.
- Pipelines must preserve failure reason codes in stage outputs.

## Review Checklist Addendum

- No silent failure paths introduced.
- All exception handlers are specific and logged with required fields.
- Fallback behavior is explicit and tested.
