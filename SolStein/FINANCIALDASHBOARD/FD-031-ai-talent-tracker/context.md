# FD-031 Context

**Last Updated**: 2026-02-17

## Technical Background

The Financial Dashboard project has 30 completed or planned tickets across 4 phases. Phase 3 introduced PE-firm-ready intelligence sheets (AI Maturity Matrix, M&A Vulnerability, Threat Timeline, etc.). FD-031 adds a new dimension: **people intelligence** -- who are the AI builders at competitor companies, and what would it take to acquire that talent.

This is classified as a "nuclear option" because talent intelligence is the most aggressive form of competitive intelligence. It directly supports:
- **Acqui-hire strategy**: Identifying small companies worth buying primarily for their AI team
- **Defensive retention**: Understanding where Eneve's own talent might be poached to
- **Capability gap analysis**: Mapping what AI skills competitors have that Eneve lacks

## Current Focus

**Implementation complete.** All code deliverables are in place. The pipeline is ready to process `ai-talent.md` files as soon as the research prompt produces them.

## Key Components

- `.cursor/prompts/analysis/market/research-ai-talent.prompt.md` -- research prompt (created)
- `.cursor/scripts/analysis/market/extract_competitor_data.py` -- `extract_ai_talent()` function added
- `.cursor/scripts/analysis/market/competitor_utils.py` -- 9 new accessor functions for talent data
- `.cursor/scripts/analysis/market/generate_excel_report.py` -- `write_ai_talent_map_sheet()` added (19th sheet)
- Per-competitor `ai-talent.md` files -- to be created by running the research prompt per competitor
- `financial-dashboard.md` -- existing growth classifications feed acqui-hire scoring

## Outstanding Issues

- **Data collection pending**: Research prompt created but not yet run against competitors
- **Data quality uncertainty**: AI team composition is rarely disclosed publicly; expect gaps
- **Scoring calibration**: May need to adjust rubric after seeing first 3 competitor results

## Next Steps

1. Run `@research-ai-talent` against 3 test competitors (Octopus, Dexter, KISTERS)
2. Evaluate data quality and adjust prompt if needed
3. Run against remaining 30 competitors
4. Generate full dashboard with populated AI Talent Map sheet
5. Review bubble chart and scoring distribution for reasonableness
