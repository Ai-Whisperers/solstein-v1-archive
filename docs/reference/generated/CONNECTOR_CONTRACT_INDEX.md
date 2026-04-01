# Connector Contract Surface Index

> Auto-generated on 2026-04-01 00:58 UTC by `scripts/ci/generate_connector_contract_index.py`.
> Do not edit manually.

**Total connector classes**: 129
**Total public methods**: 445
**Async-capable connectors**: 87

## adapters/ (8 classes)

### `BaseDataSourceAdapter`

- **File**: `adapters/base.py:25`
- **Bases**: ABC
- **Public methods**: 9

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `source_type` | no | - |
| `discover` | no | market, seed_company, max_results, extra_keywords |
| `enrich` | no | company_id, company_name, ticker, website |
| `refresh` | no | company_ids, start_date, end_date |
| `get_confidence` | no | - |
| `get_authority` | no | - |
| `supports_incremental` | no | - |
| `is_healthy` | no | - |

### `DiscoverySource`

- **File**: `adapters/protocols.py:29`
- **Bases**: Protocol
- **Public methods**: 2

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `discover` | no | market, seed_company, max_results, extra_keywords |

### `EnrichmentSource`

- **File**: `adapters/protocols.py:55`
- **Bases**: Protocol
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `source_type` | no | - |
| `enrich` | no | company_id, company_name, ticker, website |

### `FactAggregator`

- **File**: `adapters/protocols.py:91`
- **Bases**: Protocol
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `aggregate` | no | company_id, raw_record |

### `InstrumentedDiscoverySource`

- **File**: `adapters/instrumented.py:105`
- **Bases**: none
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `health_records` | no | - |
| `discover` | no | market, seed_company, max_results, extra_keywords |

### `InstrumentedEnrichmentSource`

- **File**: `adapters/instrumented.py:37`
- **Bases**: none
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `source_type` | no | - |
| `health_records` | no | - |
| `enrich` | no | company_id, company_name, ticker, website |

### `SourceRegistry`

- **File**: `adapters/registry.py:27`
- **Bases**: none
- **Public methods**: 7

| Method | Async | Args |
|--------|-------|------|
| `register_discovery` | no | source |
| `register_enrichment` | no | source |
| `register_unified` | no | source |
| `discovery_sources` | no | - |
| `enrichment_sources` | no | - |
| `unified_sources` | no | - |
| `all_enrichment_sources` | no | - |

### `UnifiedDataSource`

- **File**: `adapters/protocols.py:110`
- **Bases**: Protocol
- **Public methods**: 9

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `source_type` | no | - |
| `discover` | no | market, seed_company, max_results, extra_keywords |
| `enrich` | no | company_id, company_name, ticker, website |
| `refresh` | no | company_ids, start_date, end_date |
| `get_confidence` | no | - |
| `get_authority` | no | - |
| `supports_incremental` | no | - |
| `supports_discovery` | no | - |

## adapters/discovery/ (3 classes)

### `CompetitorJsonSource`

- **File**: `adapters/discovery/competitor_json.py:20`
- **Bases**: none
- **Public methods**: 9

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `source_type` | no | - |
| `discover` | no | market, seed_company, max_results, extra_keywords |
| `enrich` | no | company_id, company_name, ticker, website |
| `refresh` | no | company_ids, start_date, end_date |
| `get_confidence` | no | - |
| `get_authority` | no | - |
| `supports_incremental` | no | - |
| `supports_discovery` | no | - |

### `StaticCatalogSource`

- **File**: `adapters/discovery/static_catalog.py:21`
- **Bases**: none
- **Public methods**: 9

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `source_type` | no | - |
| `discover` | no | market, seed_company, max_results, extra_keywords |
| `enrich` | no | company_id, company_name, ticker, website |
| `refresh` | no | company_ids, start_date, end_date |
| `get_confidence` | no | - |
| `get_authority` | no | - |
| `supports_incremental` | no | - |
| `supports_discovery` | no | - |

### `WebSearchDiscoverySource`

- **File**: `adapters/discovery/web_search.py:13`
- **Bases**: none
- **Public methods**: 2

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `discover` | no | market, seed_company, max_results, extra_keywords |

## adapters/enrichment/ (8 classes)

### `FundingEnrichment`

- **File**: `adapters/enrichment/funding.py:14`
- **Bases**: none
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `source_type` | no | - |
| `enrich` | no | company_id, company_name, ticker, website |

### `GlobalMarketEnrichment`

- **File**: `adapters/enrichment/global_market.py:15`
- **Bases**: none
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `source_type` | no | - |
| `enrich` | no | company_id, company_name, ticker, website |

### `LinkedInEnrichment`

- **File**: `adapters/enrichment/linkedin.py:15`
- **Bases**: none
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `source_type` | no | - |
| `enrich` | no | company_id, company_name, ticker, website |

### `NewsEnrichment`

- **File**: `adapters/enrichment/news.py:14`
- **Bases**: none
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `source_type` | no | - |
| `enrich` | no | company_id, company_name, ticker, website |

### `PatentEnrichment`

- **File**: `adapters/enrichment/patents.py:25`
- **Bases**: none
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `source_type` | no | - |
| `enrich` | no | company_id, company_name, ticker, website |

### `WebSearchNewsEnrichment`

- **File**: `adapters/enrichment/web_search_news.py:15`
- **Bases**: none
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `source_type` | no | - |
| `enrich` | no | company_id, company_name, ticker, website |

### `WebsiteEnrichment`

- **File**: `adapters/enrichment/website.py:14`
- **Bases**: none
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `source_type` | no | - |
| `enrich` | no | company_id, company_name, ticker, website |

### `YahooFinanceEnrichment`

- **File**: `adapters/enrichment/yahoo_finance.py:15`
- **Bases**: none
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `source_name` | no | - |
| `source_type` | no | - |
| `enrich` | no | company_id, company_name, ticker, website |

## adapters/enrichment/_retired/ (6 classes)

### `FundingUnifiedAdapter` (async)

- **File**: `adapters/enrichment/_retired/funding_unified.py:30`
- **Bases**: BaseRefreshConnector
- **Public methods**: 7

| Method | Async | Args |
|--------|-------|------|
| `discover` | no | market, seed_company, max_results, extra_keywords |
| `enrich` | no | company_id, company_name, ticker, website |
| `fetch_facts` | yes | company_ids, start_date, end_date |
| `get_confidence` | no | - |
| `get_authority` | no | - |
| `supports_incremental` | no | - |
| `supports_discovery` | no | - |

### `LinkedInUnifiedAdapter` (async)

- **File**: `adapters/enrichment/_retired/linkedin_unified.py:22`
- **Bases**: BaseRefreshConnector
- **Public methods**: 7

| Method | Async | Args |
|--------|-------|------|
| `discover` | no | market, seed_company, max_results, extra_keywords |
| `enrich` | no | company_id, company_name, ticker, website |
| `fetch_facts` | yes | company_ids, start_date, end_date |
| `get_confidence` | no | - |
| `get_authority` | no | - |
| `supports_incremental` | no | - |
| `supports_discovery` | no | - |

### `NewsUnifiedAdapter` (async)

- **File**: `adapters/enrichment/_retired/news_unified.py:53`
- **Bases**: BaseRefreshConnector
- **Public methods**: 7

| Method | Async | Args |
|--------|-------|------|
| `discover` | no | market, seed_company, max_results, extra_keywords |
| `enrich` | no | company_id, company_name, ticker, website |
| `fetch_facts` | yes | company_ids, start_date, end_date |
| `get_confidence` | no | - |
| `get_authority` | no | - |
| `supports_incremental` | no | - |
| `supports_discovery` | no | - |

### `PatentsUnifiedAdapter` (async)

- **File**: `adapters/enrichment/_retired/patents_unified.py:25`
- **Bases**: BaseRefreshConnector
- **Public methods**: 7

| Method | Async | Args |
|--------|-------|------|
| `discover` | no | market, seed_company, max_results, extra_keywords |
| `enrich` | no | company_id, company_name, ticker, website |
| `fetch_facts` | yes | company_ids, start_date, end_date |
| `get_confidence` | no | - |
| `get_authority` | no | - |
| `supports_incremental` | no | - |
| `supports_discovery` | no | - |

### `WebSearchUnifiedAdapter` (async)

- **File**: `adapters/enrichment/_retired/web_search_unified.py:31`
- **Bases**: BaseRefreshConnector
- **Public methods**: 7

| Method | Async | Args |
|--------|-------|------|
| `discover` | no | market, seed_company, max_results, extra_keywords |
| `enrich` | no | company_id, company_name, ticker, website |
| `fetch_facts` | yes | company_ids, start_date, end_date |
| `get_confidence` | no | - |
| `get_authority` | no | - |
| `supports_incremental` | no | - |
| `supports_discovery` | no | - |

### `WebsiteUnifiedAdapter` (async)

- **File**: `adapters/enrichment/_retired/website_unified.py:29`
- **Bases**: BaseRefreshConnector
- **Public methods**: 7

| Method | Async | Args |
|--------|-------|------|
| `discover` | no | market, seed_company, max_results, extra_keywords |
| `enrich` | no | company_id, company_name, ticker, website |
| `fetch_facts` | yes | company_ids, start_date, end_date |
| `get_confidence` | no | - |
| `get_authority` | no | - |
| `supports_incremental` | no | - |
| `supports_discovery` | no | - |

## agents/ (12 classes)

### `BaseDataGatheringAgent` (async)

- **File**: `agents/base_agent.py:29`
- **Bases**: ABC
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `gather` | yes | company_name, context |
| `log_info` | no | message |
| `log_warning` | no | message |
| `log_error` | no | message |

### `CircuitBreaker`

- **File**: `agents/resilience.py:119`
- **Bases**: none
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `can_execute` | no | - |
| `record_success` | no | - |
| `record_failure` | no | - |
| `get_state` | no | - |

### `CompaniesHouseAgent` (async)

- **File**: `agents/companies_house_agent.py:21`
- **Bases**: BaseDataGatheringAgent
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `gather` | yes | company_name, context |

### `ExponentialBackoff`

- **File**: `agents/resilience.py:63`
- **Bases**: none
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `get_delay` | no | attempt |

### `FinancialBackendDispatcher` (async)

- **File**: `agents/financial_backends.py:114`
- **Bases**: none
- **Public methods**: 2

| Method | Async | Args |
|--------|-------|------|
| `search` | yes | ticker |
| `get_health_status` | no | - |

### `GitHubAgent` (async)

- **File**: `agents/github_agent.py:26`
- **Bases**: BaseDataGatheringAgent
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `gather` | yes | company_name, context |

### `NewsBackendDispatcher` (async)

- **File**: `agents/news_backends.py:29`
- **Bases**: none
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `search` | yes | query |

### `SearchBackendDispatcher` (async)

- **File**: `agents/search_backends.py:28`
- **Bases**: none
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `search` | yes | query |

### `SeedMarkdownAgent` (async)

- **File**: `agents/seed_markdown_agent.py:13`
- **Bases**: BaseDataGatheringAgent
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `gather` | yes | company_name, context |

### `SourceHealthStatus`

- **File**: `agents/financial_backends.py:44`
- **Bases**: none
- **Public methods**: 2

| Method | Async | Args |
|--------|-------|------|
| `record_success` | no | - |
| `record_failure` | no | reason |

### `WebSearchAgent` (async)

- **File**: `agents/web_search_agent.py:27`
- **Bases**: BaseDataGatheringAgent
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `gather` | yes | company_name, context |

### `WebsiteAgent` (async)

- **File**: `agents/website_agent.py:19`
- **Bases**: BaseDataGatheringAgent
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `gather` | yes | company_name, context |

## agents/github/ (7 classes)

### `AISignalAnalyzer`

- **File**: `agents/github/analyzers.py:95`
- **Bases**: none
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `analyze` | no | repos |

### `DependencyAnalyzer` (async)

- **File**: `agents/github/analyzers.py:136`
- **Bases**: none
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `analyze` | yes | org_name, repos |

### `GitHubClient` (async)

- **File**: `agents/github/client.py:20`
- **Bases**: none
- **Public methods**: 2

| Method | Async | Args |
|--------|-------|------|
| `get` | yes | url |
| `fetch_file` | yes | org, repo, path |

### `GitHubOrgSearcher` (async)

- **File**: `agents/github/search.py:15`
- **Bases**: none
- **Public methods**: 2

| Method | Async | Args |
|--------|-------|------|
| `search` | yes | company_name |
| `fetch_repos` | yes | org_name, max_repos |

### `GitHubRepo`

- **File**: `agents/github/models.py:10`
- **Bases**: none
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `from_api` | no | cls, data |

### `TechStackAnalyzer`

- **File**: `agents/github/analyzers.py:17`
- **Bases**: none
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `analyze` | no | repos |

### `VelocityAnalyzer`

- **File**: `agents/github/analyzers.py:74`
- **Bases**: none
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `analyze` | no | org_name, repos |

## connectors/ (2 classes)

### `BaseConnector` (async)

- **File**: `connectors/base.py:48`
- **Bases**: ABC
- **Public methods**: 5

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |
| `close` | yes | - |

### `ConnectorRegistry` (async)

- **File**: `connectors/registry.py:42`
- **Bases**: none
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `register` | no | name, connector |
| `get` | no | name |
| `list_connectors` | no | - |
| `close_all` | yes | - |

## connectors/academic/ (3 classes)

### `ArXivConnector` (async)

- **File**: `connectors/academic/__init__.py:177`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `ArxivConnector` (async)

- **File**: `connectors/academic/arxiv.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `SemanticScholarConnector` (async)

- **File**: `connectors/academic/__init__.py:23`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

## connectors/financial/ (11 classes)

### `AlphaVantageConnector` (async)

- **File**: `connectors/financial/__init__.py:120`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `AngelListConnector` (async)

- **File**: `connectors/financial/angellist.py:11`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `BetaListConnector` (async)

- **File**: `connectors/financial/betalist.py:11`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `CrunchbaseConnector` (async)

- **File**: `connectors/financial/crunchbase.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `F6SConnector` (async)

- **File**: `connectors/financial/f6s.py:11`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `OpenCorporatesConnector` (async)

- **File**: `connectors/financial/opencorporates.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `OpenCorporatesConnectorLegacy` (async)

- **File**: `connectors/financial/extra.py:71`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `SECEdgarConnector` (async)

- **File**: `connectors/financial/extra.py:20`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `SECEdgarConnector` (async)

- **File**: `connectors/financial/sec_edgar.py:13`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `YahooFinanceConnector` (async)

- **File**: `connectors/financial/__init__.py:24`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `YahooFinanceConnector` (async)

- **File**: `connectors/financial/yahoo_finance.py:13`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

## connectors/government/ (5 classes)

### `DNSConnector` (async)

- **File**: `connectors/government/dns.py:12`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `PatentsViewConnector` (async)

- **File**: `connectors/government/patentsview.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `USAspendingConnector` (async)

- **File**: `connectors/government/usaspending.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `WHOISConnector` (async)

- **File**: `connectors/government/whois.py:11`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `WaybackMachineConnector` (async)

- **File**: `connectors/government/wayback.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

## connectors/news/ (8 classes)

### `GDELTArticle`

- **File**: `connectors/news/gdelt.py:30`
- **Bases**: none
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `to_dict` | no | - |

### `GDELTConnector` (async)

- **File**: `connectors/news/gdelt.py:56`
- **Bases**: BaseConnector
- **Public methods**: 5

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |
| `normalize_to_article` | no | raw_data |

### `HackerNewsConnector` (async)

- **File**: `connectors/news/__init__.py:22`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `HackerNewsConnector` (async)

- **File**: `connectors/news/hacker_news.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `NewsAPIConnector` (async)

- **File**: `connectors/news/__init__.py:140`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `NewsAPIConnector` (async)

- **File**: `connectors/news/newsapi.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `RSSFeedConnector` (async)

- **File**: `connectors/news/__init__.py:263`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `RSSFeedConnector` (async)

- **File**: `connectors/news/rss.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

## connectors/product/ (13 classes)

### `AppStoreConnector` (async)

- **File**: `connectors/product/appstore.py:12`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `BitbucketConnector` (async)

- **File**: `connectors/product/bitbucket.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `CapterraConnector` (async)

- **File**: `connectors/product/capterra.py:11`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `DockerHubConnector` (async)

- **File**: `connectors/product/dockerhub.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `G2Connector` (async)

- **File**: `connectors/product/g2.py:13`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `GitHubConnector` (async)

- **File**: `connectors/product/github.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `GitLabConnector` (async)

- **File**: `connectors/product/gitlab.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `GooglePlayConnector` (async)

- **File**: `connectors/product/googleplay.py:11`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `MavenCentralConnector` (async)

- **File**: `connectors/product/maven.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `NPMConnector` (async)

- **File**: `connectors/product/npm.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `ProductHuntConnector` (async)

- **File**: `connectors/product/producthunt.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `PyPIConnector` (async)

- **File**: `connectors/product/pypi.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `StackOverflowConnector` (async)

- **File**: `connectors/product/stackoverflow.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

## connectors/search/ (2 classes)

### `SearXNGConnector` (async)

- **File**: `connectors/search/searxng.py:50`
- **Bases**: BaseConnector
- **Public methods**: 5

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |
| `normalize_to_search_result` | no | raw_data |

### `SearchResult`

- **File**: `connectors/search/searxng.py:28`
- **Bases**: none
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `to_dict` | no | - |

## connectors/social/ (7 classes)

### `GlassdoorConnector` (async)

- **File**: `connectors/social/glassdoor.py:11`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `LinkedInConnector` (async)

- **File**: `connectors/social/linkedin.py:11`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `PodcastIndexConnector` (async)

- **File**: `connectors/social/podcastindex.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `RedditConnector` (async)

- **File**: `connectors/social/reddit.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `TrustpilotConnector` (async)

- **File**: `connectors/social/trustpilot.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `TwitterConnector` (async)

- **File**: `connectors/social/twitter.py:14`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

### `YouTubeConnector` (async)

- **File**: `connectors/social/youtube.py:12`
- **Bases**: BaseConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `connect` | yes | - |
| `search` | yes | query |
| `get_by_id` | yes | entity_id |
| `normalize` | no | raw_data |

## data/connectors/ (10 classes)

### `CompaniesHouseConnector`

- **File**: `data/connectors/companies_house_connector.py:23`
- **Bases**: none
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `search_company_by_name` | no | company_name |
| `fetch_company_details` | no | company_number |
| `get_company_metrics` | no | company_number |

### `ConnectorResponse`

- **File**: `data/connectors/contracts.py:19`
- **Bases**: ?
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `success` | no | request, payload, metadata |
| `degraded` | no | request, payload, error, metadata |
| `failure` | no | request, error, metadata |

### `ConnectorRuntime` (async)

- **File**: `data/connectors/runtime.py:19`
- **Bases**: none
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `run` | yes | - |

### `FilingProtocol`

- **File**: `data/connectors/sec_edgar_connector.py:26`
- **Bases**: Protocol
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `obj` | no | - |

### `FinancialsProtocol`

- **File**: `data/connectors/sec_edgar_connector.py:40`
- **Bases**: Protocol
- **Public methods**: 2

| Method | Async | Args |
|--------|-------|------|
| `income_statement` | no | - |
| `balance_sheet` | no | - |

### `GitHubConnector` (async)

- **File**: `data/connectors/github_connector.py:23`
- **Bases**: none
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `get_user_repositories` | yes | username, per_page |
| `get_recent_commits` | yes | username, per_page |
| `get_repository_activity` | yes | username, per_page |

### `IdentifierLookupService` (async)

- **File**: `data/connectors/lookup_service.py:33`
- **Bases**: none
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `available_strategies` | no | - |
| `resolve_identifiers` | yes | company_name, headquarters, use_cache |
| `resolve_identifiers_enveloped` | yes | company_name, headquarters, use_cache |
| `clear_cache` | no | - |

### `NewsSignalDetector` (async)

- **File**: `data/connectors/news_signal_detector.py:44`
- **Bases**: none
- **Public methods**: 7

| Method | Async | Args |
|--------|-------|------|
| `detect_signals` | yes | company_name, signal_types |
| `detect_signals_enveloped` | yes | company_name, signal_types |
| `detect_funding_signal` | yes | company_name |
| `detect_partnership_signal` | yes | company_name |
| `detect_key_hire_signal` | yes | company_name |
| `get_rate_limit_status` | no | - |
| `clear_seen_signals` | no | - |

### `SECEdgarConnector`

- **File**: `data/connectors/sec_edgar_connector.py:53`
- **Bases**: none
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `fetch_filing` | no | ticker, year, form_type |

### `StatementProtocol`

- **File**: `data/connectors/sec_edgar_connector.py:35`
- **Bases**: Protocol
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `to_dataframe` | no | - |

## data/connectors/lookup_strategies/ (4 classes)

### `DuckDuckGoStrategy` (async)

- **File**: `data/connectors/lookup_strategies/duckduckgo.py:16`
- **Bases**: LookupStrategy
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `name` | no | - |
| `is_available` | no | - |
| `lookup` | yes | company_name |

### `LookupStrategy` (async)

- **File**: `data/connectors/lookup_strategies/base.py:10`
- **Bases**: ABC
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `name` | no | - |
| `is_available` | no | - |
| `lookup` | yes | company_name |

### `OpenCorporatesStrategy` (async)

- **File**: `data/connectors/lookup_strategies/opencorporates.py:16`
- **Bases**: LookupStrategy
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `name` | no | - |
| `is_available` | no | - |
| `lookup` | yes | company_name |

### `OpenFIGIStrategy` (async)

- **File**: `data/connectors/lookup_strategies/openfigi.py:17`
- **Bases**: LookupStrategy
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `name` | no | - |
| `is_available` | no | - |
| `lookup` | yes | company_name |

## data/connectors/signal_detectors/ (4 classes)

### `FundingSignalDetector`

- **File**: `data/connectors/signal_detectors/funding.py:12`
- **Bases**: SignalDetector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `signal_type` | no | - |
| `confidence` | no | - |
| `patterns` | no | - |
| `detect` | no | article, company_name |

### `KeyHireSignalDetector`

- **File**: `data/connectors/signal_detectors/key_hire.py:12`
- **Bases**: SignalDetector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `signal_type` | no | - |
| `confidence` | no | - |
| `patterns` | no | - |
| `detect` | no | article, company_name |

### `PartnershipSignalDetector`

- **File**: `data/connectors/signal_detectors/partnership.py:12`
- **Bases**: SignalDetector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `signal_type` | no | - |
| `confidence` | no | - |
| `patterns` | no | - |
| `detect` | no | article, company_name |

### `SignalDetector`

- **File**: `data/connectors/signal_detectors/base.py:25`
- **Bases**: ABC
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `signal_type` | no | - |
| `confidence` | no | - |
| `patterns` | no | - |
| `detect` | no | article, company_name |

## data_sources/ (2 classes)

### `CommunityPrioritizer`

- **File**: `data_sources/community_prioritization.py:42`
- **Bases**: none
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `rank` | no | suggestions, votes |

### `OpenClawEvaluator`

- **File**: `data_sources/openclaw_evaluator.py:25`
- **Bases**: none
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `evaluate` | no | api |
| `rank_apis` | no | apis |
| `top_candidates` | no | apis, limit, min_score |

## data_sources/quality/ (2 classes)

### `QualityScorer`

- **File**: `data_sources/quality/models.py:24`
- **Bases**: none
- **Public methods**: 2

| Method | Async | Args |
|--------|-------|------|
| `calculate_overall` | no | scores |
| `with_computed_overall` | no | - |

### `ReliabilityMonitor`

- **File**: `data_sources/quality/reliability_monitor.py:20`
- **Bases**: none
- **Public methods**: 2

| Method | Async | Args |
|--------|-------|------|
| `record_request` | no | - |
| `snapshot` | no | - |

## infrastructure/connectors/ (12 classes)

### `CompaniesHouseRefreshConnector` (async)

- **File**: `infrastructure/connectors/companies_house_refresh.py:12`
- **Bases**: BaseRefreshConnector
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `fetch_facts` | yes | company_ids, start_date, end_date |

### `FundingRefreshConnector` (async)

- **File**: `infrastructure/connectors/funding_refresh.py:17`
- **Bases**: BaseRefreshConnector
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `fetch_facts` | yes | company_ids, start_date, end_date |
| `get_authority` | no | - |
| `supports_incremental` | no | - |

### `GitHubRefreshConnector` (async)

- **File**: `infrastructure/connectors/github_refresh.py:12`
- **Bases**: BaseRefreshConnector
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `fetch_facts` | yes | company_ids, start_date, end_date |

### `GlobalMarketRefreshConnector` (async)

- **File**: `infrastructure/connectors/global_market_refresh.py:18`
- **Bases**: BaseRefreshConnector
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `fetch_facts` | yes | company_ids, start_date, end_date |
| `get_authority` | no | - |
| `supports_incremental` | no | - |

### `LinkedInRefreshConnector` (async)

- **File**: `infrastructure/connectors/linkedin_refresh.py:18`
- **Bases**: BaseRefreshConnector
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `fetch_facts` | yes | company_ids, start_date, end_date |
| `get_authority` | no | - |
| `supports_incremental` | no | - |

### `NewsRefreshConnector` (async)

- **File**: `infrastructure/connectors/news_refresh.py:18`
- **Bases**: BaseRefreshConnector
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `fetch_facts` | yes | company_ids, start_date, end_date |
| `get_authority` | no | - |
| `supports_incremental` | no | - |

### `NewsSignalRefreshConnector` (async)

- **File**: `infrastructure/connectors/news_signal_refresh.py:13`
- **Bases**: BaseRefreshConnector
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `fetch_facts` | yes | company_ids, start_date, end_date |

### `PatentsRefreshConnector` (async)

- **File**: `infrastructure/connectors/patents_refresh.py:18`
- **Bases**: BaseRefreshConnector
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `fetch_facts` | yes | company_ids, start_date, end_date |
| `get_authority` | no | - |
| `supports_incremental` | no | - |

### `SECEDGARRefreshConnector` (async)

- **File**: `infrastructure/connectors/sec_edgar_refresh.py:12`
- **Bases**: BaseRefreshConnector
- **Public methods**: 1

| Method | Async | Args |
|--------|-------|------|
| `fetch_facts` | yes | company_ids, start_date, end_date |

### `WebSearchRefreshConnector` (async)

- **File**: `infrastructure/connectors/web_search_refresh.py:17`
- **Bases**: BaseRefreshConnector
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `fetch_facts` | yes | company_ids, start_date, end_date |
| `get_authority` | no | - |
| `supports_incremental` | no | - |

### `WebsiteRefreshConnector` (async)

- **File**: `infrastructure/connectors/website_refresh.py:17`
- **Bases**: BaseRefreshConnector
- **Public methods**: 4

| Method | Async | Args |
|--------|-------|------|
| `fetch_facts` | yes | company_ids, start_date, end_date |
| `fetch_facts_with_websites` | yes | company_website_map, start_date, end_date |
| `get_authority` | no | - |
| `supports_incremental` | no | - |

### `YahooFinanceRefreshConnector` (async)

- **File**: `infrastructure/connectors/yahoo_finance_refresh.py:18`
- **Bases**: BaseRefreshConnector
- **Public methods**: 3

| Method | Async | Args |
|--------|-------|------|
| `fetch_facts` | yes | company_ids, start_date, end_date |
| `get_authority` | no | - |
| `supports_incremental` | no | - |
