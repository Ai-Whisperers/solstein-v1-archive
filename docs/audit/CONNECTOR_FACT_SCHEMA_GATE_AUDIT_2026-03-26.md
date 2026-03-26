# Connector Fact Schema Gate Audit — 2026-03-26

**Bug class:** Loose dict payloads crossing the connector -> refresh -> worker persistence boundary without a shared enforced fact envelope.

**Goal:** Reject malformed fact payloads before delta detection or persistence, and align the runtime boundary with a matching TypeScript contract so the same drift does not reappear in tooling.

---

## Why This Gate Was Added

The async-boundary cleanup removed one failure class, but it also exposed a second structural weakness:

- refresh connectors still returned loose dict payloads
- worker persistence validated only a partial subset of the envelope
- the same legacy alias drift (`type` vs `fact_type`) could be normalized in one path and missed in another
- stale integration tests were not a reliable signal for this boundary

Without a shared gate here, malformed payloads can survive long enough to fail later in delta detection, batch storage, or downstream reporting.

---

## Fixes Applied

### 1. Shared Python fact envelope

**File:** `src/solstein/infrastructure/fact_payloads.py`

Added `ConnectorFactPayload` with:

- required `company_id`
- required canonical `fact_type`
- legacy alias normalization from `type`
- bounded `confidence`
- normalized `metadata`
- optional `extracted_at`
- optional `_hash`

The model is intentionally permissive on extra keys for now so we can gate the canonical boundary fields without breaking connector-specific metadata abruptly.

### 2. Refresh boundary validation

**File:** `src/solstein/infrastructure/refresh.py`

`BaseRefreshConnector` now validates connector-produced facts:

- after `fetch_facts(...)` and before delta filtering in `get_facts_to_refresh(...)`
- again before persistence in `store_facts(...)`

Malformed payloads are rejected early with logging instead of flowing deeper into the pipeline.

### 3. Worker boundary reuse

**File:** `src/solstein/worker/base.py`

`FactIngestionPayload` now subclasses the shared `ConnectorFactPayload` instead of defining an overlapping partial contract. This removes duplication and keeps legacy alias handling and metadata normalization consistent.

### 4. Nested persistence mismatch fixed

**File:** `src/solstein/infrastructure/refresh.py`

While enforcing the new gate, a deeper runtime defect surfaced:

- `BaseRefreshConnector.store_facts()` was constructing `GatheringBatch` with fields not present on the ORM model
- it was also constructing `Fact` with unsupported fields such as `source`, `source_type`, `metadata`, and `value_hash`

This was not just schema looseness. It was a broken persistence path hidden behind the absence of direct tests.

The method now:

- creates an ORM-compatible `GatheringBatch`
- stores `Fact` using the actual ORM fields
- maps scalar vs string vs datetime values to the supported value columns
- marks the batch `completed` or `failed` consistently

---

## Regression Coverage Added

**File:** `tests/unit/test_connector_fact_schema_gate.py`

Added focused coverage for:

- legacy `type` alias normalization and `metadata=None` normalization
- rejection of invalid connector facts before delta filtering
- ORM-compatible `BaseRefreshConnector.store_facts()` behavior with one valid and one invalid fact payload

---

## TypeScript Contract Added

**Files:**

- `tooling/contracts-ts/src/external/facts.ts`
- `tooling/contracts-ts/src/index.ts`

Added a matching serialized contract for connector fact envelopes:

- accepts canonical `fact_type`
- accepts legacy `type` at input
- transforms to canonical `fact_type`
- normalizes `metadata`

This keeps the future TS/tooling side aligned with the Python boundary instead of inventing a different contract later.

---

## Residual Limits

1. This gate validates the fact envelope, not the inner semantic shape of each `value`.
   A `funding_summary` fact and a `market_signal` fact still need their own per-family schemas if we want full semantic enforcement.

2. The gate is intentionally not “strict all extras forbidden” yet.
   That is a later tightening step once connector-specific metadata contracts are audited.

3. `tests/integration/test_unified_adapters.py` remains stale.
   It is still not a trustworthy signal for this boundary and must be reconciled separately.

---

## Next Enforcement Step

The next schema gate should be per-family connector fact value validation for the highest-risk fact types:

1. market/news signal fact values
2. funding summary fact values
3. LinkedIn hiring signal fact values
4. unified enrichment merge payloads before scoring
