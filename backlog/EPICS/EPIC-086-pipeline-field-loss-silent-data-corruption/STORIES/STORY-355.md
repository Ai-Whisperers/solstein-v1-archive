# STORY-355: Create Unit Tests for Pipeline Extractor Layer (aggregate.py)

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P0 |
| **Size** | M (2 days) |
| **Epic** | EPIC-086 Pipeline Field Loss |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (deep wiring audit — STORY-349 done, line numbers and key contracts verified) |
| **Risk** | Low |
| **Blocked By** | none (STORY-349 is DONE) |

---

## Exact Codebase Wiring (deep audit 2026-04-03)

### Extractor Functions (`src/solstein/research/aggregate.py`)

**Dispatch** (line 101): `_extract_facts_from_source(source)` — routes to per-source extractor based on `source.source_type`.

**`_extract_yahoo_finance(content)` — line 148**

Input: `CompanyResearch.model_dump(mode='json')` — NESTED dict.

| Input path | Produced `(fact_type, value)` |
|---|---|
| `content["financials"]["revenue"]` | `("revenue", float)` |
| `content["financials"]["revenue_growth_yoy"]` | `("revenue_growth", float)` |
| `content["financials"]["profit_margin"]` | `("profit_margin", float)` |
| `content["financials"]["ebitda"]` | `("ebitda", float)` |
| `content["financials"]["net_income"]` | `("net_income", float)` |
| `content["market_cap"]` | `("market_cap", float)` |
| `content["pe_ratio"]` | `("pe_ratio", float)` |
| `content["current_price"]` | `("current_price", float)` |
| `content["eps_ttm"]` | `("eps_ttm", float)` |
| `content["employees"]` | `("employee_count", int)` |
| `content["founded"]` | `("founded_year", int)` |
| `content["description"]` | `("description", str)` |
| `content["headquarters"]` | `("headquarters", str)` |
| `content["website"]` | `("website", str)` |
| `content["name"]` | `("name", str)` |
| `content["exchange"]` | `("exchange", str)` |
| `content["growth"]["employee_count"]` | `("employee_count", int)` |
| `content["growth"]["employee_growth"]` | `("employee_growth_pct", float)` |
| `content["growth"]["job_postings_count"]` | `("open_positions", int)` |
| `content["growth"]["ai_related_jobs"]` | `("ai_related_positions", int)` |
| `content["ai"]["ai_score"]` | `("ai_score", int)` |
| `content["ai"]["ai_signal_strength"]` | `("ai_signal_strength", str)` |
| `content["technology"]["industry"]` | `("industry", str)` |
| `content["technology"]["sector"]` | `("sector", str)` |
| `content["products"]["products"]` | `("products", list[str])` |
| `content["source_currency"]` + `content["revenue"]` | GlobalMarket path: `("revenue", float)` |

**WARNING**: `content["revenue"]` at top level is `None` for `CompanyResearch`; financial data lives under `content["financials"]["revenue"]`. Tests must construct nested dicts.

**`_extract_news(content)` — line 267**

| Input key | Produced `(fact_type, value)` |
|---|---|
| `content["total_articles"]` | `("article_count", int)` |
| `content["sentiment_score"]` | `("sentiment_score", float)` |
| `content["positive_count"]` | `("positive_article_count", int)` |
| `content["negative_count"]` | `("negative_article_count", int)` |

**`_extract_exa_search(content)` — line 286**

| Input key | Produced |
|---|---|
| `content["article_count"]` | `("article_count", int)` |

**`_extract_crunchbase(content)` — line 297**

| Input key | Produced |
|---|---|
| `content["total_raised"]` | `("total_funding_raised", float)` |
| `content["last_round_amount"]` | `("last_round_amount", float)` |
| `content["last_round_valuation"]` | `("valuation", float)` |
| `content["num_rounds"]` | `("funding_rounds", int)` |
| `content["last_round_stage"]` | `("last_round_stage", str)` |
| `content["investors"]` | `("investors", list[str])` |

**`_extract_patents(content)` — line 321**

| Input key | Produced |
|---|---|
| `content["total_patents"]` | `("total_patents", int)` |
| `content["ai_related_patents"]` | `("ai_related_patents", int)` |
| `content["top_categories"]` | `("patent_categories", list[str])` |

**`_extract_linkedin(content)` — line 338**

| Input key | Produced |
|---|---|
| `content["employee_count"]` | `("employee_count", int)` |
| `content["employee_growth_pct"]` | `("employee_growth_pct", float)` |
| `content["open_positions"]` | `("open_positions", int)` |
| `content["ai_related_positions"]` | `("ai_related_positions", int)` |

**`_extract_website(content)` — line 357**

| Input key | Produced |
|---|---|
| `content["main_products"]` | `("products", list[str])` |
| `content["tech_stack"]` | `("tech_stack", list[str])` |
| `content["pricing_model"]` | `("pricing_model", str)` |
| `content["target_customers"]` | `("target_customers", list[str])` |

**`_extract_generic(content)` — line 376**

Reads top-level keys: `name`, `description`, `website`, `founded_year`, `headquarters` — produced fact_type strings are identical to the key names.

**`DefaultFactAggregator`** — line 562. Method `.aggregate()` calls `_extract_facts_from_source()` for each source and returns an `AggregatedDataRecord`.

### Missing key behavior

All extractors use `content.get(key)` — missing keys silently produce no fact (empty list, no exception). Test must verify this: absent key → no `(fact_type, ...)` tuple in output.

---

## Problem Statement

`aggregate.py` has zero isolated unit tests. These extractors are the gateway from raw adapter output to typed facts — a renamed key or changed schema silently drops data. This was the root mechanism of the 70% field loss.

---

## Acceptance Criteria

- [ ] `tests/unit/test_aggregate_extractors.py` exists
- [ ] For each extractor: test with fully-populated synthetic dict asserts the EXACT set of `(fact_type, value)` tuples
- [ ] For each extractor: test with empty dict `{}` asserts empty list returned (no exception)
- [ ] For `_extract_yahoo_finance`: test with NESTED dict (not flat top-level) — `{"financials": {"revenue": 1e6, ...}, "growth": {...}, ...}`
- [ ] `DefaultFactAggregator.aggregate()` integration test: given sources covering all extractors, assert all expected fact_types in output
- [ ] All tests run in < 200ms (no I/O, no DB, no network)
- [ ] `ruff check` 0 errors; `pytest` 0 failures

---

## Tasks

- [ ] Write helper: `def _make_full_yahoo_payload() -> dict` returning nested CompanyResearch-shaped dict
- [ ] Write `test_extract_yahoo_finance_full_payload` — assert 24+ facts
- [ ] Write `test_extract_yahoo_finance_empty_payload` — assert `[]`
- [ ] Write `test_extract_yahoo_finance_missing_financials_nested` — omit `financials` key → no revenue/ebitda/etc
- [ ] Write tests for `_extract_news`, `_extract_exa_search`, `_extract_crunchbase`, `_extract_patents`, `_extract_linkedin`, `_extract_website`, `_extract_generic` (full + empty)
- [ ] Write `test_default_fact_aggregator_aggregate` integration test

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/research/aggregate.py` | 101 | Dispatch function |
| `src/solstein/research/aggregate.py` | 148 | `_extract_yahoo_finance` |
| `src/solstein/research/aggregate.py` | 267 | `_extract_news` |
| `src/solstein/research/aggregate.py` | 286 | `_extract_exa_search` |
| `src/solstein/research/aggregate.py` | 297 | `_extract_crunchbase` |
| `src/solstein/research/aggregate.py` | 321 | `_extract_patents` |
| `src/solstein/research/aggregate.py` | 338 | `_extract_linkedin` |
| `src/solstein/research/aggregate.py` | 357 | `_extract_website` |
| `src/solstein/research/aggregate.py` | 376 | `_extract_generic` |
| `src/solstein/research/aggregate.py` | 562 | `DefaultFactAggregator` |
