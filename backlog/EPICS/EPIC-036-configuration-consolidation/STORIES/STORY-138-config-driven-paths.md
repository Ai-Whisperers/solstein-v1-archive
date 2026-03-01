# STORY-138: Replace Hardcoded Paths with Config-Driven Paths

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-036: Configuration Consolidation |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-002 (Configuration Integrity), STORY-137 |

---

## The Audit Verdict

> 15+ hardcoded paths: `/home/ai-whisperers/solstein`, `/home/ai-whisperers/.linuxbrew/bin/python3`, `/tmp/solstein-cycle-counter`, `/home/ai-whisperers/solstein/.cache`.

---

## Problem Statement

The codebase contains paths that only work on one developer's machine. `/home/ai-whisperers/` is not a standard path — it is a specific user's home directory on a specific machine. When another developer clones the repository and attempts to run the code, it fails immediately because those paths do not exist on their system. When the code is deployed to a CI runner, it fails. When it is deployed to staging or production, it fails. The code is, in a meaningful sense, not portable.

The hardcoded Python interpreter path (`/home/ai-whisperers/.linuxbrew/bin/python3`) is particularly problematic. It means the agent runner will silently use the wrong Python — or fail to start — on any machine that does not have Homebrew installed at that exact location. This is not a configuration problem. It is a portability failure.

The `/tmp/solstein-cycle-counter` path is a different category of problem: it is a non-portable temporary file location that assumes Linux semantics and a specific `/tmp` directory. On macOS, `/tmp` is a symlink to a system-managed location. In containerized environments, `/tmp` may not persist between restarts. The correct approach is to use platform-appropriate temporary directories via the standard library.

The fix is straightforward: replace all hardcoded paths with dynamic resolution using `Path(__file__).parent`, environment variables, or standard library functions (`tempfile.gettempdir()`, `shutil.which()`). Add a CI check that fails the build if any hardcoded `/home/` path is detected.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Portability** | Code only works on the original developer's machine; fails on CI, staging, production, and any other developer's workstation |
| **Deployment** | Production environments do not have `/home/ai-whisperers/`; deployment fails without manual intervention |
| **Developer Experience** | New developers cannot run the code without first hunting down and replacing hardcoded paths |
| **CI/CD** | CI runners fail on path-dependent code; hardcoded paths are a build reliability hazard |

---

## Affected Files

| File | Issue |
|------|-------|
| `bin/orchestrate_agents.py` | Hardcoded `/home/ai-whisperers/solstein` as project root |
| `bin/agents/runner.py` | Hardcoded `/home/ai-whisperers/.linuxbrew/bin/python3` as Python interpreter |
| `bin/agents/rate-limiter.py` | Hardcoded `/tmp/solstein-cycle-counter` as state file |
| `scripts/services/*.sh` | Hardcoded `PYTHONPATH` and working directory paths |
| `bin/solstein-agents.service` | Hardcoded `WorkingDirectory` and `ExecStart` paths in systemd unit |
| `src/solstein/config.py` | Hardcoded `.cache` directory path relative to `/home/ai-whisperers/solstein` |

---

## Architectural Requirements

- All hardcoded `/home/ai-whisperers/` paths replaced with environment variables or dynamic resolution
- `PROJECT_ROOT` determined dynamically using `Path(__file__).resolve().parent.parent` or equivalent; never hardcoded
- Cache directories use platform-appropriate locations: `XDG_CACHE_HOME` on Linux, `~/Library/Caches` on macOS, or `tempfile.gettempdir()` as fallback
- Python interpreter path discovered via `shutil.which('python3')` or read from a `PYTHON_EXECUTABLE` environment variable; never hardcoded
- Systemd service files use environment variables for `WorkingDirectory` and `ExecStart`; values populated at install time, not hardcoded
- Shell scripts derive paths from `$PROJECT_ROOT` environment variable or from the script's own location (`$(dirname "$0")`)
- Temporary state files use `tempfile.mkdtemp()` or a configurable `STATE_DIR` environment variable
- CI check added: build fails if `grep -r '/home/ai-whisperers' .` returns any results in tracked files

---

## Acceptance Criteria

- [ ] `grep -r '/home/ai-whisperers' src/ bin/ scripts/` returns zero results
- [ ] `grep -r '/home/ai-whisperers' *.service *.sh` returns zero results
- [ ] `PROJECT_ROOT` is determined dynamically in all files that reference it
- [ ] Python interpreter path is discovered via `shutil.which()` or environment variable
- [ ] Cache and temporary directories use platform-appropriate locations
- [ ] Systemd service files use environment variable substitution for all paths
- [ ] CI pipeline includes a step that fails if hardcoded `/home/` paths are detected
- [ ] Code runs successfully on a fresh developer machine without any path modifications

---

## Definition of Done

- **Tests Required**: Integration test that verifies `PROJECT_ROOT` resolves correctly when the code is run from a different working directory. CI check script that scans for hardcoded `/home/` paths and returns non-zero exit code if found.
- **Documentation Required**: Developer setup guide updated to remove any instructions that reference `/home/ai-whisperers/`. Operator guide updated with correct path configuration instructions.
- **Code Review Gate**: Reviewer clones the repository to a fresh directory (not `/home/ai-whisperers/`) and verifies the application starts without path-related errors. Reviewer confirms CI check is active and would catch a regression.

---

## Notes

The systemd service file (`bin/solstein-agents.service`) requires special handling. Systemd unit files do not support dynamic path resolution — paths must be concrete at install time. The correct approach is to generate the service file from a template during installation, substituting `$PROJECT_ROOT` and `$PYTHON_EXECUTABLE` at that point. The template should be committed to the repository; the generated file should not.

The `/tmp/solstein-cycle-counter` file is used by the rate limiter to persist state across process restarts. This is a reasonable use case, but the path should be configurable. The default should use `tempfile.gettempdir()` to find the platform-appropriate temp directory, with a `STATE_DIR` environment variable override for production deployments where a persistent location is required.

This story can proceed in parallel with STORY-139 after STORY-137 is complete.
