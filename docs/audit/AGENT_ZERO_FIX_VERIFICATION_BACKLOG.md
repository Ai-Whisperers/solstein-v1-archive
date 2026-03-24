# Agent Zero Fix Verification Backlog — 2026-03-23

**Purpose:** Document which fixes Ivan performed correctly and which ones require Agent Zero automation to detect and fix autonomously.

**Generated from:** FIX_INTEGRITY_AUDIT_2026-03-23.md

---

## ✅ FIXES PERFORMED CORRECTLY BY IVAN (No Agent Action Needed)

These are fixes that were implemented correctly and don't need automation:

| ID | Fix Description | File | Status |
|----|-----------------|------|--------|
| OK-01 | DataSourceType.WEB_SEARCH added | domain/models.py | ✅ Done |
| OK-02 | process_raw.py field remapping | workflow_nodes/process_raw.py | ✅ Done |
| OK-03 | extract_signals.py reads correct AggregatedFact fields | workflow_nodes/extract_signals.py | ✅ Done |
| OK-04 | RawDataSource schema consistent with all adapters | domain/models.py + adapters/* | ✅ Done |
| OK-05 | funding_unified source_type enum | adapters/enrichment/funding_unified.py | ✅ Done |
| OK-06 | web_search_unified source_type enum | adapters/enrichment/web_search_unified.py | ✅ Done |
| OK-07 | BatchFinancialReportGenerator inheritance | intelligence/financial_report_generator.py | ✅ Done |
| OK-08 | BatchGenealogyReportGenerator inheritance | intelligence/genealogy_report_generator.py | ✅ Done |
| OK-09 | BatchProtocolReportGenerator inheritance | intelligence/protocol_report_generator.py | ✅ Done |
| OK-10 | merger.py allow_empty_primary | data/unified/merger.py | ✅ Done |
| OK-11 | sec_edgar_refresh None date guard | infrastructure/connectors/sec_edgar_refresh.py | ✅ Done |
| OK-12 | business_metrics field renames | monitoring/business_metrics.py | ✅ Done |
| OK-13 | enrichment_batch status="partial" | api/routers/enrichment_batch.py | ✅ Done |
| OK-14 | market.py peer.id / target.id | api/routers/market.py | ✅ Done |
| OK-15 | scoring.py financials None guard | api/routers/scoring.py | ✅ Done |
| OK-16 | drill_down source.url fallback | api/routers/drill_down.py + drill_down_service.py | ✅ Done |
| OK-17 | evidence Cypher accepted/conflicting | evidence/repositories/company.py | ✅ Done |
| OK-18 | research_dual_write savepoint | infrastructure/research_dual_write.py | ✅ Done |
| OK-19 | coordinator_agent extracted_signals key | agents/coordinator_agent.py | ✅ Done |
| OK-20 | llm_providers.keys() join fix | config.py | ✅ Done |
| OK-21 | Classification boundaries consistent | domain/models.py | ✅ Done |
| OK-22 | saas_maturity None-guard removal | domain/models.py | ✅ Done |

---

## 🔴 BUGS FIXED DURING AUDIT (Agent Zero Should Detect These Patterns)

These bugs were discovered during the audit and fixed. Agent Zero should be equipped to detect these patterns automatically:

| ID | Bug Pattern | Detection Strategy | Fixed |
|----|-------------|-------------------|-------|
| BUG-01 | logic_fusion.py reads `.field` instead of `.fact_type` on AggregatedFact | Grep for `\.field` on AggregatedFact instances | ✅ Fixed in audit |
| BUG-02 | GrowthMomentumScorer penalty always clamped to 0 (architecture flaw) | Check scorer with base_score=0 + penalty application, verify effect | ✅ Fixed in audit |
| BUG-03 | Property `has_enrichment_errors` exists but never used | Grep for property definition, verify callers exist | ✅ Fixed in audit |

---

## ⚠️ ISSUES STILL PENDING (Agent Zero Should Track These)

These are known issues that were identified but not fully resolved. Agent Zero should track these for autonomous resolution:

| ID | Issue | Root Cause | Task # | Status |
|----|-------|------------|--------|--------|
| PEND-01 | conftest.py crashes at import without DATABASE_URL | get_test_database_url() has proper fallback in database_config.py | Task #1 | ✅ FIXED |
| PEND-02 | Extracted signals discarded from AgentTaskResult | Dead CoordinatorAgent code removed entirely (1df9c1d) | Task #6 | ✅ FIXED |
| PEND-03 | Legacy path in process_raw uses invalid DataSourceType fallback | DataSourceType.UNKNOWN is now a valid enum member | Task #7 | ✅ FIXED |
| PEND-04 | check_configuration() dead code | Not dead — actively called in main.py lifespan hook | Task #8 | ✅ NOT A BUG |
| PEND-05 | Hardcoded classification values not in single source | ai_readiness.py now uses CompanyClassification enum; competitive_mapping.py clean | Task #9 | ✅ FIXED |

---

## 🤖 AGENT ZERO DETECTION RULES

### High Priority (Runtime Crashers)

Agent Zero MUST detect these patterns automatically:

```python
# Rule 1: AggregatedFact field access
pattern: "fact.field" OR "fact.sources" 
context: AggregatedFact type
action: Raise error — use fact.fact_type, fact.sources_used

# Rule 2: Scorer penalty architecture validation
pattern: scorer with base_score=0 + negative_penalty
validation: Apply penalty to 0.0, verify result != 0.0 after clamp
action: If penalty ineffective, record ScoreComponent instead

# Rule 3: Property exists but no callers
pattern: @property defined on model
validation: Grep for usage of property name across codebase
action: If no callers, either use it or mark as candidate for removal
```

### Medium Priority (Silent Semantic Issues)

Agent Zero SHOULD detect these patterns:

```python
# Rule 4: DataSourceType fallback to invalid string
pattern: 'getattr(.*"unknown")' OR "source_type" with string default
action: Verify string is valid enum member

# Rule 5: Classification constants drift
pattern: Hardcoded numeric values for PHOENIX/SALT/LEAD
action: Cross-reference with domain/models.py constants

# Rule 6: Dead code after validation
pattern: Function checks what Pydantic already enforces
action: Flag as dead code, recommend removal
```

### Lower Priority (Code Quality)

```python
# Rule 7: Direct list access when property exists
pattern: len(model.list_field) without checking property
action: Suggest using property if available
```

---

## 📋 AGENT ZERO AUTOMATION CHECKLIST

Before marking any commit as "verified," Agent Zero should run:

- [ ] **Grep for deprecated field access** — `.field`, `.sources`, `.signal_category`
- [ ] **Runtime validation** — Scorer with missing data, verify score changes
- [ ] **Property usage check** — New property added → verify callers exist
- [ ] **Enum fallback validation** — String defaults must be valid enum members
- [ ] **Dead code detection** — Checks after Pydantic validation points
- [ ] **Classification constant drift** — All hardcoded values reference single source

---

## 📁 Related Documents

- `FIX_INTEGRITY_AUDIT_2026-03-23.md` — Full audit details
- `IVAN_FIXES_VERIFICATION_CHECKLIST.md` — Verification checklist
- `docs/active/backlog/EPIC-046-scoring-engine-correctness/` — Scoring fixes
- `docs/active/backlog/EPIC-012-type-safety-code-quality/` — Type safety EPIC

---

**Last Updated:** 2026-03-23
**Next Review:** After Agent Zero implementation validates against this backlog
