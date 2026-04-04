# STORY-310: Add patent-based AI signals (AI/ML patent filings from USPTO)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-077 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-291 (arXiv/patent adapter) |

## Description

Add patent-based AI maturity signals: count of AI/ML patent filings from USPTO PatentsView API and arXiv publications. Companies with active AI patent portfolios score higher on AI maturity.

## Acceptance Criteria

- [ ] Patent count included in AI maturity signals
- [ ] arXiv publication count included in AI maturity signals
- [ ] Signal: 0+ patents = 0 boost, 1-5 = 0.2 boost, 6-20 = 0.5 boost, 20+ = 1.0 boost
- [ ] Zero patents is not penalized (neutral signal)
