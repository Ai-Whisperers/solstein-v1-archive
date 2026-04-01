# Develop Backlog Autonomy Audit — 2026-03-30

| Field | Value |
|---|---|
| Branch | `develop` |
| Purpose | Preserve strict lint/schema/anti-slop working rules for unfinished backlog work |
| Primary Authority | `planning/QUEUE.md` |
| Secondary Authority | This audit |
| Historical Inputs | `backlog/README.md`, `backlog/EPIC_RECONCILIATION.md` |

## Why This Audit Exists

The backlog tree contains two different truths:

1. `planning/QUEUE.md` reflects the active develop-branch execution order for unfinished work.
2. Large parts of `backlog/` still show stale `Open` badges even when the work is already complete in `develop`.

Future coworker agents must not start work from stale `Open` badges alone. They should use the queue first, this audit second, and only then the canonical epic/story files.

## Consult Order For Future Agents

1. Read `planning/QUEUE.md`.
2. Read this audit.
3. Read the canonical epic README and canonical story file.
4. Read the referenced guardrail docs before implementation.

## Strict Working Rules

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`.
- Follow `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`.
- Follow `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md` for anti-slop rules.
- Follow `docs/reference/SCHEMA_INVENTORY_AND_VALIDATION_NOTES.md` when work touches payload boundaries.
- Prefer machine-checkable enforcement over prose summaries.
- Do not broaden scope beyond the current story unless the dependency is explicit in the queue or story file.

## Develop Reality: Type, Schema, and Validation Improvements Already Present

These are not aspirational backlog items anymore. Future agents should treat them as current develop-branch reality when planning follow-up work:

| Improvement | Current Evidence | Why It Matters |
|---|---|---|
| Strict Python type enforcement ratchet exists | `docs/reference/ENGINEERING_GUARDRAILS.md`, `pyproject.toml`, `docs/sessions/DEV_LOG_2026-03.md` | `basedpyright` is now a checked-in guardrail, so new high-risk work should ratchet against a frozen baseline instead of reintroducing loose typing |
| Boundary-specific Pydantic strictness is already being adopted | `src/solstein/api/schemas/enrichment.py`, `src/solstein/data/unified/batch_outcomes.py`, `tests/unit/test_issue11_batch_enrichment_outcomes.py` | The batch enrichment path now has typed outcome models and explicit validation expectations; future schema work should extend this pattern, not replace it with mocks or loose dict contracts |
| Export contract enforcement is already a real backlog line | `planning/QUEUE.md`, `backlog/EPICS/EPIC-033-data-completeness-export-integrity/README.md`, `STORY-126`, `STORY-128` | Export schema validation and field-lineage enforcement are already part of the develop backlog reality and should be reused as contract patterns |
| Validation-before-scoring exists as a real epic/story direction | `backlog/EPICS/EPIC-059-input-validation-graceful-degradation/README.md`, `STORY-206`..`STORY-210`, `tests/unit/test_story209_validation_before_scoring.py` | Future quality-gate work should plug into these validation surfaces instead of inventing a second parallel validation layer |
| Typed state and contract stories already exist for orchestration/runtime work | `backlog/EPICS/EPIC-054-stateful-graph-orchestration/README.md`, `STORY-206-typed-state-contract.md`, `backlog/EPICS/EPIC-056-tool-contracts-and-sandboxing/STORIES/STORY-214-tool-contract-schema.md` | Runtime/control-plane stories should converge on typed envelopes and schema validators rather than ad-hoc internal payloads |
| Strict generated-doc/schema-registry expansion is already the active docs story | `backlog/EPICS/EPIC-065-documentation-lifecycle-automation-ci-enforcement/README.md`, `STORY-245`, `docs/reference/SCHEMA_INVENTORY_AND_VALIDATION_NOTES.md` | Ivan should extend generated schema ownership and boundary registries from source, not hand-maintain explanatory docs |

## Verified Develop-Branch Unfinished Epics

| Epic | Queue Status | Canonical File | Operational Meaning |
|---|---|---|---|
| EPIC-017 | BLOCKED | `backlog/EPICS/EPIC-017-developer-experience/README.md` | Wait for dependency resolution before continuing setup/onboarding work |
| EPIC-052 | BLOCKED in queue snapshot | `backlog/EPICS/EPIC-052-provenance-confidence-quality-gates/README.md` | Queue blocker was missing story files; this pass adds them, so future agents must re-evaluate queue text before starting |
| EPIC-065 | READY | `backlog/EPICS/EPIC-065-documentation-lifecycle-automation-ci-enforcement/README.md` | Continue only with `STORY-245` |
| EPIC-031 | READY | `backlog/EPICS/EPIC-031-shared-library-architecture/README.md` | Structural refactors are ready one story at a time |
| EPIC-066 | BLOCKED | `backlog/EPICS/EPIC-066-architectural-boundaries-and-cycle-elimination/README.md` | Do not start until `STORY-245` and EPIC-031 prerequisites move |

## Verified Develop-Branch Unfinished Stories

| Story | Queue Status | Canonical File | Notes |
|---|---|---|---|
| STORY-057 | BLOCKED | `backlog/EPICS/EPIC-017-developer-experience/STORIES/STORY-057-automate-local-dev-setup.md` | Blocked on `STORY-059` verification |
| STORY-058 | BLOCKED | `backlog/EPICS/EPIC-017-developer-experience/STORIES/STORY-058-developer-onboarding-docs.md` | Blocked on `STORY-057` and `STORY-039` |
| STORY-198 | Canonicalized in this pass | `backlog/EPICS/EPIC-052-provenance-confidence-quality-gates/STORIES/STORY-198-enforce-provenance-completeness-at-write-boundary.md` | New canonical story file created from epic requirements |
| STORY-199 | Canonicalized in this pass | `backlog/EPICS/EPIC-052-provenance-confidence-quality-gates/STORIES/STORY-199-confidence-calibration-profile-per-source-tier.md` | New canonical story file created from epic requirements |
| STORY-200 | Canonicalized in this pass | `backlog/EPICS/EPIC-052-provenance-confidence-quality-gates/STORIES/STORY-200-quality-gate-before-scoring-and-export.md` | New canonical story file created from epic requirements |
| STORY-201 | Canonicalized in this pass | `backlog/EPICS/EPIC-052-provenance-confidence-quality-gates/STORIES/STORY-201-ci-contract-tests-for-provenance-confidence-and-synthetic-gates.md` | New canonical story file created from epic requirements |
| STORY-245 | READY | `backlog/EPICS/EPIC-065-documentation-lifecycle-automation-ci-enforcement/STORIES/STORY-245-expand-generated-api-docs-and-schema-registries.md` | Source-derived generated docs only |
| STORY-116 | READY | `backlog/EPICS/EPIC-031-shared-library-architecture/STORIES/STORY-116-centralize-retry-policy.md` | Lowest-risk EPIC-031 entry point |
| STORY-117 | READY | `backlog/EPICS/EPIC-031-shared-library-architecture/STORIES/STORY-117-fix-circular-imports-shared-package.md` | Structural boundary refactor |
| STORY-118 | READY | `backlog/EPICS/EPIC-031-shared-library-architecture/STORIES/STORY-118-formalize-cli-entrypoint.md` | Preserve CLI behavior while removing bypass patterns |
| STORY-119 | READY | `backlog/EPICS/EPIC-031-shared-library-architecture/STORIES/STORY-119-split-unified-loader.md` | Decompose without breaking call surface |
| STORY-120 | READY | `backlog/EPICS/EPIC-031-shared-library-architecture/STORIES/STORY-120-utc-timezone-policy.md` | Boundary-first UTC enforcement |
| STORY-246 | BLOCKED | `backlog/EPICS/EPIC-066-architectural-boundaries-and-cycle-elimination/STORIES/STORY-246-break-patents-unified-discovery-registry-cycle.md` | Wait for EPIC-065/031 prerequisites |
| STORY-247 | BLOCKED | `backlog/EPICS/EPIC-066-architectural-boundaries-and-cycle-elimination/STORIES/STORY-247-move-canonicalization-and-hashing-helpers-lower.md` | Wait for EPIC-065/031 prerequisites |
| STORY-248 | BLOCKED | `backlog/EPICS/EPIC-066-architectural-boundaries-and-cycle-elimination/STORIES/STORY-248-decouple-domain-value-objects-from-analytics-constants.md` | Wait for EPIC-065/031 prerequisites |
| STORY-249 | BLOCKED | `backlog/EPICS/EPIC-066-architectural-boundaries-and-cycle-elimination/STORIES/STORY-249-enforce-cycle-and-boundary-checks-in-gates.md` | Gate-promotion work only after defect removal |

## Backlog Components Future Agents Must Treat Carefully

| Component | Current Role | Rule |
|---|---|---|
| `planning/QUEUE.md` | Live execution order | Use for start/stop/go decisions |
| `backlog/README.md` | Registry and historical planning surface | Do not use stale `Open` badges as proof work is unfinished |
| `backlog/EPIC_RECONCILIATION.md` | Historical 2026-03-09 reconciliation | Do not use as current develop execution truth |
| `backlog/GUIDELINES/WORKFLOW.md` | Generic status workflow | Follow only together with the queue and this audit |

## Broader Canonical Backlog Coverage

This pass also appended generic triage-safe `Autonomous Continuation Notes` to the remaining open canonical epic READMEs and open canonical story files that were not part of the active queue slice.

Use those notes as guardrails against stale backlog badges, not as proof the item is ready to start.

## Anti-Slop Enforcement For Backlog Work

- Every future implementation should add at least one durable artifact: regression test, schema gate, AST rule, codemod, or generated reference update.
- Do not write aspirational docs that restate how the system should work.
- Document only the verified current path, current blocker, or current next action.
- When a story is blocked, say so explicitly and stop rather than writing speculative implementation guidance.

## Practical Use

If a future agent is choosing the next task:

1. Pick the first `READY` story in `planning/QUEUE.md`.
2. Read this audit entry for the story/epic.
3. Read the canonical story file.
4. Execute only that story under the referenced guardrail docs.
