# Layer Boundaries and Compatibility Policy

This document defines Solstein's target package boundaries and compatibility rules during cleanup/refactor work.

## Target Layers

- `solstein.domain`
  - Pure business models, value objects, validators, domain rules.
  - Must not import infrastructure or presentation code.
- `solstein.application`
  - Use-cases, orchestration, scoring workflows, application services.
  - Can depend on `domain`.
- `solstein.infrastructure`
  - Databases, repositories, external API clients, adapters.
  - Can depend on `application` and `domain` abstractions.
- `solstein.presentation`
  - API/CLI/web entrypoints and transport-layer concerns.
  - Can depend on `application` and `domain`.

## Dependency Direction

- Allowed (inward):
  - `presentation -> application -> domain`
  - `infrastructure -> application` and `infrastructure -> domain`
- Not allowed (outward):
  - `domain` importing `application/infrastructure/presentation`
  - `application` importing `presentation`

## Compatibility Rules for Moves

When a module is moved:

1. Keep old import path working with a shim module that re-exports public symbols.
2. Prefer thin shims only (`from new.path import X`) with no extra behavior.
3. Keep compatibility shims for at least one minor release cycle unless explicitly retired.
4. If an old path cannot be preserved, document the breaking change in README/changelog.

## Documentation URL Stability

When docs pages move:

1. Update mkdocs navigation to the new canonical path.
2. Keep a redirect/alias strategy for high-traffic pages (or explicit migration note).
3. Avoid deleting historical content; move it under `docs/archive/` and keep it out of primary navigation.

## Practical Rule During Cleanup

- Favor mechanical changes (move + shim + tests) over behavior rewrites.
- Any behavior change discovered during module consolidation must be isolated in a dedicated follow-up task.
