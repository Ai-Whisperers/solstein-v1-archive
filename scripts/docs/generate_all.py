#!/usr/bin/env python3
"""Generate all committed derived docs artifacts."""

from __future__ import annotations

from generate_ast_rule_catalog import main as generate_ast_rule_catalog
from generate_master_audit_issue_index import main as generate_master_audit_issue_index


def main() -> None:
    generate_ast_rule_catalog()
    generate_master_audit_issue_index()


if __name__ == "__main__":
    main()
