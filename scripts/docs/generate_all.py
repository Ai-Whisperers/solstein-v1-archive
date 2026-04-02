#!/usr/bin/env python3
"""Generate all committed derived docs artifacts."""

from __future__ import annotations

from generate_ast_rule_catalog import main as generate_ast_rule_catalog
from generate_docs_health import main as generate_docs_health
from generate_master_audit_issue_index import main as generate_master_audit_issue_index


def main() -> None:
    generate_ast_rule_catalog()
    generate_master_audit_issue_index()
    # Health dashboard is generated last so it can consume the freshly updated indexes
    generate_docs_health(["--skip-freshness"])


if __name__ == "__main__":
    main()
