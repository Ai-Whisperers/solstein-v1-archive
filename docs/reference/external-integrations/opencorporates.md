# OpenCorporates

Verified on `2026-03-25`.

## Local Usage

- [opencorporates.py](../../../src/solstein/data/connectors/lookup_strategies/opencorporates.py)
- [opencorporates.py](../../../src/solstein/connectors/financial/opencorporates.py)
- [extra.py](../../../src/solstein/connectors/financial/extra.py)

## Official Surfaces

- Docs: `https://api.opencorporates.com/documentation/API-Reference`
- API root `robots.txt`: `https://api.opencorporates.com/robots.txt` returned an auth error in this pass
- API root `llms.txt`: `https://api.opencorporates.com/llms.txt` returned an auth error in this pass

## Good Patterning

- Use OpenCorporates for registry and identifier lookup, not for broad market metrics.
- Keep jurisdiction code, company number, and legal name as first-class normalized fields.
- Bound search breadth aggressively and preserve the original match confidence.
- Validate that a company number exists before treating a hit as useful.

## Caveats

- The API-domain root-level discoverability files were not publicly readable in this pass.
- OpenCorporates is valuable for cross-jurisdiction registry coverage, but matching quality still needs local validation.
- Search hits should not overwrite stronger registry identifiers without explicit confidence logic.

## Test Gates

- search result normalization
- empty and multi-hit behavior
- jurisdiction-code handling
- confidence-preserving merge tests
