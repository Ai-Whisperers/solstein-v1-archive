# OpenFIGI

Verified on `2026-03-25`.

## Local Usage

- [openfigi.py](../../../src/solstein/data/connectors/lookup_strategies/openfigi.py)

## Official Surfaces

- Docs: `https://www.openfigi.com/api/documentation`
- `robots.txt`: `https://www.openfigi.com/robots.txt`
- Official examples repo: `https://github.com/OpenFIGI/api-examples`
- `llms.txt`: `https://www.openfigi.com/llms.txt` was not present in this pass

## Good Patterning

- Treat OpenFIGI as identifier resolution infrastructure, not a company profile source.
- Keep request payload shape and response normalization strongly typed.
- Separate true identifiers from inferred fields.
- Do not over-trust company-number inference from descriptive text.

## Caveats

- The current strategy infers `company_number` from `securityDescription`.
- That inference is heuristic and should never be treated as authoritative registry truth.
- OpenFIGI is strongest when used to enrich identifier graphs, not to replace registry systems.

## Test Gates

- request payload contract tests
- response-list and empty-response handling
- heuristic-inference tests proving inferred company numbers remain optional
