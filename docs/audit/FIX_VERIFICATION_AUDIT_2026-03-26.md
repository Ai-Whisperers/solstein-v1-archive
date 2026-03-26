# Fix Verification Audit — 2026-03-26

**Scope:** Re-verify the current branch against a selected set of master-audit issues that were previously claimed fixed or appeared stale in the 2026-03-18 master audit.

**Why this file exists:** The original [18-03-2026_MASTER_AUDIT.md](./18-03-2026_MASTER_AUDIT.md) is still the canonical historical audit artifact and must not be overwritten. As of this verification pass it remains intact at **7,548 lines**.

**Method:** Current source inspection plus focused regression tests. Items are marked `Verified fixed`, `Verified fixed with residual debt`, `Partially fixed`, or `Not revalidated`.

---

## Verified Fixes

| Issue | Audit title | Current status | Why this is considered fixed | Evidence |
|---|---|---|---|---|
| ISSUE-188 | Sync `get_funding_data()` blocks event loop in `funding_refresh.py` | Verified fixed | `FundingRefreshConnector.fetch_facts()` now awaits the async source wrapper instead of calling a sync path. | `src/solstein/infrastructure/connectors/funding_refresh.py` |
| ISSUE-191 | Sync `get_linkedin_data()` blocks event loop | Verified fixed | `LinkedInRefreshConnector.fetch_facts()` now runs the sync lookup via `asyncio.to_thread(...)`. | `src/solstein/infrastructure/connectors/linkedin_refresh.py` |
| ISSUE-194 | Sync `get_stock_data()` blocks event loop | Verified fixed | `GlobalMarketRefreshConnector.fetch_facts()` now uses `asyncio.to_thread(...)`. | `src/solstein/infrastructure/connectors/global_market_refresh.py` |
| ISSUE-197 | Sync `search_company_patents()` blocks event loop | Verified fixed with residual debt | `PatentsRefreshConnector.fetch_facts()` now uses `asyncio.to_thread(...)`. The specific audited file is fixed. A sibling async path still calls the same sync function directly in `adapters/enrichment/patents_unified.py`, so the bug class still exists elsewhere. | `src/solstein/infrastructure/connectors/patents_refresh.py`, `src/solstein/adapters/enrichment/patents_unified.py` |
| ISSUE-199 | Sync `get_news()` blocks event loop | Verified fixed | `NewsRefreshConnector.fetch_facts()` now uses `asyncio.to_thread(...)`. | `src/solstein/infrastructure/connectors/news_refresh.py` |
| ISSUE-200 | No `None` guard on `coverage` before attribute access | Verified fixed | `NewsRefreshConnector.fetch_facts()` now checks `coverage is None` before reading attributes. | `src/solstein/infrastructure/connectors/news_refresh.py` |
| ISSUE-204 | `WebsiteRefreshConnector.fetch_facts()` unconditionally skips every company | Verified fixed | The connector no longer returns early unconditionally. It now resolves websites from the DB and delegates to `fetch_facts_with_websites(...)` when websites exist. | `src/solstein/infrastructure/connectors/website_refresh.py` |
| ISSUE-205 | Sync `scrape_company_website()` blocks event loop | Verified fixed | The connector now awaits the async website source wrapper, which internally delegates blocking scrape work off-thread. | `src/solstein/infrastructure/connectors/website_refresh.py`, `src/solstein/data/sources/web.py` |
| ISSUE-207 | Sync `researcher.research()` blocks event loop | Verified fixed | `YahooFinanceRefreshConnector.fetch_facts()` now wraps `researcher.research` in `asyncio.to_thread(...)`. | `src/solstein/infrastructure/connectors/yahoo_finance_refresh.py` |
| ISSUE-224 | `DataSourceType.WEB_SEARCH` missing | Verified fixed | `DataSourceType.WEB_SEARCH` exists again and regression coverage asserts it directly. | `src/solstein/domain/models.py`, `tests/unit/test_model_construction.py` |
| ISSUE-225 | Missing `Company` import in `deep_analyzer.py` | Verified fixed | `deep_analyzer.py` imports `Company`, and `generate_from_dict()` now constructs and returns a real `DeepAnalysisReport`. | `src/solstein/intelligence/deep_analyzer.py`, `tests/unit/test_audit_regressions_march_2026.py` |
| ISSUE-230 | `source_type="funding"` invalid for `RawDataSource` | Verified fixed | `FundingUnifiedAdapter` now uses `DataSourceType.CRUNCHBASE` instead of an invalid free-form string. | `src/solstein/adapters/enrichment/funding_unified.py`, `tests/unit/test_audit_regressions_march_2026.py` |
| ISSUE-231 | `source_type="web_search"` invalid for `RawDataSource` | Verified fixed | `WebSearchUnifiedAdapter` now uses `DataSourceType.EXA_SEARCH` as its `source_type`. | `src/solstein/adapters/enrichment/web_search_unified.py`, `tests/unit/test_audit_regressions_march_2026.py` |
| ISSUE-232 | `DiscoveryCandidate` constructed with wrong field names | Verified fixed | `PatentsUnifiedAdapter.discover()` now builds `DiscoveryCandidate` with the actual dataclass fields. | `src/solstein/adapters/enrichment/patents_unified.py`, `tests/unit/test_audit_regressions_march_2026.py` |
| ISSUE-265 | `CompanyRecord.ai_data_quality_score` does not exist | Verified fixed | `BusinessMetricsCollector.collect_company_metrics()` now reads `CompanyRecord.ai_score`. | `src/solstein/monitoring/business_metrics.py`, `tests/unit/test_audit_regressions_march_2026.py` |
| ISSUE-266 | `CompanyRecord.enrichment_updated_at` does not exist | Verified fixed | `BusinessMetricsCollector.collect_company_metrics()` now filters on `CompanyRecord.last_updated`. | `src/solstein/monitoring/business_metrics.py`, `tests/unit/test_audit_regressions_march_2026.py` |
| ISSUE-267 | `status="partial_failure"` rejected by batch response schema | Verified fixed after deep verification | The batch route already used `status="partial"` at the top level, but verification exposed a nested schema mismatch: per-item results still emitted `status="failed"`. This pass corrected that to `status="failure"` and added a regression test. | `src/solstein/api/routers/enrichment_batch.py`, `tests/unit/test_audit_regressions_march_2026.py` |

---

## Verification Notes

### 1. Some audit entries marked `Open` are genuinely stale

The master audit still marks several of the issues above as open, but current `HEAD` no longer matches those failure conditions. This is why a second verification artifact is required instead of trusting the status column blindly.

### 2. One issue was only partially fixed before this pass

`ISSUE-267` looked fixed at first glance because the batch response now used `status="partial"`, but runtime verification showed a deeper schema mismatch still existed at the per-result level:

- batch response status: fixed before this pass
- per-result status: still broken before this pass
- current state after this pass: both aligned to schema

### 3. Class-level debt still exists even where the audited file is fixed

The best example is the patents stack:

- the audited refresh connector path is fixed
- the async unified adapter path still calls `search_company_patents(...)` directly without `to_thread(...)`

This means the individual audit issue can be marked fixed for its file, but the broader “blocking sync work inside async code” debt has not been eliminated globally.

### 4. Test harness debt still leaks into verification work

Focused unit regressions now collect more cleanly than before, but route-level imports still pull in heavy config paths. Verifying the batch route required explicit environment variables such as `COMPANIES_HOUSE_API_KEY`. The harness is improved, but not yet fully modular.

---

## Regression Coverage Added Or Reused

The following checks now backstop the verified issues:

- `tests/unit/test_audit_regressions_march_2026.py`
- `tests/unit/test_model_construction.py`

Key coverage added in this pass:

- global market refresh null-safe behavior
- news refresh `None` coverage guard
- website refresh positive path with explicit websites
- unified adapter contract checks for funding, web search, and patents
- business metrics schema-drift regression
- batch enrichment status-schema regression

---

## Commands Run

```bash
wc -l docs/audit/18-03-2026_MASTER_AUDIT.md
uv run python -m py_compile src/solstein/api/routers/enrichment_batch.py tests/unit/test_audit_regressions_march_2026.py
DATABASE__URL=postgresql+asyncpg://user:pass@localhost/test \
SECURITY__SECRET_KEY=test-secret \
GITHUB_TOKEN=test-token \
COMPANIES_HOUSE_API_KEY=test-key \
uv run pytest tests/unit/test_audit_regressions_march_2026.py tests/unit/test_model_construction.py -q
```

Result:

- master audit line count preserved: `7548`
- regression suite: `27 passed`

---

## Next Recommended Audit Step

Reconcile the next stale-open cluster from the master audit in the same format:

1. infrastructure vector/query/transaction issues (`ISSUE-211`, `212`, `214`, `216`, `217`, `218`, `220`)
2. remaining coordinator / agent / dead-path items that may have been removed or superseded
3. duplicated blocking-sync patterns outside the original audited files
