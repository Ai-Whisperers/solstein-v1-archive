#!/usr/bin/env python3
"""
SOLSTEIN AGENT ORCHESTRATOR

Runs the 5-agent autonomous system in sequence:
1. RUNNER - Execute tests & gather metrics
2. CRITIQUER - Analyze issues
3. PLANNER - Create improvement plan
4. IMPLEMENTER - Apply fixes
5. DOCUMENTER - Record audit trail

Cycle runs every 6 hours (4 cycles per day)
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
import sys


class AgentOrchestrator:
    def __init__(self):
        self.project_root = Path("/home/ai-whisperers/solstein")
        self.agents_dir = self.project_root / "bin" / "agents"
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)

        # Calculate cycle number (0-based, increments every 6 hours)
        import os

        self.cycle_num = int(os.environ.get("CYCLE_NUM", "1"))

    def log(self, message):
        """Print with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S UTC")
        print(f"[{timestamp}] {message}")

    def run_agent(self, agent_name):
        """Run a single agent"""
        self.log(f"🤖 STARTING AGENT: {agent_name.upper()}")

        agent_script = self.agents_dir / f"{agent_name}.py"

        try:
            result = subprocess.run(
                ["python3", str(agent_script), str(self.cycle_num)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per agent
            )

            self.log(f"✅ {agent_name.upper()} completed (exit code: {result.returncode})")

            if result.returncode != 0:
                self.log(f"⚠️  Agent returned non-zero exit code")
                if result.stderr:
                    self.log(f"   Error: {result.stderr[:200]}")

            # Print agent output
            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    self.log(f"   {line}")

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            self.log(f"❌ {agent_name.upper()} timed out after 5 minutes")
            return False
        except Exception as e:
            self.log(f"❌ {agent_name.upper()} failed: {e}")
            return False

    def run_cycle(self):
        """Execute full cycle (5 agents)"""
        self.log("=" * 70)
        self.log(f"🧙 SOLSTEIN AUTONOMOUS CYCLE #{self.cycle_num}")
        self.log("=" * 70)
        self.log("")

        agents = ["runner", "critiquer", "planner", "implementer", "documenter"]
        results = {}
        start_time = datetime.now()

        for i, agent_name in enumerate(agents, 1):
            self.log(f"[{i}/{len(agents)}] {agent_name.upper()}")
            results[agent_name] = self.run_agent(agent_name)
            self.log("")

            # Small delay between agents
            if i < len(agents):
                time.sleep(2)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Summary
        self.log("=" * 70)
        self.log("CYCLE SUMMARY")
        self.log("=" * 70)

        passed = sum(1 for v in results.values() if v)
        self.log(f"Agents completed: {passed}/{len(agents)}")

        for agent_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            self.log(f"  {agent_name:15} {status}")

        self.log(f"Total duration: {duration:.1f} seconds")
        self.log(f"Cycle complete at: {end_time.isoformat()}")
        self.log("")

        return all(results.values())

    def schedule_next_cycle(self):
        """Schedule next cycle in 6 hours"""
        import schedule
        import atexit

        def run_scheduler():
            schedule.every(6).hours.do(self.run_cycle)
            while True:
                schedule.run_pending()
                time.sleep(60)

        self.log("Next cycle scheduled in 6 hours")
        self.log("Press Ctrl+C to stop")

        try:
            run_scheduler()
        except KeyboardInterrupt:
            self.log("\nCycle scheduler stopped")


def main():
    orchestrator = AgentOrchestrator()

    # Run once or continuous?
    continuous = "--continuous" in sys.argv or "--daemon" in sys.argv

    if continuous:
        orchestrator.log("Running in CONTINUOUS mode (systemd timer)")
        orchestrator.run_cycle()
    else:
        orchestrator.log("Running in ONE-SHOT mode")
        success = orchestrator.run_cycle()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
