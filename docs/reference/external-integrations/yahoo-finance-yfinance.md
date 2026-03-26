# Yahoo Finance Via `yfinance`

Verified on `2026-03-25`.

## Local Usage

- [fetchers.py](../../../src/solstein/data/fetchers.py)
- [company_research.py](../../../src/solstein/data/company_research.py)
- [yahoo_finance.py](../../../src/solstein/connectors/financial/yahoo_finance.py)

## Important Distinction

The repo currently depends on the `yfinance` library, not on a first-party Yahoo Finance developer API contract.

## Wrapper Surfaces

- `yfinance` docs: `https://ranaroussi.github.io/yfinance/`
- `yfinance` repo: `https://github.com/ranaroussi/yfinance`
- `llms.txt`: `https://ranaroussi.github.io/yfinance/llms.txt` returned `404` in this pass
- `robots.txt`: `https://ranaroussi.github.io/yfinance/robots.txt` returned `404` in this pass

## Good Patterning

- Treat all `yfinance`-derived data as wrapper-dependent and potentially shape-unstable.
- Normalize quote, history, and index data at the boundary before merge.
- Keep null and missing-market-field handling explicit.
- Prefer cached and batched access over repeated ad hoc calls.

## Caveats

- This is not the same risk profile as an official documented enterprise API.
- Upstream HTML or unofficial endpoint changes can break behavior even when our code is “correct”.
- Schema validation and regression fixtures matter more here because the wrapper surface can drift silently.

## Test Gates

- quote payload normalization fixtures
- historical-data empty-frame handling
- index fallback behavior
- strict schemas for the normalized market-data objects the rest of the pipeline consumes
