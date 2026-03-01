# EPIC-033: Data Completeness & Export Integrity

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Owner** | Product Engineering |
| **Created** | 2026-03-01 |

## Context

Forensic audit found ~20 fields present in domain models are silently DROPPED in Excel export. Fields like parent_company, subsidiaries, tech_stack, revenue_timeline, funding_war_chest never make it to the analyst's deliverable. Additionally, profit_margin exists in BOTH FinancialMetric AND Company top-level — risking divergence.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-125 | Restore 20 Dropped Fields to Excel Export | P1 |
| STORY-126 | Add Export Schema Validation | P1 |
| STORY-127 | Deduplicate profit_margin and employee Fields | P1 |
| STORY-128 | Document Field Lineage from Ingestion to Export | P2 |

## Dependencies

- EPIC-030 (export pipeline modernization)

## Notes

This is data loss presented as a feature. Analysts make decisions on incomplete data because the export silently drops fields that were collected.
