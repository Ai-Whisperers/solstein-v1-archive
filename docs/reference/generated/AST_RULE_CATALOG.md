# AST Rule Catalog and Structural Guardrail Registry

Generated on `2026-04-05` from `tooling/ast-grep/rules`.

This catalog covers all structural guardrails enforced in this repository — both `ast-grep` YAML rules and non-ast-grep CI script gates.

See also: [Engineering Guardrails Guide](../../standards/guardrails.md)

---

## ast-grep Rules

Pattern-based structural checks enforced at PR time via `npm run ast-grep`.

| Rule ID | Severity | Blocking | Related Issues | Rule File | Tests | Rationale |
|---|---|---|---|---|---|---|
| no-batch-enrichment-fallback-company | error | yes | ISSUE-11 | `tooling/ast-grep/rules/no-batch-enrichment-fallback-company.yml` | tooling/ast-grep/rule-tests/no-batch-enrichment-fallback-company-test.yml | docs/audit/ISSUE_11_BATCH_ENRICHMENT_OUTCOME_AUDIT_2026-03-26.md |
| no-silent-score-fallback | error | yes | ISSUE-04 | `tooling/ast-grep/rules/no-silent-score-fallback.yml` | tooling/ast-grep/rule-tests/no-silent-score-fallback-test.yml | docs/audit/SCORING_FAILURE_MODE_AUDIT_2026-03-26.md |

---

## CI Script Gates

Non-ast-grep structural checks enforced by Python scripts in `scripts/ci/` or `scripts/docs/`.

| Gate ID | Severity | Blocking | Related Issues | Script | Rationale |
|---|---|---|---|---|---|
| class-size-limit | warning | no | - | `scripts/ci/check_class_sizes.py` | .claude/rules/code-quality.md |
| code-smell-detection | warning | no | - | `scripts/ci/code_smell_detector.py` | .claude/rules/error-handling.md |
| dead-code-detection | warning | no | EPIC-037 | `scripts/ci/detect_dead_code.py` | - |
| file-size-limit | warning | no | - | `scripts/ci/check_file_sizes.py` | .claude/rules/code-quality.md |
| function-size-limit | warning | no | - | `scripts/ci/check_function_sizes.py` | .claude/rules/code-quality.md |
| generated-docs-freshness | error | yes | STORY-244 | `scripts/docs/check_generated_docs.py` | docs/governance/docs-topology.md |
| no-import-cycles | error | yes | EPIC-066 | `scripts/ci/detect_import_cycles.py` | - |
| no-requests-in-adapters | error | yes | STORY-136 | `scripts/ci/check_banned_imports.py` | docs/developers/async-http-guidelines.md |
