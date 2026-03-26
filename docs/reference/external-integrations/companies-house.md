# Companies House

Verified on `2026-03-25`.

## Local Usage

- [companies_house_connector.py](../../../src/solstein/data/connectors/companies_house_connector.py)
- [companies_house_agent.py](../../../src/solstein/agents/companies_house_agent.py)
- [unified.py](../../../src/solstein/data/unified/unified.py)

## Official Surfaces

- Developer hub: `https://developer.company-information.service.gov.uk/api/docs/`
- Official GitHub org: `https://github.com/companieshouse`
- `llms.txt`: `https://developer.company-information.service.gov.uk/llms.txt` returned `404` in this pass
- `robots.txt`: `https://developer.company-information.service.gov.uk/robots.txt` returned `404` in this pass

## Good Patterning

- Treat Companies House as authoritative UK registry data, not a general financial market API.
- Use the API key with the auth method the provider expects. This must stay explicit in connector tests.
- Normalize company number formatting before downstream matching.
- Keep profile, filing history, and derived company facts as separate layers.
- Preserve jurisdiction and incorporation metadata without overfitting them into financial fields the source does not truly provide.

## Caveats

- This source is strongest for corporate registration and filing metadata, not broad market intelligence.
- The developer subdomain did not expose `llms.txt` or `robots.txt` in this pass.
- UK-only authority should not be generalized into non-UK entity assumptions.

## Test Gates

- auth-shape regression tests
- company-number normalization tests
- filing-history parsing fixtures
- merge tests ensuring Companies House data only fills the fields it truly owns
