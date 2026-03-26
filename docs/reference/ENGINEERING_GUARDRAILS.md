# Engineering Guardrails

Solstein uses layered, mostly tokenless guardrails to keep regressions out of commercially critical pipeline paths.

## Tooling stack

- `ruff`: fast syntax, import, and correctness linting.
- `mypy`: targeted incremental Python type coverage on critical packages.
- `basedpyright`: repository-wide strict type analysis with a checked-in baseline so existing debt is frozen and new type regressions fail.
- `ast-grep`: AST rules for recurring bug classes that normal linters do not express well.
- `LibCST`: safe codemods for repetitive, semantics-preserving Python migrations.
- `mkdocstrings` + `Griffe`: reference docs generated from source signatures and docstrings instead of manually duplicated prose.

## Enforcement model

1. Fix the runtime bug.
2. Add a regression test.
3. Add a schema or type boundary if the bug crossed a contract edge.
4. Add an AST rule when the failure mode is structural and likely to recur.
5. Document the rule, rationale, and verification in the audit/dev log.

## Strictness policy

- `basedpyright` runs in strict mode with a baseline file committed in the repo.
- New type problems fail the gate; existing debt stays visible in the baseline until deliberately removed.
- `ast-grep` rules must be narrow, evidence-driven, and tested.
- Generated reference docs should come from AST/source introspection wherever possible.
- The strict docs build currently targets a maintained subset with `mkdocs.strict.yml`; the legacy docs tree still has independent link debt and is not yet safe to treat as a blocking gate.

## Current commands

```bash
make type-strict
make lint-ast
make ast-test
make docs-strict
make gate-engineering
```

## Current structural guards

- Async boundary guard in `scripts/ci/check_async_boundaries.py`
- Connector fact envelope validation in `solstein.infrastructure.fact_payloads`
- AST score-fallback guard in `tooling/ast-grep/rules/no-silent-score-fallback.yml`
- AST-generated reference docs for `worker` and `infrastructure` package boundaries
