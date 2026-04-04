# STORY-283: WebsiteEnrichment: auto-discover website URL via SearXNG when not provided

| Field | Value |
|-------|-------|
| **Epic** | EPIC-072 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

WebsiteEnrichment currently fails when no website URL is provided. Add auto-discovery via SearXNG: search for "{company_name} official website" and extract the top result.

## Acceptance Criteria

- [ ] WebsiteEnrichment discovers URL for companies without pre-configured URL
- [ ] Discovery uses SearXNG (not hardcoded search engine)
- [ ] Result has `confidence < 0.6` for auto-discovered URLs
- [ ] Returns empty result with `confidence = 0.0` if SearXNG unavailable
