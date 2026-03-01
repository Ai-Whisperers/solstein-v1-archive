# STORY-114: Add PDF Export Format

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-030: Export Pipeline Modernization |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-111 |

## The Audit Verdict

> `src/solstein/exporters/` — Excel, Markdown, LLM text exports present. No PDF export. PDF is the standard deliverable format for PE/VC due diligence reports.

## Problem Statement

PE/VC analysts deliver competitive intelligence in PDF. Not Excel, not Markdown, not JSON. PDF. The absence of a PDF exporter means Solstein's output requires manual post-processing before it can be shared with a Partner. This is an unnecessary friction that makes Solstein feel like a developer tool rather than an analyst product. A PDF export that renders company profiles with structured sections, charts, and citations closes this gap.

## Impact

| Dimension | Impact |
|-----------|--------|
| **User Experience** | Output format mismatch for PE/VC workflow |
| **Product** | Deliverable requires manual conversion step |

## Affected Files

| File | Issue |
|------|-------|
| New: `src/solstein/exporters/pdf.py` | Does not exist |

## Architectural Requirements

- PDF generation library: WeasyPrint (HTML→PDF) or ReportLab (programmatic) — selection based on template maintainability
- PDF structure: Cover page (company name, date, classification badge), Executive Summary, Financial Overview, Signal Intelligence (by category), Data Sources & Citations, Scoring Methodology
- Source citations: every signal that has a source_url appears as a footnote or endnote
- Charts: revenue trend chart, employee growth chart — embedded as SVG (not raster) for print quality
- PDF branded with configurable logo and color scheme (per-tenant branding, future consideration)
- PDF export runs as async Celery task (STORY-111 dependency)
- PDF size target: ≤5MB for a single-company report
- A4 and Letter page sizes supported (configurable)

## Acceptance Criteria

- [ ] PDF export generates successfully for a company with full signal data
- [ ] PDF includes source citations as footnotes
- [ ] Charts render in PDF (not blank boxes)
- [ ] PDF file size ≤5MB for single company
- [ ] A4 and Letter formats produce correctly sized output

## Definition of Done

- **Tests Required**: Manual review of generated PDF against template spec
- **Documentation Required**: PDF export usage guide
- **Code Review Gate**: Reviewer verifies source citations present and charts render

## Notes

PDF is the standard PE/VC deliverable format.
