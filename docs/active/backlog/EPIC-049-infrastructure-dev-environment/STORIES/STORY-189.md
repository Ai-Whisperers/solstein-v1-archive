# STORY-189: Document Infrastructure Troubleshooting Guide

| Field | Value |
|-------|-------|
| **Status** | 🟡 Open |
| **Priority** | P2 — Medium |
| **Size** | S (< half a day) |
| **Epic** | EPIC-049 Infrastructure & Dev Environment |
| **Created** | 2026-03-01 |
| **Risk** | Low — documentation only |
| **Assigned** | — |

---

## Audit Verdict

**DOCUMENTATION GAP** — no centralized troubleshooting guide for infrastructure issues.

During the live analysis run, we encountered:
- `ModuleNotFoundError: No module named 'redis'`
- `ModuleNotFoundError: No module named 'solstein.exporters.report_generator'`
- PostgreSQL connection warnings about default credentials
- Unclear how to start full system

These required source code inspection to diagnose. A troubleshooting guide would have accelerated resolution.

---

## Problem Statement

Developers need a single reference for common infrastructure and runtime issues: what the error looks like, why it happens, and how to fix it. This reduces support burden and accelerates onboarding.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Developer Experience | 🟡 Medium — faster problem resolution |
| Onboarding | 🟡 Medium — self-service troubleshooting |
| Support Burden | 🟡 Medium — fewer "how do I..." questions |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `docs/TROUBLESHOOTING.md` | New (~200 lines) | Troubleshooting guide |
| `README.md` | Existing | Link to troubleshooting |
| `docs/development.md` | Existing | Link to troubleshooting |

---

## Dependencies

- **Hard**: None
- **Soft**: STORY-187, 188 (document docker-compose and startup scripts)
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: Create `docs/TROUBLESHOOTING.md` with sections:

1. **Installation Issues**
   - `ModuleNotFoundError: No module named 'redis'` → `uv add redis`
   - `ModuleNotFoundError: No module named 'solstein...'` → Check PYTHONPATH
   - `pip install` vs `uv sync` confusion

2. **Database Issues**
   - `pg_isready` fails → Start PostgreSQL
   - Default credentials warning → Update `.env`
   - Connection refused → Check port, firewall

3. **Redis Issues**
   - Import error → Install redis module
   - Connection refused → Start Redis
   - Celery can't connect → Check REDIS__URL

4. **CLI Issues**
   - `score` command crashes → JSON format issue (STORY-169)
   - `generate-llm-report` crashes → Missing module (STORY-170)
   - Deprecation warnings → Loader migration (STORY-171)

5. **API Issues**
   - Can't connect to localhost:8000 → Server not started
   - 503 errors → Redis not available
   - 401 errors → API key missing

6. **Report Issues**
   - Reports in wrong location → Path nesting bug (STORY-181)
   - Unrounded scores → Formatting issue (STORY-182)
   - Empty reports → Check input data

**REQ-2**: Each entry follows format:
```markdown
### Error: <error message or symptom>

**Symptom**: What you see
**Cause**: Why it happens
**Fix**: Step-by-step resolution
**Prevention**: How to avoid in future
```

**REQ-3**: Include quick diagnostic commands:
```bash
# Check all services
pg_isready -h localhost -p 5432
redis-cli ping
curl http://localhost:8000/health
```

---

## Acceptance Criteria

- [ ] `docs/TROUBLESHOOTING.md` exists and covers all issues from live analysis
- [ ] Each issue has symptom, cause, fix, and prevention
- [ ] Quick diagnostic commands section included
- [ ] Linked from README.md and development.md
- [ ] New developer can resolve common issues without asking for help

---

## Definition of Done

- [ ] Troubleshooting guide written
- [ ] Links added from main docs
- [ ] Reviewed by team member who didn't write it (clarity test)

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Identified need during live debugging session |
