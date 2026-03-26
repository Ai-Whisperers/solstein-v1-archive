# PatentsView

Verified on `2026-03-26`.

## Local Usage

- [patents.py](../../../src/solstein/data/sources/patents.py)
- [patentsview.py](../../../src/solstein/connectors/government/patentsview.py)
- [patents_refresh.py](../../../src/solstein/infrastructure/connectors/patents_refresh.py)

## Official Surfaces

- Search docs: `https://search.patentsview.org/docs/`
- Search docs `llms.txt`: `https://search.patentsview.org/llms.txt` returned `404` in this pass
- Search docs `robots.txt`: `https://search.patentsview.org/robots.txt` returned `404` in this pass

Important result from this pass:

- `https://api.patentsview.org/` returned `410 discontinued`

## Current Contract Drift

Two different PatentsView-era contracts exist in the repo today:

- [patents.py](../../../src/solstein/data/sources/patents.py) uses `https://search.patentsview.org/api/v1`
- [patentsview.py](../../../src/solstein/connectors/government/patentsview.py) still uses `https://api.patentsview.org/patents/query`

That older API root now returns `410 discontinued`, so this is no longer just a style inconsistency.

## Good Patterning

- Standardize on the active search platform contract before adding more patent logic.
- Treat patent search payloads as their own schema family.
- Keep patent portfolio totals, recent patents, and AI-related patent counts separate in normalized models.
- Validate the active API host at connector startup rather than discovering drift only during refresh jobs.

## Caveats

- Patent retrieval is not a single-source problem in this repo. There are also fallback and unified patent paths outside PatentsView.
- Any tests that only mock a happy-path patent shape without validating the host and endpoint contract will miss the real failure mode.

## Test Gates

- startup contract test for the live PatentsView host
- schema fixture for patent search responses
- regression test proving the discontinued host cannot silently remain in production code
- merge tests for patent counts and AI-related patent ratios
