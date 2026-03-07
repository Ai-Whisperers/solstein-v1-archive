# STORY-106: Bootstrap Next.js Dashboard with Supabase Auth

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-029: Frontend Dashboard |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-019 (Multi-Tenancy), EPIC-020 (Supabase Auth) |

## The Audit Verdict

> `dashboard/` directory — **DOES NOT EXIST**. Referenced in `AGENTS.md:54` as an existing Next.js application. It is not there.

## Problem Statement

The platform has no user interface. Research results exist only as JSON API responses. PE/VC analysts are not expected to curl endpoints and parse JSON to evaluate investment opportunities — they need a dashboard. The absence of a frontend isn't a deferred feature; it's a missing layer of the product stack.

Every month without a UI is a month where user adoption depends entirely on technical users who know how to operate APIs. For a PE/VC intelligence product competing with Crunchbase and PitchBook — both of which have polished UIs — this is a significant gap. It is the difference between "a product" and "a backend that could theoretically become a product someday."

The first step is the most foundational: scaffold a Next.js application with Supabase Auth integration, protected routes, and a shared layout. This story produces a running dashboard that authenticates users, enforces tenant isolation, and provides the navigation shell that every subsequent story renders into.

## Impact

| Dimension | Impact |
|-----------|--------|
| **User Experience** | Zero non-technical user access to the platform. The product is invisible to its intended audience. |
| **Reliability** | N/A — cannot be unreliable if it does not exist |
| **Scalability** | N/A |
| **Developer Experience** | Every frontend story is blocked until this ships. No incremental UI work is possible without a scaffold. |

## Affected Files

| File | Issue |
|------|-------|
| `dashboard/` (entire directory) | Does not exist. Must be created from scratch. |
| `AGENTS.md:54` | References `dashboard/` as existing — will become accurate after this story |
| `docker-compose.yml` | No dashboard service defined |

## Architectural Requirements

- Next.js 14+ with App Router and TypeScript — no Pages Router, no JavaScript-only files
- Supabase Auth integration using `@supabase/ssr` for server-side session management
- Cookie-based session persistence — auth tokens must never touch localStorage or sessionStorage
- Login page supporting email/password and magic link (both handled by Supabase Auth)
- Tenant-aware routing: after login, all data queries scoped to the user's tenant_id
- Protected route middleware: any unauthenticated request to a dashboard route redirects to `/login`
- Shared layout with sidebar navigation: Companies, Research, Exports, Settings
- Environment variables: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_API_URL`
- Tailwind CSS configured and operational
- `dashboard/` added to `docker-compose.yml` as an optional dev service on port 3000
- ESLint and Prettier configured for the dashboard directory
- `tsconfig.json` with strict mode enabled

## Acceptance Criteria

- [ ] `cd dashboard && npm run dev` starts a working Next.js application on port 3000
- [ ] Login with valid Supabase Auth credentials redirects to the dashboard home page
- [ ] Login with invalid credentials displays an error message (not a generic crash)
- [ ] Unauthenticated access to any protected route (e.g., `/companies`) redirects to `/login`
- [ ] User session persists across page refreshes — cookie-based, not localStorage
- [ ] Tenant isolation: logged-in user's API requests include tenant-scoped auth headers
- [ ] Logout clears the session and redirects to `/login`
- [ ] Sidebar navigation renders with all four sections (Companies, Research, Exports, Settings)
- [ ] `npm run build` completes without errors
- [ ] `npm run lint` passes with zero warnings

## Definition of Done

- **Tests Required**: E2E test (Playwright): login → land on dashboard → navigate sidebar → logout → verify redirect to `/login`. Unit tests for auth middleware logic.
- **Documentation Required**: `dashboard/README.md` with setup instructions, environment variable reference, and development workflow.
- **Code Review Gate**: Reviewer verifies no auth tokens stored in localStorage. Reviewer confirms cookie settings include `HttpOnly`, `Secure`, and `SameSite=Lax` (or stricter).

## Notes

- Magic link login requires Supabase project email configuration. If Supabase email is not configured, magic link should be hidden from the UI (feature flag or env var).
- The Settings page is a placeholder in this story — it exists in the sidebar for navigation consistency but renders a "Coming Soon" message.
- Docker service should be marked as optional (`profiles: ["dashboard"]`) so it doesn't start with `docker-compose up` unless explicitly requested.
- Consider adding a health check endpoint at `/api/health` for the dashboard service itself, independent of the backend API health check.
