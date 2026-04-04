# STORY-322: Configure fallback LLM provider chain (3+ providers)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-080 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-321 |

## Description

Configure at least 2 additional LLM providers as fallbacks in the provider chain (e.g., Ollama local + OpenAI or Gemini). When the primary provider fails, the system automatically falls back.

## Acceptance Criteria

- [ ] At least 3 providers configured in fallback chain
- [ ] Fallback triggers correctly when primary returns error
- [ ] Fallback does not add more than 5 seconds of additional latency
- [ ] Failed provider logged at WARNING level
