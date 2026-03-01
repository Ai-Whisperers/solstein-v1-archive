# STORY-162: Template-Based Scoring Model Customization

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-042: Rapid Market Validation Methodology |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-007, STORY-161 |

## The Strategic Context

> "Template-based scoring models that can be customized quickly."

## Problem Statement

Each market/sector has different scoring priorities: energy values compliance, fintech values regulatory licenses, SaaS values growth metrics. Solstein needs template-based scoring models: start with a sector template (e.g., "energy"), customize weights and signals for specific sub-sector (e.g., "renewable energy trading"), deploy in days not months. This enables rapid market validation without rebuilding scoring from scratch.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Speed to Market** | Rapid scoring model deployment |
| **Flexibility** | Adapt to any sector quickly |
| **Consistency** | Base templates ensure quality baseline |

## Affected Files

| File | Issue |
|------|-------|
| `analytics/scoring.py` | Hardcoded scoring, not template-based |
| `domain/models/` | No scoring template models |

## Architectural Requirements

- Scoring template library: base templates for major sectors (energy, fintech, healthcare, etc.)
- Template structure: dimensions (growth, financial health, etc.), weights, signals, thresholds
- Customization UI: adjust weights, add/remove signals, set thresholds without code changes
- Inheritance: base template + sector-specific overrides + market-specific overrides
- Validation: ensure customized model still produces valid scores (0-100 range, etc.)
- A/B testing: compare template variations for predictive accuracy
- Versioning: track template versions, roll back if needed
- Export: template export for sharing across Solstein instances

## Acceptance Criteria

- [ ] Scoring template library with base templates
- [ ] Customization UI for non-technical users
- [ ] Template inheritance works (base + sector + market)
- [ ] Validation ensures score validity
- [ ] A/B testing compares template performance

## Definition of Done

- **Tests Required**: Template customization and validation tests
- **Documentation Required**: Scoring template guide
- **Code Review Gate**: Reviewer verifies templates produce consistent scores

## Notes

The "customize in days, not months" capability.
