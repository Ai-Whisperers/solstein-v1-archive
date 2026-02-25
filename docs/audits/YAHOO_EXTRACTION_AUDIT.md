# Yahoo Finance Extraction Audit

## Section 1: Summary
Date: 2026-02-24
Auditor: gesttaltt (human) + Sisyphus (AI orchestrator)
Scope: Nyx's rewrite of `_extract_yahoo_finance()` in `src/solstein/research/aggregate.py`
Severity: SEVERE REGRESSION, approximately 15 fields silently returning None

## Section 2: What Went Wrong
Nyx rewrote `_extract_yahoo_finance()` using flat top-level keys like `content["revenue"]`, `content["profit_margin"]`, `content["revenue_growth"]`, `content["eps"]`, `content["industry"]`, `content["sector"]`, and `content["tech_stack"]`.

The actual data shape comes from `CompanyResearch.model_dump(mode="json")`, which produces nested dictionaries. The correct paths are:
- `content["financials"]["revenue"]`
- `content["financials"]["profit_margin"]`
- `content["financials"]["revenue_growth"]`
- `content["financials"]["eps"]`
- `content["overview"]["industry"]`
- `content["overview"]["sector"]`
- `content["technology"]["tech_stack"]`

Nyx didn't inspect the `CompanyResearch` Pydantic model in `src/solstein/data/company_research.py`. It assumed the data was raw yfinance API output with flat keys. In reality, the Yahoo Finance adapter calls `CompanyResearcher().research(ticker)`, which returns a `CompanyResearch` model. The `.model_dump(mode="json")` call serializes it into nested dicts matching the model hierarchy.

The data transformation chain is: yfinance API -> CompanyResearcher -> CompanyResearch (Pydantic) -> .model_dump() -> nested dict -> RawDataSource.raw_content -> _extract_yahoo_finance().

Nyx operated on assumption rather than inspection. This is a class of error where AI agents extrapolate API shapes from library names instead of tracing the actual data flow.

## Section 3: Impact Analysis
Approximately 15 fields silently returned `None` instead of real values. No runtime errors occurred because calling `.get()` on a dictionary with incorrect keys returns `None` by default. This produced empty or degraded scoring for all companies analyzed via Yahoo Finance.

The bug is silent. It doesn't crash the system, it just quietly loses data. Downstream metrics like `growth_score`, `financial_health_score`, and `competitive_position_score` were all degraded.

## Section 4: Prevention Measures
We implemented schema docstrings for all `_extract_*` functions in `aggregate.py`. These document the expected `raw_content` shape with the exact keys they access. Future editors can see the expected schema without tracing the full data chain.

Unit tests in `tests/unit/research/test_aggregate_extractors.py` now contain 29 tests, including fixtures with realistic `CompanyResearch.model_dump()` output. Any key-path regression will immediately fail.

This audit document serves as institutional memory for why flat keys are incorrect in this context.

## Section 5: Recommendations for AI Agent Workflows
AI agents must inspect upstream data models before rewriting extraction functions. Don't assume API data shapes from library names. Always trace the actual transformation chain.

Pydantic models are the source of truth for serialized data shapes in this codebase. When in doubt, run `ModelClass.model_json_schema()` to see the exact output structure.
