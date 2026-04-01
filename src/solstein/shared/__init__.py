"""Shared utilities package — zero imports from application layers.

STORY-117: This package is the lowest layer in the import hierarchy.
It MUST NOT import from: api, application, domain, analytics, infrastructure,
research, intelligence, data, connectors, evidence, exporters, extractors,
validation, worker, or any other application-level package.

Import graph:
    shared/ -> (nothing — standard library and third-party only)
    domain/ -> shared/
    infrastructure/ -> shared/ + domain/
    application/ -> domain/ + infrastructure/
    api/ -> application/ + shared/
"""
