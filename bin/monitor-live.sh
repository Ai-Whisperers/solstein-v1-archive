#!/bin/bash
# Live monitoring dashboard for continuous cycles

clear
echo "🔄 SOLSTEIN CONTINUOUS OPERATION MONITOR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Timer Status:"
systemctl --user status solstein-agents.timer 2>&1 | grep -E "Active|Trigger"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Live Agent Execution:"
echo ""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
echo "Watching $PROJECT_ROOT/logs/ for new cycles..."
echo ""
journalctl --user -u solstein-agents.service -f --no-pager 2>&1 | grep -E "\[RUNNER\]|\[CRITIQUER\]|\[PLANNER\]|\[IMPLEMENTER\]|\[DOCUMENTER\]|Agents completed|complete at"
