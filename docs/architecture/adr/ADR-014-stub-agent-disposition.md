# ADR-014: Disposition of 7 Stub Agents (STORY-078)

## Status

**Accepted** — Implemented as part of STORY-078 (EPIC-022: LangGraph Agent Orchestration)

## Context

`src/solstein/agents/additional_agents.py` defined 7 agent classes that returned
hardcoded mock data strings. These stubs were identified in STORY-017 as a critical
data integrity risk: stub data is indistinguishable from real data in research outputs,
meaning every report produced by the platform could contain fabricated information.

STORY-078 required a concrete decision for each of the 7 agents:
either implement with a real API integration, or explicitly exclude with a documented rationale.

"We haven't gotten to it yet" is not a valid rationale for keeping a stub in production.

## Decisions

### 1. LinkedInAgent — EXCLUDED

**Original purpose:** LinkedIn company profile, employee count, and hiring trends.

**Decision:** Excluded from the research graph.

**Rationale:**
- LinkedIn's API is not publicly accessible. LinkedIn requires a formal Partner API
  application with approval by LinkedIn's partner team.
- Scraping LinkedIn violates their Terms of Service and has resulted in cease-and-desist
  letters and litigation against third-party scrapers (hiQ v. LinkedIn, 2022).
- No compliant, cost-effective alternative API exists that provides LinkedIn-specific
  data (follower counts, connection trends, engagement metrics).
- Employee headcount signals are partially available from Companies House (UK filings
  include employee counts in annual accounts) and GitHub (org size from contributor counts).

**Status in graph:** Not registered as a node. The `companies_house` node captures
UK employee headcount where available.

---

### 2. SECEdgarAgent — IMPLEMENTED

**Original purpose:** SEC EDGAR financial filings (10-K, 10-Q) — revenue, net income,
R&D spending, auditor, risk factors.

**Decision:** Implemented as the `sec_filings` LangGraph node.

**Rationale:**
- SEC EDGAR is a free, public API with no API key requirement. The `edgar` Python
  library (already a project dependency) provides typed access to EDGAR filings.
- The `SECEdgarConnector` class already existed in
  `src/solstein/data/connectors/sec_edgar_connector.py` with full test coverage.
- EDGAR data is authoritative, not scraped — it is the primary source for US public
  company financial data used by professional investors.

**Implementation:** `src/solstein/research/graph/nodes/sec_filings_node.py`

**Limitation:** Only covers US-listed public companies that have a known stock ticker.
Companies without a ticker (UK, EU, private companies) produce a coverage gap recorded
in `data_collection_errors`, not a pipeline error.

---

### 3. PatentsAgent — EXCLUDED

**Original purpose:** Patent portfolio analysis — total patents, citation count,
technology areas, pending applications.

**Decision:** Excluded from the research graph.

**Rationale:**
- The USPTO Patent Full-Text and Image Database (PatFT/AppFT) provides bulk data downloads
  but no real-time API suitable for per-company lookups in a research pipeline.
- Google Patents API was deprecated in 2015.
- The USPTO Patent Examination Data System (PEDS) API is rate-limited to 3 requests/second
  and requires USPTO-specific company entity IDs that are non-trivial to resolve from
  company names.
- Lens.org and Espacenet provide patent search APIs but require organisation-level
  agreements for commercial use at scale.
- Patent data is slow-moving (patents are filed quarterly, take 18+ months to publish)
  and has limited signal value for the near-term competitive intelligence use cases
  Solstein serves (fundraising events, hiring signals, product launches).

**Status in graph:** Not registered as a node.

---

### 4. NewsAgent — IMPLEMENTED

**Original purpose:** News coverage, press mentions, brand sentiment.

**Decision:** Implemented as the `news_search` LangGraph node.

**Rationale:**
- The `WebSearchAgent` class already existed in
  `src/solstein/agents/web_search_agent.py` with Google Custom Search API integration.
- Google Custom Search API provides access to news content with structured metadata
  (title, URL, snippet, published date).
- This covers press releases, TechCrunch/Forbes/VentureBeat articles, and general
  web search results that reflect brand awareness and recent company activity.

**Implementation:** `src/solstein/research/graph/nodes/news_node.py`

**Limitation:** Requires `GOOGLE_API_KEY` and a configured Google Custom Search Engine ID.
When either is absent, the agent returns a coverage gap rather than crashing.

---

### 5. JobsAgent — EXCLUDED

**Original purpose:** Job posting analysis — active openings, hiring departments,
geographic expansion, monthly hiring rate.

**Decision:** Excluded from the research graph.

**Rationale:**
- Indeed's API was restricted in 2018 and now requires a publisher agreement that
  is no longer accepting new applications from non-staffing companies.
- LinkedIn Jobs API requires a LinkedIn Partner API agreement (same barrier as
  LinkedInAgent above).
- Glassdoor's partner API program was closed to new applications in 2023.
- Adzuna and Reed.co.uk provide job posting APIs but primarily cover UK postings
  and require paid plans for meaningful volume.
- Jobs data has moderate signal value: it is available with a 24-48 hour lag, and
  aggregate signals (e.g., "company is hiring 15 engineers") are available more
  reliably through GitHub (contributor growth) and Companies House (employee
  headcount trends in annual filings).

**Status in graph:** Not registered as a node.

---

### 6. TechTrendsAgent — EXCLUDED

**Original purpose:** Technology adoption signals — cloud providers, AI adoption,
frameworks, databases, DevOps tools, modernization score.

**Decision:** Excluded as a standalone node. Tech stack signals are partially
covered by the `web_profile` node (WebsiteAgent).

**Rationale:**
- Wappalyzer's API was made paid-only in 2022 (€49–€249/month for API access).
- BuiltWith API costs $295–$995/month.
- SimilarTech requires a commercial agreement.
- The `WebsiteAgent` (implemented as the `web_profile` node) already extracts
  technology stack signals from HTML meta-tags, script src attributes, and
  framework fingerprints during web scraping at no additional API cost.
- GitHub (implemented as the `github_data` node) provides authoritative technology
  signals: primary language, topics, and dependency files.
- Combining `web_profile` and `github_data` outputs in the `conflict_resolution`
  node provides equivalent or better technology signals than a standalone paid API.

**Status in graph:** Not registered as a standalone node. Signals covered by
`web_profile` and `github_data` nodes.

---

### 7. WebsiteAgent — IMPLEMENTED

**Original purpose:** Website traffic, tech stack, core web vitals, Alexa rank.

**Decision:** Implemented as the `web_profile` LangGraph node.

**Rationale:**
- The `WebsiteAgent` class already existed in `src/solstein/agents/website_agent.py`
  with SSRF-protected HTTP GET, HTML title/meta parsing, and AI signal extraction.
- Website data is freely available (no API required) for any company with a public
  website URL.
- The `web_profile` node provides title, description, AI signals, and detected
  technology stack — directly replacing the stub data.

**Implementation:** `src/solstein/research/graph/nodes/web_profile_node.py`

**Limitation:** Requires a known website URL. The URL must be provided in
`state["config"]["websites"]` as a `{company_id: url}` mapping, or in
`config["configurable"]["websites"]`. Without a URL, the company produces a
coverage gap in `data_collection_errors`.

---

## Summary Table

| Stub Agent | Decision | Rationale Summary | Graph Node |
|------------|----------|-------------------|------------|
| LinkedInAgent | Excluded | No public API, ToS violation risk | — |
| SECEdgarAgent | Implemented | Free public API, connector existed | `sec_filings` |
| PatentsAgent | Excluded | No cost-effective real-time API | — |
| NewsAgent | Implemented | Google Custom Search API existed | `news_search` |
| JobsAgent | Excluded | All major job APIs closed/paid | — |
| TechTrendsAgent | Excluded | Paid APIs; signals covered by web_profile + github | — |
| WebsiteAgent | Implemented | Free HTTP scraping, agent existed | `web_profile` |

## Consequences

**Positive:**
- `additional_agents.py` has been deleted. No stub agents remain in the codebase.
- Research reports no longer contain hardcoded fabricated data.
- The 5 data-collection nodes in the LangGraph pipeline all call real external APIs.
- Each excluded agent has a clear, documented rationale that can be revisited
  if better API options become available.
- Graph nodes are independently testable (see `tests/unit/test_story078_real_agent_nodes.py`).

**Negative / Trade-offs:**
- LinkedIn headcount and job posting signals are not available without paid/partner APIs.
- Patent data is not available without significant API integration effort.
- The `sec_filings` node only covers US public companies with known ticker symbols.
- The `web_profile` node requires a known website URL per company.

**Future Considerations:**
- If Solstein secures a LinkedIn Partner API agreement, `LinkedInAgent` can be
  re-implemented as a `linkedin_data` graph node.
- If patent signal becomes a priority, the USPTO PEDS API or Lens.org commercial
  agreement could be evaluated.
- A job signal approximation (not production-ready) could be built on Adzuna's free
  tier for UK-based companies.
