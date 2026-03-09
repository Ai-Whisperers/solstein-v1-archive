# Unified Adapter Migration Guide

## Why This Exists

The unified adapter migration standardizes adapter behavior around a shared refresh-oriented connector pattern while preserving production reliability behaviors (validation, retry policy, and structured error handling).

## Canonical Adapters

Use unified adapters as the canonical import targets.

| Legacy Adapter | Unified Replacement |
|---|---|
| `news.py` | `news_unified.py` |
| `funding.py` | `funding_unified.py` |
| `website.py` | `website_unified.py` |
| `linkedin.py` | `linkedin_unified.py` |
| `patents.py` | `patents_unified.py` |
| `web_search_news.py` | `web_search_unified.py` |

## Import Guidance

- Prefer registry-based construction through `solstein.adapters.registry.build_default_registry`.
- Avoid direct imports of legacy adapter modules in new code.
- For migration work, keep parity tests green before deleting legacy modules.

## Behavioral Parity Checklist

- Input validation before network calls.
- Provider-specific retry behavior.
- Structured error propagation (no silent `None` fallback).
- Cross-source enrichment behavior preserved.

## Historical Context

- STORY-121 restored unified news error handling behavior.
- STORY-122 restored funding wrapper behavior.
- STORY-123 restored website validation behavior.
- STORY-124 governs legacy adapter deletion only after parity verification.
