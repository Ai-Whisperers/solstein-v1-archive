# EPIC-040: Multi-Market Geographic Expansion

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Owner** | Market Expansion |
| **Created** | 2026-03-01 |

## Context

The call identified three geographic markets for expansion: Netherlands (primary, with Energy 21 proof case), Spain (identified opportunity), and UK/London (potential London team). Solstein needs infrastructure to support multi-market operations: localized data sources (e.g., Spanish company registry, UK Companies House), multi-language support, and market-specific scoring adjustments. This is not just translation — it's understanding that Dutch energy markets have different regulatory frameworks than UK or Spanish markets.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-153 | Dutch Market Localization & Data Sources | P2 |
| STORY-154 | Spanish Market Localization & Expansion | P2 |
| STORY-155 | UK/London Market Entry Infrastructure | P2 |
| STORY-156 | Multi-Language Support Infrastructure | P2 |

## Dependencies

- EPIC-019 (Multi-Tenancy) — for market-specific tenant isolation
- EPIC-036 (Configuration Consolidation) — for market-specific settings

## Notes

Geographic expansion requires more than translation — it requires local market intelligence integration.
