#!/usr/bin/env python3
"""
SOLSTEIN AGENT ORCHESTRATOR - FIXED VERSION

Runs the 5-agent autonomous system in sequence:
1. RUNNER - Execute tests & gather metrics
2. CRITIQUER - Analyze issues
3. PLANNER - Create improvement plan
4. IMPLEMENTER - Apply fixes
5. DOCUMENTER - Record audit trail

Cycle runs every 30 minutes (48 cycles per day)
"""

import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

# Resolve project root dynamically: bin/orchestrate_agents.py → project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# State directory: configurable via STATE_DIR env var, falls back to platform temp dir
_STATE_DIR = Path(os.environ.get("STATE_DIR", tempfile.gettempdir()))


class AgentOrchestrator:
    def __init__(self):
        self.project_root = _PROJECT_ROOT
        self.agents_dir = self.project_root / "bin" / "agents"
        self.logs_dir = self.project_root / "logs"
        self.counter_file = _STATE_DIR / "solstein-cycle-counter"
        self.logs_dir.mkdir(exist_ok=True)

        # Get and increment cycle number
        self.cycle_num = self._get_and_increment_cycle_number()

    def _get_and_increment_cycle_number(self):
        """Get current cycle number and increment for next time"""
        try:
            if self.counter_file.exists():
                with open(self.counter_file) as f:
                    cycle_num = int(f.read().strip())
            else:
                cycle_num = 1
        except (OSError, ValueError):
            cycle_num = 1

        # Write incremented number for next cycle
        with open(self.counter_file, "w") as f:
            f.write(str(cycle_num + 1))

        return cycle_num

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
                self.log("⚠️  Agent returned non-zero exit code")
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
        except (subprocess.SubprocessError, OSError, FileNotFoundError) as e:
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
        self.log(f"Next cycle number: {self.cycle_num + 1}")
        self.log("")

        return all(results.values())


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
