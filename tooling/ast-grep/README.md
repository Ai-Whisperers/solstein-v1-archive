# AST Guardrails

Structural, tokenless repository rules enforced with `ast-grep`.

## Purpose

- Block known bug classes from re-entering after targeted fixes.
- Complement `ruff`, `basedpyright`, and runtime regression tests with syntax-tree rules.
- Keep rules narrow and evidence-driven. Do not add vague style rules here.

## Commands

```bash
npm run ast-grep -- --error
npm run ast-grep:test
```

## Current rules

- `no-silent-score-fallback`: prevents `*_score or 0.0` masking in scoring code paths.
- `no-batch-enrichment-fallback-company`: prevents batch enrichment from appending the original company directly on failure.

## Rule discipline

- Every rule must map to a real incident, audit issue, or regression class.
- Every rule must have a corresponding `rule-tests/*.yml` file.
- Prefer adding a new narrow rule when a bug class repeats twice.
