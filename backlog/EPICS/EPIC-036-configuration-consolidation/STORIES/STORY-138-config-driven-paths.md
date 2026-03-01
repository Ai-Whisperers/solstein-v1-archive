# STORY-138: Replace Hardcoded Paths with Config-Driven Paths

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-036: Configuration Consolidation |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> 15+ hardcoded paths: /home/ai-whisperers/solstein, /home/ai-whisperers/.linuxbrew/bin/python3, /tmp/solstein-cycle-counter, /home/ai-whisperers/solstein/.cache.

## Problem Statement

The codebase is full of paths that only work on one developer's machine. /home/ai-whisperers/ is not a standard path — it's a specific user's home directory. When another developer tries to run the code, it fails because those paths don't exist. When deployed to production, it fails because /home/ai-whisperers/ doesn't exist there either. The fix is config-driven paths that use environment variables or standard locations.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Portability** | Code only works on original developer's machine |
| **Deployment** | Production paths differ |
| **Developer Experience** | New developers can't run the code |

## Affected Files

| File | Issue |
|------|-------|
| `bin/orchestrate_agents.py` | Hardcoded paths |
| `bin/agents/runner.py` | Hardcoded paths |
| `bin/agents/rate-limiter.py` | Hardcoded paths |
| `scripts/services/*.sh` | Hardcoded PYTHONPATH |
| `bin/solstein-agents.service` | Hardcoded WorkingDirectory |

## Architectural Requirements

- All hardcoded /home/ai-whisperers/ paths replaced with environment variables or relative paths
- PROJECT_ROOT determined dynamically (Path(__file__).parent.parent) or via env var
- Cache directories use platform-appropriate locations (tempfile.gettempdir(), XDG_CACHE_HOME)
- Python interpreter path discovered via shutil.which() or env var, not hardcoded
- Service files use environment variables for WorkingDirectory
- CI verification: code fails if hardcoded /home/ paths detected

## Acceptance Criteria

- [ ] No hardcoded /home/ai-whisperers/ paths
- [ ] PROJECT_ROOT determined dynamically
- [ ] Cache uses platform-appropriate locations
- [ ] Python path discovered dynamically
- [ ] CI catches hardcoded paths

## Definition of Done

- **Tests Required**: None
- **Documentation Required**: None
- **Code Review Gate**: grep for "/home/ai-whisperers" returns zero results

## Notes

Code should work on any machine, not just the original developer's.
