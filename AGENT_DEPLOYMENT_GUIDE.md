# 🤖 Solstein Autonomous Agents - Deployment Guide

**Status**: Ready for deployment  
**Version**: 1.0  
**Components**: 5 agents + orchestrator  

---

## 📋 Overview

The Solstein autonomous agent system runs 5 specialized agents in sequence, continuously improving the codebase 24/7:

```
RUNNER → CRITIQUER → PLANNER → IMPLEMENTER → DOCUMENTER
  (tests)   (analysis)  (strategy)  (coding)    (reporting)
```

**Cycle Time**: ~30-45 minutes per cycle  
**Frequency**: Every 6 hours (4 cycles/day)  
**Daily Cycles**: 4  
**Documentation**: Comprehensive audit trails in `/docs/agent-cycles/`

---

## 🚀 Quick Start

### Option 1: Run Single Cycle (Testing)

```bash
# Test one complete cycle
cd /home/ai-whisperers/solstein
python3 bin/orchestrate_agents.py

# Check results
ls logs/
ls docs/agent-cycles/2026-02-26/
```

### Option 2: Run Continuous (systemd timer)

```bash
# Install service and timer
sudo cp bin/solstein-agents.service /etc/systemd/system/
sudo cp bin/solstein-agents.timer /etc/systemd/system/

# Enable and start
sudo systemctl enable solstein-agents.timer
sudo systemctl start solstein-agents.timer

# Check status
sudo systemctl status solstein-agents.timer
journalctl -u solstein-agents -f  # Watch logs
```

---

## 🤖 Agent Specifications

### Agent 1: RUNNER
**Purpose**: Execute tests and gather baseline metrics  
**Time**: ~10 minutes  
**Output**: Test results, code quality metrics

```python
# Runs:
- pytest (full suite)
- mypy (type checking)
- bandit (security)
- radon (complexity)
```

### Agent 2: CRITIQUER
**Purpose**: Analyze issues and create recommendations  
**Time**: ~5 minutes  
**Input**: Runner output  
**Output**: Prioritized issues, recommendations

```python
# Analyzes:
- Test failures
- Security vulnerabilities
- Type errors
- Complexity violations
```

### Agent 3: PLANNER
**Purpose**: Create improvement strategy  
**Time**: ~3 minutes  
**Input**: Critiquer analysis  
**Output**: Prioritized task plan, success criteria

```python
# Defines:
- Cycle objective
- Top 5 tasks (prioritized)
- Estimated effort
- Success criteria
```

### Agent 4: IMPLEMENTER
**Purpose**: Apply fixes and verify  
**Time**: ~15-20 minutes  
**Input**: Plan  
**Output**: Code changes, test results, commit

```python
# Executes:
- Apply fixes (code changes)
- Run tests after each change
- Create git commits
- Verify success criteria
```

### Agent 5: DOCUMENTER
**Purpose**: Create comprehensive audit trail  
**Time**: ~2 minutes  
**Input**: All previous agent outputs  
**Output**: Cycle report (Markdown + JSON)

```python
# Records:
- What was done (executive summary)
- Why (rationale)
- Issues found and fixed
- Metrics before/after
- Recommendations for next cycle
```

---

## 📊 Documentation Structure

Each cycle generates:

```
/solstein/docs/agent-cycles/
├── 2026-02-26/
│   ├── cycle-001.md          ← Human-readable report
│   ├── cycle-002.md
│   ├── cycle-003.md
│   ├── cycle-004.md
│   └── DAILY_SUMMARY_2026-02-26.md
└── AGENT_WORK_LOG.md         ← Master index
```

### Cycle Report Contents

- Executive summary (2-3 sentences)
- Metrics table (tests, coverage, quality)
- What was done (bulleted)
- Why (rationale)
- Issues found and fixed
- Recommendations for next cycle
- Commit SHA and timestamps

---

## 🔄 Cycle Timing

**Default Schedule** (with systemd timer):

```
Cycle #1:  00:00-00:45 UTC  (Runner → Documenter)
Cycle #2:  06:00-06:45 UTC
Cycle #3:  12:00-12:45 UTC
Cycle #4:  18:00-18:45 UTC
(Daily)
```

**Per-Cycle Timeline**:

```
00:00 Runner starts       (test execution)
10:00 Critiquer starts    (analysis)
15:00 Planner starts      (strategy)
18:00 Implementer starts  (code changes)
33:00 Documenter starts   (reporting)
45:00 Cycle complete      (git commit + markdown report)
```

---

## 📈 Example Daily Report

```
# 📊 Daily Summary — 2026-02-26

**Period**: 4 cycles (spanning 24 hours)  
**Total Work**: 3 hours of autonomous improvement

## Executive Summary

Agents completed 4 autonomous cycles, improving code quality from 72→82 
and expanding test coverage to ~28%. Eight bugs fixed, three complex 
functions refactored. System stable, all tests passing.
and expanding test coverage from 57%→65%. Eight bugs fixed, three complex 
functions refactored. System stable, all tests passing.

## Key Achievements

- 🏆 Coverage: ~28% line coverage (improving)
- 🏆 Quality score: 72 → 82 (+10 pts)
- 🏆 Bugs fixed: 8
- 🏆 Zero test flakiness

## Cycle Breakdown

| Cycle | Objective | Result | Commit |
|-------|-----------|--------|--------|
| #1 | Fix race condition | ✅ Fixed in 28 min | abc1234 |
| #2 | Refactor complexity | ✅ 3 functions split | def5678 |
| #3 | Add tests | ✅ +12 new tests | ghi9012 |
| #4 | Type safety | ✅ 0 type errors | jkl3456 |

## Metrics Dashboard

[Chart showing coverage trend, issue resolution rate, code quality trajectory]

---
```

---

## 🛠️ Manual Intervention Points

Agents are **autonomous** but you can intervene:

### Pause Cycles
```bash
sudo systemctl stop solstein-agents.timer
```

### View Live Logs
```bash
sudo journalctl -u solstein-agents -f --lines=50
```

### Check Last Cycle Results
```bash
# See all cycle reports
ls /home/ai-whisperers/solstein/docs/agent-cycles/*/

# View latest report
cat /home/ai-whisperers/solstein/docs/agent-cycles/2026-02-26/cycle-004.md
```

### Force Immediate Cycle
```bash
# Run outside of schedule
python3 /home/ai-whisperers/solstein/bin/orchestrate_agents.py CYCLE_NUM=999
```

---

## 🎯 Success Metrics

Monitor these in cycle reports:

- ✅ **Tests passing**: Should be 100%
- ✅ **Coverage trending**: Should increase or stay ≥75%
- ✅ **Issues found/fixed ratio**: Should be 1:1 (found issues get fixed same cycle)
- ✅ **Code quality**: Should trend upward
- ✅ **Cycle duration**: Should stay <1 hour
- ✅ **Build status**: Should always be ✅ PASS

---

## 🚨 Troubleshooting

### Agents not running?
```bash
# Check systemd status
sudo systemctl status solstein-agents.timer
sudo systemctl status solstein-agents.service

# Check logs
journalctl -u solstein-agents -n 50
```

### Cycles taking too long?
- Check if tests are hanging (increase timeout)
- Check if project is too large (split test suite)
- Monitor resources: `top`, `docker stats`

### Documentation not being created?
- Check `/solstein/docs/agent-cycles/` permissions
- Verify Python can write to logs directory
- Check for exceptions in agent logs

---

## 📝 Environment Variables

```bash
# Control cycle numbering
export CYCLE_NUM=1

# Control behavior
export TIMEOUT_SECONDS=300  # Agent timeout
export SKIP_TESTS=false     # Always run tests
export VERBOSE=true         # More logging
```

---

## 🔐 Security Notes

- Agents run as `ai-whisperers` user (non-root)
- Resource limits enforced (2GB memory, 50% CPU)
- systemd isolates processes (`ProtectHome=yes`)
- All changes committed to git (full audit trail)
- Reports logged and versioned in `/docs/agent-cycles/`

---

## 📞 Support

For issues or customization:

1. Check `journalctl -u solstein-agents`
2. Review last cycle report in `/docs/agent-cycles/`
3. Test manually: `python3 bin/orchestrate_agents.py`

---

**Status**: Ready for deployment ✅  
**Next Step**: Install systemd service and start continuous operation
