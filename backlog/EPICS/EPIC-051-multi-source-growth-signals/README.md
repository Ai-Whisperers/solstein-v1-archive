# EPIC-051: Multi-Source Growth Signal Enrichment

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Created** | 2026-03-10 |
| **Stories** | STORY-194, STORY-195, STORY-196, STORY-197 |
| **Dependencies** | EPIC-050 (Web Acquisition Pipeline), EPIC-028 (External Service Consolidation) |

## Context

Real-data testing showed strong financial coverage but weak growth-signal coverage. The scoring engine is calibrated, yet classification quality is limited by missing growth inputs (employee growth, hiring momentum, product velocity, and go-to-market traction).

This epic expands enrichment to multi-source growth signals and formalizes fallback behavior across paid/free tiers.

## Scope

| Category | Action |
|----------|--------|
| Hiring Signals | Add connectors for employee count trend and open roles |
| Company Momentum | Add product-release and website change indicators |
| Funding Dynamics | Add funding event recency and stage transitions |
| Source Policy | Define source tiering and fallback order by signal |
| Data Contract | Normalize all growth signals to typed canonical schema |

## Stories

| Story | Title | Priority | Status |
|-------|-------|----------|--------|
| STORY-194 | Build hiring signal adapters (employee trend, open jobs) | P1 | 🔴 Not Started |
| STORY-195 | Build product and web-momentum extractors from crawl output | P1 | 🔴 Not Started |
| STORY-196 | Add growth-signal normalization contract and merge policy | P1 | 🔴 Not Started |
| STORY-197 | Implement source fallback matrix (premium/free/degraded) | P1 | 🔴 Not Started |

## Target Integration Points

- `src/solstein/data/sources/models.py`
- `src/solstein/data/sources/__init__.py`
- `src/solstein/data/source_policy.py`
- `src/solstein/data/enrichment/models.py`
- `src/solstein/data/enrichment/strategies/base.py`
- `src/solstein/analytics/signals/extractors.py`

## Architectural Requirements

- **REQ-1**: Growth signals must be represented in canonical typed fields with source attribution.
- **REQ-2**: Each signal family must have at least one free-tier fallback source.
- **REQ-3**: Missing signal fields must be explicit (`unknown`) rather than fabricated defaults.
- **REQ-4**: Merge logic must preserve source confidence and recency when conflicts exist.
- **REQ-5**: Signal extraction must be deterministic for the same input payload.

## Success Criteria

- Growth-signal field fill rate increases from current baseline to >= 70% on real-company runs.
- At least 3 independent growth signal families available per company (hiring/product/funding).
- Fallback matrix covers 100% of required growth fields when premium connectors are unavailable.
- Unknown-field rate for core growth dimensions reduced by >= 40%.

## Risks

| Risk | Mitigation |
|------|------------|
| Public hiring data is sparse for private companies | Blend site-job parsing + third-party APIs + fallback confidence downgrade |
| Signal staleness skews scores | Add freshness windows and stale penalties in scoring inputs |
| Connector proliferation increases maintenance burden | Use strategy interfaces and shared adapter contracts |
| Paid API lock-in | Keep premium providers optional behind source policy tiers |

## Notes

The objective is not maximal data volume. It is decision-grade growth coverage. Signals must be attributable, fresh enough, and resilient under connector outages.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
