# FD-003: Context

## Status: PENDING

## Current State

`extract_competitor_data.py` extracts revenue, profitability (partial), funding (partial), employees, and scorecard data. The profitability section stores `raw_metrics` as a text dict but doesn't parse structured fields like EBITDA margin. Geographic expansion, SaaS metrics, and detailed funding investor data are completely ignored.

## Key Code Locations

- `extract_competitor_data.py`: `extract_profitability()`, `extract_funding()` -- enhance these
- `extract_competitor_data.py`: `extract_competitor()` -- wire in new extraction functions
- `competitor_utils.py` -- add new accessor functions
- Source data: `tickets/COMPETITION/*/financial-growth.md`

## Data Format Examples

Profitability table in source markdown:
```
| Data Point | Value | Source | Confidence |
|---|---|---|---|
| EBITDA Margin | 15.2% | Annual Report | High |
| Revenue per Employee | EUR 185K | Calculation | Medium |
```

SaaS section in source markdown:
```
### SaaS Transition Metrics
| Metric | Value |
|---|---|
| Deployment Model | Hybrid (SaaS + On-Premise) |
| Cloud Revenue % | 42% |
```

## Immediate Next Steps

1. Enhance `extract_profitability()` to parse EBITDA margin and revenue/employee
2. Enhance `extract_funding()` to extract lead investors and war chest signals
3. Add `extract_geographic()` and `extract_saas_metrics()` functions
4. Wire into `extract_competitor()` main function
5. Add accessor functions to `competitor_utils.py`
