# FD-033: Context

**Last Updated**: 2026-02-17

## Technical Background

FD-017 (Geographic Expansion Tracker) and FD-023 (Geographic Map) require country-level operational data per competitor. Currently, geographic data is collected as a single 1-10 score within `research-financial-growth.prompt.md` (one of 6 dimensions). This score is insufficient for building a country-vs-competitor matrix or rendering a map. The `research-protocols.prompt.md` does country-based mapping but for protocols, not company operations.

## Current Focus

Design the prompt using the systematic-mapping-research pattern (already proven for protocol mapping) adapted for geographic intelligence.

## Key Components

- `.cursor/templars/analysis/market/systematic-mapping-research-templar.md` -- Structural pattern to follow
- `.cursor/prompts/analysis/market/research-protocols.prompt.md` -- Closest analogy (country-based mapping)
- `.cursor/exemplars/analysis/market/research-protocols-exemplar.md` -- Exemplar reference
- `.cursor/scripts/analysis/market/extract_competitor_data.py` -- Must produce compatible output
- `tickets/COMPETITION/*/financial-growth.md` -- Existing geographic scores to cross-reference

## Outstanding Issues

- Output format must be compatible with extraction script expectations
- Country list needs to cover markets relevant to Eneve's strategy
- Some competitors have minimal public geographic data (opaque private companies)

## Next Steps

1. Study systematic-mapping-research templar pattern
2. Study protocols prompt/exemplar as closest analogy
3. Define country matrix output format
4. Draft prompt and exemplar
