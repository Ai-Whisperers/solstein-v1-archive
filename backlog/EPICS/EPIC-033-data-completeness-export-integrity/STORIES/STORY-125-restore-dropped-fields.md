# STORY-125: Restore 20 Dropped Fields to Excel Export

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-033: Data Completeness & Export Integrity |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-127 (Deduplicate Fields — canonical sources must be established before export is rebuilt) |

---

## The Audit Verdict

> "Forensic audit found ~20 fields present in domain models are NOT exported: `employee_cagr_3yr`, `open_positions`, `lead_investors`, `funding_rounds`, `funding_war_chest`, `tech_stack`, `key_customers`, `parent_company`, `subsidiaries`, `acquisitions`, `notes`, `source_links`, `revenue_timeline`, `revenue_cagr_5yr`, `revenue_per_employee_eur_k`, `data_availability`, `data_source_per_field`, `merge_conflicts`."

---

## Problem Statement

The Excel export is the primary deliverable for PE/VC analysts. When they receive a report, they expect it to contain all the data the platform has collected. It doesn't. Twenty fields — including critical competitive intelligence like `tech_stack`, `funding_war_chest`, and `parent_company` relationships — are silently dropped during export. The analyst doesn't know these fields exist. The platform knows but doesn't tell them. This is data loss presented as a feature.

The silence is the worst part. There is no warning in the export, no footnote saying "additional fields available," no log entry recording the omission. The analyst opens their Excel file, sees a professional-looking report, and makes investment decisions on data that is, at minimum, 40% incomplete. The platform has done its job of collecting the data. It simply forgot to deliver it.

This is not a minor gap. Fields like `parent_company` and `subsidiaries` are foundational to competitive mapping. `tech_stack` is a primary signal for technology-sector PE deals. `funding_war_chest` directly informs competitive threat assessment. These are not edge-case fields that analysts occasionally want — they are core intelligence that the platform was explicitly built to surface. Their absence from the export is a product failure, not a backlog item.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Data Integrity** | 20 fields collected by the platform never reach the analyst's deliverable; data loss is total and silent |
| **User Experience** | Analysts make investment decisions on structurally incomplete data without knowing it is incomplete |
| **Trust** | Platform appears to have less intelligence capability than it actually does; analysts may seek alternative tools |
| **Competitive Positioning** | The platform's differentiation is depth of intelligence; the export undermines that differentiation at the moment of delivery |

---

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/exporters/excel.py` | Primary export logic; missing field mappings for all 20 dropped fields |
| `src/solstein/domain/models.py` | Source of truth for field definitions; export does not consume all defined fields |

---

## Architectural Requirements

### Field Routing by Sheet

The 20 dropped fields must be routed to appropriate sheets based on their nature and expected analyst workflow:

**Main "Company" Sheet (existing)**
- `tech_stack` — technology profile is a primary company attribute
- `key_customers` — customer intelligence belongs alongside company overview
- `open_positions` — hiring signal is a company-level indicator
- `data_availability` — data quality indicator relevant to all company data

**"Financials" Sheet (existing)**
- `funding_rounds` — funding history belongs with financial data
- `funding_war_chest` — available capital is a financial metric
- `lead_investors` — investor identity is financial context
- `revenue_cagr_5yr` — growth metric belongs with revenue data
- `revenue_per_employee_eur_k` — efficiency metric belongs with financial data
- `employee_cagr_3yr` — workforce growth belongs with financial metrics

**New "Revenue History" Sheet**
- `revenue_timeline` — time-series data requires its own sheet; cannot be flattened into a single row without losing structure
- Sheet must support variable-length time series (companies have different numbers of historical data points)
- Columns: Company Name, Year, Revenue (EUR M), Source

**New "Advanced Data" Sheet**
- `parent_company` — corporate structure data; less frequently needed but critical when relevant
- `subsidiaries` — corporate structure data
- `acquisitions` — M&A history
- `notes` — analyst notes and qualitative observations
- `source_links` — data provenance; preserved as hyperlinks where the value is a valid URL
- `data_source_per_field` — field-level provenance metadata
- `merge_conflicts` — data quality flags indicating conflicting source data

### General Requirements

- All 20 fields must appear in the exported Excel with no exceptions
- Fields with list or structured values (e.g., `tech_stack`, `subsidiaries`, `funding_rounds`) must be serialized in a human-readable format appropriate for Excel consumption — comma-separated strings for simple lists, structured rows for complex objects
- `source_links` values that are valid URLs must be rendered as Excel hyperlinks, not plain text
- New sheets must follow the existing visual style (header formatting, column widths, freeze panes) established in the current export
- Existing sheets must not have columns removed or reordered — only additions are permitted (backward compatibility)
- Export schema documentation must be committed alongside the implementation, specifying which fields appear on which sheets
- The export must handle missing/null values for all 20 fields gracefully — a field being absent from a specific company's data must not cause the export to fail or omit the company

---

## Acceptance Criteria

- [ ] All 20 identified dropped fields are present in the exported Excel file
- [ ] `tech_stack`, `key_customers`, `open_positions`, and `data_availability` appear on the main Company sheet
- [ ] `funding_rounds`, `funding_war_chest`, `lead_investors`, `revenue_cagr_5yr`, `revenue_per_employee_eur_k`, and `employee_cagr_3yr` appear on the Financials sheet
- [ ] A new "Revenue History" sheet exists and contains `revenue_timeline` data as time-series rows
- [ ] A new "Advanced Data" sheet exists and contains `parent_company`, `subsidiaries`, `acquisitions`, `notes`, `source_links`, `data_source_per_field`, and `merge_conflicts`
- [ ] `source_links` values that are valid URLs are rendered as Excel hyperlinks
- [ ] Existing export tests pass without modification (backward compatibility confirmed)
- [ ] Export schema documentation committed to `docs/export-schema.md` specifying field-to-sheet mapping
- [ ] Export does not fail when any of the 20 fields is null or absent for a given company
- [ ] New sheets follow existing visual style (headers, column widths, freeze panes)

---

## Definition of Done

- **Tests Required**: Manual verification — export a company with known data for all 20 fields, open the Excel file, confirm each field is present in the correct sheet. Automated regression test asserting all 20 field names appear in the export output.
- **Documentation Required**: `docs/export-schema.md` committed, listing every exported field, its sheet, its column header, and its data type.
- **Code Review Gate**: Reviewer checks each of the 20 fields individually against the export output. No field may be marked "done" without explicit confirmation it appears in the correct sheet with correct data.

---

## Notes

**On serialization of complex fields:** Fields like `tech_stack` (likely a list), `funding_rounds` (likely a list of objects), and `subsidiaries` (likely a list of company references) require a serialization decision. The requirement is human-readable Excel output, not machine-parseable data. Comma-separated strings are acceptable for simple lists. For complex objects like `funding_rounds`, a structured approach (one row per round in a dedicated section or sheet) is preferred over JSON-in-a-cell.

**On backward compatibility:** The constraint is additive-only. Existing columns on existing sheets must not move, be renamed, or be removed. New columns may be appended to the right of existing columns. New sheets may be added. This ensures existing downstream consumers (scripts, other tools) that reference columns by position or name are not broken.

**On the "Advanced Data" sheet name:** The name is intentionally generic. If the team has a preferred naming convention for supplementary data sheets, that convention should be applied — but the sheet must exist and must contain the specified fields.

**Dependency note:** This story depends on STORY-127 (Deduplicate Fields). The export must pull `profit_margin` and `employee_count` from the canonical source established in STORY-127, not from the duplicated top-level Company fields. Implementing this story before STORY-127 risks building the export on top of the wrong source of truth.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
