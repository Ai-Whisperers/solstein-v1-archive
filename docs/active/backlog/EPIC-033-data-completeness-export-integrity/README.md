# EPIC-033: Data Completeness & Export Integrity

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Created** | 2026-03-01 |
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

---

## Delivery Sequence

```
STORY-127 (Deduplicate)
    │
    ▼
STORY-125 (Restore Fields)
    │
    ▼
STORY-126 (Schema Validation)
    │
    ▼
STORY-128 (Field Lineage Docs)
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

- **EPIC-030: Export Pipeline Modernization** — This epic assumes the export pipeline architecture established in EPIC-030 is in place. STORY-125 and STORY-126 build on top of that foundation.

---

## Notes

The root cause of this failure is architectural: the export layer was built without a contract. There is no schema, no validation, no test that asserts "these fields must be present." The export tests validate what the export currently produces, not what it should produce. This is a common failure mode — tests that describe behavior rather than specify it — and it means the test suite actively conceals the problem.

The fix is not just adding 20 fields. The fix is establishing the contract that prevents the next 20 fields from being silently dropped.
