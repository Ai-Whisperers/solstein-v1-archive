# STORY-304: Add LLM-based capability matching

| Field | Value |
|-------|-------|
| **Epic** | EPIC-076 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 READY |
| **Dependencies** | LLM provider configured (STORY-321) |

## Description

Add LLM-based capability matching as a fallback when keyword matching finds no overlap. Classifies company descriptions against Eneve's 8 capabilities using structured extraction.

## Acceptance Criteria

- [ ] LLM classifier runs when keyword overlap = 0
- [ ] Uses structured extraction schema (not free text)
- [ ] Returns capability list with confidence per capability
- [ ] Gracefully skips when LLM unavailable
