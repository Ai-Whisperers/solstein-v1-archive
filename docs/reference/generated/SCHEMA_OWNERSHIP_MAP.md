# Schema Ownership Map

> Auto-generated on 2026-04-01 00:58 UTC by `scripts/ci/generate_schema_ownership_map.py`.
> Do not edit manually.

**Total schemas**: 173

## _config_timeouts.py/ (3 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `CeleryTimingConfig` | pydantic | `_config_timeouts.py:143` | 3 |
| `CircuitBreakerConfig` | pydantic | `_config_timeouts.py:104` | 4 |
| `HttpTimeoutsConfig` | pydantic | `_config_timeouts.py:10` | 15 |

## agents/ (1 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `AgentTaskResult` | pydantic | `agents/base_agent.py:16` | 8 |

## analytics/ (4 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `FilterResponse` | pydantic | `analytics/filters/llm.py:18` | 2 |
| `SP500Membership` | pydantic | `analytics/valuation/models.py:199` | 3 |
| `Signal` | pydantic | `analytics/signals/base.py:26` | 6 |
| `ValuationContext` | pydantic | `analytics/valuation/models.py:23` | 9 |

## api/ (46 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `AdjudicationRequest` | pydantic | `api/routers/scoring.py:32` | 6 |
| `ApproveRequest` | pydantic | `api/routers/review.py:35` | 1 |
| `AsyncBatchEnrichmentRequest` | pydantic | `api/routers/async_jobs.py:50` | 3 |
| `AsyncEnrichmentRequest` | pydantic | `api/routers/async_jobs.py:39` | 4 |
| `AuditEntry` | pydantic | `api/schemas/enrichment.py:358` | 7 |
| `AuditTrailResponse` | pydantic | `api/schemas/enrichment.py:370` | 4 |
| `AuthTokenResponse` | pydantic | `api/routers/auth.py:59` | 5 |
| `BatchEnrichmentRequest` | pydantic | `api/schemas/enrichment.py:49` | 4 |
| `BatchEnrichmentResponse` | pydantic | `api/schemas/enrichment.py:298` | 7 |
| `BatchEnrichmentResult` | pydantic | `api/schemas/enrichment.py:263` | 5 |
| `CacheCheckResponse` | pydantic | `api/schemas/enrichment.py:399` | 5 |
| `CacheClearResponse` | pydantic | `api/schemas/enrichment.py:421` | 3 |
| `CursorPage` | pydantic | `api/schemas/pagination.py:83` | 3 |
| `DLQEntryResponse` | pydantic | `api/routers/admin_dlq.py:52` | 11 |
| `DLQListResponse` | pydantic | `api/routers/admin_dlq.py:68` | 4 |
| `EnrichmentRequest` | pydantic | `api/schemas/enrichment.py:17` | 2 |
| `EnrichmentResponse` | pydantic | `api/schemas/enrichment.py:212` | 5 |
| `EnrichmentResultData` | pydantic | `api/schemas/enrichment.py:172` | 6 |
| `ErrorDetail` | pydantic | `api/schemas/errors.py:41` | 5 |
| `ErrorResponse` | pydantic | `api/schemas/enrichment.py:444` | 4 |
| `ErrorResponse` | pydantic | `api/schemas/errors.py:64` | 1 |
| `ExportJobResponse` | pydantic | `api/routers/exports.py:80` | 10 |
| `ExportListResponse` | pydantic | `api/routers/exports.py:95` | 5 |
| `ExportRequest` | pydantic | `api/routers/exports.py:61` | 3 |
| `HealthCheckResponse` | pydantic | `api/schemas/enrichment.py:94` | 4 |
| `JobResultResponse` | pydantic | `api/routers/async_jobs.py:77` | 4 |
| `JobStatusResponse` | pydantic | `api/routers/async_jobs.py:60` | 12 |
| `LoginRequest` | pydantic | `api/routers/auth.py:24` | 2 |
| `MetricsResponse` | pydantic | `api/schemas/enrichment.py:146` | 4 |
| `PaginatedResponse` | pydantic | `api/schemas/pagination.py:25` | 4 |
| `RateLimitErrorResponse` | pydantic | `api/schemas/enrichment.py:480` | 4 |
| `ReadinessCheckResponse` | pydantic | `api/schemas/enrichment.py:128` | 3 |
| `RefreshRequest` | pydantic | `api/routers/auth.py:48` | 1 |
| `RejectRequest` | pydantic | `api/routers/review.py:44` | 2 |
| `ResearchJobListResponse` | pydantic | `api/routers/research_jobs.py:45` | 2 |
| `ResearchJobResponse` | pydantic | `api/routers/research_jobs.py:27` | 11 |
| `ResolveResponse` | pydantic | `api/routers/admin_dlq.py:77` | 3 |
| `ReviewQueueEntryResponse` | pydantic | `api/routers/review.py:56` | 11 |
| `SemanticSearchRequest` | pydantic | `api/schemas/semantic_search.py:12` | 5 |
| `SemanticSearchResponse` | pydantic | `api/schemas/semantic_search.py:100` | 6 |
| `SemanticSearchResultItem` | pydantic | `api/schemas/semantic_search.py:66` | 11 |
| `ServiceUnavailableErrorResponse` | pydantic | `api/schemas/enrichment.py:516` | 4 |
| `SignupRequest` | pydantic | `api/routers/auth.py:36` | 2 |
| `StrictRequestModel` | pydantic | `api/schemas/validation.py:11` | 0 |
| `UserInfoResponse` | pydantic | `api/routers/auth.py:69` | 3 |
| `UserPayload` | pydantic | `api/dependencies.py:72` | 3 |

## config.py/ (8 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `APIConfig` | pydantic | `config.py:77` | 8 |
| `DataConfig` | pydantic | `config.py:138` | 4 |
| `DatabaseConfig` | pydantic | `config.py:21` | 3 |
| `LoggingConfig` | pydantic | `config.py:119` | 5 |
| `RedisConfig` | pydantic | `config.py:39` | 2 |
| `SecurityConfig` | pydantic | `config.py:101` | 3 |
| `Settings` | pydantic | `config.py:172` | 76 |
| `SupabaseConfig` | pydantic | `config.py:68` | 4 |

## core/ (6 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `AIReadinessScoringConfig` | pydantic | `core/scoring_config.py:160` | 5 |
| `CompetitivePositionConfig` | pydantic | `core/scoring_config.py:86` | 11 |
| `CompositeScoringConfig` | pydantic | `core/scoring_config.py:125` | 6 |
| `FinancialHealthConfig` | pydantic | `core/scoring_config.py:46` | 24 |
| `GrowthScoringConfig` | pydantic | `core/scoring_config.py:17` | 16 |
| `ScoringSettings` | pydantic | `core/scoring_config.py:185` | 5 |

## data/ (21 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `BatchEnrichmentOutcome` | pydantic | `data/unified/batch_outcomes.py:14` | 4 |
| `CompanyAIAssessment` | pydantic | `data/company_research.py:86` | 8 |
| `CompanyFinancials` | pydantic | `data/company_research.py:39` | 9 |
| `CompanyGrowthSignals` | pydantic | `data/company_research.py:74` | 7 |
| `CompanyLeadership` | pydantic | `data/company_research.py:29` | 5 |
| `CompanyNews` | pydantic | `data/company_research.py:99` | 5 |
| `CompanyProducts` | pydantic | `data/company_research.py:53` | 5 |
| `CompanyResearch` | pydantic | `data/company_research.py:109` | 23 |
| `CompanyTechnology` | pydantic | `data/company_research.py:63` | 6 |
| `CurrencyRate` | pydantic | `data/markets/models.py:66` | 4 |
| `FundingData` | pydantic | `data/sources/models.py:44` | 8 |
| `GlobalStockData` | pydantic | `data/markets/models.py:78` | 13 |
| `IndexData` | pydantic | `data/markets/models.py:137` | 8 |
| `LinkedInData` | pydantic | `data/sources/models.py:32` | 7 |
| `MarketDataPoint` | pydantic | `data/markets/models.py:127` | 5 |
| `MarketIndex` | pydantic | `data/markets/models.py:56` | 5 |
| `NewsArticle` | pydantic | `data/sources/models.py:10` | 6 |
| `PatentData` | pydantic | `data/sources/models.py:57` | 5 |
| `PressCoverage` | pydantic | `data/sources/models.py:21` | 6 |
| `ProductInfo` | pydantic | `data/sources/models.py:67` | 6 |
| `StockExchange` | pydantic | `data/markets/models.py:42` | 5 |

## domain/ (31 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `AggregatedDataRecord` | pydantic | `domain/models.py:947` | 8 |
| `AggregatedFact` | pydantic | `domain/models.py:921` | 13 |
| `ApiKey` | pydantic | `domain/models.py:1090` | 11 |
| `Company` | pydantic | `domain/models/company_refactored.py:124` | 85 |
| `Company` | pydantic | `domain/models.py:151` | 97 |
| `CompanyAnalysisAuditTrail` | pydantic | `domain/models.py:1036` | 19 |
| `CompanyValidator` | pydantic | `domain/validators.py:14` | 5 |
| `CompetitiveOverlap` | pydantic | `domain/models.py:842` | 6 |
| `ConfidenceCalibration` | sqlalchemy | `domain/facts.py:240` | 15 |
| `DataSourceConflict` | sqlalchemy | `domain/facts.py:178` | 22 |
| `DateRange` | pydantic | `domain/value_objects.py:200` | 2 |
| `Fact` | sqlalchemy | `domain/facts.py:54` | 11 |
| `FactSource` | sqlalchemy | `domain/facts.py:113` | 7 |
| `FinancialMetric` | pydantic | `domain/models.py:89` | 15 |
| `GatheringBatch` | sqlalchemy | `domain/facts.py:25` | 5 |
| `GatheringBatch` | pydantic | `domain/models.py:1004` | 17 |
| `MarketAnalysis` | pydantic | `domain/models.py:749` | 11 |
| `MarketCondition` | pydantic | `domain/simulation.py:31` | 5 |
| `Money` | pydantic | `domain/value_objects.py:56` | 2 |
| `Percentage` | pydantic | `domain/value_objects.py:110` | 1 |
| `RawDataRecord` | pydantic | `domain/models.py:900` | 6 |
| `RawDataSource` | pydantic | `domain/models.py:882` | 11 |
| `RefreshMetadata` | sqlalchemy | `domain/facts.py:144` | 11 |
| `Scenario` | pydantic | `domain/simulation.py:43` | 5 |
| `Score` | pydantic | `domain/value_objects.py:141` | 1 |
| `ScoreComponent` | pydantic | `domain/models.py:794` | 5 |
| `ScoringExplanation` | pydantic | `domain/models.py:806` | 5 |
| `ScoringInputValidator` | pydantic | `domain/validators.py:65` | 5 |
| `SignalExtraction` | pydantic | `domain/models.py:971` | 9 |
| `SignalExtractionRecord` | pydantic | `domain/models.py:993` | 4 |
| `SimulationResult` | pydantic | `domain/simulation.py:55` | 9 |

## evidence/ (5 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `Claim` | pydantic | `evidence/models.py:62` | 27 |
| `ConfidenceComponent` | pydantic | `evidence/models.py:53` | 4 |
| `Contradiction` | pydantic | `evidence/models.py:172` | 10 |
| `EvidenceReadiness` | pydantic | `evidence/models.py:201` | 13 |
| `SourceDocument` | pydantic | `evidence/models.py:135` | 16 |

## exporters/ (2 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `SWOTAnalysis` | pydantic | `exporters/report_generators/base.py:12` | 4 |
| `StrategicRecommendations` | pydantic | `exporters/report_generators/base.py:21` | 1 |

## infrastructure/ (27 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `ApiKeyRecord` | sqlalchemy | `infrastructure/models/infrastructure.py:87` | 11 |
| `ApiKeyUsageRecord` | sqlalchemy | `infrastructure/models/infrastructure.py:135` | 7 |
| `AuditTrailRecord` | sqlalchemy | `infrastructure/models/company.py:293` | 0 |
| `Base` | sqlalchemy | `infrastructure/models/base.py:6` | 0 |
| `CompanyRecord` | sqlalchemy | `infrastructure/models/company.py:21` | 0 |
| `ConnectorFactPayload` | pydantic | `infrastructure/fact_payloads.py:12` | 7 |
| `ContradictionRecord` | sqlalchemy | `infrastructure/models/research.py:221` | 12 |
| `ContradictionTransitionRecord` | sqlalchemy | `infrastructure/models/research.py:260` | 8 |
| `DataAccessAuditRecord` | sqlalchemy | `infrastructure/models/audit.py:20` | 0 |
| `EmbeddingRecord` | sqlalchemy | `infrastructure/vector_store.py:69` | 0 |
| `EnrichmentAuditRecord` | sqlalchemy | `infrastructure/models/enrichment.py:20` | 0 |
| `EnrichmentCacheRecord` | sqlalchemy | `infrastructure/models/enrichment.py:77` | 0 |
| `EnrichmentJobRecord` | sqlalchemy | `infrastructure/models/enrichment.py:129` | 0 |
| `EvidenceReadinessRecord` | sqlalchemy | `infrastructure/models/research.py:189` | 12 |
| `ExportJobRecord` | sqlalchemy | `infrastructure/models/export.py:34` | 14 |
| `MarketSnapshot` | sqlalchemy | `infrastructure/models/company.py:252` | 0 |
| `MetricObservationRecord` | sqlalchemy | `infrastructure/models/research.py:153` | 8 |
| `OutboxRecord` | sqlalchemy | `infrastructure/models/infrastructure.py:19` | 10 |
| `ReleaseGateAuditRecord` | sqlalchemy | `infrastructure/models/enrichment.py:191` | 0 |
| `ResearchArtifactRecord` | sqlalchemy | `infrastructure/models/research.py:91` | 7 |
| `ResearchJobRecord` | sqlalchemy | `infrastructure/models/research.py:281` | 13 |
| `ResearchRunRecord` | sqlalchemy | `infrastructure/models/research.py:34` | 15 |
| `ResearchStageRecord` | sqlalchemy | `infrastructure/models/research.py:65` | 8 |
| `ScoringRecord` | sqlalchemy | `infrastructure/models/company.py:168` | 0 |
| `SignalRecord` | sqlalchemy | `infrastructure/models/company.py:214` | 0 |
| `SourceDocumentRecord` | sqlalchemy | `infrastructure/models/research.py:119` | 12 |
| `TenantRecord` | sqlalchemy | `infrastructure/models/infrastructure.py:40` | 0 |

## intelligence/ (3 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `CapabilityMatch` | pydantic | `intelligence/capability_overlap.py:33` | 5 |
| `CapabilityOverlapMatrix` | pydantic | `intelligence/capability_overlap.py:167` | 8 |
| `EneveCapability` | pydantic | `intelligence/capability_overlap.py:23` | 5 |

## llm/ (3 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `CompanyExtractionResponse` | pydantic | `llm/schemas/research.py:53` | 15 |
| `ResearchPlanResponse` | pydantic | `llm/schemas/research.py:25` | 2 |
| `SearchQueryItem` | pydantic | `llm/schemas/research.py:15` | 3 |

## research/ (4 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `PipelineRunState` | pydantic | `research/contracts.py:67` | 4 |
| `ResearchState` | typed_dict_or_namedtuple | `research/graph/state.py:40` | 20 |
| `StageRequestEnvelope` | pydantic | `research/contracts.py:24` | 6 |
| `StageResponseEnvelope` | pydantic | `research/contracts.py:33` | 8 |

## review_queue/ (1 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `ReviewQueueEntry` | pydantic | `review_queue/models.py:29` | 11 |

## security/ (2 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `TokenResponse` | pydantic | `security/jwt_handler.py:23` | 3 |
| `UserPayload` | pydantic | `security/jwt_handler.py:14` | 4 |

## tenant/ (6 schemas)

| Class | Type | File | Fields |
|-------|------|------|--------|
| `Tenant` | pydantic | `tenant/models.py:36` | 8 |
| `TenantConfig` | pydantic | `tenant/models.py:101` | 11 |
| `TenantFeatures` | pydantic | `tenant/models.py:81` | 6 |
| `TenantLimits` | pydantic | `tenant/models.py:63` | 5 |
| `TenantUsage` | pydantic | `tenant/models.py:220` | 6 |
| `TenantUser` | pydantic | `tenant/models.py:199` | 7 |
