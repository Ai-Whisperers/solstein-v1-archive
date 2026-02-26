#!/usr/bin/env python3
"""
SOLSTEIN PLANNER AGENT - Cycle #{cycle_number}

Agent 3 of 5: Prioritization + Strategy
- Review issues from critiquer
- Create improvement plan
- Allocate effort
- Set success criteria
"""

import json
from datetime import datetime
from pathlib import Path


class PlannerAgent:
    def __init__(self, cycle_num):
        self.cycle_num = cycle_num
        self.project_root = Path("/home/ai-whisperers/solstein")
        self.logs_dir = self.project_root / "logs"

    def create_plan(self):
        """Create improvement plan"""
        print(f"[PLANNER] Cycle #{self.cycle_num}: Creating improvement plan...")

        # Load critiquer output
        critiquer_log = self.logs_dir / f"cycle-{self.cycle_num:03d}-critiquer.json"
        if critiquer_log.exists():
            with open(critiquer_log) as f:
                critiquer_data = json.load(f)
        else:
            critiquer_data = {}

        # Prioritize recommendations
        recommendations = critiquer_data.get("recommendations", [])

        plan = {
            "cycle": self.cycle_num,
            "timestamp": datetime.now().isoformat(),
            "objective": self._create_objective(recommendations),
            "tasks": self._create_tasks(recommendations),
            "success_criteria": self._define_success_criteria(),
            "estimated_effort": self._estimate_effort(recommendations),
        }

        return plan

    def _create_objective(self, recommendations):
        """Define cycle objective"""
        if not recommendations:
            return "Maintain code quality and expand test coverage"

        high_priority = [r for r in recommendations if r["priority"] in ["P0", "P1"]]
        if high_priority:
            return f"Resolve {len(high_priority)} critical issues and improve code quality"
        else:
            return "Continuous improvement: fix medium/low priority issues"

    def _create_tasks(self, recommendations):
        """Create actionable tasks"""
        tasks = []
        for i, rec in enumerate(recommendations[:5], 1):  # Top 5 tasks
            tasks.append(
                {
                    "id": f"task-{i}",
                    "priority": rec["priority"],
                    "action": rec["action"],
                    "effort": rec["estimated_effort"],
                    "owner": "implementer",
                }
            )
        return tasks

    def _define_success_criteria(self):
        """Define what success looks like"""
        return [
            "All P0/P1 issues resolved",
            "Test coverage maintained ≥75%",
            "All tests passing",
            "Zero new security issues",
            "Code quality score improved or maintained",
        ]

    def _estimate_effort(self, recommendations):
        """Estimate total effort"""
        p0_p1_count = len([r for r in recommendations if r["priority"] in ["P0", "P1"]])
        hours = max(0.5, p0_p1_count * 0.5)
        return f"{hours} hours"

    def execute(self):
        """Execute planner phase"""
        plan = self.create_plan()

        # Save to logs
        log_file = self.logs_dir / f"cycle-{self.cycle_num:03d}-planner.json"
        with open(log_file, "w") as f:
            json.dump(plan, f, indent=2)

        print(f"[PLANNER] ✅ Cycle #{self.cycle_num} complete")
        print(f"[PLANNER] Objective: {plan['objective']}")
        print(f"[PLANNER] Effort: {plan['estimated_effort']}")
        print(f"[PLANNER] Logs: {log_file}")

        return plan


if __name__ == "__main__":
    import sys

    cycle = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    agent = PlannerAgent(cycle)
    agent.execute()
