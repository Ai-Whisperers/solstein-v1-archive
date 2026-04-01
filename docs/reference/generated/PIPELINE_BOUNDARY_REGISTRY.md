# Pipeline Boundary Registry

> Auto-generated on 2026-04-01 00:58 UTC by `scripts/ci/generate_pipeline_boundary_registry.py`.
> Do not edit manually.

**Total cross-layer imports**: 390
**Layer pairs with traffic**: 91

## Layer Dependency Matrix

Shows how many imports flow from source (row) to target (column).

| Source \ Target | `_config_timeouts` | `adapters` | `agents` | `analytics` | `api` | `application` | `celery_config` | `celery_config.py` | `config` | `config.py` | `config_template` | `connectors` | `core` | `data` | `domain` | `evidence` | `exceptions` | `exporters` | `extractors` | `infrastructure` | `intelligence` | `llm` | `migrations` | `monitoring` | `observability` | `presentation` | `research` | `review_queue` | `security` | `tenant` | `utils` | `validation` | `worker` | `worker_tasks.py` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `_config_timeouts` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `adapters` | . | . | . | . | . | . | . | . | 4 | . | . | . | . | 14 | 19 | . | . | . | . | 24 | . | . | . | . | . | . | 12 | . | . | . | . | . | . | . |
| `agents` | . | . | . | . | . | . | . | . | 8 | . | . | 8 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `analytics` | . | . | . | . | . | . | . | . | . | . | . | . | 1 | . | 15 | . | . | . | . | 1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `api` | . | . | . | 4 | . | . | 3 | . | 5 | . | . | . | 2 | 13 | 2 | . | 1 | . | . | 21 | . | . | . | 3 | 1 | . | 1 | 1 | . | 1 | . | . | 2 | . |
| `application` | . | 1 | 10 | 1 | 1 | . | . | . | 1 | . | . | . | . | . | 5 | . | . | 1 | . | 2 | . | 1 | . | . | . | . | . | . | . | . | . | . | . | . |
| `celery_config` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `celery_config.py` | . | . | . | . | . | . | . | . | 1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `config` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `config.py` | 1 | . | . | . | . | . | . | . | . | . | 1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | 1 | . | . | . |
| `config_template` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `connectors` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `core` | . | . | . | . | . | . | . | . | 2 | . | . | . | . | . | 1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `data` | . | 1 | . | . | . | 1 | . | . | 9 | . | . | . | 4 | . | 12 | . | . | . | 1 | 3 | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `domain` | . | . | . | 3 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | 1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `evidence` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `exceptions` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `exporters` | . | . | . | 1 | . | . | . | . | 2 | . | . | . | 1 | . | 14 | . | 1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `extractors` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `infrastructure` | . | 12 | . | . | . | . | . | . | 7 | . | . | . | . | 12 | 3 | . | . | . | . | . | . | . | . | . | . | . | 2 | . | . | . | . | . | . | . |
| `intelligence` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | 1 | 1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `llm` | . | . | . | . | . | . | . | . | 4 | . | . | . | . | . | 1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `migrations` | . | . | . | . | . | . | . | . | 1 | . | . | . | . | . | . | . | . | . | . | 1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `monitoring` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | 1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `observability` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `presentation` | . | . | . | 2 | . | . | . | . | . | . | . | . | . | . | 3 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `research` | . | 5 | 4 | 1 | . | . | . | . | 4 | . | . | . | . | 3 | 9 | . | . | 1 | 1 | 2 | . | . | . | . | . | . | . | 1 | . | . | . | . | . | . |
| `review_queue` | . | . | . | . | . | . | . | . | 1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `security` | . | . | . | . | . | . | . | . | 2 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `tenant` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | 9 | . | . | . | . | . | . | . | . | 1 | . | . | . | . | . |
| `utils` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `validation` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | 1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| `worker` | . | . | . | . | . | . | 1 | . | 4 | . | . | . | . | 2 | 1 | . | . | 7 | . | 21 | . | . | . | 1 | . | . | . | . | . | . | 1 | . | . | . |
| `worker_tasks.py` | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | 6 | . |

## Top 20 Boundary Hotspots

Files with the most cross-layer imports (potential coupling risk).

| File | Cross-Layer Imports |
|------|---------------------|
| `infrastructure/unified_registry.py` | 14 |
| `worker/export_tasks.py` | 13 |
| `worker/refresh_tasks.py` | 13 |
| `api/routers/exports_helpers.py` | 12 |
| `adapters/enrichment/_retired/funding_unified.py` | 8 |
| `api/main.py` | 8 |
| `adapters/enrichment/_retired/news_unified.py` | 7 |
| `adapters/enrichment/_retired/web_search_unified.py` | 7 |
| `adapters/enrichment/_retired/website_unified.py` | 7 |
| `api/routers/scoring.py` | 7 |
| `tenant/api_key_service.py` | 6 |
| `worker/base.py` | 6 |
| `worker_tasks.py` | 6 |
| `adapters/enrichment/_retired/linkedin_unified.py` | 5 |
| `adapters/enrichment/_retired/patents_unified.py` | 5 |
| `agents/news_backends.py` | 5 |
| `application/agents/__init__.py` | 5 |
| `application/services/semantic_search_service.py` | 5 |
| `research/pipeline_stages.py` | 5 |
| `adapters/discovery/competitor_json.py` | 4 |
