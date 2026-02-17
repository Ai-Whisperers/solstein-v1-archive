# FD-031: AI Talent Tracker -- Key Personnel Intelligence

## Objective

Add an "AI Talent Map" sheet to the financial dashboard Excel workbook, identifying key AI/ML talent at each competitor -- the people who make the AI engine run. This is the most sensitive sheet in the dashboard: it maps who built what, where they came from, and what losing them would mean.

**Classification: NUCLEAR** -- This sheet is for CTO/Board eyes only. It directly supports acqui-hire strategy (buying companies primarily for their AI talent) and defensive talent retention planning.

**In scope**: Per-competitor AI leadership identification, team size estimates, key hire tracking, acqui-hire target scoring, talent concentration risk.
**Out of scope**: Individual salary estimates, personal contact details, social media stalking, anything that crosses ethical/legal lines.

## Requirements

1. For each of the 33 competitors, identify:
   - **AI/ML Leadership**: CTO, VP Engineering, Head of AI/ML, Chief Data Scientist -- named where public
   - **AI Team Size**: Estimated headcount of AI/ML engineers, data scientists, ML ops
   - **AI Talent Density**: AI team as % of total engineering headcount
   - **Key Hires (last 24 months)**: Notable AI/ML hires from LinkedIn, press releases, conference speakers
   - **Talent Origin**: Where their AI talent came from (academia, FAANG, other energy companies, startups)
   - **AI Publication/Patent Activity**: Conference papers, patents filed, open-source contributions
2. Score each competitor on **AI Talent Concentration Risk** (1-10):
   - High score = AI capability concentrated in 1-3 key individuals (fragile)
   - Low score = Deep bench, distributed AI knowledge (resilient)
3. Score each competitor on **Acqui-Hire Attractiveness** (1-10):
   - Combines: talent quality, team cohesion, company vulnerability (Dinosaur/Steady classification), reasonable acquisition cost
   - High score = prime acqui-hire target
4. Include a "What Happens If They Leave" column for top-10 AI-dependent competitors
5. Map talent flows: which companies are losing AI talent, which are gaining
6. Chart: bubble chart -- AI Team Size (x) vs AI Talent Density (y), bubble size = Acqui-Hire Score, color = Growth Classification

## Implementation Strategy

1. **Research prompt**: Create `research-ai-talent.prompt.md` to systematically gather AI talent data per competitor from LinkedIn, conference proceedings, patent databases, press releases, GitHub profiles
2. **Data collection**: Run prompt against all 33 competitors, store results in per-competitor `ai-talent.md` files alongside existing `financial-growth.md`
3. **Extraction logic**: Extend `extract_competitor_data.py` to parse `ai-talent.md` and extract structured fields (leadership, team size, density, key hires, publications, scores)
4. **Classification logic**: Apply Talent Concentration Risk and Acqui-Hire Attractiveness scoring from Requirements 2-3
5. **Sheet creation**: Build "AI Talent Map" sheet with conditional formatting -- red for high concentration risk, green for acqui-hire targets
6. **Talent flow analysis**: Cross-reference key hires to identify talent migration patterns between competitors
7. **Bubble chart**: Create AI Team Size vs Density chart with acqui-hire scoring as bubble size
8. **Sensitivity marking**: Add "CONFIDENTIAL -- STRATEGIC INTELLIGENCE" watermark/header to the sheet

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Requires novel research prompt creation, synthesis of unstructured talent data from multiple public sources, judgment-based scoring on two new dimensions, and sensitivity-appropriate presentation. No established pattern for talent intelligence in the current dashboard.

**Criteria Met**:
- Root Cause: Multiple (research prompt + data collection + scoring + visualization + sensitivity controls)
- Files Affected: 5+ (new prompt, extraction script, generation script, per-competitor files, Excel output)
- Lines Changed: >100 (new sheet logic, new extraction fields, new scoring algorithms, chart, research prompt)
- Risk Level: High (ethical boundaries must be respected; data quality varies widely; subjective scoring)
- Solution Pattern: Novel (no existing talent tracking pattern in this dashboard)

**Effort**: 4-6h (excluding per-competitor research time which is prompt-driven)

## Acceptance Criteria

- [ ] AI Talent Map sheet present in the dashboard Excel workbook
- [ ] All 33 competitors have AI team size estimates (even if "Unknown")
- [ ] AI Talent Concentration Risk scored 1-10 for each competitor
- [ ] Acqui-Hire Attractiveness scored 1-10 for each competitor
- [ ] Top-10 AI-dependent competitors have "What Happens If They Leave" analysis
- [ ] Talent flow patterns identified (who's gaining, who's losing AI talent)
- [ ] Bubble chart renders correctly in Excel
- [ ] Sheet marked as CONFIDENTIAL with appropriate sensitivity header
- [ ] Research prompt created and tested against at least 3 competitors
- [ ] No personal contact details, salary data, or ethically questionable information included

## Ethical Guardrails

This ticket deliberately stays within public information boundaries:
- LinkedIn public profiles and job postings only
- Published conference papers and patents (public record)
- Press releases and company announcements
- GitHub/open-source contributions (public)
- NO scraping private data, NO purchasing data broker lists, NO social engineering

## Dependencies

- FD-024 (Prompt-Dashboard Data Alignment) -- informs prompt structure
- Existing `financial-dashboard.md` -- growth classification feeds into acqui-hire scoring
- Per-competitor research files -- existing `deep-analysis.md` may mention AI capabilities

## Status

Implementation Complete (awaiting data collection via research prompt)
