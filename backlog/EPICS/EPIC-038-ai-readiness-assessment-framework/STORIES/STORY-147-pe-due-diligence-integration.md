# STORY-147: PE Due Diligence Integration Module

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | High |
| **Epic** | EPIC-038: AI-Readiness Assessment Framework |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-145, STORY-146 |

## The Strategic Context

> "AI-enabled due diligence exposes perfume on coal."

## Problem Statement

Traditional PE due diligence looks at financials, market position, and team. It doesn't systematically evaluate AI-readiness. Solstein needs a due diligence module that integrates AI-readiness assessment into the standard PE workflow: data room integration, red flag identification, competitive AI positioning, and investment memo generation. This makes Solstein indispensable to the due diligence process, not just a nice-to-have research tool.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Workflow Integration** | Solstein becomes part of standard DD process |
| **Red Flag Detection** | Identify AI risks before investment |
| **Competitive Edge** | AI-readiness as DD differentiator |

## Affected Files

| File | Issue |
|------|-------|
| New: `application/due_diligence/` | Does not exist |
| `exporters/` | No DD report export |

## Architectural Requirements

- Due Diligence workspace: create DD project, add target companies, track assessment progress
- Data room integration: ingest documents (PDF, Excel) for AI analysis
- Red flag identification: automated detection of AI-risk signals (legacy tech, data silos, no API strategy)
- Competitive AI positioning: how does target compare to peers on AI-readiness?
- Investment memo generation: LLM-powered draft memo with AI-readiness section
- Checklist: standard PE DD checklist with AI-specific additions
- Collaboration: multiple team members can contribute to DD assessment
- Export: full DD report with Solstein intelligence + AI assessment

## Acceptance Criteria

- [ ] DD workspace can be created and target companies added
- [ ] Data room documents ingested and analyzed for AI signals
- [ ] Red flags automatically identified and highlighted
- [ ] Investment memo generated with AI-readiness section
- [ ] Full DD report exportable for investment committee

## Definition of Done

- **Tests Required**: End-to-end DD workflow test
- **Documentation Required**: DD module user guide
- **Code Review Gate**: Reviewer verifies workflow matches standard PE DD process

## Notes

This makes Solstein part of the investment process, not just research.
