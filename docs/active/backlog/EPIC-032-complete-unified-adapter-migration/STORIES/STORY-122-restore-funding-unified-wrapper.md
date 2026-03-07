# STORY-122: Restore Funding Adapter Wrapper

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-032: Complete Unified Adapter Migration |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-092 (merge task files) |

---

## The Audit Verdict

> `funding.py` has `news_api_key` parameter and `AdditionalDataSources` wrapper. `funding_unified.py` lacks both.

---

## Problem Statement

The funding unified adapter was written to use the new base connector pattern, but in the process it lost the ability to accept a news API key for cross-referencing and lost the wrapper that handled Crunchbase API errors gracefully. The old adapter could enrich funding data with news signals — a deliberate design decision that improved signal quality for PE analysis. The unified adapter cannot. This is a feature regression masquerading as a refactor.

The `news_api_key` parameter in `funding.py` was not an accident. Funding data alone tells you what happened. Funding data cross-referenced with news signals tells you why it happened and what the market reaction was. A Series B announcement paired with contemporaneous news coverage of the company's product launch or competitive threat is a materially different signal than the funding event in isolation. The unified adapter dropped this enrichment capability without documentation, without a deprecation notice, and without a replacement.

The `AdditionalDataSources` wrapper in `funding.py` handled Crunchbase's error behavior specifically. Crunchbase returns 401 for expired API keys, 403 for quota exhaustion on certain endpoints, 429 for rate limits, and 500 for transient failures. Each of these requires a different response. The unified adapter handles none of them. A 401 from Crunchbase will propagate as an unhandled exception. A 429 will not retry. A 403 will not produce a useful error message. The research pipeline will fail, and the error will be difficult to diagnose.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Data Quality** | Lost news cross-reference capability reduces funding signal richness; PE analysts receive less context per funding event |
| **Reliability** | Unhandled Crunchbase 401/403/429/500 responses crash the research pipeline |
| **Maintainability** | Two funding adapters with different capabilities; the "official" one is the less capable one |
| **Error Observability** | Crunchbase authentication failures produce cryptic exceptions instead of actionable error messages |

---

## Affected Files

| File | Issue |
|------|-------|
| `data/funding_unified.py` | Missing `news_api_key` parameter; missing `AdditionalDataSources` wrapper; no Crunchbase error handling |
| `data/funding.py` | Reference implementation — contains the wrapper and cross-reference logic that must be ported; to be deleted after parity |

---

## Architectural Requirements

- `news_api_key` parameter must be restored to `funding_unified.py` with the same semantics as in `funding.py`
- When `news_api_key` is provided, the adapter must query news signals and attach them to funding records
- When `news_api_key` is absent or `None`, the adapter must function without news enrichment (graceful degradation)
- Error handling wrapper equivalent to `AdditionalDataSources` in `funding.py` must be present in `funding_unified.py`
- Crunchbase HTTP 401 must produce a structured authentication error with a clear message indicating key expiry
- Crunchbase HTTP 403 must produce a structured authorization error distinguishing quota exhaustion from permission denial
- Crunchbase HTTP 429 must trigger retry with exponential backoff
- Crunchbase HTTP 500 must trigger retry with exponential backoff
- All retry attempts must be logged at WARNING level
- Final failure must be logged at ERROR level with full context including which Crunchbase endpoint was called
- `funding.py` must be deleted only after integration tests confirm `funding_unified.py` handles all scenarios correctly
- The public interface of `funding_unified.py` must remain backward-compatible with existing callers

---

## Acceptance Criteria

- [ ] `funding_unified.py` accepts `news_api_key` as a parameter
- [ ] When `news_api_key` is provided, funding records include news cross-reference data
- [ ] When `news_api_key` is absent, funding records are returned without news enrichment (no error)
- [ ] Crunchbase HTTP 401 produces a structured domain error with message indicating authentication failure
- [ ] Crunchbase HTTP 403 produces a structured domain error distinguishing quota from permission
- [ ] Crunchbase HTTP 429 triggers retry with exponential backoff
- [ ] Crunchbase HTTP 500 triggers retry with exponential backoff
- [ ] Integration test: funding fetch with `news_api_key` verifies both Crunchbase and NewsAPI are queried
- [ ] `funding.py` is deleted
- [ ] No import of `funding.py` remains anywhere in the codebase

---

## Definition of Done

- **Tests Required**: Integration test that provides a valid `news_api_key` and mocks both Crunchbase and NewsAPI responses; verifies that the returned funding record contains fields from both sources. Separate integration test that mocks Crunchbase to return 429 on first call and 200 on second; verifies retry behavior. Unit test that mocks Crunchbase 401 and verifies a structured authentication error is raised.
- **Documentation Required**: Inline docstring on the `news_api_key` parameter explaining the cross-reference behavior and what fields are added to funding records when news enrichment is active.
- **Code Review Gate**: Reviewer must verify that `news_api_key` flows correctly through the adapter to the NewsAPI call. Reviewer must confirm that Crunchbase error handling covers all four status codes (401, 403, 429, 500) with distinct behavior. Reviewer must verify `funding.py` is absent from the repository after merge.

---

## Notes

The news cross-reference feature is not a nice-to-have. For PE analysis, the combination of funding event timing and contemporaneous news coverage is a primary signal for assessing market momentum. Dropping it silently in a "refactor" is the kind of decision that gets noticed six months later when an analyst asks why the funding signals look thin.

The distinction between Crunchbase 401 and 403 matters operationally. A 401 means the API key is expired and needs rotation. A 403 on a specific endpoint means the subscription tier doesn't cover that data. These require different responses from the operations team. Collapsing them into a generic "auth error" loses information that is genuinely useful.
