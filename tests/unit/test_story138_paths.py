"""STORY-138: Tests verifying config-driven path resolution and the CI hardcoded-path guard.

DoD requirements:
- _PROJECT_ROOT resolves correctly even when invoked from a different working directory.
- CI check script returns non-zero when hardcoded /home/ paths exist in src/bin/scripts.
- CI check script returns 0 when those directories are clean.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CI_SCRIPT = ROOT / "scripts" / "ci" / "check_hardcoded_paths.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_ci_module():
    """Dynamically load check_hardcoded_paths without executing main()."""
    spec = importlib.util.spec_from_file_location("check_hardcoded_paths", CI_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Tests: CI guard (check_hardcoded_paths.py)
# ---------------------------------------------------------------------------

def test_ci_guard_passes_on_clean_tree(tmp_path: Path) -> None:
    """scan() returns empty list when no /home/ paths are present."""
    module = _load_ci_module()

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "clean_module.py").write_text(
        "from pathlib import Path\n\nROOT = Path(__file__).resolve().parent\n"
    )

    violations = module.scan(tmp_path, scope_dirs=["src"])
    assert violations == [], f"Expected no violations, got: {violations}"


def test_ci_guard_detects_hardcoded_home_path(tmp_path: Path) -> None:
    """scan() returns a violation when a file in scope has a hardcoded /home/ path."""
    module = _load_ci_module()

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "bad_module.py").write_text(
        'PROJECT_ROOT = "/home/ai-whisperers/solstein"\n'
    )

    violations = module.scan(tmp_path, scope_dirs=["src"])
    assert len(violations) == 1
    file_path, lineno, content = violations[0]
    assert "bad_module.py" in str(file_path)
    assert lineno == 1
    assert "/home/ai-whisperers/solstein" in content


def test_ci_guard_ignores_template_files(tmp_path: Path) -> None:
    """*.template files are exempt from the check."""
    module = _load_ci_module()

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "agent.service.template").write_text(
        "WorkingDirectory=/home/someuser/project\n"
    )

    violations = module.scan(tmp_path, scope_dirs=["bin"])
    assert violations == [], "Template files should be exempt"


def test_ci_guard_ignores_out_of_scope_dirs(tmp_path: Path) -> None:
    """Files outside src/bin/scripts are not scanned."""
    module = _load_ci_module()

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "history.md").write_text(
        "Previously we used /home/ai-whisperers/solstein as the project root.\n"
    )

    # scan with default scope_dirs — docs is not in scope
    violations = module.scan(tmp_path, scope_dirs=["src", "bin", "scripts"])
    assert violations == [], "Docs directory should not be scanned"


def test_ci_guard_detects_violation_in_scripts(tmp_path: Path) -> None:
    """Violations inside scripts/ are detected."""
    module = _load_ci_module()

    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "run_job.sh").write_text(
        "#!/bin/bash\ncd /home/ci-runner/project && python main.py\n"
    )

    violations = module.scan(tmp_path, scope_dirs=["scripts"])
    assert len(violations) == 1
    _, lineno, _ = violations[0]
    assert lineno == 2


# ---------------------------------------------------------------------------
# Tests: _PROJECT_ROOT resolution in agent entry-points
# ---------------------------------------------------------------------------

def test_runner_project_root_resolves_correctly() -> None:
    """bin/agents/runner.py _PROJECT_ROOT should point to the repo root."""
    runner_path = ROOT / "bin" / "agents" / "runner.py"
    if not runner_path.exists():
        return  # skip if file not present

    spec = importlib.util.spec_from_file_location("runner_mod", runner_path)
    assert spec and spec.loader

    # We cannot exec runner.py fully (it imports solstein), but we can verify
    # the constant is computed relative to __file__, not hardcoded.
    source = runner_path.read_text()
    assert "Path(__file__).resolve()" in source, (
        "runner.py must use Path(__file__).resolve() for _PROJECT_ROOT"
    )
    assert "/home/" not in source, (
        "runner.py must not contain any hardcoded /home/ path"
    )


def test_orchestrate_agents_project_root_resolves_correctly() -> None:
    """bin/orchestrate_agents.py _PROJECT_ROOT must use dynamic resolution."""
    orch_path = ROOT / "bin" / "orchestrate_agents.py"
    if not orch_path.exists():
        return

    source = orch_path.read_text()
    assert "Path(__file__).resolve()" in source, (
        "orchestrate_agents.py must use Path(__file__).resolve() for _PROJECT_ROOT"
    )
    assert "/home/" not in source, (
        "orchestrate_agents.py must not contain any hardcoded /home/ path"
    )


def test_shell_scripts_use_bash_source_pattern() -> None:
    """Key shell scripts must derive PROJECT_ROOT via BASH_SOURCE, not hardcoded paths."""
    shell_scripts = [
        ROOT / "bin" / "monitor-live.sh",
        ROOT / "scripts" / "services" / "start_api_server.sh",
        ROOT / "scripts" / "services" / "start_celery_workers.sh",
        ROOT / "scripts" / "workflows" / "run_eneve_complete_flow.sh",
    ]
    for script in shell_scripts:
        if not script.exists():
            continue
        source = script.read_text()
        assert "BASH_SOURCE" in source, (
            f"{script.name} must use ${{BASH_SOURCE[0]}} for path resolution"
        )
        assert "/home/" not in source, (
            f"{script.name} must not contain any hardcoded /home/ path"
        )


def test_ci_guard_script_itself_excluded() -> None:
    """The CI guard script exempts itself from scanning."""
    module = _load_ci_module()
    assert module._is_allowed(CI_SCRIPT)


def test_ci_guard_project_scan_passes() -> None:
    """The real project scan must return zero violations (regression guard)."""
    module = _load_ci_module()
    violations = module.scan(ROOT)
    assert violations == [], (
        "Hardcoded /home/ paths found in project:\n"
        + "\n".join(f"  {f}:{n}  {c}" for f, n, c in violations)
    )
