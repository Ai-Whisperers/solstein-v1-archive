# EPIC-080: Configure LLM Providers

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Phase** | P3 — Run as Real Service |
| **Effort** | S (1–2 days) |
| **Stories** | 3 ([STORY-321](STORIES/STORY-321.md) through [STORY-323](STORIES/STORY-323.md)) |
| **Created** | 2026-04-01 |
| **Updated** | 2026-04-05 (added metadata, DoD) |

## Context

LLM-based features (company descriptions, AI maturity assessment, competitor identification) require a configured LLM provider. Without API keys, the deep_analyzer falls back to templates and produces useless output. A fallback chain with 3+ providers is required for reliability.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-321](STORIES/STORY-321.md) | Configure primary LLM provider (Anthropic Claude) with API key in .env | 🔴 READY | Deps: none |
| [STORY-322](STORIES/STORY-322.md) | Configure fallback LLM provider chain (3+ providers) | 🔴 READY | Deps: [STORY-321](STORIES/STORY-321.md) |
| [STORY-323](STORIES/STORY-323.md) | Verify LLM health check + deep_analyzer produces real output (not template) | 🔴 READY | Deps: [STORY-321](STORIES/STORY-321.md) |

## Success Criteria

- Anthropic Claude API key configured and validated at startup
- Fallback chain configured with at least 2 additional providers
- `deep_analyzer` call produces real company description (not "No description available")
- LLM health check returns true in `/health` endpoint

## Definition of Done

- [ ] [STORY-321](STORIES/STORY-321.md): `ANTHROPIC_API_KEY` set in `.env`; startup logs show "LLM provider: anthropic"
- [ ] [STORY-322](STORIES/STORY-322.md): fallback chain has ≥ 2 additional providers configured
- [ ] [STORY-323](STORIES/STORY-323.md): `deep_analyzer` output for test company is not a template string
- [ ] `/health` returns `"llm": true`

## Dependencies

None — LLM configuration is independent of infrastructure.
