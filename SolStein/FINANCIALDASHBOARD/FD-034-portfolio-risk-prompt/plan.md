# FD-034: Create Portfolio Risk Synthesis Prompt

## Objective

Create `assess-portfolio-risk.prompt.md` that synthesizes threat data from all competitor research files into a structured risk matrix with probability and severity scores. This feeds FD-020 (Portfolio Risk Dashboard) which currently computes risk algorithmically from scattered data without a dedicated structured input.

## Requirements

- Create `.cursor/prompts/analysis/market/assess-portfolio-risk.prompt.md`
- Prompt reads all competitor files and market trends to produce portfolio-level risk assessment
- Output includes: Risk Category (Regulatory/Market/Technology/Competitive), Probability (1-5), Severity (1-5), Risk Score (P x S), Mitigation Status, Eneve Exposure
- Produces structured risk register table compatible with FD-020 script consumption
- Includes risk matrix visualization (Mermaid quadrant chart: probability vs severity)
- Aggregates individual competitor threats into portfolio-level risk themes
- References `research-market-trends.prompt.md` output for regulatory/market risks
- References `research-competitive-overlap.prompt.md` output for competitive proximity risks

## Acceptance Criteria

- [ ] Prompt file created following prompt-creation-rule standards
- [ ] Uses `multi-source-synthesis-dashboard-templar.md` as structural basis
- [ ] Output produces structured risk register table
- [ ] 4 risk categories covered: Regulatory, Market, Technology, Competitive
- [ ] Probability (1-5) and Severity (1-5) scoring rubrics defined
- [ ] Risk matrix (probability x severity) visualization included
- [ ] Top-5 portfolio risks ranked with mitigation recommendations
- [ ] Downstream feed mapping to FD-020 documented
- [ ] Few-shot example included

## Implementation Strategy

1. Read `multi-source-synthesis-dashboard-templar.md` for structural pattern
2. Read FD-020 plan.md for exact data requirements of Portfolio Risk sheet
3. Define risk categories, scoring rubrics, and output format
4. Write prompt with synthesis process from multiple input files
5. Validate output format against `generate_excel_report.py` `write_portfolio_risk_sheet()` data needs

## Complexity Assessment

**Track**: Simple Fix
**Rationale**: Single new prompt file, well-defined output format from FD-020 requirements, existing synthesis templar available.
- Root Cause: No dedicated risk synthesis prompt; FD-020 computes risk from scattered sources
- Files Affected: 1 new file
- Risk Level: Low
- Solution Pattern: Known (multi-source-synthesis-dashboard templar)

## Status

Planning
