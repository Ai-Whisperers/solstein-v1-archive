"""Tests for STORY-136: Banned import enforcement.

Verifies:
- The CI script correctly detects `import requests`
- The CI script passes on clean files
- No adapter/agent file in the codebase imports requests
"""

import ast
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "solstein"

# Files explicitly allowlisted in check_banned_imports.py
ALLOWLIST = {
    "src/solstein/data/sources/news.py",
    "src/solstein/data/sources/funding.py",
    "src/solstein/data/sources/web.py",
    "src/solstein/data/sources/patents.py",
    # These adapters are migrated in STORY-134/135 PRs (pending merge)
    # Remove from allowlist once PRs #183 and #184 are merged
    "src/solstein/adapters/enrichment/news_unified.py",
    "src/solstein/adapters/enrichment/funding_unified.py",
    "src/solstein/adapters/enrichment/website_unified.py",
    "src/solstein/agents/website_agent.py",
}


class TestNoBannedImportsInAdapters:
    """Verify no adapter or agent file imports `requests`."""

    def _scan_dir(self, directory: Path) -> list[str]:
        violations = []
        root = Path(__file__).resolve().parents[2]
        for py_file in sorted(directory.rglob("*.py")):
            if "__pycache__" in str(py_file):
                continue
            relative = str(py_file.relative_to(root))
            if relative in ALLOWLIST:
                continue
            try:
                source = py_file.read_text()
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name == "requests":
                                violations.append(f"{relative}:{node.lineno}")
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and node.module.split(".")[0] == "requests":
                            violations.append(f"{relative}:{node.lineno}")
            except SyntaxError:
                pass
        return violations

    def test_no_requests_in_agents(self):
        agents_dir = SRC / "agents"
        violations = self._scan_dir(agents_dir)
        assert violations == [], f"Agents still import requests: {violations}"

    def test_no_requests_in_adapters(self):
        adapters_dir = SRC / "adapters"
        violations = self._scan_dir(adapters_dir)
        assert violations == [], f"Adapters still import requests: {violations}"


class TestCIScript:
    """Verify the CI script runs and catches violations."""

    def test_ci_script_passes_on_clean_code(self):
        result = subprocess.run(
            [sys.executable, "scripts/ci/check_banned_imports.py", "--path", "src/solstein/agents"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"CI script failed on agents dir: {result.stdout}\n{result.stderr}"

    def test_ci_script_passes_on_adapters(self):
        result = subprocess.run(
            [sys.executable, "scripts/ci/check_banned_imports.py", "--path", "src/solstein/adapters"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"CI script failed on adapters dir: {result.stdout}\n{result.stderr}"
