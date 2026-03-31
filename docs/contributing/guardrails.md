# Engineering Guardrails Guide

> **Owner**: Platform Engineering
> **Review Cadence**: Quarterly
> **Class**: Standard (see [Docs Topology](../governance/docs-topology.md))

---

## Purpose

This document describes the structural guardrails enforced in this repository — rules and CI checks
that prevent specific classes of architectural bugs from being merged. Guardrails complement code
review: they block known-bad patterns automatically, without requiring a reviewer to remember them.

---

## Guardrail Registry

The canonical, machine-readable catalog is generated automatically from the repository source:

- **Markdown**: [`docs/reference/generated/AST_RULE_CATALOG.md`](../reference/generated/AST_RULE_CATALOG.md)
- **JSON**: [`docs/reference/generated/AST_RULE_CATALOG.json`](../reference/generated/AST_RULE_CATALOG.json)

The catalog is regenerated on every commit via the `pre-commit` hook and on every CI run.
If the committed catalog is stale, CI fails (see `make docs-generated-check`).

---

## Gate Categories

### ast-grep Rules (Pattern-Level)

Applied by `npm run ast-grep` during CI. Each rule targets a specific code pattern that has caused
production bugs or silent data corruption. See the [rule files](../../tooling/ast-grep/rules/) for
the YAML pattern and the [catalog](../reference/generated/AST_RULE_CATALOG.md) for severity and
blocking status.

**Currently enforced rules:**

| Rule | Bug Class |
|---|---|
| `no-batch-enrichment-fallback-company` | Silent data loss when batch enrichment returns Company objects instead of structured outcomes |
| `no-silent-score-fallback` | Scores silently degrade to 0.0 when a sub-scorer throws — hiding scorer failures |

### CI Script Gates (Policy-Level)

Enforced by Python scripts in `scripts/ci/` and `scripts/docs/`. These cover patterns that are
difficult or verbose to express as single-node AST patterns.

**Blocking gates (fail CI):**

| Gate | Policy |
|---|---|
| `no-requests-in-adapters` | All HTTP must use `httpx`; `requests` is banned in adapter/agent code |
| `no-import-cycles` | Zero static import cycles allowed in `src/solstein` |
| `generated-docs-freshness` | Committed generated docs must match fresh regeneration |

**Advisory gates (warn, do not fail):**

| Gate | Policy |
|---|---|
| `file-size-limit` | Files over 500 lines are architecture debt |
| `function-size-limit` | Functions over 100 lines must be split |
| `class-size-limit` | Classes over 300 lines must be extracted |
| `code-smell-detection` | Bare-except and broad-exception patterns |
| `dead-code-detection` | Modules with zero instantiation sites |

---

## Running Guardrails Locally

```bash
# Full engineering gate (blocking only)
make gate-engineering

# ast-grep rules only
npm run ast-grep --error

# Banned import check
python scripts/ci/check_banned_imports.py

# Import cycle detection
python scripts/ci/detect_import_cycles.py src/solstein

# Generated docs freshness
make docs-generated-check
```

---

## Adding a New Guardrail

### For ast-grep rules

1. Create a new YAML rule in `tooling/ast-grep/rules/<rule-id>.yml`.
2. Add a test fixture in `tooling/ast-grep/rule-tests/<rule-id>-test.yml`.
3. Add comment metadata to the YAML (`# related-issues:`, `# rationale-doc:`).
4. Run `make docs-generate` — the catalog updates automatically.

### For CI script gates

1. Create the script in `scripts/ci/` or `scripts/docs/`.
2. Add an entry to the `SCRIPT_GATES` list in `scripts/docs/generate_ast_rule_catalog.py`.
3. Wire the script into the appropriate CI workflow.
4. Run `make docs-generate` — the catalog updates automatically.

---

## Guardrail Policy

- **Blocking gates** (`severity: error`) fail CI and must not be bypassed without a tracked exception.
- **Advisory gates** (`severity: warning`) produce informational output; violations do not block merges
  but should be addressed as part of ongoing code quality work.
- Every blocking gate must have a `rationale_doc` reference in the catalog.
- Exceptions to blocking gates require `owner`, `rationale`, and `expiry` metadata in an allowlist
  file co-located with the gate script (see individual scripts for allowlist format).
