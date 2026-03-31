# EPIC-068: Boundary Schemas and Type Gates

> **Priority**: P0 - Ship Blocker
> **Stories**: 4 (STORY-259 through STORY-262)
> **Effort**: L (2-3 weeks)
> **Dependencies**: EPIC-067 (Legacy Runtime Canonicalization), EPIC-052 (Provenance, Confidence, and Quality Gates)
> **Status**: 🔴 Not Started

---

## Problem

The codebase still allows loose dictionaries, alias transforms, and weak type gates to cross critical boundaries:

- `pyproject.toml` keeps `mypy` non-strict and limits typed enforcement to a small subset of files.
- `src/solstein/domain/payload_compat.py` rewrites payloads dynamically to preserve backward compatibility.
- `src/solstein/data/converters/company.py` still injects confidence aliases.
- Many connectors and graph nodes use `dict[str, Any]` envelopes instead of strict boundary models.

The result is that the system can appear to work while silently accepting malformed or legacy-shaped data.

Current baseline artifact:
- [`docs/audit/RUNTIME_DEPTH_AND_DUPLICATION_LEDGER_2026-03-31.md`](../../../docs/audit/RUNTIME_DEPTH_AND_DUPLICATION_LEDGER_2026-03-31.md) identifies the currently retained runtime seams, placeholder control-plane paths, and alias-heavy boundaries this epic must harden.

---

## Scope

| Category | Action |
|---|---|
| Canonical DTOs | Define strict Pydantic boundary models for research runs, provider envelopes, and company payloads |
| Type Gates | Expand strict type-checking in the highest-risk modules and make failure blocking |
| Alias Elimination | Remove compatibility transforms from write boundaries and replace them with explicit migration failures |
| Zod Alignment | Generate JSON Schema/Zod artifacts from canonical Python schemas for future TS surfaces instead of hand-written drift |

---

## Stories

| Story | Title | Priority | Size | Status |
|---|---|---|---|---|
| [STORY-259](STORIES/STORY-259-define-canonical-boundary-models-for-runs-providers-and-company-payloads.md) | Define canonical boundary models for runs, providers, and company payloads | P0 | M | 🔴 Open |
| [STORY-260](STORIES/STORY-260-make-type-checking-strict-for-high-risk-modules.md) | Make type checking strict for high-risk modules | P0 | M | 🔴 Open |
| [STORY-261](STORIES/STORY-261-remove-write-boundary-compatibility-transforms.md) | Remove write-boundary compatibility transforms | P0 | M | 🔴 Open |
| [STORY-262](STORIES/STORY-262-generate-json-schema-and-zod-from-canonical-python-contracts.md) | Generate JSON Schema and Zod from canonical Python contracts | P1 | M | 🔴 Open |

---

## Architectural Requirements

- **REQ-1**: No unvalidated `dict[str, Any]` payload may cross orchestration, provider, export, or worker boundaries.
- **REQ-2**: Canonical schemas must have one owner and one versioned artifact.
- **REQ-3**: Compatibility aliasing at write boundaries must be removed; migrations must be explicit.
- **REQ-4**: Any future TypeScript control plane must consume generated contracts, not parallel hand-maintained schemas.

---

## Success Criteria

- Canonical Pydantic models exist for every high-risk boundary.
- Strict type gates cover the canonical runtime path.
- Legacy alias writes are rejected or migrated explicitly with audit evidence.
- JSON Schema/Zod artifacts are generated from the canonical contract set.
