# Import Graph Architecture

STORY-117: Documented import hierarchy enforced by CI.

## Layer Import Rules

```
shared/           -> (nothing — stdlib and third-party only)
domain/           -> shared/
infrastructure/   -> shared/ + domain/
application/      -> domain/ + infrastructure/
api/              -> application/ + shared/
core/             -> shared/ (exception: scoring_utils.py -> domain — tracked for migration)
analytics/        -> domain/ + shared/ + core/
data/             -> domain/ + shared/ + core/ + infrastructure/
connectors/       -> shared/ + domain/
evidence/         -> domain/ + shared/
research/         -> domain/ + analytics/ + data/ + llm/
worker/           -> application/ + infrastructure/
```

## Enforcement

The `shared/` package purity is enforced by `scripts/ci/check_shared_purity.py` which verifies zero imports from any application-level package.

Known exceptions are tracked in the `core/scoring_utils.py` file which imports from `domain.models`. This is scheduled for migration in a future story.

## Principles

1. **shared/ is the foundation**: only stdlib and third-party imports
2. **domain/ defines business types**: models, value objects, interfaces
3. **infrastructure/ implements outbound adapters**: DB, HTTP, cache
4. **application/ orchestrates**: use cases combining domain + infrastructure
5. **api/ presents**: HTTP endpoints calling application services
6. **No circular imports**: enforced by `scripts/ci/detect_import_cycles.py`
