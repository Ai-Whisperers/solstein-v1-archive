# Docs Health Dashboard

Generated on `2026-04-03`. Updated automatically on every push to `develop` and weekly on Mondays.

This dashboard aggregates metrics from the repository's documentation CI gates.
See [docs/guides/docs-change-control.md](../../../guides/docs-change-control.md) for the
remediation workflow.

## Summary

| Metric | Status | Detail |
|---|---|---|
| Quality Gate (placeholders + metadata) | **FAIL** | 535 blocking, 0 warnings |
| Stale Docs | **PASS** | 0 actionable stale (344 scanned) |
| Generated Docs Freshness | **N/A** | N/A |
| AST Guardrail Gates | **OK** | 2 ast-grep rules, 8 CI script gates, 5 blocking |
| Open Audit Issues | **OK** | 270 open / 271 total |

## Remediation Links

| Red/Warn Metric | Remediation |
|---|---|
| Quality Gate: blocking violations | Add allowlist entry - `scripts/ci/docs-quality-allowlist.json` |
| Quality Gate: governance metadata | Add blockquote front-matter - see [docs-change-control.md](../../../guides/docs-change-control.md) |
| Stale Docs | Review the doc or add exemption - `scripts/ci/stale-docs-allowlist.json` |
| Generated Docs Freshness | Run `make docs-generate` and commit updated artifacts |
| Open Audit Issues | See [MASTER_AUDIT_ISSUE_INDEX.md](../../../audit/generated/MASTER_AUDIT_ISSUE_INDEX.md) |

## Data Sources

- AST catalog: [AST_RULE_CATALOG.json](AST_RULE_CATALOG.json) (generated 2026-04-03)
- Audit index: [MASTER_AUDIT_ISSUE_INDEX.json](../../../audit/generated/MASTER_AUDIT_ISSUE_INDEX.json) (generated 2026-04-03)
- Quality gate: `scripts/ci/check_docs_quality.py`
- Stale docs: `scripts/ci/check_stale_docs.py`
- Freshness: `scripts/docs/check_generated_docs.py`
