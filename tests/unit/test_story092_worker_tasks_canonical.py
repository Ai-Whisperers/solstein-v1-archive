"""Tests for STORY-092: canonical worker_tasks module integrity.

Verifies that:
- worker_tasks_v2.py does not exist
- All 12 Beat-scheduled tasks are registered in the canonical module
- No duplicate @shared_task definitions for the same task name
- Module-level docstring lists all tasks
- Idempotency guard is wired (deduplicate with task_name_override)
- STORY-088/089/090 patterns are incorporated
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path

import solstein.worker_tasks as worker_tasks_module
from solstein.worker.idempotency import deduplicate as idempotency_deduplicate


class TestWorkerTasksV2Gone:
    """worker_tasks_v2.py must not exist (STORY-142 + STORY-092 together)."""

    def test_worker_tasks_v2_does_not_exist(self) -> None:
        """Acceptance criterion 1: worker_tasks_v2.py absent from codebase."""
        src = Path("src/solstein")
        v2_path = src / "worker_tasks_v2.py"
        assert not v2_path.exists(), "worker_tasks_v2.py still exists — must be deleted as part of STORY-092"

    def test_no_import_of_worker_tasks_v2_in_production_code(self) -> None:
        """No production source file should have an import statement for worker_tasks_v2."""
        src = Path("src/solstein")
        violations = []
        import_pattern = re.compile(r"^\s*(import|from)\s+\S*worker_tasks_v2", re.MULTILINE)
        for py_file in src.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            if import_pattern.search(content):
                violations.append(str(py_file))
        assert not violations, f"Production files still import worker_tasks_v2: {violations}"


class TestAllTwelveTasksRegistered:
    """All 12 Beat-scheduled tasks must be present in canonical module."""

    EXPECTED_TASKS = [
        "refresh_sec_edgar",
        "refresh_companies_house",
        "refresh_news_signals",
        "refresh_github",
        "refresh_yahoo_finance",
        "refresh_patents",
        "refresh_news",
        "refresh_website",
        "refresh_linkedin",
        "refresh_funding",
        "refresh_global_market",
        "refresh_web_search",
    ]

    def test_all_twelve_tasks_in_all_list(self) -> None:
        """Acceptance criterion: all 12 task names present in __all__."""
        for task_name in self.EXPECTED_TASKS:
            assert task_name in worker_tasks_module.__all__, f"Task '{task_name}' missing from worker_tasks.__all__"

    def test_all_twelve_tasks_importable(self) -> None:
        """Each task is accessible as an attribute of worker_tasks."""
        for task_name in self.EXPECTED_TASKS:
            assert hasattr(worker_tasks_module, task_name), f"Task '{task_name}' not accessible on worker_tasks module"


class TestNoDuplicateTaskDefinitions:
    """No two tasks may share the same Celery task name."""

    def test_no_duplicate_create_refresh_task_calls(self) -> None:
        """Each task name is passed exactly once to create_refresh_task()."""
        src = Path("src/solstein/worker/refresh_tasks.py").read_text(encoding="utf-8")
        # Match only the first argument in create_refresh_task("...") calls,
        # excluding docstring examples by requiring the match to be on a line
        # that starts a create_refresh_task call (not inside a docstring).
        names = re.findall(
            r'^refresh_\w+\s*=\s*create_refresh_task\(\s*"(solstein\.worker_tasks\.\w+)"',
            src,
            re.MULTILINE,
        )
        seen: set[str] = set()
        duplicates: list[str] = []
        for name in names:
            if name in seen:
                duplicates.append(name)
            seen.add(name)
        assert len(names) == 12, f"Expected 12 create_refresh_task calls, found {len(names)}: {names}"
        assert not duplicates, f"Duplicate task name registrations found: {duplicates}"


class TestModuleDocstring:
    """Module docstring must list all registered tasks (acceptance criterion)."""

    def test_worker_tasks_docstring_mentions_all_twelve_sources(self) -> None:
        """Docstring in worker_tasks.py names all 12 data sources."""
        src = Path("src/solstein/worker_tasks.py").read_text(encoding="utf-8")
        sources = [
            "refresh_sec_edgar",
            "refresh_companies_house",
            "refresh_news_signals",
            "refresh_github",
            "refresh_yahoo_finance",
            "refresh_patents",
            "refresh_news",
            "refresh_website",
            "refresh_linkedin",
            "refresh_funding",
            "refresh_global_market",
            "refresh_web_search",
        ]
        missing = [s for s in sources if s not in src]
        assert not missing, f"worker_tasks.py docstring missing task references: {missing}"

    def test_worker_tasks_docstring_mentions_story_092(self) -> None:
        """Docstring acknowledges STORY-092 (capstone marker)."""
        src = Path("src/solstein/worker_tasks.py").read_text(encoding="utf-8")
        assert "STORY-092" in src, "worker_tasks.py docstring must mention STORY-092"


class TestIdempotencyWired:
    """STORY-090 idempotency lock must be wired via create_refresh_task factory."""

    def test_deduplicate_imported_in_refresh_tasks(self) -> None:
        """refresh_tasks.py imports the deduplicate function."""
        src = Path("src/solstein/worker/refresh_tasks.py").read_text(encoding="utf-8")
        assert "from .idempotency import deduplicate" in src, (
            "refresh_tasks.py must import deduplicate from idempotency"
        )

    def test_deduplicate_called_with_task_name_override(self) -> None:
        """The factory applies deduplicate with task_name_override."""
        src = Path("src/solstein/worker/refresh_tasks.py").read_text(encoding="utf-8")
        assert "task_name_override=task_name" in src, (
            "create_refresh_task must pass task_name_override=task_name to deduplicate"
        )

    def test_task_name_override_parameter_exists(self) -> None:
        """deduplicate() accepts task_name_override parameter."""
        sig = inspect.signature(idempotency_deduplicate)
        assert "task_name_override" in sig.parameters, (
            "deduplicate() must accept task_name_override parameter for factory use"
        )


class TestEpic025PatternsIncorporated:
    """STORY-088/089/090 patterns must all be present in the canonical module."""

    def test_story088_dlq_wired_in_refresh_tasks(self) -> None:
        """DLQ (STORY-088) is invoked on MaxRetriesExceededError."""
        src = Path("src/solstein/worker/refresh_tasks.py").read_text(encoding="utf-8")
        assert "dead_letter_queue.record_failure" in src, (
            "refresh_tasks.py must call dead_letter_queue.record_failure on exhausted retries"
        )

    def test_story089_acks_late_in_celery_config(self) -> None:
        """task_acks_late=True (STORY-089) is configured in celery_config.py."""
        src = Path("src/solstein/celery_config.py").read_text(encoding="utf-8")
        assert "task_acks_late=True" in src, "celery_config.py must set task_acks_late=True (STORY-089)"
        assert "task_reject_on_worker_lost=True" in src, (
            "celery_config.py must set task_reject_on_worker_lost=True (STORY-089)"
        )

    def test_story090_idempotency_module_exists(self) -> None:
        """idempotency.py module exists (STORY-090)."""
        assert Path("src/solstein/worker/idempotency.py").exists(), (
            "src/solstein/worker/idempotency.py must exist (STORY-090)"
        )
