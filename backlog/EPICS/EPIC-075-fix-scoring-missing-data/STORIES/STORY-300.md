# STORY-300: Add DataCompletenessScorer

| Field | Value |
|-------|-------|
| **Epic** | EPIC-075 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Create a new `DataCompletenessScorer` that measures the percentage of key data fields populated per company. Outputs a 0.0-1.0 completeness ratio used to weight the composite score.

Key fields: name, website_url, ticker, revenue, employee_count, founded_year, industry, description, linkedin_slug, github_org, funding_total, tech_stack.

## Acceptance Criteria

- [ ] `DataCompletenessScorer` implements scorer interface
- [ ] Returns 0.0-1.0 ratio (not a score in 0-10 range)
- [ ] 12 key fields measured; each missing field reduces ratio by 1/12
- [ ] Unit tests for 0%, 50%, 100% completeness
