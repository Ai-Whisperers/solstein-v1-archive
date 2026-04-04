# STORY-321: Configure primary LLM provider (Anthropic Claude) with API key

| Field | Value |
|-------|-------|
| **Epic** | EPIC-080 |
| **Priority** | P1 |
| **Size** | XS |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Configure the primary LLM provider (Anthropic Claude) by adding the API key to `.env.production` and verifying the startup validation accepts it.

## Acceptance Criteria

- [ ] `ANTHROPIC_API_KEY` set in `.env.production`
- [ ] Startup validation passes (no "missing API key" errors)
- [ ] Test query to Claude returns valid response
- [ ] LLM health check returns `true` in `/health` response
