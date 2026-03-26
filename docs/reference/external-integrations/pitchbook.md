# PitchBook

Verified on `2026-03-26`.

## Current Repo Status

PitchBook is documented as a premium target provider, but there is no active production connector in the main runtime paths yet.

## Official Surfaces

- Product page referenced in repo docs: `https://pitchbook.com/products/api-data-feed`
- `robots.txt`: `https://pitchbook.com/robots.txt`
- `llms.txt`: `https://pitchbook.com/llms.txt`

Observed in this pass:

- the product page returned a Cloudflare challenge page
- the `llms.txt` route also returned a challenge page
- `robots.txt` was reachable

So public discoverability exists, but automated retrieval is gated.

## Why It Matters

PitchBook is one of the few provider candidates in the repo that could materially change private-market coverage quality if integrated correctly.

It is especially relevant for:

- deal data
- private valuations
- investor participation
- fund and ownership context

## Good Patterning

- Keep PitchBook as a premium authoritative private-market source if adopted.
- Do not model it like public-web search or news-derived funding.
- Create separate schemas for:
  - organization profile
  - financing event
  - investor participation
  - valuation facts

## Caveats

- The public web surface is protected enough that future agent retrieval may require logged-in or manually exported docs.
- Repo docs mention PitchBook, but that is not the same as a verified working integration.
- If adopted, PitchBook should become a first-class contract with strict tests before it is trusted in the scoring path.

## Test Gates

- provider contract fixtures from real sample payloads
- strict valuation and round-event schemas
- merge tests versus Crunchbase and news-derived funding
