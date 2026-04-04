# EPIC-033: Data Completeness & Export Integrity

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High ([STORY-381](STORIES/STORY-381.md) is P0 — migration inserts untagged records) |
| **Severity** | Critical |
| **Created** | 2026-03-01 |
| **Updated** | 2026-04-03 ([STORY-381](STORIES/STORY-381.md) added from contamination audit) |
| **Owner** | Platform Engineering |
| **Dependencies** | EPIC-030: Export Pipeline Modernization |

---

## Executive Summary

A forensic audit of the Solstein export pipeline revealed that approximately **20 fields** present in the domain models are silently dropped before reaching the analyst's Excel deliverable. Fields representing critical competitive intelligence — parent company relationships, subsidiary structures, technology stacks, funding war chests, and revenue timelines — are collected by the platform and then discarded at the export boundary without warning, without logging, and without any mechanism to detect the loss.

The platform knows more than it tells. That is the problem.

Additionally, the audit identified a structural consistency hazard: `profit_margin` exists in both `FinancialMetric` and `Company` top-level models with no synchronization mechanism. The same metric can simultaneously hold two different values depending on which model was last updated. `employees` (in `FinancialMetric`) and `employee_count` (in `Company`) present the same problem. There is no single source of truth, and the export pulls from both.

This epic addresses the full scope of the data completeness failure: restoring dropped fields, establishing a schema validation contract, eliminating duplicated fields, and documenting field lineage so this class of failure cannot silently recur.

---

## Audit Findings

> *"The Excel export is the primary deliverable for PE/VC analysts. When they receive a report, they expect it to contain all the data the platform has collected. It doesn't. Twenty fields — including critical competitive intelligence like tech_stack, funding_war_chest, and parent_company relationships — are silently dropped during export. The analyst doesn't know these fields exist. The platform knows but doesn't tell them."*

### Dropped Fields (20 confirmed)

| Field | Domain Location | Export Status |
|-------|----------------|---------------|
| `employee_cagr_3yr` | FinancialMetric | ❌ Dropped |
| `open_positions` | Company | ❌ Dropped |
| `lead_investors` | FundingData | ❌ Dropped |
| `funding_rounds` | FundingData | ❌ Dropped |
| `funding_war_chest` | FundingData | ❌ Dropped |
| `tech_stack` | Company | ❌ Dropped |
| `key_customers` | Company | ❌ Dropped |
| `parent_company` | Company | ❌ Dropped |
| `subsidiaries` | Company | ❌ Dropped |
| `acquisitions` | Company | ❌ Dropped |
| `notes` | Company | ❌ Dropped |
| `source_links` | Company | ❌ Dropped |
| `revenue_timeline` | FinancialMetric | ❌ Dropped |
| `revenue_cagr_5yr` | FinancialMetric | ❌ Dropped |
| `revenue_per_employee_eur_k` | FinancialMetric | ❌ Dropped |
| `data_availability` | Company | ❌ Dropped |
| `data_source_per_field` | Company | ❌ Dropped |
| `merge_conflicts` | Company | ❌ Dropped |

### Duplication Hazards

| Field | Location A | Location B | Risk |
|-------|-----------|-----------|------|
| `profit_margin` | `FinancialMetric` | `Company` (top-level) | Divergence |
| `employees` / `employee_count` | `FinancialMetric` | `Company` (top-level) | Divergence |

---

## Stories

| Story | Title | Priority | Status |
|-------|-------|----------|--------|
| [STORY-125](STORIES/STORY-125-restore-dropped-fields.md) | Restore 20 Dropped Fields to Excel Export | P1 | 🔴 Not Started |
| [STORY-126](STORIES/STORY-126-export-schema-validation.md) | Add Export Schema Validation | P1 | 🔴 Not Started |
| [STORY-127](STORIES/STORY-127-deduplicate-fields.md) | Deduplicate profit_margin and employee Fields | P1 | 🔴 Not Started |
| [STORY-128](STORIES/STORY-128-document-field-lineage.md) | Document Field Lineage from Ingestion to Export | P2 | 🔴 Not Started |
| [STORY-250](STORIES/STORY-250-reconcile-export-schema-with-workbook-output.md) | Reconcile Export Schema Contract with Workbook Output | P1 | 🔴 Not Started |
| [STORY-381](STORIES/STORY-381.md) | Fix `load_competitor_data.py` migration — set `data_source_type` on all `CompanyRecord` inserts | **P0** | 🔴 READY |
| [STORY-384](STORIES/STORY-384.md) | Add `data_source_type` column to `CompanyRecord` DB schema + Alembic migration | **P0** | 🔴 READY |
| [STORY-386](STORIES/STORY-386.md) | Fix `load_competitor_data.py` — remove `get_database_url(test=True)` from production migration | **P0** | 🔴 READY |

> **[STORY-381](STORIES/STORY-381.md)** added 2026-04-03 from contamination audit. `_build_company_record()` in
> `src/solstein/migrations/load_competitor_data.py:53–80` sets `data_source="competitor_data.json"`
> (free-text) but never `data_source_type`, making migrated records indistinguishable from real data
> by the export gate. This is a P0 fix independent of all other EPIC-033 stories.

---

## Delivery Sequence

```
[STORY-127](STORIES/STORY-127-deduplicate-fields.md) (Deduplicate)
    │
    ▼
[STORY-125](STORIES/STORY-125-restore-dropped-fields.md) (Restore Fields)
    │
    ▼
[STORY-126](STORIES/STORY-126-export-schema-validation.md) (Schema Validation)
    │
    ▼
[STORY-128](STORIES/STORY-128-document-field-lineage.md) (Field Lineage Docs)
```

**Rationale:** Deduplication must precede field restoration to ensure the export pulls from a single canonical source. Schema validation must follow field restoration to validate the complete, correct export. Lineage documentation is written last, when the correct data flow is established and stable.

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Fields exported vs. fields in domain | ~60% | 100% |
| Duplicate field definitions | 2 pairs | 0 |
| Export schema validation coverage | 0% | 100% |
| Field lineage documentation coverage | 0% | 100% |
| CI detection of field drops | None | Automated |
| Exporter passes its own schema gate | No | Yes |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Backward compatibility break in export consumers | Medium | High | Additive-only changes to existing sheets; new sheets for new data |
| Data reconciliation reveals widespread divergence in duplicated fields | Medium | Medium | Reconciliation report generated before migration; manual review gate |
| Schema validation too strict, blocks valid exports | Low | Medium | Schema supports optional fields; validation is warn-before-fail in first release |
| Lineage doc becomes stale immediately | High | Medium | CI check warns on undocumented fields added to domain model |

---

## Dependencies

- **EPIC-030: Export Pipeline Modernization** — This epic assumes the export pipeline architecture established in EPIC-030 is in place. [STORY-125](STORIES/STORY-125-restore-dropped-fields.md) and [STORY-126](STORIES/STORY-126-export-schema-validation.md) build on top of that foundation.

---

## Notes

The root cause of this failure is architectural: the export layer was built without a contract. There is no schema, no validation, no test that asserts "these fields must be present." The export tests validate what the export currently produces, not what it should produce. This is a common failure mode — tests that describe behavior rather than specify it — and it means the test suite actively conceals the problem.

The fix is not just adding 20 fields. The fix is establishing the contract that prevents the next 20 fields from being silently dropped.

## Autonomous Continuation Notes

### Verified Codebase State (2026-04-04)

Direct file reads confirm the P0 schema gap is STILL PRESENT:

**`CompanyRecord` missing `data_source_type` column ([STORY-384](STORIES/STORY-384.md)):**
- `src/solstein/infrastructure/models/company.py:77` — only `data_source = Column(String(100), nullable=True)` exists
- No `data_source_type` column anywhere in the ORM model
- `alembic/versions/`: 22 migration files (001–019 + 3 merge/misc), **none add `data_source_type`** to `company_records`
- Without this column, the export gate at EPIC-052 cannot filter DB-loaded records by source type

**`load_competitor_data.py` never sets `data_source_type` ([STORY-381](STORIES/STORY-381.md)):**
- `src/solstein/migrations/load_competitor_data.py:77` — `_build_company_record()` sets `data_source="competitor_data.json"` (free-text) only
- No `data_source_type` argument passed to `CompanyRecord(...)` constructor — migrated competitor records are indistinguishable from real data by the gate

**`load_competitor_data.py` uses test DB URL in production path ([STORY-386](STORIES/STORY-386.md)):**
- The migration script calls `get_database_url(test=True)` — runs against the test database, not production
- Migrated records therefore never reach the production `company_records` table

**Execution order for P0 stories:**
1. [STORY-384](STORIES/STORY-384.md) — Add `data_source_type` column + Alembic migration 020 (required for 381 and 385 to have a column to write)
2. [STORY-381](STORIES/STORY-381.md) — Fix `load_competitor_data.py`: set `data_source_type="real"` on migrated records
3. [STORY-386](STORIES/STORY-386.md) — Fix `load_competitor_data.py`: remove `test=True` from `get_database_url()` call
4. [STORY-385](STORIES/STORY-385.md) (in EPIC-052) — Fix converter fallback from `"real"` to `"unknown"` — benefits from 384 being in place

**Minimum Verification for Future Agents:**
- After STORY-384: run `alembic upgrade head` and confirm `data_source_type` column present in `company_records` via `\d company_records`
- After STORY-381: confirm `_build_company_record()` passes `data_source_type="real"` to `CompanyRecord()`
- After STORY-386: confirm `get_database_url()` is called without `test=True`

**Required Working Style:**
- Follow `docs/reference/ENGINEERING_GUARDRAILS.md` and `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`
- Prefer narrow, machine-checkable progress — each story should include a test that proves the fix
