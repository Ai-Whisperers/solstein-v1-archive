# STORY-058: Write Comprehensive Developer Onboarding Documentation

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-017: Developer Experience](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-057: Automate Local Dev Setup](STORY-057-automate-local-dev-setup.md), [STORY-039: Document Scoring Business Rationale](../../EPIC-011-business-rules-documentation/STORIES/STORY-039-document-scoring-business-rationale.md) |

---

## The Audit Verdict
> The existing AGENTS.md provides a structural overview but does not constitute onboarding documentation. A new engineer cannot learn how a research job flows through the system, why the codebase is structured as it is, or where to make changes for common tasks, from reading the current documentation.

## Problem Statement
Absent onboarding documentation forces knowledge transfer via synchronous conversation with existing engineers. This is a scaling constraint and a bus factor risk. When the engineer who understands the enrichment pipeline is unavailable, no one can modify it. When a new hire joins, they absorb days of another engineer's time learning things that should be written down.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Onboarding** | New engineer time-to-productivity is high and variable — depends entirely on the availability of knowledgeable teammates |
| **Knowledge** | Tribal knowledge about system behaviour is not preserved — it exists only in the heads of current engineers |
| **Bus Factor** | Knowledge concentrated in the few engineers who built the system — their departure would be catastrophic |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `docs/architecture.md` | Add | System architecture, data flow, module purposes |
| `docs/contributing.md` | Add | How to add data sources, scoring components, endpoints |
| `docs/troubleshooting.md` | Add | Common failures and their solutions |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: A `docs/architecture.md` must describe the system architecture with a diagram, the data flow for a research job, and the purpose of each major module
- **REQ-2**: A `docs/contributing.md` must describe: how to add a new data source, how to add a new scoring component, how to add a new endpoint, and the code review process
- **REQ-3**: A `docs/troubleshooting.md` must document the most common local setup and runtime failures with their solutions
- **REQ-4**: All documentation must be accurate as of the time of writing — inaccurate documentation is worse than no documentation
- **REQ-5**: A new engineer must be able to make a successful API call within 30 minutes using only the documentation

## Acceptance Criteria
- [ ] `docs/architecture.md` exists with a system diagram and request flow walkthrough
- [ ] `docs/contributing.md` exists with step-by-step guides for common extension tasks
- [ ] `docs/troubleshooting.md` exists with solutions for at least 5 common issues
- [ ] A new engineer (or peer unfamiliar with the codebase) can follow the docs to make a successful API call in under 30 minutes

## Definition of Done

**Tests Required:**
- [ ] Peer review of all documentation by someone unfamiliar with the codebase — they must follow the docs and report any step where they got stuck

**Documentation Required:**
- [ ] All linked resources verified to exist and return correct content
- [ ] All code examples verified to work

**Code Review Gate:**
- [ ] Reviewer confirms architecture diagram matches the actual codebase structure
- [ ] Reviewer confirms contributing guide references actual file paths and patterns

## Notes
This story depends on STORY-057 (automated setup) because the onboarding docs must reference `make setup` as the starting point. It also depends on STORY-039 (scoring business rationale) because the architecture doc should reference the scoring methodology document rather than re-explaining it. Documentation should be written by someone who understands the system and reviewed by someone who does not — the reviewer's confusion is the most valuable feedback. Resist the temptation to write aspirational documentation about how the system should work — document how it actually works today.
