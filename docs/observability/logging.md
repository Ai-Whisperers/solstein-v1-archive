# Observability: Logging and Correlation IDs

## Correlation IDs

Every inbound HTTP request is assigned a `correlation_id` that propagates through
all log entries produced during that request's lifetime. This makes it possible to
trace a single request across services and log aggregators.

## Context Middleware

The `CorrelationIdMiddleware` (or equivalent Context middleware) intercepts each
incoming request, reads the `X-Correlation-ID` header if present, or generates a
new UUID, and stores it in a request-scoped context variable. All downstream
loggers read from this context variable automatically.

## Request-scoped Storage

The correlation_id is stored in a `contextvars.ContextVar` so it is scoped to the
current request and does not leak across concurrent requests or threads.

## Log Format

Structured log entries include `correlation_id` as a top-level field:

```json
{
  "timestamp": "2026-04-01T00:00:00Z",
  "level": "INFO",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Company scored successfully"
}
```
