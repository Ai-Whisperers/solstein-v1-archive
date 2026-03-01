# STORY-125: Restore 20 Dropped Fields to Excel Export

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-033: Data Completeness & Export Integrity |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> Forensic audit found ~20 fields present in domain models are NOT exported: employee_cagr_3yr, open_positions, lead_investors, funding_rounds, funding_war_chest, tech_stack, key_customers, parent_company, subsidiaries, acquisitions, notes, source_links, revenue_timeline, revenue_cagr_5yr, revenue_per_employee_eur_k, data_availability, data_source_per_field, merge_conflicts.

## Problem Statement

The Excel export is the primary deliverable for PE/VC analysts. When they receive a report, they expect it to contain all the data the platform has collected. It doesn't. Twenty fields — including critical competitive intelligence like tech_stack, funding_war_chest, and parent_company relationships — are silently dropped during export. The analyst doesn't know these fields exist. The platform knows but doesn't tell them. This is data loss presented as a feature.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Data Integrity** | 20 fields collected but never delivered |
| **User Experience** | Analysts make decisions on incomplete data |
| **Trust** | Platform appears to have less data than it actually does |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/exporters/excel.py` | Missing 20 fields |
| `src/solstein/domain/models.py` | Has fields that aren't exported |

## Architectural Requirements

- All 20 identified fields added to Excel export
- New worksheet "Advanced Data" for less commonly used fields (parent_company, subsidiaries, acquisitions, notes)
- tech_stack and key_customers added to main Company sheet
- funding_rounds and funding_war_chest added to Financials sheet
- revenue_timeline as time-series data in new "Revenue History" sheet
- source_links preserved as hyperlinks where possible
- Export schema documented: which fields go to which sheets
- Backward compatibility: existing export consumers not broken by new columns

## Acceptance Criteria

- [ ] All 20 fields present in exported Excel
- [ ] New "Advanced Data" sheet contains parent/subsidiary relationships
- [ ] New "Revenue History" sheet contains time-series data
- [ ] Existing export tests still pass (backward compatibility)
- [ ] Export schema documentation committed

## Definition of Done

- **Tests Required**: Manual verification: export a company, open Excel, verify all 20 fields
- **Documentation Required**: Export schema doc
- **Code Review Gate**: Reviewer checks each of the 20 fields against the export

## Notes

Data loss presented as a feature.
