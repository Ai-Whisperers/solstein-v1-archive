# STORY-380: Fix `CompetitorJsonSource.discover()` — propagate `data_source_type` into pipeline

**Epic**: EPIC-093 — Production Loader Synthetic Tagging
**Priority**: P0
**Size**: S (2–4 hours)
**Status**: 🔴 READY (depends on STORY-379 being complete for correct tagging at loader level)

---

## Context

`src/solstein/adapters/discovery/competitor_json.py:41–73` is a production pipeline adapter
used in every `run_market_intelligence()` call. It instantiates `CompetitorDataLoader()`, loads
companies, and converts them to `DiscoveryCandidate` objects — but drops the `data_source_type`
along the way:

```python
def discover(self, market, seed_company, max_results=50, ...) -> list[DiscoveryCandidate]:
    from solstein.data.loaders import CompetitorDataLoader
    loader = CompetitorDataLoader()
    companies = loader.load_companies()       # after STORY-379: companies have data_source_type
    for company in companies[:max_results]:
        candidates.append(
            DiscoveryCandidate(
                company_id=...,
                name=company.name,
                ...
                # data_source_type is NOT passed to DiscoveryCandidate
            )
        )
    return candidates
```

If `DiscoveryCandidate` supports a `data_source_type` field (or equivalent), it must be
propagated here. If it does not, this story adds the field to `DiscoveryCandidate`.

---

## Acceptance Criteria

- [ ] Read `src/solstein/research/discovery.py` (or wherever `DiscoveryCandidate` is defined)
      to determine if it has a `data_source_type` or `source_quality` field
- [ ] If the field exists: pass `company.data_source_type` from the loaded company to the candidate
- [ ] If the field does not exist: add `data_source_type: str = "unknown"` to `DiscoveryCandidate`
      and propagate it from the loader
- [ ] The discovery pipeline (in `research/pipeline.py`) must then carry `data_source_type` through
      to the final `Company` object so the export gate can inspect it
- [ ] Unit test: `CompetitorJsonSource.discover()` with a loader that returns synthetic companies →
      returned candidates have `data_source_type="synthetic"`

---

## Technical Notes

**Read before coding**:
1. `src/solstein/research/discovery.py` — `DiscoveryCandidate` model definition
2. `src/solstein/research/pipeline.py` — how `DiscoveryCandidate` is converted to `Company`
3. `src/solstein/adapters/discovery/competitor_json.py:55–73` — the full candidate construction

The goal is end-to-end propagation: loader → candidate → pipeline → Company → export gate.
STORY-379 handles the loader side. This story handles the adapter → pipeline path.

If the propagation path is complex (more than 50 lines of changes), scope this story to
just the adapter-level fix and create a follow-up story for the pipeline propagation.

---

## Definition of Done

- [ ] `DiscoveryCandidate` has a `data_source_type` field (add if absent)
- [ ] `CompetitorJsonSource.discover()` propagates `company.data_source_type` to candidates
- [ ] Pipeline converts it through to the final `Company.data_source_type`
- [ ] Unit test verifying end-to-end propagation
- [ ] `pytest` 0 failures, `ruff check` 0 errors
