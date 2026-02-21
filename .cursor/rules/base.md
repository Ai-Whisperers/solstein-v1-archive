# Solstein Repository Rules

You are working on the Solstein project, an advanced agentic intelligence platform for Energy Software analysis.

## Core Philosophy
- **Alchemical Transmutation**: We don't just "process" data; we transmute it from lead (raw facts) to gold (actionable intelligence).
- **Deep Transparency**: Every score and classification must be traceable back to its source facts and logic chains.
- **Aura Observability**: Structured, contextual logging is mandatory via the `Aura` layer.

## Technical Standards
- **Asynchronous First**: All I/O operations (DB, API, Agent calls) MUST be `async`.
- **Python**: Use `ruff` for linting and `pytest` for testing. Target 90%+ coverage.
- **Frontend**: Next.js + React. Use the "Sunstone" design system (see `globals.css`).
- **Nomenclature**:
    - High growth -> **Phoenix** 🔥
    - Stable/Neutral -> **Salt** 🧂
    - Risky/Legacy -> **Lead** ⚖️

## Observation Layer (Aura)
- Use `logger.contextualize` for long-running agent tasks.
- Always include `request_id` in API responses and logs.
- Prefix important stage logs with `Aura |`.

## Persistence Layer (Stone)
- All database interactions go through `src/solstein/infrastructure`.
- Models must use `AuditTrailRecord` for any intelligence-gathering event.
