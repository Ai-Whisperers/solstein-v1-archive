# STORY-128: Document Field Lineage from Ingestion to Export

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-033: Data Completeness & Export Integrity |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-125 (Restore 20 Dropped Fields), STORY-126 (Export Schema Validation), STORY-127 (Deduplicate Fields) — lineage documentation is written after the correct data flow is established |

---

## The Audit Verdict

> "No documentation exists showing which fields flow from ingestion → domain → analytics → export. Silent drops discovered only by forensic audit."

---

## Problem Statement

The platform has no map of its data flow. Fields are added to ingestion, maybe added to domain, maybe consumed by analytics, maybe exported. The only way to know if a field makes it to the analyst is to trace it manually through 10+ files. This is how 20 fields were lost — nobody knew they were supposed to be exported because there was no documentation saying they should be. The fix is a field lineage document that traces each field from source to deliverable.

The absence of lineage documentation is not a documentation problem — it is a systems design problem. When a developer adds a new field to an ingestion adapter, there is no checklist, no template, no CI check that asks "where does this field go?" The field gets added to the adapter, maybe gets added to the domain model, and then silently stops there because nobody thought to ask whether it should appear in the export. The 20 dropped fields are not the result of negligence; they are the result of a system that provides no guidance on what "done" means for a new field.

The lineage document is the map that makes "done" explicit. It defines the expected journey of every field: from which adapter it enters the system, through which domain model it passes, which analytics components consume it, and in which export sheet it ultimately appears. When a field is added to the domain model but not to the lineage document, the CI check warns. When a field appears in the lineage document as "exported to Financials sheet" but the export schema validation fails to find it there, the CI fails. The two systems — lineage documentation and schema validation — form a closed loop that makes silent field loss structurally impossible.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Developer Experience** | No visibility into data flow; adding a new field requires archaeology across 10+ files to understand where it should go |
| **Data Integrity** | Fields lost in undocumented gaps between system layers; loss is invisible until forensic audit |
| **Maintainability** | Removing or renaming a field requires manual search to find all consumers; no authoritative list exists |
| **Onboarding** | New developers cannot understand the data model without reading every file; knowledge is tribal |

---

## Affected Files

| File | Issue |
|------|-------|
| `docs/` | No field lineage documentation exists; data flow is undocumented |

---

## Architectural Requirements

### Field Lineage Document Structure

- A field lineage document must be created at `docs/field-lineage.md`
- The document must cover every field in the domain model — not just the 20 previously dropped fields
- For each field, the lineage entry must specify:
  - **Field name** — canonical name as defined in the domain model
  - **Source adapter** — which ingestion adapter introduces this field (e.g., Crunchbase adapter, manual entry, computed)
  - **Domain model** — which domain model class holds this field (e.g., `Company`, `FinancialMetric`, `FundingData`)
  - **Analytics consumers** — which analytics components read this field (or "None" if not consumed by analytics)
  - **Export destination** — which Excel sheet this field appears on (or "Not exported" if intentionally excluded)
  - **Export column header** — the human-readable column name in the Excel output
  - **Notes** — any special handling, derivation logic, or known issues

### Mermaid Data Flow Diagram

- A Mermaid diagram must be committed to `docs/diagrams/field-data-flow.md` showing the high-level data flow
- The diagram must show the four layers: Ingestion Adapters → Domain Models → Analytics Engine → Export Engine
- The diagram must show which domain models feed which analytics components and which export sheets
- The diagram must be accurate — it must reflect the actual system architecture after STORY-125, STORY-126, and STORY-127 are complete, not the pre-fix architecture

### Gap Analysis Section

- The lineage document must include a "Current Gaps" section identifying fields that are present in the domain model but intentionally not exported
- For each intentionally unexported field, a justification must be provided (e.g., "internal metadata, not relevant to analyst deliverable")
- Fields that are unexported without justification must be flagged as potential gaps requiring a decision
- The gap analysis section must be reviewed and signed off by a product owner or lead engineer

### CI Check for Undocumented Fields

- A CI check must be implemented that compares the fields defined in the domain model against the fields documented in the lineage document
- If a field exists in the domain model but is absent from the lineage document, the CI check must emit a warning
- The warning must name the specific undocumented field(s)
- The CI check must not fail the build (warning only) — the goal is visibility, not a hard gate that blocks development
- The CI check must run on every build that modifies `src/solstein/domain/models.py`

### Living Document Requirements

- The lineage document must be treated as a living document, updated whenever fields are added, removed, or rerouted
- The document must include a "Last Updated" date and a changelog section recording significant changes
- The CI check for undocumented fields is the enforcement mechanism that keeps the document current

---

## Acceptance Criteria

- [ ] `docs/field-lineage.md` exists and covers all fields in the domain model
- [ ] Each field entry specifies: source adapter, domain model, analytics consumers, export destination, export column header
- [ ] The 20 previously dropped fields are explicitly documented with their correct export destinations (as established by STORY-125)
- [ ] Mermaid diagram committed to `docs/diagrams/field-data-flow.md` showing Ingestion → Domain → Analytics → Export flow
- [ ] Diagram accurately reflects the system architecture after STORY-125/126/127 are complete
- [ ] "Current Gaps" section identifies all intentionally unexported fields with justifications
- [ ] CI check warns when a domain model field is absent from the lineage document
- [ ] CI check names the specific undocumented field(s) in its warning output
- [ ] Lineage document includes a changelog section and "Last Updated" date
- [ ] A new developer, given only the lineage document, can trace any field from its source adapter to its export column without reading source code

---

## Definition of Done

- **Tests Required**: CI check verified — add a dummy field to the domain model without updating the lineage document, confirm CI emits a warning naming that field. Remove the dummy field. Verify the warning disappears.
- **Documentation Required**: `docs/field-lineage.md` committed with full field coverage. `docs/diagrams/field-data-flow.md` committed with Mermaid diagram. Gap analysis section reviewed and signed off.
- **Code Review Gate**: Reviewer verifies the diagram accurately reflects the actual code architecture (not aspirational). Reviewer spot-checks 5 fields from the lineage document against the source code to verify accuracy. Reviewer confirms the 20 previously dropped fields are correctly documented.

---

## Notes

**On the diagram accuracy requirement:** The Mermaid diagram must reflect the system as it exists after STORY-125, STORY-126, and STORY-127 are complete. It must not be a wishful architecture diagram. If the diagram shows a field flowing from ingestion to export and the code does not actually implement that flow, the diagram is worse than no diagram — it is actively misleading. The code review gate must verify diagram accuracy against the actual implementation.

**On the "living document" challenge:** Documentation that is not enforced becomes stale. The CI check for undocumented fields is the enforcement mechanism. It is intentionally a warning rather than a hard failure to avoid blocking development when a field is added quickly and the lineage doc update is deferred. However, the warning must be visible and must be addressed before the next release. A policy decision is needed: how long can an undocumented field remain in the domain model before the warning escalates to a failure?

**On the gap analysis sign-off requirement:** The gap analysis identifies fields that are collected but not exported. Some of these are legitimately internal (e.g., `merge_conflicts` is a data quality flag, not analyst intelligence). Others may be fields that should be exported but were overlooked. The sign-off requirement ensures a human makes a deliberate decision about each gap, rather than the gap persisting by default.

**On scope:** This story documents the data flow as it exists after the other three stories in this epic are complete. It is not a design document for a future state. The lineage document describes reality, not aspiration. If reality is messy, the document reflects that mess — and the mess becomes visible, which is the point.

**Delivery note:** This story is explicitly last in the delivery sequence. Writing lineage documentation before the data flow is correct (i.e., before STORY-125/126/127) would document the broken state and require immediate revision. The documentation effort is most valuable when it describes a system that is working correctly.
