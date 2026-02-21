# FD-033: Create Geographic Intelligence Research Prompt + Exemplar

## Objective

Create a dedicated `research-geographic-intelligence.prompt.md` and companion exemplar that collects country-level operational data for each competitor: which countries they operate in, operational status (Active/Entering/Planned), entry year, HQ location, and revenue distribution by region. This feeds FD-017 (Geographic Expansion Tracker) and FD-023 (Geographic Map) which are both blocked without structured geographic data.

## Requirements

- Create `.cursor/prompts/analysis/market/research-geographic-intelligence.prompt.md`
- Create `.cursor/exemplars/analysis/market/research-geographic-intelligence-exemplar.md`
- Prompt produces per-competitor country matrix: Country | Status | Entry Year | Revenue Signal | Source | Confidence
- Prompt produces aggregate country-vs-competitor matrix (like protocol map pattern)
- Output covers 14+ European countries minimum (NL, DE, AT, CH, UK, NO, SE, DK, FI, FR, ES, IT, PL, BE)
- Status classification: Active (confirmed operations), Entering (recent expansion signals), Planned (stated plans), Unknown
- Integrate with existing competitor data in `tickets/COMPETITION/[company-slug]/`
- Follow `systematic-mapping-research-templar.md` pattern (country-vs-company matrix is a mapping pattern)
- Include Mermaid geographic density chart

## Acceptance Criteria

- [ ] Prompt file created following prompt-creation-rule standards
- [ ] Exemplar file created with "exceptional" quality rating
- [ ] Prompt uses `systematic-mapping-research-templar.md` as structural basis
- [ ] Output format produces machine-parseable country matrix
- [ ] 14+ European countries covered with status classification
- [ ] Few-shot examples span data availability spectrum (well-documented vs opaque)
- [ ] Search query templates included for geographic discovery
- [ ] Self-correction checklist included
- [ ] Downstream feed mapping to FD-017 and FD-023 documented
- [ ] Prompt references existing geographic data in `research-financial-growth.prompt.md` as starting context

## Implementation Strategy

1. Read `systematic-mapping-research-templar.md` for structural pattern
2. Read `research-protocols.prompt.md` and `research-protocols-exemplar.md` as closest analogous examples (country-based mapping)
3. Define geographic research categories (HQ, subsidiaries, partnerships, customer base, market entry signals)
4. Define country matrix output format compatible with `extract_competitor_data.py` expectations
5. Write prompt with scoring rubric, few-shot examples, search strategies
6. Write exemplar documenting why the prompt is exemplary
7. Validate against prompt-creation-rule quality criteria

## Complexity Assessment

**Track**: Complex Implementation
**Rationale**: New prompt + exemplar creation requiring research pattern design, output format specification that must integrate with extraction scripts, and cross-referencing with 3+ existing prompts.
- Root Cause: No dedicated geographic data collection exists; current data is a byproduct of financial growth research (single 1-10 score, not country-level matrix)
- Files Affected: 2 new files + potential update to extraction script
- Risk Level: Medium (output format must match script expectations)
- Solution Pattern: Known (systematic-mapping-research templar)

## Status

Planning

## Testing Strategy

- Invoke prompt for 2-3 known competitors with varying geographic breadth
- Verify output format is parseable by extraction scripts
- Validate country matrix completeness against known competitor presence

## Notes

- This is the second-highest priority prompt improvement
- Blocks: FD-017 (Geographic Expansion Tracker), FD-023 (Geographic Map)
- Leverages: `systematic-mapping-research-templar.md` (already exists for protocol mapping)
- Cross-references: `research-financial-growth.prompt.md` geographic dimension, `research-protocols.prompt.md` country-based research
