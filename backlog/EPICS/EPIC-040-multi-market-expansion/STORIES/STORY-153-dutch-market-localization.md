# STORY-153: Dutch Market Localization & Data Sources

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-040: Multi-Market Geographic Expansion |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-019 |

## The Strategic Context

> "Netherlands is the primary market with Energy 21 as the proof case."

## Problem Statement

Solstein needs deep Dutch market integration: KVK (Chamber of Commerce) data, Dutch energy regulator (ACM) filings, Dutch grid operators (TenneT, Stedin, Liander), and Dutch-specific regulatory frameworks. Energy 21 proves the methodology works in Netherlands — now Solstein needs to productize this for broader Dutch energy market coverage.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Market Penetration** | Deep Dutch market coverage |
| **Proof Case Scale** | Expand Energy 21 methodology |
| **Local Credibility** | Dutch data sources = local trust |

## Affected Files

| File | Issue |
|------|-------|
| `adapters/` | No Dutch-specific adapters |
| `config.py` | No Dutch market configuration |

## Architectural Requirements

- KVK integration: Dutch Chamber of Commerce company data, annual reports, officer information
- ACM (Authority for Consumers & Markets): regulatory filings, market monitoring data
- Grid operators: TenneT (TSO), Stedin/Liander/Enexis (DSO) connection data
- Energy-specific: Energieakkoord participation, SDE++ subsidy data, renewable energy certificates (GOs)
- Language: Dutch language support for company names, descriptions, documents
- Localization: Dutch number formats, currency (EUR), date formats
- Market-specific scoring: adjust scoring models for Dutch regulatory environment
- Data quality: validate Dutch data sources for completeness and freshness

## Acceptance Criteria

- [ ] KVK company data integrated
- [ ] ACM regulatory filings accessible
- [ ] Grid operator data connected
- [ ] Dutch language support active
- [ ] Dutch market scoring models calibrated

## Definition of Done

- **Tests Required**: End-to-end Dutch company research workflow
- **Documentation Required**: Dutch market data source guide
- **Code Review Gate**: Reviewer verifies Dutch data covers >80% of energy market

## Notes

Netherlands is the beachhead — get it right here first.
