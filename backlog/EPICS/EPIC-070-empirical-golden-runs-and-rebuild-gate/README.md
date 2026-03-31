# EPIC-070: Empirical Golden Runs and Rebuild Gate

> **Priority**: P0 - Ship Blocker
> **Stories**: 4 (STORY-267 through STORY-270)
> **Effort**: L (2-3 weeks)
> **Dependencies**: EPIC-067 (Legacy Runtime Canonicalization), EPIC-068 (Boundary Schemas and Type Gates), EPIC-069 (Provider Surface Rationalization)
> **Status**: 🔴 Not Started

---

## Problem

The project still lacks executable proof that the canonical runtime works reliably enough to trust. There are quality gates and audits, but not yet a small set of representative, repeatable golden runs that prove:

- provider contracts behave as expected,
- a full market run stays deterministic enough to inspect,
- silent failures and placeholder outputs are blocked,
- and the team knows when to stop salvaging the legacy path and rebuild.

Without this epic, the repo can continue producing convincing artifacts without trustworthy evidence.

Current baseline artifact:
- [`docs/audit/RUNTIME_DEPTH_AND_DUPLICATION_LEDGER_2026-03-31.md`](../../../docs/audit/RUNTIME_DEPTH_AND_DUPLICATION_LEDGER_2026-03-31.md) defines the current placeholder, mock, disabled, and duplicate surfaces that golden runs must reject or retire.

---

## Scope

| Category | Action |
|---|---|
| Provider Proof | Add representative provider-level contract runs |
| End-to-End Proof | Add full-market golden run with artifact diffing |
| Silent-Failure Detection | Block empty, placeholder, mock, and partial-success illusions |
| Rebuild Gate | Make the save-vs-rebuild decision from measured evidence |

---

## Stories

| Story | Title | Priority | Size | Status |
|---|---|---|---|---|
| [STORY-267](STORIES/STORY-267-add-provider-level-golden-contract-runs.md) | Add provider-level golden contract runs | P0 | M | 🔴 Open |
| [STORY-268](STORIES/STORY-268-add-full-market-golden-run-with-artifact-diffing.md) | Add full-market golden run with artifact diffing | P0 | M | 🔴 Open |
| [STORY-269](STORIES/STORY-269-block-empty-placeholder-and-mock-success-paths.md) | Block empty, placeholder, and mock success paths | P0 | M | 🔴 Open |
| [STORY-270](STORIES/STORY-270-make-save-vs-rebuild-decision-from-golden-run-evidence.md) | Make save-vs-rebuild decision from golden-run evidence | P0 | M | 🔴 Open |

---

## Architectural Requirements

- **REQ-1**: Golden runs must execute against the canonical legacy runtime only.
- **REQ-2**: Provider and market-run outputs must be diffable and attributable to exact artifacts.
- **REQ-3**: Empty or placeholder success states must fail the gate.
- **REQ-4**: Rebuild decisions must cite measured failure classes, not informal impressions.

---

## Success Criteria

- At least two representative provider contract runs are executable and stable enough for regression use.
- One full-market golden run exists with artifact diffing and silent-failure checks.
- Placeholder/mock success states are blocked in CI or release verification.
- A documented decision is made to continue legacy salvage or begin controlled rebuild work.
