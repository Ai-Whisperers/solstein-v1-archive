# EPIC-074: Revenue & Financial Data Validation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 — Phase P1: Data Supply |
| **Phase** | P1 — Make Pipeline Produce Real Data |
| **Created** | 2026-04-01 |

## Context

Financial data from multiple sources arrives in inconsistent formats: revenue in thousands vs millions vs billions, mixed currencies, employee counts that are orders of magnitude off. Without validation, garbage data flows into scores and analyst deliverables with full confidence.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-293](STORIES/STORY-293.md) | Add revenue sanity checks in aggregation: cap at industry-appropriate max, flag outliers > 3 sigma | 🔴 READY | Deps: none |
| [STORY-294](STORIES/STORY-294.md) | Normalize revenue units: detect thousands/millions/billions strings, convert all to EUR millions | 🔴 READY | Deps: none |
| [STORY-295](STORIES/STORY-295.md) | Cross-validate revenue across 2+ sources before accepting high-confidence value | 🔴 READY | Deps: none |
| [STORY-296](STORIES/STORY-296.md) | Add employee count validation (1-10M range, cross-reference with revenue/employee ratio) | 🔴 READY | Deps: none |
| [STORY-297](STORIES/STORY-297.md) | Add funding amount validation with automatic currency conversion to EUR | 🔴 READY | Deps: none |

## Success Criteria

- No revenue value outside EUR 0.1M–EUR 1T reaches a company score
- All revenue values in EUR millions (consistent unit)
- Employee counts validated against revenue/headcount ratio heuristics
- Funding amounts all normalized to EUR
