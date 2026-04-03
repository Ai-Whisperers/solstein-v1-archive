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

## Problem Statement

`celery_config.py` defines 12 Beat-scheduled tasks. There is no test that verifies all 12 task function paths are importable and properly `@app.task`-decorated. A renamed module or missing decorator silently breaks the entire Beat schedule — tasks stop running with no error at startup.

## Acceptance Criteria

- [ ] A unit test reads the `beat_schedule` dict from `celery_config.py`
- [ ] For each entry: imports the module path, resolves the function, asserts it is a registered Celery task
- [ ] Test runs in < 500ms (no network, no broker, no DB)
- [ ] Test fails if any scheduled task path is unresolvable

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
