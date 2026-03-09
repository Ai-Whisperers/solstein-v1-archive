# Code Review Checklist

## Exceptions and Reliability

- No bare `except:` blocks.
- No silent `None` returns on unexpected exceptions.
- Exceptions are logged with structured context (`component`, `operation`, `error_type`).
- Retry behavior is bounded and explicit for transient failures.
- Fallback behavior is explicit and covered by tests.

## General

- Tests cover new or changed behavior.
- Configuration and docs are updated when runtime behavior changes.
