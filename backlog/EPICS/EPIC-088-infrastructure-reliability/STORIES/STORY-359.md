# STORY-359: Add Task Discovery Test — All 13 Beat-Scheduled Tasks Are Importable

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P2 |
| **Size** | S (half day) |
| **Epic** | EPIC-088 Infrastructure Reliability |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (deep wiring audit) |
| **Risk** | Low |

---

## Exact Codebase Wiring (deep audit 2026-04-03)

### Beat Schedule (`src/solstein/celery_config.py:109–184`)

All 13 static tasks:

| Schedule key | Task path | Crontab | Line |
|---|---|---|---|
| `refresh-sec-edgar-daily` | `solstein.worker_tasks.refresh_sec_edgar` | `hour=9, min=0` | 113 |
| `refresh-companies-house-daily` | `solstein.worker_tasks.refresh_companies_house` | `hour=9, min=30` | 118 |
| `refresh-news-signals-hourly` | `solstein.worker_tasks.refresh_news_signals` | `min=0` | 123 |
| `refresh-github-every-6-hours` | `solstein.worker_tasks.refresh_github` | `hour="*/6"` | 128 |
| `refresh-yahoo-finance-every-6-hours` | `solstein.worker_tasks.refresh_yahoo_finance` | `hour="*/6", min=15` | 136 |
| `refresh-patents-daily` | `solstein.worker_tasks.refresh_patents` | `hour=10, min=0` | 141 |
| `refresh-news-every-2-hours` | `solstein.worker_tasks.refresh_news` | `hour="*/2", min=30` | 146 |
| `refresh-website-daily` | `solstein.worker_tasks.refresh_website` | `hour=11, min=0` | 151 |
| `refresh-linkedin-every-12-hours` | `solstein.worker_tasks.refresh_linkedin` | `hour="*/12", min=0` | 156 |
| `refresh-funding-every-6-hours` | `solstein.worker_tasks.refresh_funding` | `hour="*/6", min=45` | 161 |
| `refresh-global-market-every-6-hours` | `solstein.worker_tasks.refresh_global_market` | `hour="*/6", min=30` | 166 |
| `refresh-web-search-every-6-hours` | `solstein.worker_tasks.refresh_web_search` | `hour="*/6", min=0` | 171 |
| `refresh-all-sources-weekly` | `solstein.worker_tasks.refresh_all_sources` | `day_of_week=0, hour=2` | 180 |

Dynamic tasks from `settings.refresh_schedule` (line ~190) — NOT part of this test.

### Module Structure (`src/solstein/worker_tasks.py`)

`worker_tasks.py` is a real module at `src/solstein/worker_tasks.py` that re-exports from `solstein.worker.*` submodules:
- `refresh_sec_edgar` → `worker/refresh_tasks.py` via `create_refresh_task()` factory (line 193)
- `refresh_companies_house` → same factory (line 201)
- (all 12 refresh tasks defined at lines 192–286 of `refresh_tasks.py`)
- `refresh_all_sources` → `worker/orchestration.py:29` (`@shared_task(name="solstein.worker_tasks.refresh_all_sources")`)

All 12 refresh tasks use `create_refresh_task()` factory at `refresh_tasks.py:97–185`:
- Registers with `@shared_task(name=task_name, bind=True, max_retries=3)`
- Task name matches `solstein.worker_tasks.*` exactly

### Re-export chain:
```
celery_config.py beat_schedule["task"] = "solstein.worker_tasks.refresh_sec_edgar"
           ↓
worker_tasks.py (module) re-exports refresh_sec_edgar from worker.refresh_tasks
           ↓
worker/refresh_tasks.py: create_refresh_task("solstein.worker_tasks.refresh_sec_edgar", ...)
```

`celery_app.tasks` dict will contain all tasks once `worker_tasks` is imported (via `celery_app.conf.include = ["solstein.worker_tasks", ...]`).

---

## Problem Statement

There is no test that verifies all 13 beat_schedule task paths are importable and registered. A renamed connector class, a broken import in `worker_tasks.py`, or a typo in a task name string would silently break the entire Beat schedule — tasks stop running with no error at app startup. This is the worst kind of silent failure.

---

## Acceptance Criteria

- [ ] `tests/unit/test_celery_task_discovery.py` exists
- [ ] Test asserts exactly **13** tasks in `celery_app.conf.beat_schedule` (static entries only — dynamic `settings.refresh_schedule` excluded)
- [ ] For each of the 13 task paths: task is registered in `celery_app.tasks` after importing `solstein.worker_tasks`
- [ ] All 13 task functions have a `.delay` attribute (are proper Celery tasks)
- [ ] Test runs in < 500ms (no network, no broker, no DB)
- [ ] Test fails loudly if any task is unresolvable

---

## Tasks

- [ ] Create `tests/unit/test_celery_task_discovery.py`:
  ```python
  """STORY-359: verify all 13 beat-scheduled tasks are importable."""
  import importlib
  import pytest
  from solstein.celery_config import celery_app

  EXPECTED_TASKS = {
      "solstein.worker_tasks.refresh_sec_edgar",
      "solstein.worker_tasks.refresh_companies_house",
      "solstein.worker_tasks.refresh_news_signals",
      "solstein.worker_tasks.refresh_github",
      "solstein.worker_tasks.refresh_yahoo_finance",
      "solstein.worker_tasks.refresh_patents",
      "solstein.worker_tasks.refresh_news",
      "solstein.worker_tasks.refresh_website",
      "solstein.worker_tasks.refresh_linkedin",
      "solstein.worker_tasks.refresh_funding",
      "solstein.worker_tasks.refresh_global_market",
      "solstein.worker_tasks.refresh_web_search",
      "solstein.worker_tasks.refresh_all_sources",
  }

  def test_beat_schedule_has_exactly_13_static_tasks():
      # Exclude dynamic tasks added by settings.refresh_schedule at runtime
      static_tasks = {
          k: v for k, v in celery_app.conf.beat_schedule.items()
          if not k.startswith("refresh-")  # dynamic keys have different naming
          or v["task"] in EXPECTED_TASKS
      }
      beat_task_names = {e["task"] for e in celery_app.conf.beat_schedule.values()}
      assert EXPECTED_TASKS == beat_task_names & EXPECTED_TASKS, \
          f"Missing: {EXPECTED_TASKS - beat_task_names}"

  def test_all_beat_tasks_importable():
      import solstein.worker_tasks  # trigger registration
      for task_path in EXPECTED_TASKS:
          module_path, func_name = task_path.rsplit(".", 1)
          module = importlib.import_module(module_path)
          task_fn = getattr(module, func_name, None)
          assert task_fn is not None, f"Not found: {task_path}"
          assert hasattr(task_fn, "delay"), f"Not a Celery task: {task_path}"
  ```
- [ ] Add to CI fast-test gate

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/celery_config.py` | 109–184 | `beat_schedule` — 13 static entries |
| `src/solstein/worker_tasks.py` | 95–129 | Re-export module; all task functions here |
| `src/solstein/worker/refresh_tasks.py` | 97–286 | `create_refresh_task()` factory; 12 tasks |
| `src/solstein/worker/orchestration.py` | 29 | `refresh_all_sources` — the 13th task |
