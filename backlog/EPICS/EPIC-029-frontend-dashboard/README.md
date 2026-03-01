# EPIC-029: Frontend Dashboard

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Created** | 2026-03-01 |
| **Stories** | STORY-106 through STORY-110 |
| **Dependencies** | EPIC-019 (Multi-Tenancy), EPIC-020 (Supabase Auth), EPIC-024 (Realtime Job Status) |

## Context

The `dashboard/` directory referenced in AGENTS.md does not exist. There is no frontend. The platform is API-only.

PE/VC analysts — the actual users — have no interface for viewing company research results, triggering new research, or monitoring pipeline status. Everything requires either API calls or Python scripts. This is not a product; it is a service waiting for a product to be built on top of it.

Solstein competes — aspirationally, at least — in a space dominated by Crunchbase, PitchBook, and CB Insights, all of which have polished, purpose-built interfaces. An API-only offering is appropriate for a platform play. Solstein is not a platform play. It is a PE/VC intelligence tool whose users are analysts, associates, and VPs who expect to open a browser, not a terminal.

This epic delivers the minimum viable dashboard: authentication, company list, company detail, research trigger, real-time job status, and export download. It is not a full-featured frontend — it is the smallest set of pages that makes Solstein usable by a non-technical person.

## Scope

| Story | Title | Summary |
|-------|-------|---------|
| STORY-106 | Bootstrap Next.js Dashboard with Supabase Auth | Project scaffolding, auth integration, protected routes, shared layout |
| STORY-107 | Company List and Detail Pages | Paginated company table, classification badges, full detail view with signals |
| STORY-108 | Research Pipeline Trigger UI | Search-and-trigger interface for new company research |
| STORY-109 | Real-Time Job Status UI via Supabase Realtime | Live progress tracking for research jobs without polling |
| STORY-110 | Export Download UI | Export trigger, history, and signed URL download |

## Architecture Decisions

- **Framework**: Next.js 14+ with App Router and TypeScript. The App Router provides server components and server-side rendering, both of which are critical for initial load performance and SEO-irrelevant-but-security-relevant server-side auth checks.
- **Auth**: Supabase Auth via `@supabase/ssr`. Server-side session management with cookies. No localStorage tokens. This is non-negotiable — localStorage auth tokens in a PE/VC intelligence product would be a security audit finding before the first user logs in.
- **Styling**: Tailwind CSS. Component library selection deferred to implementation.
- **Realtime**: Supabase Realtime subscriptions for job status. Fallback to polling if WebSocket connection drops.
- **Data fetching**: Server components fetch from the API with the user's session token. Client components subscribe to Realtime channels for live updates.

## Dependency Graph

```
EPIC-019 (Multi-Tenancy) ──┐
                            ├──→ STORY-106 (Bootstrap) ──→ STORY-107 (Companies)
EPIC-020 (Supabase Auth) ──┘                            ├──→ STORY-108 (Research Trigger)
                                                        ├──→ STORY-109 (Job Status)
EPIC-024 (Realtime) ────────────────────────────────────┘
                                                        └──→ STORY-110 (Exports)
EPIC-030/STORY-111 (Async Exports) ─────────────────────────→ STORY-110 (Exports)
```

## Out of Scope

- Admin panel (user management, tenant management) — separate epic
- Mobile-responsive design beyond basic viewport handling
- Internationalization / localization
- Custom branding per tenant (logo, colors) — future consideration noted in STORY-114
- Offline support / PWA

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Supabase Realtime connection instability | Medium | High | Polling fallback (STORY-109) |
| EPIC-019/020 delays block all dashboard work | High | Critical | STORY-106 can scaffold with mock auth |
| API schema changes during dashboard development | Medium | Medium | OpenAPI contract as source of truth |
| Next.js App Router immaturity in edge cases | Low | Medium | Server components only where necessary |

## Success Metrics

- Non-technical user can complete full workflow (login → view company → trigger research → download export) without API calls or scripts
- Time to first meaningful content after login: <3 seconds
- Zero auth token exposure in browser DevTools (no localStorage, no URL params)
