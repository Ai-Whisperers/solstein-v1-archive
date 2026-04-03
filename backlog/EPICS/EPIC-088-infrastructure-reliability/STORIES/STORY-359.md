# STORY-359: Add Task Discovery Test — All Beat-Scheduled Tasks Are Importable

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P2 |
| **Size** | S (half day) |
| **Epic** | EPIC-088 Infrastructure Reliability |
| **Created** | 2026-04-03 |
| **Risk** | Low |

---

## Actual Codebase State (verified 2026-04-03)

`src/solstein/celery_config.py` defines **13 static Beat-scheduled tasks** (12 refresh sources + `refresh_all_sources` weekly). All task paths use the prefix `solstein.worker_tasks.*`. The module `src/solstein/worker_tasks.py` exists and re-exports all task functions from `solstein.worker.*` submodules — it is a valid import target.

Dynamic tasks may also be added from `settings.refresh_schedule` at runtime (line ~190 of `celery_config.py`) — the test only needs to cover static tasks.

---

## Problem Statement

`celery_config.py` defines 13 Beat-scheduled tasks (12 refresh sources + `refresh_all_sources`). There is no test that verifies all task function paths are importable and properly `@app.task`-decorated. A renamed module or missing decorator silently breaks the entire Beat schedule — tasks stop running with no error at startup.

## Acceptance Criteria

- [ ] A unit test reads the static `beat_schedule` dict from `celery_config.py` (all 13 entries)
- [ ] For each entry: imports the module path, resolves the function, asserts it is a registered Celery task
- [ ] Test runs in < 500ms (no network, no broker, no DB)
- [ ] Test fails if any scheduled task path is unresolvable
- [ ] Dynamic tasks added via `settings.refresh_schedule` are explicitly out of scope for this test

## Tasks

- [ ] Read `src/solstein/celery_config.py` and extract all `"task"` strings from `beat_schedule`
- [ ] Write `tests/unit/test_celery_task_discovery.py`
- [ ] For each task path: `importlib.import_module(module)`, `getattr(module, func_name)`, assert `isinstance(task, celery.Task)`
- [ ] Add to CI fast-test gate

## Test Skeleton

```python
# tests/unit/test_celery_task_discovery.py
import importlib
from solstein.celery_config import celery_app

def test_all_beat_tasks_are_importable():
    for name, entry in celery_app.conf.beat_schedule.items():
        task_path = entry["task"]
        module_path, func_name = task_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        task_fn = getattr(module, func_name, None)
        assert task_fn is not None, f"Task function not found: {task_path}"
        assert hasattr(task_fn, "delay"), f"Not a Celery task: {task_path}"
```
