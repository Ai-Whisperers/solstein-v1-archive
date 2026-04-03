# STORY-356: Create Unit Tests for Signal Extraction Layer (signals.py)

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P0 |
| **Size** | M (1-2 days) |
| **Epic** | EPIC-086 Pipeline Field Loss |
| **Created** | 2026-04-03 |
| **Risk** | Low |
| **Blocked By** | STORY-349 (signal extractors must be complete before tests are authoritative) |

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

- [ ] Write `_make_fact(fact_type, value, confidence)` test helper
- [ ] Write tests for each of the 10 existing signal extractors (plus any added in STORY-349)
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
