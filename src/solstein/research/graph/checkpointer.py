"""LangGraph checkpoint store factory for the research pipeline.

STORY-079: Provides durable checkpoint storage so a crashed research graph
resumes from the last successful node instead of restarting from the beginning.

Backend selection:
    - Production / default: SqliteSaver — persists to a SQLite file at
      ``Settings.graph_checkpoint_db_path``. Survives process restart,
      deployment, and crash recovery (REQ-2).
    - Tests: MemorySaver — in-memory, no file I/O, safe for parallel tests.

Usage:
    from solstein.research.graph.checkpointer import build_checkpointer

    checkpointer = build_checkpointer(Path("data/checkpoints/research_graph.db"))
    graph = compile_research_graph(checkpointer=checkpointer)

    # Resume a crashed graph for run_id "abc-123":
    result = graph.invoke(
        None,  # No new input needed — resumes from checkpoint
        config={"configurable": {"thread_id": "abc-123"}},
    )
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from langgraph.checkpoint.memory import MemorySaver

try:
    from langgraph.checkpoint.sqlite import SqliteSaver as _SqliteSaver

    _SQLITE_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SqliteSaver = None  # type: ignore[assignment,misc]
    _SQLITE_AVAILABLE = False

__all__ = ["build_checkpointer", "build_memory_checkpointer"]


def build_checkpointer(db_path: Path) -> Any:
    """Build a durable SQLite-backed LangGraph checkpointer.

    Creates the parent directory if it does not exist. The SQLite file is
    created automatically on first write.

    Args:
        db_path: Absolute or relative path to the SQLite database file.
                 The parent directory is created if missing.

    Returns:
        A SqliteSaver instance configured with a synchronous SQLite connection.
        The connection is created with ``check_same_thread=False`` so it can be
        used from the async FastAPI request handlers that resume interrupted graphs.

    Raises:
        ImportError: If ``langgraph-checkpoint-sqlite`` is not installed.
        OSError: If the parent directory cannot be created.
    """
    if not _SQLITE_AVAILABLE or _SqliteSaver is None:
        raise ImportError(
            "langgraph-checkpoint-sqlite is required for durable checkpointing. "
            "Install it with: pip install langgraph-checkpoint-sqlite"
        )

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    return _SqliteSaver(conn)


def build_memory_checkpointer() -> MemorySaver:
    """Build an in-memory LangGraph checkpointer for tests and development.

    The in-memory checkpointer does not persist across process restarts.
    Use ``build_checkpointer()`` for production.

    Returns:
        A MemorySaver instance.
    """
    return MemorySaver()
