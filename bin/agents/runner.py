#!/usr/bin/env python3
"""
SOLSTEIN RUNNER AGENT - Cycle #{cycle_number}

Agent 1 of 5: Code Execution + Baseline Metrics
- Run full test suite
- Execute code quality checks
- Gather baseline metrics
- Identify new issues
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Resolve project root dynamically from this file's location: bin/agents/runner.py → project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Discover Python interpreter: prefer the current interpreter, fall back to shutil.which
_PYTHON = sys.executable or shutil.which("python3") or "python3"


class RunnerAgent:
    def __init__(self, cycle_num):
        self.cycle_num = cycle_num
        self.project_root = _PROJECT_ROOT
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)

    def run_tests(self):
        """Execute full test suite"""
        print(f"[RUNNER] Cycle #{self.cycle_num}: Running test suite...")
        result = subprocess.run(
            [_PYTHON, "-m", "pytest", "tests/", "-v", "--tb=short"],
            cwd=self.project_root,
            capture_output=True,
            text=True,
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timestamp": datetime.now().isoformat(),
        }

    def run_quality_checks(self):
        """Run code quality analysis"""
        print(f"[RUNNER] Cycle #{self.cycle_num}: Running quality checks...")
        checks = {
            "mypy": self._run_mypy(),
            "bandit": self._run_bandit(),
            "radon": self._run_radon(),
        }
        return checks

    def _run_mypy(self):
        result = subprocess.run(
            [_PYTHON, "-m", "mypy", "src/", "--ignore-missing-imports"],
        )
        return {"exit_code": result.returncode, "output": result.stdout}

    def _run_bandit(self):
        result = subprocess.run(
            ["bandit", "-r", "src/", "-f", "json"],
        )
        try:
            return json.loads(result.stdout)
        except (json.JSONDecodeError, ValueError):
            return {"error": result.stderr}

    def _run_radon(self):
        result = subprocess.run(
            ["radon", "cc", "src/", "-a", "-nc"],
        )
        return {"output": result.stdout}

    def gather_metrics(self):
        """Collect baseline metrics"""
        print(f"[RUNNER] Cycle #{self.cycle_num}: Gathering metrics...")
        return {
            "cycle": self.cycle_num,
            "timestamp": datetime.now().isoformat(),
            "tests": self.run_tests(),
            "quality": self.run_quality_checks(),
        }

    def execute(self):
        """Execute runner phase"""
        metrics = self.gather_metrics()

        # Save to logs
        log_file = self.logs_dir / f"cycle-{self.cycle_num:03d}-runner.json"
        with open(log_file, "w") as f:
            json.dump(metrics, f, indent=2)

        print(f"[RUNNER] ✅ Cycle #{self.cycle_num} complete")
        print(f"[RUNNER] Logs: {log_file}")

        return metrics


if __name__ == "__main__":
    import sys

    cycle = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    agent = RunnerAgent(cycle)
    agent.execute()
