#!/usr/bin/env python3
"""
SOLSTEIN CRITIQUER AGENT - Cycle #{cycle_number}

Agent 2 of 5: Analysis + Issue Detection
- Analyze test results
- Find bugs and issues
- Prioritize problems
- Create improvement recommendations
"""

import json
from datetime import datetime
from pathlib import Path


class CritiquerAgent:
    def __init__(self, cycle_num):
        self.cycle_num = cycle_num
        self.project_root = Path("/home/ai-whisperers/solstein")
        self.logs_dir = self.project_root / "logs"

    def analyze_results(self):
        """Analyze runner results"""
        print(f"[CRITIQUER] Cycle #{self.cycle_num}: Analyzing results...")

        # Load runner output
        runner_log = self.logs_dir / f"cycle-{self.cycle_num:03d}-runner.json"
        if runner_log.exists():
            with open(runner_log) as f:
                runner_data = json.load(f)
        else:
            runner_data = {}

        # Analyze for issues
        issues = self._find_issues(runner_data)

        return {
            "cycle": self.cycle_num,
            "timestamp": datetime.utcnow().isoformat(),
            "issues_found": len(issues),
            "issues": issues,
            "recommendations": self._generate_recommendations(issues),
        }

    def _find_issues(self, data):
        """Extract issues from test/quality data"""
        issues = []

        # Check test failures
        if "tests" in data:
            tests = data["tests"]
            if tests.get("exit_code", 0) != 0:
                issues.append(
                    {
                        "severity": "HIGH",
                        "category": "Test",
                        "description": "Test suite failure detected",
                        "impact": "CI blocking",
                    }
                )

        # Check security issues
        if "quality" in data and "bandit" in data["quality"]:
            bandit = data["quality"]["bandit"]
            if isinstance(bandit, dict) and "results" in bandit:
                for result in bandit["results"]:
                    issues.append(
                        {
                            "severity": result.get("severity", "MEDIUM"),
                            "category": "Security",
                            "description": result.get("issue_text", "Security issue"),
                            "file": result.get("filename", "unknown"),
                            "line": result.get("line_number", "unknown"),
                        }
                    )

        return issues

    def _generate_recommendations(self, issues):
        """Generate fix recommendations"""
        recommendations = []

        for issue in issues:
            if issue["severity"] == "CRITICAL":
                priority = "P0"
            elif issue["severity"] == "HIGH":
                priority = "P1"
            else:
                priority = "P2"

            recommendations.append(
                {
                    "priority": priority,
                    "action": f"Fix {issue['category']} issue: {issue['description']}",
                    "estimated_effort": "15-30 min",
                }
            )

        return sorted(recommendations, key=lambda x: x["priority"])

    def execute(self):
        """Execute critiquer phase"""
        analysis = self.analyze_results()

        # Save to logs
        log_file = self.logs_dir / f"cycle-{self.cycle_num:03d}-critiquer.json"
        with open(log_file, "w") as f:
            json.dump(analysis, f, indent=2)

        print(f"[CRITIQUER] ✅ Cycle #{self.cycle_num} complete")
        print(f"[CRITIQUER] Found {analysis['issues_found']} issues")
        print(f"[CRITIQUER] Logs: {log_file}")

        return analysis


if __name__ == "__main__":
    import sys

    cycle = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    agent = CritiquerAgent(cycle)
    agent.execute()
