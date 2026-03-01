# STORY-128: Document Field Lineage from Ingestion to Export

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-033: Data Completeness & Export Integrity |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-125 |

## The Audit Verdict

> No documentation exists showing which fields flow from ingestion → domain → analytics → export. Silent drops discovered only by forensic audit.

## Problem Statement

The platform has no map of its data flow. Fields are added to ingestion, maybe added to domain, maybe consumed by analytics, maybe exported. The only way to know if a field makes it to the analyst is to trace it manually through 10+ files. This is how 20 fields were lost — nobody knew they were supposed to be exported because there was no documentation saying they should be. The fix is a field lineage document that traces each field from source to deliverable.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Developer Experience** | No visibility into data flow |
| **Data Integrity** | Fields lost in undocumented gaps |
| **Maintainability** | Adding a field requires archaeology |

## Affected Files

| File | Issue |
|------|-------|
| `docs/` | No lineage documentation |

## Architectural Requirements

- Field lineage documentation: for each field, list: source (adapter), domain model, analytics consumers, export destination
- Mermaid diagram showing data flow: Ingestion → Domain → Analytics → Export
- Gap analysis: fields present in domain but not in export (current gaps)
- CI check: if a field is added to domain model but not to lineage doc, warn
- Living document: updated when fields are added/removed

## Acceptance Criteria

- [ ] Lineage doc covers all 20 previously-dropped fields
- [ ] Mermaid diagram committed to docs/
- [ ] Gap analysis identifies current gaps
- [ ] CI warns on undocumented fields

## Definition of Done

- **Tests Required**: None
- **Documentation Required**: Field lineage document with Mermaid diagram
- **Code Review Gate**: New developer can trace any field from source to export using only the lineage doc

## Notes

Prevents future field loss through documentation.
