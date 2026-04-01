# Scoring Business Rationale

> Satisfies STORY-039 (EPIC-011: Business Rules Documentation)

## Classification System

Every company in a market is scored and classified into three tiers:

| Classification | Score Range | What It Means |
|---|---|---|
| 🔥 **Phoenix** | ≥ 7.0 | High-growth, AI-native or rapidly adopting. Act now. |
| 🧂 **Salt** | 4.5 – 6.99 | Stable players. Watch for directional signals. |
| ⚖️ **Lead** | ≤ 4.49 | Legacy weight. Hidden diamonds or dead weight. |

## Three Scoring Dimensions

### 1. Growth Score
Revenue trajectory and margin health. Measures whether the company is accelerating, stable, or declining.

### 2. Financial Health Score
Scale, funding cushion, and operational efficiency. Indicates runway and resilience.

### 3. Competitive Position Score
AI maturity, SaaS adoption, and tech stack depth. Measures how modern and defensible the technology is.

## Threshold Calibration

Thresholds are set in `src/solstein/analytics/constants.py`:

```python
PHOENIX_SCORE_THRESHOLD = 7.0   # Top ~20% of actual distribution
SALT_SCORE_THRESHOLD = 4.5      # Middle 60-70%
LEAD_SCORE_THRESHOLD = 4.49     # Bottom 15-20%
```

These thresholds were calibrated against a live dataset of 29 European energy software companies (see `docs/PITCH/case-study.md`). The distribution matches PE due diligence expectations:
- ~20% high-growth targets worth immediate attention
- ~65% stable companies requiring directional monitoring  
- ~15% legacy/opportunity companies needing people-level assessment

## Score Range
- Maximum: 10.0
- Minimum: 0.0
- Composite score is weighted average of the three dimensions

## Confidence Thresholds
| Level | Threshold | Meaning |
|---|---|---|
| High | ≥ 0.9 | Multiple corroborating sources |
| Medium | ≥ 0.7 | Sufficient data, some gaps |
| Low | < 0.3 | Sparse data, treat with caution |

## Why These Numbers?

The classification boundaries serve Private Equity decision-making:
- **Phoenix ≥ 7.0**: These companies are acquisition targets NOW. Waiting costs money.
- **Salt 4.5-6.99**: Worth monitoring quarterly. May move to Phoenix or Lead.
- **Lead ≤ 4.49**: Either hidden diamonds (great team, bad tech) or dead weight. Requires human assessment of the people, not just the numbers.

The 80/20 principle applies: 80% of PE deal value comes from the top 20% of companies (Phoenixes). The scoring exists to surface them quickly.
