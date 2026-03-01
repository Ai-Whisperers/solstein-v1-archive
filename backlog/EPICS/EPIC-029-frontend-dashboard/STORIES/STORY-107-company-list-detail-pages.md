# STORY-107: Company List and Detail Pages

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-029: Frontend Dashboard |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-106 |

## The Audit Verdict

> No frontend exists. Company data accessible only via `GET /api/v1/companies` JSON endpoint. The core value proposition of the product — competitive intelligence on companies — is invisible to non-technical users.

## Problem Statement

The companies endpoint returns rich data: scores, classifications, financials, signals with source citations and confidence percentages. As raw JSON, this data is unreadable for a non-technical analyst. Worse, it's unreadable for a technical analyst too — nobody evaluates competitive positioning by scrolling through a 4,000-line JSON response in a terminal.

A company list page with sortable columns, classification badges, and score indicators, combined with a detail page showing the full competitive profile, is the core value surface of the product. This is where Solstein either looks like a professional intelligence tool or a weekend hackathon project. The data is already there; it just needs a face.

Without these pages, Solstein is a data warehouse with an API door and no windows. The data goes in. It does not come out in any form a human would voluntarily look at.

## Impact

| Dimension | Impact |
|-----------|--------|
| **User Experience** | Analysts cannot view research results without direct API access. The product's primary output is inaccessible. |
| **Reliability** | N/A — the page doesn't exist to be unreliable |
| **Scalability** | Pagination required from day one. Loading 10,000 companies into a single DOM is not a feature; it's a denial-of-service against the user's browser. |
| **Developer Experience** | Establishes component patterns (tables, badges, cards) reused across the entire dashboard. |

## Affected Files

| File | Issue |
|------|-------|
| `dashboard/app/companies/page.tsx` | Does not exist. Company list page. |
| `dashboard/app/companies/[id]/page.tsx` | Does not exist. Company detail page. |
| `dashboard/components/ClassificationBadge.tsx` | Does not exist. Reusable classification badge component. |
| `dashboard/components/ScoreIndicator.tsx` | Does not exist. Score display with directional arrow. |
| `dashboard/components/SignalCard.tsx` | Does not exist. Signal display with source citation. |

## Architectural Requirements

- **Company list page**: paginated table with 50 companies per page, server-side pagination via API query params
- **Table columns**: company name, classification badge (Lead/Phoenix/Prospect/Dead), overall score, last researched timestamp, research trigger button (links to STORY-108)
- **Classification badges**: color-coded — Lead=green, Phoenix=blue, Prospect=yellow, Dead=grey. Badge is a reusable component.
- **Score column**: numeric display with directional indicator (↑/↓/→) showing change from previous score, if available
- **Sortable columns**: name (alphabetical), score (numeric), classification (categorical), last researched (temporal)
- **Filterable**: by classification (multi-select), by score range (min/max), by date range (last researched)
- **Company detail page**: full profile view with tabbed or sectioned layout
  - **Overview tab**: company name, classification, overall score, score breakdown by dimension (bar chart or radar), last researched date
  - **Financials section**: revenue, employee count, growth rates — if data available; "No financial data" message if not
  - **Signals section**: list of all signals grouped by signal_type, each showing: signal_type, value, source name, source URL (clickable external link), extraction_timestamp, confidence percentage
  - **Classification history**: if available, a timeline of classification changes with dates
- **Signal cards**: source URL rendered as a clickable external link with `target="_blank"` and `rel="noopener noreferrer"`. Signals without source URLs render gracefully (no broken links, no empty `<a>` tags).
- **Empty state**: when no companies exist, display a clear message with a "Run Your First Research" call-to-action linking to the research trigger (STORY-108)
- **All data fetched** from API with tenant-scoped auth header (Bearer token from Supabase session)
- **Loading states**: skeleton loaders for list and detail pages during data fetch
- **Error states**: API errors render inline with actionable context, not a blank page

## Acceptance Criteria

- [ ] Company list shows all companies for the authenticated tenant, paginated at 50 per page
- [ ] Classification badge colors match specification (Lead=green, Phoenix=blue, Prospect=yellow, Dead=grey)
- [ ] Sorting by any column works without full page reload
- [ ] Filtering by classification, score range, and date range works correctly
- [ ] Company detail page renders all available sections (overview, financials, signals)
- [ ] Signal cards display source citations with clickable URLs
- [ ] Signals without source URLs render without broken links or layout issues
- [ ] Empty state displays when no companies exist, with CTA to research page
- [ ] Page navigation (list ↔ detail) preserves filter/sort state via URL params
- [ ] Loading skeleton renders during data fetch (no flash of empty content)

## Definition of Done

- **Tests Required**: Visual regression test for classification badges (all four states). E2E test: navigate to company detail, verify signal source links open correctly in new tab. Unit tests for sort/filter logic.
- **Documentation Required**: Component storybook entries for ClassificationBadge, ScoreIndicator, SignalCard (if Storybook is adopted; otherwise component-level JSDoc).
- **Code Review Gate**: Reviewer verifies all data is tenant-scoped. Reviewer confirms no `dangerouslySetInnerHTML` usage. Reviewer checks that external links include `rel="noopener noreferrer"`.

## Notes

- The research trigger button in the company list (per-row action) links to the research trigger page (STORY-108) with the company name pre-filled. It does not trigger research inline — that complexity belongs in STORY-108.
- Score breakdown by dimension depends on the scoring algorithm exposing per-dimension scores via the API. If the API only returns an aggregate score, the detail page should show only the aggregate with a note that dimensional breakdown is forthcoming.
- Consider URL-based filter state (`?classification=Lead&minScore=60`) so that filtered views are shareable and bookmarkable. This is a product differentiator for analysts who share links with colleagues.
- The financials section will be sparse for many companies early on. Design for graceful degradation — "Data not yet available" is better than an empty section with column headers and no rows.
