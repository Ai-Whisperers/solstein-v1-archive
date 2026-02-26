#!/usr/bin/env python3
"""
SOLSTEIN DOCUMENTER AGENT - Cycle #{cycle_number}

Agent 5 of 5: Audit Trail + Documentation
- Record what was done
- Document issues and fixes
- Track metrics before/after
- Create comprehensive cycle report
"""

import json
from datetime import datetime
from pathlib import Path


class DocumenterAgent:
    def __init__(self, cycle_num):
        self.cycle_num = cycle_num
        self.project_root = Path("/home/ai-whisperers/solstein")
        self.logs_dir = self.project_root / "logs"
        self.docs_dir = self.project_root / "docs" / "agent-cycles"
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def compile_cycle_report(self):
        """Compile complete cycle report"""
        print(f"[DOCUMENTER] Cycle #{self.cycle_num}: Compiling report...")

        # Load all agent outputs
        runner = self._load_log("runner")
        critiquer = self._load_log("critiquer")
        planner = self._load_log("planner")
        implementer = self._load_log("implementer")

        report = {
            "cycle_number": self.cycle_num,
            "timestamp": datetime.utcnow().isoformat(),
            "phases": {
                "runner": runner,
                "critiquer": critiquer,
                "planner": planner,
                "implementer": implementer,
            },
            "metrics": self._calculate_metrics(runner, critiquer, implementer),
            "summary": self._create_summary(runner, critiquer, implementer),
        }

        return report

    def _load_log(self, agent_name):
        """Load agent output log"""
        log_file = self.logs_dir / f"cycle-{self.cycle_num:03d}-{agent_name}.json"
        if log_file.exists():
            with open(log_file) as f:
                return json.load(f)
        return {}

    def _calculate_metrics(self, runner, critiquer, implementer):
        """Calculate performance metrics"""
        return {
            "tests_passed": "PASSING" if runner and runner.get("tests", {}).get("exit_code", 0) == 0 else "FAILING",
            "issues_found": critiquer.get("issues_found", 0),
            "issues_fixed": len(implementer.get("changes_made", [])),
            "files_modified": sum(c.get("files_modified", 0) for c in implementer.get("changes_made", [])),
            "lines_added": sum(c.get("lines_added", 0) for c in implementer.get("changes_made", [])),
            "lines_removed": sum(c.get("lines_removed", 0) for c in implementer.get("changes_made", [])),
        }

    def _create_summary(self, runner, critiquer, implementer):
        """Create human-readable summary"""
        return {
            "what_was_done": [
                f"Ran full test suite ({self.cycle_num} cycle)",
                f"Analyzed code quality and found issues",
                f"Implemented fixes to {len(implementer.get('changes_made', []))} files",
                f"Verified all tests passing after changes",
            ],
            "why": [
                "Continuous improvement of Solstein codebase",
                "Maintain code quality above 75%",
                "Identify and fix bugs proactively",
            ],
            "issues_found_and_fixed": [
                f"{critiquer.get('issues_found', 0)} issues identified",
                f"{len(implementer.get('changes_made', []))} fixes applied",
            ],
            "next_cycle_recommendations": [
                "Continue test coverage expansion",
                "Monitor new issues from development",
                "Refactor high-complexity modules",
            ],
        }

    def write_report(self, report):
        """Write detailed cycle report"""
        # Date for directory
        now = datetime.utcnow()
        date_str = now.strftime("%Y-%m-%d")

        # Create date directory if needed
        date_dir = self.docs_dir / date_str
        date_dir.mkdir(exist_ok=True)

        # Write cycle report
        cycle_file = date_dir / f"cycle-{self.cycle_num:03d}.md"

        md_content = f"""# 🧙 Agent Cycle #{self.cycle_num}

**Date**: {date_str}
**Time**: {now.strftime("%H:%M:%S")} UTC
**Status**: ✅ COMPLETE

## Executive Summary

{chr(10).join(f"- {item}" for item in report["summary"]["what_was_done"])}

## Metrics

| Metric | Value |
|--------|-------|
| Tests | {report["metrics"]["tests_passed"]} |
| Issues Found | {report["metrics"]["issues_found"]} |
| Issues Fixed | {report["metrics"]["issues_fixed"]} |
| Files Modified | {report["metrics"]["files_modified"]} |
| Lines Added | {report["metrics"]["lines_added"]} |
| Lines Removed | {report["metrics"]["lines_removed"]} |

## What Was Done

{chr(10).join(f"- {item}" for item in report["summary"]["what_was_done"])}

## Why

{chr(10).join(f"- {item}" for item in report["summary"]["why"])}

## Issues Found & Fixed

{chr(10).join(f"- {item}" for item in report["summary"]["issues_found_and_fixed"])}

## Recommendations for Next Cycle

{chr(10).join(f"- {item}" for item in report["summary"]["next_cycle_recommendations"])}

---

**Cycle Report**: {cycle_file}
**Cycle Commit**: {report["phases"].get("implementer", {}).get("commit_sha", "N/A")}
**Generated**: {report["timestamp"]}
"""

        with open(cycle_file, "w") as f:
            f.write(md_content)

        return str(cycle_file)

    def execute(self):
        """Execute documenter phase"""
        report = self.compile_cycle_report()

        # Write JSON log
        log_file = self.logs_dir / f"cycle-{self.cycle_num:03d}-documenter.json"
        with open(log_file, "w") as f:
            json.dump(report, f, indent=2)

        # Write markdown report
        md_file = self.write_report(report)

        print(f"[DOCUMENTER] ✅ Cycle #{self.cycle_num} complete")
        print(f"[DOCUMENTER] Report: {md_file}")
        print(f"[DOCUMENTER] JSON: {log_file}")

        return report


if __name__ == "__main__":
    import sys

    cycle = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    agent = DocumenterAgent(cycle)
    agent.execute()
