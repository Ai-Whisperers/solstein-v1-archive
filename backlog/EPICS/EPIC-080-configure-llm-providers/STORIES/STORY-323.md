# STORY-323: Verify LLM health check + deep_analyzer produces real output

| Field | Value |
|-------|-------|
| **Epic** | EPIC-080 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-321 |

## Description

Verify that the LLM health check passes and that `deep_analyzer` produces real company descriptions (not template placeholders like "No description available").

## Acceptance Criteria

- [ ] LLM health check returns `true` in `/health` endpoint
- [ ] `deep_analyzer` call for a known company returns ≥ 100 characters of real description
- [ ] Description does not contain "No description available" or "Template"
- [ ] Response time < 10 seconds for single company analysis
