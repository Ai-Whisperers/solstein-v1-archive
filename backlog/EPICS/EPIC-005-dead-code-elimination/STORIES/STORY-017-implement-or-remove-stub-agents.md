# STORY-017: Implement or Permanently Remove Stub Agents

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-005: Dead Code Elimination](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `agents/additional_agents.py` lines 45–268 contain 7 agent classes: `LinkedInAgent`, `SECEdgarAgent`, `PatentsAgent`, `NewsSignalAgent`, `JobsAgent`, `TechTrendsAgent`, and `WebsiteAgent`. Each returns hardcoded string data. None contact any external system. They exist in the agent registry and are presumably being called in production, returning fabricated data to clients.

## Problem Statement

Seven agents claiming to query real external data sources — LinkedIn profiles, SEC EDGAR filings, patent databases, news APIs, job postings, technology trend aggregators, and company websites — return static hardcoded strings. They are not placeholders with `raise NotImplementedError`. They return data that looks real but is not.

If these agents are wired into the research pipeline via the agent coordinator, they are injecting fabricated competitive intelligence into client reports. A client asking for SEC filing analysis receives hardcoded text, not actual EDGAR data. A client asking for patent landscape analysis receives a static string, not patent search results.

This is a product integrity issue, not just a code quality issue.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Product Integrity** | Clients may receive fabricated competitive intelligence presented as real external data |
| **Data Quality** | Fake data mixed with real data contaminates all downstream analysis and scoring |
| **Trust** | If clients discover fabricated data in reports, the platform's credibility is destroyed |
| **Legal** | Presenting fabricated data as real research may have contractual or regulatory implications |
| **Agent Registry** | The registry cannot distinguish real agents from stubs |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/agents/additional_agents.py` | Modify/Delete | Lines 45–268: 7 stub agent classes returning hardcoded data |
| `src/solstein/agents/coordinator_agent.py` | Modify | Audit which agents are registered and callable in production |
| Research pipeline entry points | Evaluate | Determine if stub agents are invoked in production workflows |
| Agent registry configuration | Modify | Must reflect only agents that contact real external systems |

## Architectural Requirements

- **REQ-1**: Each of the 7 stub agents must be individually evaluated: implement with real external API integration, or remove from the codebase and agent registry entirely
- **REQ-2**: No agent in the production registry may return hardcoded data strings — ever
- **REQ-3**: If an agent is designated as a planned future implementation, it must be explicitly excluded from the production agent registry with clear documentation stating it is not yet implemented
- **REQ-4**: The agent registry must reflect only agents that contact real external systems and return real data

## Acceptance Criteria

- [ ] Zero agents in the production agent registry return hardcoded data
- [ ] Agents excluded as future work are documented in an ADR and excluded from the registry
- [ ] The audit produces a definitive list: for each of the 7 stub agents, whether it was implemented, removed, or deferred — with rationale
- [ ] The agent coordinator does not invoke any agent that returns fabricated data

## Definition of Done

**Tests Required:**
- [ ] Integration test for each retained agent confirming it attempts a real external API call (external call mocked in test, but the agent must construct and attempt the call)
- [ ] Registry test confirming only real agents are registered in production mode

**Documentation Required:**
- [ ] ADR documenting the fate of each stub agent: implemented (with which API), removed (with rationale), or deferred (with timeline and registry exclusion confirmation)

**Code Review Gate:**
- [ ] Reviewer confirms no hardcoded data strings remain in any registered agent
- [ ] Reviewer confirms the agent registry matches the ADR's documented decisions

## Notes

The immediate priority is determining whether these stubs are actually being called in production. Check `coordinator_agent.py` to see which agents are registered and under what conditions they are invoked. If they are being called, this is a P0 hotfix — fabricated data in client deliverables is not acceptable at any priority level.

For agents that are genuinely planned features (e.g., SEC EDGAR integration), the correct approach is: remove from registry now, implement later, re-register when the implementation passes integration tests. "Coming soon" is not a valid agent state in production.
