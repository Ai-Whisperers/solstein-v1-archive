#!/usr/bin/env python3
"""Detect blocking sync work and async misuse inside async code paths.

This gate is intentionally narrow. It enforces a small set of high-risk rules:

1. Known blocking sync helpers must not be called directly inside ``async def``.
2. Known async detector methods must be awaited (directly or via awaited gather).

The purpose is to prevent the specific bug class that repeatedly broke refresh
connectors, unified adapters, and research helpers.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_PATHS = [Path("src/solstein")]

FORBIDDEN_SYNC_CALLS: dict[str, str] = {
    "search_company_patents": "Run patent search behind asyncio.to_thread(...) in async code.",
    "search_company_info": "Run web search behind asyncio.to_thread(...) in async code.",
    "search_company_news": "Run web search behind asyncio.to_thread(...) in async code.",
    "DDGS": "DuckDuckGo search is synchronous; call it behind asyncio.to_thread(...).",
}

FORBIDDEN_SYNC_ATTRS: set[tuple[str, str]] = {
    ("requests", "get"),
}

ASYNC_METHODS_REQUIRING_AWAIT: dict[str, str] = {
    "detect_funding_signal": "Async detector method must be awaited.",
    "detect_partnership_signal": "Async detector method must be awaited.",
    "detect_key_hire_signal": "Async detector method must be awaited.",
}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    function: str
    rule: str
    code: str
    detail: str


def _call_name(node: ast.Call) -> tuple[str | None, tuple[str, str] | None]:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id, None
    if isinstance(func, ast.Attribute):
        if isinstance(func.value, ast.Name):
            return func.attr, (func.value.id, func.attr)
        return func.attr, None
    return None, None


def _is_guarded_by_await(ancestors: list[ast.AST]) -> bool:
    return any(isinstance(node, ast.Await) for node in ancestors)


def scan_file(path: Path) -> list[Finding]:
    try:
        text = path.read_text()
        tree = ast.parse(text, filename=str(path))
    except Exception:
        return []

    findings: list[Finding] = []
    parents: dict[ast.AST, ast.AST] = {}

    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent

    def ancestors(node: ast.AST) -> list[ast.AST]:
        chain: list[ast.AST] = []
        current = parents.get(node)
        while current is not None:
            chain.append(current)
            current = parents.get(current)
        return chain

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.async_stack: list[ast.AsyncFunctionDef] = []

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self.async_stack.append(node)
            self.generic_visit(node)
            self.async_stack.pop()

        def visit_Call(self, node: ast.Call) -> None:
            if not self.async_stack:
                self.generic_visit(node)
                return

            function_name = self.async_stack[-1].name
            code = (ast.get_source_segment(text, node) or "").strip()
            name, attr_name = _call_name(node)
            node_ancestors = ancestors(node)

            if attr_name in FORBIDDEN_SYNC_ATTRS:
                findings.append(
                    Finding(
                        path=str(path),
                        line=node.lineno,
                        function=function_name,
                        rule=f"{attr_name[0]}.{attr_name[1]}",
                        code=code,
                        detail="requests.get(...) is synchronous; do not call it directly in async code.",
                    )
                )
            elif name in FORBIDDEN_SYNC_CALLS:
                findings.append(
                    Finding(
                        path=str(path),
                        line=node.lineno,
                        function=function_name,
                        rule=name,
                        code=code,
                        detail=FORBIDDEN_SYNC_CALLS[name],
                    )
                )
            elif name in ASYNC_METHODS_REQUIRING_AWAIT and not _is_guarded_by_await(node_ancestors):
                findings.append(
                    Finding(
                        path=str(path),
                        line=node.lineno,
                        function=function_name,
                        rule=name,
                        code=code,
                        detail=ASYNC_METHODS_REQUIRING_AWAIT[name],
                    )
                )

            self.generic_visit(node)

    Visitor().visit(tree)
    return findings


def scan_paths(paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for base in paths:
        if base.is_file() and base.suffix == ".py":
            findings.extend(scan_file(base))
            continue
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            findings.extend(scan_file(path))
    return findings


def main(argv: list[str]) -> int:
    paths = [Path(arg) for arg in argv] if argv else DEFAULT_PATHS
    findings = scan_paths(paths)

    if not findings:
        print("async-boundary check passed")
        return 0

    print("async-boundary violations found:")
    for finding in findings:
        print(f"{finding.path}:{finding.line} [{finding.function}] {finding.rule}: {finding.detail} :: {finding.code}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
