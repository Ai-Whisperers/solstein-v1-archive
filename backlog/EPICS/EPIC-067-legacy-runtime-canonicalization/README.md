# EPIC-067: Legacy Runtime Canonicalization

> **Priority**: P0 - Ship Blocker
> **Stories**: 5 (STORY-255 through STORY-258, STORY-271)
> **Effort**: L (2-3 weeks)
> **Dependencies**: EPIC-058 (Data Conversion Pipeline Consolidation), EPIC-066 (Architectural Boundaries and Cycle Elimination)
> **Status**: 🔴 Not Started

---

## Problem

Solstein currently carries two competing research runtimes, but only one of them is materially closer to working:

- `src/solstein/research/pipeline.py` executes a real staged flow: discovery, gather, source gates, contradiction/readiness gates, scoring, analysis, and export.
- `src/solstein/research/graph/topology.py` still leaves core graph behavior unimplemented by returning empty `resolved_facts`, `confidence_scores`, and `company_scores`.
- `src/solstein/research/pipeline_async.py` preserves a backward-compatible alias (`run_market_intelligence = run_market_intelligence_async`) that obscures which path is canonical.
- `src/solstein/adapters/registry.py` still splits behavior with `feature_new_unified_loader`, keeping two enrichment shapes alive.

This is exactly the condition that keeps producing compatibility patches instead of reliable behavior.

---

## Scope

| Category | Action |
|---|---|
| Runtime Reality Ledger | Publish a wired/unwired/orphan inventory and dual-system LOC/file duplication ledger before more migration work |
| Runtime Choice | Make the legacy pipeline the sole canonical execution path until parity is proven elsewhere |
| Alias Removal | Delete runtime aliases and branching flags that keep two orchestration paths alive |
| Graph Freeze | Explicitly mark incomplete graph surfaces as non-production and remove misleading entrypoints |
| Decision Gate | Define the empirical criteria that would force a legacy rebuild instead of continued salvage |

---

## Stories

| Story | Title | Priority | Size | Status |
|---|---|---|---|---|
| [STORY-271](STORIES/STORY-271-publish-runtime-depth-and-duplication-ledger.md) | Publish runtime depth, wiring, and duplication ledger | P0 | M | 🔴 Open |
| [STORY-255](STORIES/STORY-255-freeze-graph-runtime-and-declare-legacy-canonical.md) | Freeze graph runtime and declare legacy pipeline canonical | P0 | S | 🔴 Open |
| [STORY-256](STORIES/STORY-256-delete-runtime-aliases-and-feature-branching.md) | Delete runtime aliases and feature-flag branching around orchestration | P0 | M | 🔴 Open |
| [STORY-257](STORIES/STORY-257-repair-legacy-entrypoints-to-share-one-registry-and-one-converter.md) | Repair legacy entrypoints to share one registry and one converter | P0 | M | 🔴 Open |
| [STORY-258](STORIES/STORY-258-define-salvage-vs-rebuild-trigger-for-legacy-runtime.md) | Define salvage-vs-rebuild trigger for the legacy runtime | P1 | M | 🔴 Open |

---

## Architectural Requirements

- **REQ-1**: One and only one research runtime may be presented as production-capable.
- **REQ-2**: Compatibility aliases must not conceal which code path is authoritative.
- **REQ-3**: If two runtimes remain temporarily, their coexistence must be justified by a measured LOC/file duplication ledger and deletion plan.
- **REQ-4**: Graph/runtime replacement work must be blocked until parity is proven against the canonical legacy path.
- **REQ-5**: The rebuild trigger must be based on measured defect classes, not intuition.

---

## Success Criteria

- Every CLI/API research entrypoint resolves to one canonical pipeline path.
- A runtime-depth ledger exists showing wired, unwired, placeholder, and orphan surfaces.
- Incomplete graph nodes are no longer reachable as implied production behavior.
- Registry and conversion ownership are singular and explicit.
- A documented save-vs-rebuild scorecard exists for the legacy path and is tied to machine-checkable evidence.
