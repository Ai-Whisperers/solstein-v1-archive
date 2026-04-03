# STORY-356: Create Unit Tests for Signal Extraction Layer (signals.py)

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P0 |
| **Size** | M (1-2 days) |
| **Epic** | EPIC-086 Pipeline Field Loss |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (deep wiring audit — 15 extractors confirmed with input/output contracts) |
| **Risk** | Low |
| **Blocked By** | none (STORY-349 is DONE) |

---

## Exact Codebase Wiring (deep audit 2026-04-03)

### Signal Extractors (`src/solstein/research/signals.py`)

All 15 extractor functions registered in `_SIGNAL_EXTRACTORS` list (line 466):

| Line | Function | Required fact_type(s) | Produced `signal_name` | Returns None when |
|------|----------|----------------------|----------------------|-------------------|
| 40 | `_signal_revenue_level` | `"revenue"` | `"revenue_level"` | `"revenue"` absent |
| 61 | `_signal_growth_rate` | `"revenue_growth"` | `"growth_rate"` | `"revenue_growth"` absent |
| 81 | `_signal_profitability` | `"profit_margin"` | `"profitability"` | `"profit_margin"` absent |
| 101 | `_signal_company_size` | `"employee_count"` | `"company_size"` | `"employee_count"` absent |
| 139 | `_signal_valuation` | `"valuation"` or `"market_cap"` | `"valuation"` | both absent |
| 171 | `_signal_innovation` | `"total_patents"` | `"innovation"` | `"total_patents"` absent |
| 202 | `_signal_ai_maturity` | `"ai_signal_strength"` | `"ai_maturity"` | `"ai_signal_strength"` absent |
| 242 | `_signal_hiring_velocity` | `"open_positions"` | `"hiring_velocity"` | `"open_positions"` absent |
| 279 | `_signal_market_sentiment` | `"sentiment_score"` OR `"positive_article_count"` + `"negative_article_count"` | `"market_sentiment"` | all absent |
| 329 | `_signal_funding` | `"funding_rounds"` | `"funding"` | `"funding_rounds"` absent |
| 372 | `_signal_ebitda` | `"ebitda"` | `"ebitda"` | `"ebitda"` absent |
| 390 | `_signal_net_income` | `"net_income"` | `"net_income"` | `"net_income"` absent |
| 408 | `_signal_pe_ratio` | `"pe_ratio"` | `"pe_ratio"` | `"pe_ratio"` absent |
| 426 | `_signal_current_price` | `"current_price"` | `"current_price"` | `"current_price"` absent |
| 444 | `_signal_eps_ttm` | `"eps_ttm"` | `"eps_ttm"` | `"eps_ttm"` absent |

`extract_signals()` entry point at line 491. Calls each extractor in `_SIGNAL_EXTRACTORS`; if one raises, it is caught+logged (graceful degradation), the rest continue.

### `SignalExtraction` Fields

From `src/solstein/domain/models.py` (or domain models package):

| Field | Type | Note |
|-------|------|------|
| `signal_name` | `str` | matches `signal_name` column above |
| `signal_value` | `float \| str \| None` | the computed value |
| `signal_confidence` | `float` | 0–1 |
| `source_facts` | `list[str]` | fact_types that were used |

### `AggregatedFact` Fields (test helper input)

```python
AggregatedFact(
    fact_type="revenue",
    value=1_000_000,
    confidence=0.85,
    sources_used=["yahoo_finance"],
    source_agreement_percentage=1.0,
    source_credibility_scores={"yahoo_finance": 0.85},
)
```

### Special: `_signal_market_sentiment` (line 279)

Two computation paths:
1. If `"sentiment_score"` fact present → use directly
2. If absent but `"positive_article_count"` AND `"negative_article_count"` present → compute polarity: `(pos - neg) / (pos + neg)` (or similar)
3. If none present → return `None`

Tests must cover all three paths.

---

## Problem Statement

`signals.py` has no isolated unit tests. The 15 extractors are the second transformation layer — wrong fact_type string, missing dict key, or silent exception would produce wrong signal values with no detection. The test must verify both the happy path and the "returns None" contract.

---

## Acceptance Criteria

- [ ] `tests/unit/test_signal_extraction.py` exists
- [ ] `_make_fact(fact_type, value, confidence=0.9)` helper defined in test file
- [ ] For each of the 15 extractors: test with required fact → assert correct `signal_name`, non-None `signal_value`, correct `signal_confidence`
- [ ] For each of the 15 extractors: test with empty `{}` dict → assert `None` returned (no exception)
- [ ] `_signal_market_sentiment` tested on all 3 input paths (direct score, computed polarity, absent)
- [ ] `extract_signals()` integration test: fully-populated `AggregatedDataRecord` → all 15 signal names present in output
- [ ] `extract_signals()` empty facts test: 0 signals, no exception
- [ ] All tests run in < 100ms
- [ ] `ruff check` 0 errors; `pytest` 0 failures

---

## Tasks

- [ ] Write `_make_fact()` helper
- [ ] Write 2 tests per extractor (happy + missing): 30 tests total
- [ ] Write 3 tests for `_signal_market_sentiment` (3 paths)
- [ ] Write `extract_signals()` integration test
- [ ] Write `extract_signals()` empty test

## Test Helper Pattern

```python
from solstein.domain.models import AggregatedFact

def _make_fact(fact_type: str, value, confidence: float = 0.9) -> AggregatedFact:
    return AggregatedFact(
        fact_type=fact_type,
        value=value,
        confidence=confidence,
        sources_used=["test_source"],
        source_agreement_percentage=1.0,
        source_credibility_scores={"test_source": confidence},
    )

def test_signal_revenue_level_happy_path():
    facts = {"revenue": _make_fact("revenue", 1_000_000, 0.85)}
    signal = _signal_revenue_level(facts)
    assert signal is not None
    assert signal.signal_name == "revenue_level"
    assert signal.signal_value == 1_000_000
    assert signal.signal_confidence == 0.85

def test_signal_revenue_level_missing_fact():
    assert _signal_revenue_level({}) is None
```

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/research/signals.py` | 40–464 | All 15 extractor functions |
| `src/solstein/research/signals.py` | 466 | `_SIGNAL_EXTRACTORS` list |
| `src/solstein/research/signals.py` | 491 | `extract_signals()` entry point |
| `src/solstein/research/signals.py` | 279–328 | `_signal_market_sentiment` — 3 code paths |
