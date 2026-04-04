# STORY-192: Implement schema extraction contracts for product/team/tech fields

| Field | Value |
|-------|-------|
| **Epic** | EPIC-050 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 Not Started |
| **Dependencies** | EPIC-028, EPIC-035 |

## Description

Implement the Extract stage: apply schema-validated extraction contracts to crawled page HTML. Extract structured data for: company description, team members, product features, technology mentions, funding events.

## Acceptance Criteria

- [ ] Extraction schemas defined as Pydantic models per page type
- [ ] LLM-based extraction with structured output format
- [ ] Schema validation rejects malformed extractions
- [ ] `confidence` field populated based on extraction completeness
- [ ] Failed extraction returns empty result (not exception)
- [ ] Unit tests for each schema type with sample HTML fixtures
