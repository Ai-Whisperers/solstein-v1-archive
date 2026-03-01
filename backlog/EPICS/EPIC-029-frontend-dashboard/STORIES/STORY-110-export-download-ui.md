# STORY-110: Export Download UI

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-029: Frontend Dashboard |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-107, EPIC-030 |

## The Audit Verdict

> Exports triggered via `/api/v1/export` — no UI. Exports write to local disk (STORY-105 migrates to Supabase Storage). No download link surfaced to users.

## Problem Statement

Exports are the primary deliverable of the platform — the Excel report or PDF that an analyst presents to a Partner. Currently, triggering an export requires an API call and downloading the file requires knowing the local filesystem path. After STORY-105 (Supabase Storage), exports will have signed URLs. This story surfaces those URLs in the dashboard as a download button.

## Impact

| Dimension | Impact |
|-----------|--------|
| **User Experience** | Core deliverable inaccessible via UI |
| **Product** | Export is the final step of the analyst workflow with no UI completion |

## Affected Files

| File | Issue |
|------|-------|
| New: `dashboard/app/exports/page.tsx` | Does not exist |
| New: `dashboard/components/ExportButton.tsx` | Does not exist |

## Architectural Requirements

- Per-company export button on company detail page (STORY-107): triggers async export job, shows progress indicator
- Export history page: list of all tenant exports with: company name, format (Excel/PDF/Markdown), created_at, expires_at, download button (signed URL)
- Download button: opens signed Supabase Storage URL in new tab
- Expired exports: download button disabled, tooltip showing expiry date, option to re-generate
- Export format selector: Excel, Markdown, PDF (pending STORY-114)
- Export status: async export shows "Generating..." spinner until Realtime update signals completion
- Exports scoped to tenant — users cannot see other tenants' exports

## Acceptance Criteria

- [ ] Export button on company detail page triggers export and shows progress
- [ ] Completed exports appear in export history with working download link
- [ ] Download link opens the file (not a 404 or 403)
- [ ] Expired export links are disabled in the UI
- [ ] Export list shows only current tenant's exports

## Definition of Done

- **Tests Required**: E2E test: trigger export, wait for completion, click download, verify file downloads
- **Documentation Required**: None
- **Code Review Gate**: Reviewer verifies expired URL handling doesn't crash the UI

## Notes

The deliverable needs a download button.
