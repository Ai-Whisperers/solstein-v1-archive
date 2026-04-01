# STORY-199: Confidence Calibration Profile per Source Tier

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-052 Provenance, Confidence, Quality Gates |
| **Created** | 2026-04-01 |

## Problem Statement
All data sources report raw confidence scores on different scales. A 0.8 from GitHub API means something different than 0.8 from a web scraper.

## Acceptance Criteria
- [ ] Define source tiers: Tier 1 (APIs with auth), Tier 2 (public APIs), Tier 3 (web scraping)
- [ ] Each tier has a calibration multiplier applied to raw confidence
- [ ] Calibration config is in `analytics/constants.py` (not hardcoded in adapters)
- [ ] Tests: calibration produces expected normalized scores for each tier
