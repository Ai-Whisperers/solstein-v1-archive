# TypeScript Critical Nodes Plan

Date: `2026-03-26`

## Why Start Here

There is no real TypeScript workspace in the repo today.

The only `package.json` currently found at the repo root depth is:

- `.opencode/package.json`

That means a broad TypeScript migration would be premature unless it starts from a narrow, high-value boundary.

The right first move is a strict contracts layer for the payloads that are most likely to drift:

- external integration outputs
- search and heuristic evidence
- exported JSON payloads used outside Python

## First Critical Targets

### 1. External Search Result Contracts

Reason:

- the repo currently mixes Exa, SearXNG, DuckDuckGo, and an unpinned `google_search` package
- fallback provenance can be lost or mislabeled

Desired TS layer:

- strict normalized search result schema
- explicit backend enum
- evidence class enum

### 2. LinkedIn Heuristic Contracts

Reason:

- the repo uses LinkedIn-themed heuristic signals, not a real authoritative LinkedIn contract
- the most dangerous failure is semantic drift, not syntax failure

Desired TS layer:

- explicit heuristic source schema
- explicit authority and method tagging
- fact envelope that cannot masquerade as official LinkedIn data

### 3. External Evidence Envelope

Reason:

- many boundaries still pass around loose dicts
- Python models exist, but the weak spots are cross-boundary handoffs and downstream consumers

Desired TS layer:

- normalized evidence envelope
- typed metadata
- schema-safe serialization for exports and UI consumers

## Implementation Strategy

Phase 1:

- create isolated TS contracts package
- define `zod` schemas for the highest-risk external boundaries
- keep it independent from the Python runtime

Phase 2:

- generate golden JSON fixtures from Python
- validate those fixtures in TS as a second contract gate

Phase 3:

- use the same TS schemas in future frontend or admin tooling
- use the same TS schemas in contract linting and regression tooling

## Non-Goals For The First Step

- rewriting the backend into Node or TypeScript
- duplicating all Pydantic models in one shot
- introducing a large frontend stack before contracts are stable

## Immediate Deliverable In This Repo

The first implementation starts in:

- [tooling/contracts-ts/README.md](../../tooling/contracts-ts/README.md)

This package is intentionally narrow and focused on external contract validation.

## Issue-Oriented Follow-Up

The next planning layer now exists in:

- [TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md](./TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md)

That document maps specific audit issues to:

- Python-only fixes
- TS-beneficial boundaries
- combined Python + TS implementation opportunities

The first combined target is `ISSUE-11`, where TypeScript should validate the serialized batch enrichment outcome contract, not replace the Python enrichment loop itself.
