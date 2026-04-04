# STORY-332: Add LLM-powered competitor identification from web search results

| Field | Value |
|-------|-------|
| **Epic** | EPIC-082 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | ⏳ BLOCKED |
| **Dependencies** | STORY-321 (LLM provider), STORY-331 |

## Description

Add LLM-based filtering and identification to the web discovery adapter. Raw search results often include non-competitors; LLM classifies each result as "competitor", "vendor", "partner", or "irrelevant".

## Acceptance Criteria

- [ ] LLM classifier runs on raw search results
- [ ] Classification uses structured extraction schema
- [ ] Precision ≥ 80% (few false positives admitted to pipeline)
- [ ] Misclassified results logged for review
