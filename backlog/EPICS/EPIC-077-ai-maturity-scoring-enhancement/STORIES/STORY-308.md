# STORY-308: Use LLM to assess AI maturity from company descriptions

| Field | Value |
|-------|-------|
| **Epic** | EPIC-077 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 READY |
| **Dependencies** | LLM provider (STORY-321) |

## Description

Add LLM-based AI maturity assessment as an enrichment of the keyword-based signal. Classifies company descriptions on a 5-point AI maturity scale using structured extraction.

## Acceptance Criteria

- [ ] LLM assessment runs as supplemental signal (not replacement for keywords)
- [ ] Outputs structured: maturity_level (1-5), evidence (list of quotes), confidence (0-1)
- [ ] Gracefully skips when LLM unavailable (keyword-only path unchanged)
- [ ] Test: 3 known AI-native and 3 known non-AI companies correctly classified
