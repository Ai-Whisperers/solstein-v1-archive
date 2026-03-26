# BuiltWith

Verified on `2026-03-26`.

## Current Repo Status

BuiltWith is documented as a desired provider, but there is no active production connector in the main runtime paths yet.

## Official Surfaces

- Main site: `https://builtwith.com`
- `robots.txt`: `https://builtwith.com/robots.txt`
- `llms.txt`: `https://builtwith.com/llms.txt`

The main site also exposes navigation links to `api.builtwith.com`.

## Why It Matters

BuiltWith is a higher-quality technology-detection surface than Solstein's current direct website keyword scraping.

That makes it a strong candidate for replacing or at least calibrating:

- ad hoc website HTML keyword extraction
- tech stack guesses inferred from generic web search

## Good Patterning

- Treat BuiltWith as technology-detection evidence, not company-profile evidence.
- Keep vendor/product detections separate from inferred technology categories.
- Preserve detection date and confidence if the API provides them.
- Use BuiltWith as a typed enrichment source, not as unstructured supplemental text.

## Caveats

- This is currently a planned integration, not a hardened live dependency.
- It should not be mixed with website-scraping heuristics under one schema.
- The provider is valuable precisely because it can replace a weaker heuristic path, so the boundary should stay clear.

## Test Gates

- BuiltWith normalized payload schema
- merge tests for tech-stack enrichment
- regression tests proving BuiltWith data and scraped-website heuristics remain distinguishable
