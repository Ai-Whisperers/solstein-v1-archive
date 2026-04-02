# EPIC-028: External Service Consolidation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Created** | 2026-03-01 |
| **Stories** | STORY-101, STORY-102, STORY-103, STORY-104, STORY-105 |
| **Dependencies** | EPIC-019 (Multi-Tenancy), EPIC-020 (Supabase Integration) |

## Context

The platform calls 10+ external services across data collection, LLM inference, and search. Some are stable. Some are held together with duct tape and optimism.

**The brittle:**
- **Yahoo Finance** — accessed via `yfinance`, a community HTML scraper. Yahoo changes their page structure roughly quarterly; each change breaks the scraper silently. The platform continues to run, records zero financial data, and nobody notices until a PE partner asks why the market data is three weeks old.
- **Google Custom Search** — 100 free queries/day, $5 per 1000 after. A platform that researches hundreds of companies per day will exhaust this in the first hour of operation. The free tier is a demo, not a service tier.
- **NewsAPI** — free tier prohibits commercial use. The paid tier starts at $449/month. GDELT is free, open, and more comprehensive.

**The absent:**
- **Notifications** — completely missing. Research pipelines that take 10 minutes to complete report their result only via API polling. Users poll, get PENDING, give up, and re-trigger the pipeline. The platform runs the same research twice and charges for both LLM calls.

**The fragile:**
- **File exports** — written to local disk. In a containerized deployment, local disk is ephemeral. In a horizontally scaled deployment, local disk is replica-local. Both are problems.

This epic rationalizes the external service layer. Replace paid/brittle services with free/robust alternatives. Add the notification layer that should have existed from day one. Move file storage from "the container's hard drive" to Supabase Storage.

## Scope

| Category | Action |
|----------|--------|
| Web Search | Replace Google Custom Search with self-hosted SearXNG |
| News Intelligence | Replace NewsAPI with GDELT + RSS aggregation |
| Financial Data | Stabilize Yahoo Finance with proper API + circuit breaker |
| Notifications | Build Slack + Email notification service from scratch |
| File Storage | Migrate exports from local disk to Supabase Storage |

## Stories

| Story | Title | Priority | Status |
|-------|-------|----------|--------|
| [STORY-101](STORIES/STORY-101-searxng-web-search.md) | Replace Google Custom Search with Self-Hosted SearXNG | P2 | 🔴 Not Started |
| [STORY-102](STORIES/STORY-102-gdelt-rss-news.md) | Replace NewsAPI with GDELT + RSS Aggregation | P2 | 🔴 Not Started |
| [STORY-103](STORIES/STORY-103-yahoo-finance-stability.md) | Stabilize Yahoo Finance Integration | P2 | 🔴 Not Started |
| [STORY-104](STORIES/STORY-104-notification-service.md) | Add Slack and Email Notification Service | P2 | 🔴 Not Started |
| [STORY-105](STORIES/STORY-105-supabase-storage-exports.md) | Move File Exports to Supabase Storage | P2 | 🔴 Not Started |

## Dependency Graph

```
EPIC-019 (Multi-Tenancy) ──┐
                            ├──► STORY-105 (Supabase Storage)
EPIC-020 (Supabase) ────────┘

EPIC-026 (Docker) ──► STORY-101 (SearXNG)

STORY-101 (SearXNG) ─┐
                      ├──► Can be parallelized — no inter-story dependencies
STORY-102 (GDELT) ────┤    except STORY-104 (Notifications) is referenced
STORY-103 (Yahoo) ─────┤    by EPIC-027 STORY-099 (staging workflow)
STORY-104 (Notify) ───┘
```

## Success Criteria

- Web search runs without a Google API key (SearXNG is primary)
- News pipeline runs without a NewsAPI key (GDELT + RSS is primary)
- Financial data source failure is detected within 3 consecutive fetches and flagged
- Research completion triggers a Slack notification within 30 seconds
- Export files are downloadable from any API replica via signed URL
- Monthly external service cost reduced (Google CSE eliminated, NewsAPI eliminated or optional)

## Cost Analysis

| Service | Current Cost | After Consolidation |
|---------|-------------|-------------------|
| Google Custom Search | ~$50-200/month (variable) | $0 (SearXNG self-hosted) |
| NewsAPI | $449/month (commercial tier) | $0 (GDELT + RSS) |
| Yahoo Finance (yfinance) | $0 (scraping) | $0 or ~$30/month (Alpha Vantage basic) |
| Notification Service | N/A (doesn't exist) | ~$0-20/month (Slack webhook free, Sendgrid free tier) |
| Supabase Storage | N/A (local disk) | Included in Supabase plan |
| **Total** | **~$500-650/month** | **~$0-50/month** |

## Risks

| Risk | Mitigation |
|------|------------|
| SearXNG search quality lower than Google CSE | Google CSE retained as fallback; SearXNG aggregates multiple engines |
| GDELT coverage gaps for niche companies | RSS aggregation supplements GDELT for company-specific sources |
| Financial data API free tier limits | Cache aggressively; stale data with freshness indicator is better than no data |
| Notification delivery failures | Fire-and-forget with retry; notifications are best-effort, not critical path |
| Supabase Storage costs at scale | Lifecycle policies (7-day expiry) limit storage growth |

## Notes

The theme of this epic is operational independence. Every external service the platform depends on is a single point of failure that we don't control. Google can deprecate CSE. NewsAPI can raise prices. Yahoo can change their HTML. The goal is not zero external dependencies — that's impossible — but controllable degradation. When a service goes down, the platform should log a warning, serve stale data with a freshness indicator, and keep running. Not crash. Not serve empty data silently. Not require a human to notice.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
