---
name: research-ai-talent
description: "Please perform a deep AI talent intelligence research on an energy software competitor"
category: analysis
tags: competition, ai, talent, acqui-hire, personnel, leadership, nuclear
argument-hint: "Company name and path to company folder (e.g., Volue ASA @tickets/COMPETITION/volue/)"
tools:
  - web/*
  - search/codebase
  - fileSystem
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
  - .cursor/rules/prompts/prompt-registry-integration-rule.mdc
---

# Research AI Talent - Per-Competitor Deep-Dive

Please perform a structured AI talent intelligence research session on an energy software competitor to Eneve's eBase platform. This prompt drives systematic public-source research focused on AI/ML team composition, key personnel, talent concentration risk, and acqui-hire attractiveness, then writes an `ai-talent.md` file in the competitor's folder.

**Classification: NUCLEAR** -- This research output is for CTO/Board eyes only.

**Pattern**: Guided Analysis Pattern
**Effectiveness**: Maps the people behind competitor AI capabilities using only public sources
**Use When**: After initial competitor identification and financial research are complete

---

## Purpose

This prompt identifies the human capital powering competitor AI capabilities by:

- Mapping AI/ML leadership (CTO, VP Engineering, Head of AI, Chief Data Scientist)
- Estimating AI team size and density within the engineering org
- Tracking key AI/ML hires over the last 24 months
- Identifying talent origins (academia, FAANG, energy sector, startups)
- Cataloguing public AI output (papers, patents, open-source contributions)
- Scoring **Talent Concentration Risk** (how fragile is their AI capability?)
- Scoring **Acqui-Hire Attractiveness** (is this company worth buying for the people?)

The end goal: identify which competitors have deep, resilient AI benches and which are one-departure away from losing their AI edge. This feeds directly into acqui-hire strategy and defensive talent retention planning.

---

## Ethical Guardrails

This research MUST stay within public information boundaries:

- LinkedIn public profiles and job postings only
- Published conference papers, patents, and academic citations (public record)
- Press releases and company announcements
- GitHub/open-source contributions (public repositories)
- Company careers pages and job descriptions
- Conference speaker lists and presentation recordings
- NO scraping private data
- NO purchasing data broker lists
- NO social engineering or pretexting
- NO salary data or compensation estimates
- NO personal contact details (email, phone, home address)
- NO information from private/locked social media profiles

**If in doubt about a data source, skip it.**

---

## Required Context

- **Company Name**: The competitor to research (e.g., "Volue ASA")
- **Company Folder**: Path to the competitor's folder in `tickets/COMPETITION/` (e.g., `@tickets/COMPETITION/volue/`)
- **Existing Data**: Read `financial-growth.md` and `deep-analysis.md` from the company folder for headcount, AI mentions, and growth classification

**Optional Parameters**:
- **Research Depth**: `quick` (leadership + team size only) or `full` (all 5 categories, default)
- **Focus Area**: Override to focus on a specific talent category (e.g., "publications only")

---

## Reasoning Process (for AI Agent)

Before beginning research, the AI should:

1. **Understand the target**: Read existing files to build baseline understanding of the company's size, growth trajectory, and AI posture
2. **Classify company type** to calibrate expectations:

```text
Is the company a Rocket with >100 employees?
├── YES → Expect visible AI team, LinkedIn searchable, possibly published
│
├── Is the company a startup (<50 employees)?
│   ├── YES → AI team may be founders; search founding team backgrounds
│   └── NO → Search for AI-titled roles on LinkedIn
│
└── Is the company a Dinosaur/Steady?
    ├── YES → AI team likely small or non-existent; may have "analytics" not "AI"
    └── Check for recent AI hiring signals (job postings, press releases)
```

3. **Start with leadership**: Finding the AI leader often unlocks the rest of the team (their connections, co-authors, team mentions)
4. **Cross-reference sources**: LinkedIn + conference papers + GitHub can triangulate team size
5. **Be honest about gaps**: Mark "Unknown" rather than guessing. For private companies, AI team info is often opaque
6. **Score rigorously**: Apply the rubric criteria, not gut feeling. A Dinosaur with no visible AI team scores Concentration Risk 9-10 (if they have any AI, it's probably one person)
7. **Self-review before writing**: Before finalizing `ai-talent.md`, verify every data point has a source, every score uses the rubric, and no ethical boundaries were crossed

---

## Process

### Step 1: Read Existing Profile

Read the competitor's existing files from the company folder. Extract any AI/talent data already present -- particularly from `deep-analysis.md` (AI & Innovation section) and `financial-growth.md` (employee data, open positions). Note existing headcount, AI staff %, and any named individuals.

### Step 2: Read Eneve Positioning

Read `tickets/COMPETITION/README.md` to understand Eneve's AI capabilities for contrast.

### Step 3: Web Research by Talent Category

For each of the 5 talent research categories below, perform targeted web searches. Prioritize these source types (in order of reliability):

1. **LinkedIn public profiles** (role titles, tenure, background)
2. **Company careers page** (open AI/ML roles, tech stack signals)
3. **Conference proceedings** (NeurIPS, ICML, IEEE, Energy conferences)
4. **Patent databases** (Google Patents, Espacenet)
5. **GitHub organization** (public repos, contributors)
6. **Press releases** (key hire announcements, team growth)
7. **Academic papers** (Google Scholar, arXiv)
8. **Company blog/tech blog** (AI team introductions, tech deep-dives)
9. **Podcast/interview appearances** (CTO/AI lead interviews)
10. **Industry events** (Windeurope, E-world, European Utility Week speaker lists)

### Step 4: Map AI Leadership

Identify the AI/ML leadership chain. For each person found:
- Name (public LinkedIn)
- Current title
- Tenure at this company
- Previous employer/role (most recent)
- Academic background (if notable -- PhD, published researcher)
- Public visibility (conference speaker, blog author, etc.)

### Step 5: Estimate Team Composition

Build the best estimate of AI/ML team size and composition:
- Total AI/ML headcount (from LinkedIn, job postings, company claims)
- Breakdown by role type (ML Engineer, Data Scientist, ML Ops, Research Scientist)
- AI team as % of total engineering headcount
- AI team as % of total company headcount
- Open AI/ML positions (signals growth or backfill)

### Step 6: Track Recent Key Hires

Identify notable AI/ML hires in the last 24 months:
- Who joined from where (origin company/institution)
- What role they took
- What they brought (specific expertise, connections, IP knowledge)

### Step 7: Score Talent Dimensions

Using the **Talent Scorecard Criteria** defined below, assign scores for Talent Concentration Risk and Acqui-Hire Attractiveness. Use the rubric, not gut feeling.

### Step 8: Final Review (Self-Correction)

Before writing the output file, verify:
- Every data point has a source attribution
- Every data point has a confidence level
- Both scores use the rubric criteria, not just intuition
- No ethical guardrails were violated
- "Unknown" is used honestly where data is unavailable
- The output format matches the template exactly

### Step 9: Write AI Talent File

Write the output to a **separate file** within the competitor's folder:

- **File path**: `tickets/COMPETITION/[company-slug]/ai-talent.md`
- Create the company folder if it doesn't exist
- If an `ai-talent.md` already exists, replace it with the updated version

---

## Usage Modes

### Quick Mode (15-20 min)

For rapid assessment when time is limited. Focus on Categories 1-2 only:

```text
@research-ai-talent Volue ASA @tickets/COMPETITION/volue/ --quick
```

**Covers**: AI leadership identification + team size estimate + scores
**Skips**: Key hires tracking, publications/patents, infrastructure signals
**Output**: Abbreviated `ai-talent.md` with Leadership, Team Composition, and Scorecard sections only

### Full Mode (45-60 min, default)

Complete deep-dive across all 5 categories:

```text
@research-ai-talent Octopus Energy Group @tickets/COMPETITION/octopus-energy-kraken/
```

**Covers**: All 5 research categories, all output sections
**Output**: Complete `ai-talent.md` per the Output Format template

---

## Research Categories

### Category 1: AI/ML Leadership

| Data Point | Search Strategy |
| --- | --- |
| CTO / VP Engineering | LinkedIn, company About page, press releases |
| Head of AI / ML | LinkedIn title search, company blog |
| Chief Data Scientist | LinkedIn, conference speaker lists |
| AI Team Lead(s) | LinkedIn, GitHub commit history, paper authorship |
| Reporting structure | LinkedIn profiles (who reports to whom) |
| Leadership tenure | LinkedIn start dates |
| Leadership origin | LinkedIn previous experience |

### Category 2: Team Size & Composition

| Data Point | Search Strategy |
| --- | --- |
| Total AI/ML headcount | LinkedIn people search (company + AI/ML titles), company claims |
| ML Engineers | LinkedIn title search |
| Data Scientists | LinkedIn title search |
| ML Ops / Platform | LinkedIn title search, job postings |
| Research Scientists | LinkedIn, academic affiliations |
| AI team % of engineering | Calculated from headcount estimates |
| AI team % of total company | Calculated from total headcount |
| Open AI/ML positions | Careers page, LinkedIn Jobs, Indeed |
| Hiring velocity | Compare current openings to team size |

### Category 3: Key Hires & Talent Flows

| Data Point | Search Strategy |
| --- | --- |
| Notable hires (last 24mo) | LinkedIn new role announcements, press releases |
| Origin companies | LinkedIn previous experience |
| Origin institutions | LinkedIn education, Google Scholar |
| Expertise areas | LinkedIn skills, paper topics, GitHub repos |
| Departures (if visible) | LinkedIn role changes away from company |
| Net talent flow direction | Compare arrivals vs departures |

### Category 4: Publications, Patents & Open Source

| Data Point | Search Strategy |
| --- | --- |
| Conference papers | Google Scholar, DBLP, arXiv (search company name + AI/ML) |
| Patents filed | Google Patents, Espacenet |
| Open-source repos | GitHub organization, key contributor profiles |
| Blog posts / tech articles | Company tech blog, Medium, personal blogs |
| Conference talks | YouTube, conference archives, SlideShare |
| Academic collaborations | Paper co-authorship with universities |

### Category 5: AI Infrastructure & Maturity Signals

| Data Point | Search Strategy |
| --- | --- |
| ML platform / tools used | Job postings (tech stack requirements), blog posts |
| Cloud AI services used | Job postings, case studies, partner announcements |
| Model deployment approach | Blog posts, conference talks |
| Data engineering capability | Job postings, LinkedIn team composition |
| MLOps maturity | Job postings for MLOps roles, blog posts on deployment |

---

## Talent Scorecard Criteria

### Talent Concentration Risk (1-10)

Measures how fragile the AI capability is. **Higher = more fragile / more concentrated.**

| Score | Criteria |
| --- | --- |
| 9-10 | AI capability depends on 1 person; no backup; departure would collapse AI efforts |
| 7-8 | AI capability concentrated in 2-3 key individuals; limited bench depth |
| 5-6 | Small AI team (5-10) with some specialization overlap; moderate resilience |
| 3-4 | Established AI team (10-20) with role redundancy; knowledge distributed |
| 1-2 | Deep AI bench (20+); multiple senior leaders; highly resilient to departures |

### Acqui-Hire Attractiveness (1-10)

Measures how attractive the company is as an acquisition target primarily for its AI talent. **Higher = more attractive target.**

| Score | Criteria |
| --- | --- |
| 9-10 | Exceptional AI team + company is vulnerable (Dinosaur/Steady) + small enough to acquire (<EUR 100M) + team is cohesive |
| 7-8 | Strong AI team + company shows weakness + reasonable acquisition cost + team has rare energy domain expertise |
| 5-6 | Competent AI team + company is Riser but acquirable + team brings useful capabilities |
| 3-4 | Average AI capability + company is too large or too healthy to acquire for talent alone |
| 1-2 | Minimal AI capability, or company is a Rocket/too expensive, or talent is generic (not energy-specialized) |

**Scoring inputs** (weight approximately equally):
- **Talent quality**: Leadership caliber, publication record, industry recognition
- **Team cohesion**: How long has team worked together, cultural fit signals
- **Company vulnerability**: Growth classification (Dinosaur > Steady > Riser > Rocket)
- **Acquisition cost**: Revenue, funding, valuation relative to talent value
- **Domain specificity**: Energy/commodity domain expertise (harder to replicate)

---

## Data Confidence Framework

Every data point in the output must carry a confidence level. Use these definitions consistently:

| Level | Definition | When to Use |
| --- | --- | --- |
| **Confirmed** | Directly stated in an authoritative source (company website, press release, published paper) | Official announcements, company About page, authored papers |
| **Estimated** | Inferred from multiple signals that agree (e.g., LinkedIn count + job posting volume) | Team size from LinkedIn search, AI % calculated from headcount |
| **Speculated** | Based on a single weak signal or indirect inference | One blog post mention, inferred from tech stack in job posting |
| **Unknown** | No data found despite searching | Always prefer "Unknown" over guessing |

**Conflict Resolution**: When sources disagree, state both values and note the discrepancy. Prefer the more authoritative source (company official > LinkedIn > press > blog).

---

## Search Query Templates

**AI Leadership**:
- `site:linkedin.com "[COMPANY]" "Head of AI" OR "VP AI" OR "Chief Data Scientist" OR "ML Lead"`
- `"[COMPANY]" "hired" OR "joins" OR "appointed" AI OR "machine learning" OR "data science"`
- `"[COMPANY]" CTO AI machine learning energy`

**Team Composition**:
- `site:linkedin.com "[COMPANY]" "machine learning engineer" OR "data scientist" OR "ML ops"`
- `"[COMPANY]" careers AI OR "machine learning" OR "data science" job`
- `"[COMPANY]" team AI OR "data science" blog`

**Publications & Patents**:
- `"[COMPANY]" site:scholar.google.com`
- `"[COMPANY]" site:arxiv.org`
- `"[COMPANY]" site:patents.google.com`
- `"[COMPANY]" energy AI OR "machine learning" conference paper 2024 2025 2026`

**Key Hires**:
- `"[COMPANY]" "joins" OR "hired" OR "welcomes" AI OR "machine learning" OR "data" 2024 2025 2026`
- `site:linkedin.com "[COMPANY]" "new position" OR "started" AI OR ML`

**Open Source**:
- `site:github.com "[COMPANY]" OR "[company-slug]" machine-learning OR ML OR AI`
- `"[COMPANY]" open source energy AI`

---

## Output Format

Structure the output as a **standalone markdown file** saved to `tickets/COMPETITION/[company-slug]/ai-talent.md`:

````markdown
# AI Talent Intelligence - [COMPANY NAME]

**Research Date**: YYYY-MM-DD
**Data Availability**: High / Medium / Low
**Classification**: CONFIDENTIAL -- STRATEGIC INTELLIGENCE

---

## AI/ML Leadership

| Name | Title | Tenure | Previous Role | Academic Background | Public Visibility | Source |
| --- | --- | --- | --- | --- | --- | --- |
| [name] | [title] | [X years] | [company, role] | [degree, institution] | [speaker/author/none] | [LinkedIn/press] |

**Leadership Assessment**: [1-2 sentences on leadership depth and quality]

## Team Composition

| Metric | Value | Source | Confidence |
| --- | --- | --- | --- |
| Total AI/ML Headcount | [N] | [source] | [Confirmed/Estimated] |
| ML Engineers | [N] | [source] | ... |
| Data Scientists | [N] | [source] | ... |
| ML Ops / Platform | [N] | [source] | ... |
| Research Scientists | [N] | [source] | ... |
| AI Team % of Engineering | [X%] | Calculated | ... |
| AI Team % of Total Company | [X%] | Calculated | ... |
| Open AI/ML Positions | [N] | [careers page] | Confirmed |

**Team Assessment**: [1-2 sentences on team maturity and depth]

## Key Hires (Last 24 Months)

| Date | Name | Role | Origin | Expertise Brought | Source |
| --- | --- | --- | --- | --- | --- |
| [YYYY-MM] | [name] | [title] | [company/institution] | [specific expertise] | [LinkedIn/press] |

**Hiring Pattern**: [1-2 sentences on talent acquisition direction]

## Talent Origin Map

| Origin Category | Count | Notable Examples |
| --- | --- | --- |
| FAANG / Big Tech | [N] | [examples] |
| Academia / Research | [N] | [examples] |
| Energy Sector | [N] | [examples] |
| Other Startups | [N] | [examples] |
| Internal Promotion | [N] | [examples] |

## Publications, Patents & Open Source

| Type | Count | Notable Items |
| --- | --- | --- |
| Conference Papers | [N] | [key papers with venues] |
| Patents Filed | [N] | [key patents with topics] |
| Open-Source Repos | [N] | [repos with star counts] |
| Blog Posts / Articles | [N] | [notable posts] |
| Conference Talks | [N] | [notable talks with events] |

**Research Output Assessment**: [1-2 sentences on intellectual output quality]

## AI Infrastructure Signals

| Signal | Evidence | Source |
| --- | --- | --- |
| ML Platform | [tools/frameworks used] | [job postings/blog] |
| Cloud Provider | [AWS/Azure/GCP] | [job postings/blog] |
| Deployment Approach | [batch/real-time/edge] | [blog/talks] |
| MLOps Maturity | [manual/CI-CD/full MLOps] | [job postings] |

## Talent Scorecard

| Dimension | Score (1-10) | Evidence Summary |
| --- | --- | --- |
| Talent Concentration Risk | [X] | [1-line justification: who holds the keys?] |
| Acqui-Hire Attractiveness | [X] | [1-line justification: talent quality vs acquisition feasibility] |

## What Happens If Key People Leave

[For top AI-dependent competitors only -- skip for companies with deep benches]

| Person/Role | Impact If Lost | Replacement Difficulty | Mitigation |
| --- | --- | --- | --- |
| [Name/Role] | [impact on AI capability] | [Easy/Medium/Hard/Critical] | [what company could do] |

## Talent Flow Summary

**Net Direction**: [Gaining / Losing / Stable]
**Key Inflows From**: [companies/institutions talent is coming from]
**Key Outflows To**: [companies/institutions talent is leaving to, if visible]

---

**Data Quality Note**: [Honest assessment of data completeness and confidence. Note major gaps.]

> **Ethical Compliance**: This research used only publicly available information from LinkedIn profiles, published papers, patents, press releases, GitHub, and company websites. No private data was accessed.
````

---

## Examples (Few-Shot)

### Example 1: Rocket with Visible AI Team (Octopus/Kraken)

**Input**: `@research-ai-talent Octopus Energy Group @tickets/COMPETITION/octopus-energy-kraken/`

**Reasoning**: Large, well-funded Rocket company (~7,000 employees) with public AI claims and a dedicated technology platform (Kraken). Expect high data availability: leadership identifiable on LinkedIn, team size estimable, conference papers and patents likely.

**Expected Output Snippet** (Leadership table):

```markdown
## AI/ML Leadership

| Name | Title | Tenure | Previous Role | Academic Background | Public Visibility | Source |
| --- | --- | --- | --- | --- | --- | --- |
| [Person A] | VP of Data Science | 3 years | Google, Senior ML Engineer | PhD Machine Learning, UCL | Speaker at NeurIPS Energy Workshop 2025 | LinkedIn |
| [Person B] | Head of ML Platform | 2 years | Spotify, ML Platform Lead | MSc Computer Science, Imperial | Author of Kraken ML blog series | LinkedIn, Company Blog |

## Talent Scorecard

| Dimension | Score (1-10) | Evidence Summary |
| --- | --- | --- |
| Talent Concentration Risk | 3 | Deep AI bench (est. 50+ ML staff); multiple senior leaders; resilient |
| Acqui-Hire Attractiveness | 2 | Exceptional talent but company is too large and healthy to acquire for talent |
```

### Example 2: Startup with AI Focus (Dexter Energy)

**Input**: `@research-ai-talent Dexter Energy @tickets/COMPETITION/dexter/`

**Reasoning**: Small, AI-first startup (~20 employees). Founders are the AI team. LinkedIn profiles give background. GitHub repos may show technical depth. Limited public data beyond founder profiles.

**Expected Output Snippet** (Scorecard):

```markdown
## Talent Scorecard

| Dimension | Score (1-10) | Evidence Summary |
| --- | --- | --- |
| Talent Concentration Risk | 8 | AI capability concentrated in 2 co-founders; departure of either would cripple ML efforts |
| Acqui-Hire Attractiveness | 7 | Strong energy-domain AI talent, acquirable size (<EUR 20M), rare forecasting expertise |
```

### Example 3: Dinosaur with Minimal AI (KISTERS)

**Input**: `@research-ai-talent KISTERS AG @tickets/COMPETITION/kisters-belvis/`

**Reasoning**: Legacy company, slow growth, ~500 employees. May have "data analytics" but not "AI/ML" roles. LinkedIn search may find 0-2 people with AI titles. Expect low data availability.

**Expected Output Snippet** (Team Composition):

```markdown
## Team Composition

| Metric | Value | Source | Confidence |
| --- | --- | --- | --- |
| Total AI/ML Headcount | 2-3 | LinkedIn title search | Estimated |
| ML Engineers | 0 | LinkedIn | Estimated |
| Data Scientists | 1-2 | LinkedIn ("Data Analyst" titles, not "Data Scientist") | Speculated |
| AI Team % of Engineering | <2% | Calculated from ~150 est. engineering | Speculated |
| Open AI/ML Positions | 0 | Careers page (checked 2026-02-17) | Confirmed |

**Team Assessment**: Minimal dedicated AI capability. Analytics staff appear to use traditional statistical methods rather than ML. No visible ML engineering or MLOps investment.
```

---

## Troubleshooting

### Problem: Company is Private with No LinkedIn Presence

**Cause**: Small private companies or those in certain regions may have minimal LinkedIn adoption.
**Solution**: Shift focus to alternative signals -- GitHub repos, conference papers, patent filings, job postings on local boards (StepStone, Indeed.de), company blog. Note "Low" data availability in output and explain gaps honestly.

### Problem: "Data Scientist" vs "Data Analyst" Ambiguity

**Cause**: Many energy companies use "Data Analyst" for roles that may or may not involve ML.
**Solution**: Check job descriptions and LinkedIn skill endorsements for ML-specific tools (TensorFlow, PyTorch, scikit-learn). If unclear, count separately with a note: "X Data Analysts (ML involvement uncertain)".

### Problem: AI Team Size Estimates Vary Wildly Across Sources

**Cause**: LinkedIn counts include departed employees; company claims may include adjacent roles.
**Solution**: Report range (e.g., "8-15") with source for each bound. Use the Data Confidence Framework: note "Estimated" and explain the discrepancy.

### Problem: No AI Leadership Identified

**Cause**: Company may embed AI within general engineering (no dedicated AI titles).
**Solution**: Search for CTO/VP Engineering and check their backgrounds for AI/ML experience. Look for "Analytics" or "Data" leadership. Report finding as-is -- absence of dedicated AI leadership is itself a meaningful signal (likely scores Concentration Risk 9-10).

### Problem: Ethical Boundary Uncertainty

**Cause**: Unclear whether a source qualifies as "public" (e.g., semi-private LinkedIn post).
**Solution**: When in doubt, skip it. Only use data that is clearly on a public page accessible without login or connection. Note the gap rather than risk an ethical violation.

---

## Quality Criteria

- [ ] All 5 talent research categories addressed (no sections skipped unless Quick mode)
- [ ] AI leadership table populated (even if "No public AI leadership identified")
- [ ] Team size estimated with source and confidence level
- [ ] Key hires tracked for last 24 months (or "None identified" if truly none)
- [ ] Every data point has a source attribution
- [ ] Every data point has a confidence level (Confirmed/Estimated/Speculated/Unknown)
- [ ] Talent Concentration Risk scored 1-10 using rubric
- [ ] Acqui-Hire Attractiveness scored 1-10 using rubric
- [ ] "What Happens If They Leave" included for top AI-dependent competitors
- [ ] Output saved to `tickets/COMPETITION/[company-slug]/ai-talent.md`
- [ ] No personal contact details, salary data, or ethically questionable information
- [ ] CONFIDENTIAL header present on output file
- [ ] Ethical compliance statement included
- [ ] Data Confidence Framework applied consistently

---

## Usage

**Full deep-dive (default)**:
```text
@research-ai-talent Octopus Energy Group @tickets/COMPETITION/octopus-energy-kraken/
@research-ai-talent Dexter Energy @tickets/COMPETITION/dexter/
@research-ai-talent KISTERS AG @tickets/COMPETITION/kisters-belvis/
```

**Quick scan (leadership + team size only)**:
```text
@research-ai-talent Volue ASA @tickets/COMPETITION/volue/ --quick
```

**Focused research (single category)**:
```text
@research-ai-talent KISTERS AG @tickets/COMPETITION/kisters-belvis/ --focus publications
```

---

## Related Prompts

- `analysis/market/research-financial-growth.prompt.md` - Financial research (complementary; run first)
- `analysis/market/research-competitor.prompt.md` - Broader deep analysis
- `analysis/market/generate-financial-dashboard.prompt.md` - Dashboard that consumes talent data

---

## Pattern Used

This prompt implements:
- `.cursor/templars/analysis/market/multi-dimensional-research-scorecard-templar.md` (dual scoring rubrics)
- `.cursor/templars/analysis/market/structured-web-research-templar.md` (research categories + confidence)
- `.cursor/templars/analysis/market/guided-research-prompt-templar.md` (step-by-step guided research)

## Reference Example

See exemplar: `.cursor/exemplars/analysis/market/research-ai-talent-exemplar.md`

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt creation standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Registry format requirements

---

**Created**: 2026-02-17
**Improved**: 2026-02-17 (improve-prompt + enhance-prompt applied)
**Context**: tickets/FINANCIALDASHBOARD/FD-031 AI Talent Tracker
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.1.0
