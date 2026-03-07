# STORY-157: Cap Table Integration & Equity Tracking

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-041: Equity Participation Business Model |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-019 |

## The Strategic Context

> "Long play: equity in transformed companies, not just consulting/SaaS fees."

## Problem Statement

Solstein's strategic shift to equity participation requires infrastructure to track equity positions: cap table integration, ownership percentages, investment rounds, dilution tracking. This transforms Solstein from a SaaS vendor into an investment platform that happens to provide intelligence. The platform needs to know: what do we own, what's it worth, how is it performing.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Business Model** | Enable equity-based revenue |
| **Portfolio Tracking** | Unified view of equity positions |
| **LP Reporting** | Show equity portfolio performance |

## Affected Files

| File | Issue |
|------|-------|
| New: `domain/equity/` | Does not exist |
| `infrastructure/database_models.py` | No equity tracking tables |

## Architectural Requirements

- Equity entity: track Solstein's equity positions in portfolio companies
- Cap table integration: ingest cap tables from portfolio companies (Carta, Ledgy, or manual)
- Ownership tracking: percentage ownership, share classes, voting rights
- Investment round tracking: when invested, at what valuation, round type (seed/Series A/etc.)
- Dilution modeling: track dilution from subsequent rounds, option pool changes
- Valuation tracking: mark-to-market valuations, 409A equivalents
- Rights tracking: pro-rata rights, anti-dilution, liquidation preferences
- Multi-entity support: track equity in multiple entities (fund, SPV, direct)

## Acceptance Criteria

- [ ] Equity positions tracked in platform
- [ ] Cap table data ingested and stored
- [ ] Ownership percentages calculated correctly
- [ ] Investment rounds documented
- [ ] Dilution tracked across rounds

## Definition of Done

- **Tests Required**: Cap table calculation accuracy tests
- **Documentation Required**: Equity tracking user guide
- **Code Review Gate**: Reviewer verifies dilution math is correct

## Notes

This is the infrastructure for Solstein as investment firm, not just software vendor.
