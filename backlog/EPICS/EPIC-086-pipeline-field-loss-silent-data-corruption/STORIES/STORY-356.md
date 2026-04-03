# STORY-356: Create Unit Tests for Signal Extraction Layer (signals.py)

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P0 |
| **Size** | M (1-2 days) |
| **Epic** | EPIC-086 Pipeline Field Loss |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (revised after codebase audit — STORY-349 is DONE, 15 extractors exist) |
| **Risk** | Low |
| **Blocked By** | none (STORY-349 is DONE) |

---

## Problem Statement

`src/solstein/research/signals.py` has no isolated unit tests. The signal extractors (`_signal_revenue_level`, `_signal_growth_rate`, etc.) are the second transformation layer — they convert typed facts into scored business signals. Without tests at this layer, it is impossible to verify that a signal is correctly computed from its source facts, or that a missing fact correctly produces `None` rather than a wrong value.

## Acceptance Criteria

- [ ] `tests/unit/test_signal_extraction.py` exists with tests for every `_signal_*` function
- [ ] Each test provides a synthetic `dict[str, AggregatedFact]` and asserts the correct `SignalExtraction` output (name, value, confidence, source_facts)
- [ ] Each test also asserts that absence of required facts produces `None` (extractor returns None, not raises)
- [ ] `extract_signals()` integration test: given a fully-populated `AggregatedDataRecord`, asserts all expected signal names are present in the output
- [ ] All tests run in < 100ms (no I/O, no DB, no network)
- [ ] Coverage of `signals.py` reaches 95%+

## Tasks

## Actual Codebase State (verified 2026-04-03)

**15 signal extractor functions** exist in `src/solstein/research/signals.py` (STORY-349 added 5):

| Line | Function | Source fact |
|------|----------|-------------|
| 40 | `_signal_revenue_level` | `revenue` |
| 61 | `_signal_growth_rate` | `revenue_growth` |
| 81 | `_signal_profitability` | `profit_margin` |
| 101 | `_signal_company_size` | `employee_count` |
| 139 | `_signal_valuation` | `valuation` / `market_cap` |
| 171 | `_signal_innovation` | `total_patents`, `ai_related_patents` |
| 202 | `_signal_ai_maturity` | `ai_signal_strength` |
| 242 | `_signal_hiring_velocity` | `open_positions` |
| 279 | `_signal_market_sentiment` | `sentiment_score` / article counts |
| 329 | `_signal_funding` | `funding_rounds`, `last_round_stage`, `last_round_amount` |
| 372 | `_signal_ebitda` | `ebitda` |
| 390 | `_signal_net_income` | `net_income` |
| 408 | `_signal_pe_ratio` | `pe_ratio` |
| 426 | `_signal_current_price` | `current_price` |
| 444 | `_signal_eps_ttm` | `eps_ttm` |

`extract_signals()` entry point at line 491. `_SIGNAL_EXTRACTORS` list at line 466.

---

## Tasks

- [ ] Write `_make_fact(fact_type, value, confidence)` test helper
- [ ] Write tests for all 15 signal extractors (see table above)
- [ ] Write a test for `extract_signals()` with a fully populated `AggregatedDataRecord`
- [ ] Verify: `extract_signals()` with empty facts produces `SignalExtractionRecord` with 0 signals (no crash)
- [ ] Verify: signal extractor exception is caught and logged, not propagated (graceful degradation)

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

def test_signal_revenue_level():
    facts = {"revenue": _make_fact("revenue", 1_000_000, 0.85)}
    signal = _signal_revenue_level(facts)
    assert signal is not None
    assert signal.signal_name == "revenue_level"
    assert signal.signal_value == 1_000_000
    assert signal.signal_confidence == 0.85

def test_signal_revenue_level_none_when_missing():
    signal = _signal_revenue_level({})
    assert signal is None
```
