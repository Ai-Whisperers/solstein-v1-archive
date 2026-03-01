# Issues & Gotchas

## 2026-03-01

### task() timeout issue
- ALL task() calls with run_in_background=false timeout at 600s
- Use run_in_background=true + background_output() polling
- Agents spend too long on exploration + test suite runs

### auth.py bypass
- `src/solstein/api/routers/auth.py` lines ~57-60: comment "# Demo: Accept any credentials"
- Returns valid JWT for any email/password — MUST fix in EPIC-020

### monitoring.py fake health checks
- `src/solstein/monitoring.py` calls asyncio.sleep(0.01) and reports success
- Fix in EPIC-044/014

### research_dual_write.py atomicity
- 7 sequential DB commits, no transaction wrapping, no rollback on failure
- Fix in EPIC-004

### llm/enhanced_client.py silent failures
- 661-line custom LLM client with silent `return None` in exception handlers
- Fix in EPIC-034/021

### worker_tasks_v2.py
- Possibly dead code / duplicate of worker_tasks.py
- Verify imports before deleting (EPIC-037)

### agents/ stubs
- 7 stub agents returning hardcoded mock data
- Fix in EPIC-022
