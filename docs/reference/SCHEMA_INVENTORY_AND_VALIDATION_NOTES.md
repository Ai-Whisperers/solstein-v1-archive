# Schema Inventory And Validation Notes

## Why This Exists

Solstein has multiple overlapping schema layers. A large part of the integration debt comes from values crossing boundaries as loose dicts, partial objects, or legacy payloads with no enforced contract at the exact place where the transition happens.

This document maps the active schema families and identifies where validation should become mandatory.

## Active Schema Families

### 1. Core Domain Schemas

Primary file:

- `src/solstein/domain/models.py`

Main models:

- `Company`
- `FinancialMetric`
- `MarketAnalysis`
- `RawDataSource`
- `RawDataRecord`
- `AggregatedFact`
- `AggregatedDataRecord`
- `SignalExtraction`
- `SignalExtractionRecord`
- `GatheringBatch`
- `CompanyAnalysisAuditTrail`

Current observations:

- This file acts as a high-traffic schema hub for business logic.
- It mixes entity modeling, audit trail payloads, scoring-related shapes, and pipeline-stage records.
- It is one of the most important boundaries in the system and one of the most overloaded.

Validation priority:

- high

### 2. Facts Persistence Schemas

Primary file:

- `src/solstein/domain/facts.py`

Main models:

- `GatheringBatch`
- `Fact`
- `FactSource`
- `RefreshMetadata`
- `DataSourceConflict`
- `ConfidenceCalibration`

Current observations:

- These are ORM schemas, not boundary payload schemas.
- They protect DB structure, but they do not validate inbound dict payloads before persistence.
- A new ingestion boundary schema has now been added in `src/solstein/worker/base.py` as `FactIngestionPayload`.

Validation priority:

- very high at the ingestion boundary

### 3. Evidence Graph Schemas

Primary file:

- `src/solstein/evidence/models.py`

Main models:

- `Claim`
- `SourceDocument`
- `Contradiction`
- `EvidenceReadiness`

Current observations:

- These are relatively well-typed Pydantic models.
- The main risk is not local validation but adapter/repository correctness when translating to Neo4j queries.

Validation priority:

- high at repository translation boundaries

### 4. API Request/Response Schemas

Primary file:

- `src/solstein/api/schemas/enrichment.py`

Main models:

- `EnrichmentRequest`
- `BatchEnrichmentRequest`
- `EnrichmentResultData`
- `EnrichmentResponse`
- `BatchEnrichmentResult`
- `BatchEnrichmentResponse`
- `AuditEntry`
- `AuditTrailResponse`
- `ErrorResponse`

Current observations:

- This is the cleanest explicit schema layer in the repo.
- The main problem is drift between API schemas and internal pipeline payloads.
- API schemas are stronger than several internal dict-based boundaries.

Validation priority:

- high for adapter/service outputs returned by routers

### 5. External Source / Research Schemas

Primary files:

- `src/solstein/data/sources/models.py`
- `src/solstein/data/company_research.py`
- `src/solstein/data/markets/models.py`

Main models:

- `PressCoverage`
- `LinkedInData`
- `FundingData`
- `PatentData`
- `ProductInfo`
- `CompanyResearch`
- `CompanyFinancials`
- `CompanyTechnology`
- `CompanyGrowthSignals`
- `GlobalStockData`
- `IndexData`

Current observations:

- These are key boundary contracts between external systems and internal normalization.
- Several recent bugs came from code assuming a flatter shape than the actual nested source model.
- `YahooFinanceRefreshConnector` was one such example.

Validation priority:

- very high

### 6. Validation Rule Objects

Primary files:

- `src/solstein/validation/financial_rules.py`
- `src/solstein/domain/validators.py`

Current observations:

- These define rule-level validation, not end-to-end boundary schemas.
- They are useful, but they do not replace structured payload schemas.

Validation priority:

- medium, as support layers

## Known Schema Drift Patterns

### Pattern A: Flat-vs-Nested Assumption Drift

Example:

- code reads `profile.revenue`
- actual schema stores it under `profile.financials.revenue`

Risk:

- silent empty outputs
- partial fact generation
- false “success” status with useless payloads

### Pattern B: Dict-vs-Model Ambiguity

Example:

- code calls `.get()` on a dataclass/Pydantic model
- code uses attribute access on a dict

Risk:

- runtime crashes
- incomplete fallback logic

### Pattern C: Legacy Alias Drift

Example:

- `type` versus `fact_type`
- old tests mocking `.loader` while production uses `.client`

Risk:

- tests pass against dead contracts
- invalid payloads survive too deep into the pipeline

### Pattern D: ORM Schema Mistaken For Boundary Validation

Example:

- relying on SQLAlchemy model constraints instead of validating before persistence

Risk:

- bad payloads reach DB code
- errors appear too late
- error messages are lower quality and harder to triage

## Validation Boundaries That Should Be Enforced

### Boundary 1: Connector Output -> Refresh/Worker Persistence

Current state:

- connector returns list of dicts
- worker persists dicts with minimal normalization

Now added:

- `FactIngestionPayload` in `src/solstein/worker/base.py`
- `ConnectorFactPayload` in `src/solstein/infrastructure/fact_payloads.py`
- validation in `src/solstein/infrastructure/refresh.py` before delta filtering and before persistence

Next step:

- expand it from envelope validation into per-fact-family `value` schemas and source attribution contracts explicitly

### Boundary 2: External API Response -> Source Models

Current state:

- parsing often happens inline in connector/source code

Required:

- documented contract fixtures per API
- parser tests against official example shapes
- fail-fast when response shape changes

### Boundary 3: Unified Enrichment -> Domain Audit Trail

Current state:

- several paths still rely on broad dict payloads and partially typed intermediates

Required:

- enforce typed records before merge and before scoring

### Boundary 4: Domain Objects -> API Responses

Current state:

- API schemas exist, but internal objects are not always normalized cleanly before mapping

Required:

- explicit translation functions with tests

## Immediate Enforcement Priorities

1. Fact ingestion boundary in `worker/base.py`
2. Refresh connector fact payload contracts
3. Unified adapter outputs
4. Scoring/classification input objects
5. Report/export payloads

## Structural Test Debt Connected To Schemas

1. Some tests validate stale interfaces, not the current schema contracts.
2. Global test harness imports too much application state too early.
3. Connector tests often assert only “did not crash” instead of payload shape.
4. Integration boundaries rely too much on implicit structure and too little on schema validation.

## Rule Going Forward

If a payload crosses one of these boundaries:

- external API -> source model
- source model -> connector fact dict
- connector fact dict -> persistence
- unified merge payload -> domain model
- domain model -> API/export/report

then a typed schema or explicit validator must exist at that boundary, and there must be a regression test for the contract.
