# STORY-201: Provenance Dashboard and Audit Trail

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P2 - Medium |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-052 Provenance, Confidence, Quality Gates |
| **Created** | 2026-04-01 |

## Problem Statement
There is no visibility into data provenance across the pipeline. Operators cannot see which sources contributed to a company profile or trace a classification back to its evidence.

## Acceptance Criteria
- [ ] API endpoint `/companies/{id}/provenance` returns source breakdown
- [ ] Each field shows: source, confidence, retrieved_at, tier
- [ ] Audit trail persisted in database (not just logs)
- [ ] Tests: endpoint returns correct provenance for test companies
