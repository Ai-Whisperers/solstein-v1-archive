# Engineering Guardrails

This document describes the automated quality gates enforced in this repository.

## Overview

Code quality is enforced at two levels:

1. **Static analysis** via ast-grep rules (see [AST_RULE_CATALOG.md](../reference/generated/AST_RULE_CATALOG.md))
2. **CI script gates** via `scripts/ci/` tooling

## AST Rule Catalog

The full catalog of ast-grep rules and CI script gates is auto-generated and available at:

- [`docs/reference/generated/AST_RULE_CATALOG.md`](../reference/generated/AST_RULE_CATALOG.md) — human-readable
- [`docs/reference/generated/AST_RULE_CATALOG.json`](../reference/generated/AST_RULE_CATALOG.json) — machine-readable

Regenerate with:

```bash
python scripts/docs/generate_ast_rule_catalog.py
```

## Quality Gates Summary

| Gate | Tool | Blocking |
|------|------|----------|
| Lint | ruff check | Yes |
| Format | ruff format | Yes |
| Type check | mypy (advisory) | No (EPIC-012) |
| Unit tests | pytest | Yes |
| Coverage | pytest-cov (≥25%) | Yes |
| Field lineage | check_field_lineage.py | CI only |
