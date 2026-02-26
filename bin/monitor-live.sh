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
echo "Watching /home/ai-whisperers/solstein/logs/ for new cycles..."
echo ""
journalctl --user -u solstein-agents.service -f --no-pager 2>&1 | grep -E "\[RUNNER\]|\[CRITIQUER\]|\[PLANNER\]|\[IMPLEMENTER\]|\[DOCUMENTER\]|Agents completed|complete at"
