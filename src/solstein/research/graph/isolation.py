"""Node error isolation decorator for the LangGraph research pipeline.

STORY-077: Extracted into its own module to avoid circular imports between
topology.py (which builds the graph) and executor.py (which compiles it).

Both topology.py and executor.py import from this module without creating
a dependency cycle.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any

from loguru import logger

from .state import ResearchState


def with_error_isolation(node_name: str) -> Callable:
    """Decorator that wraps a LangGraph node function with error isolation.

    When the wrapped node raises an exception:
    - The error is logged at ERROR level with full context
    - The error is recorded in the state's `data_collection_errors` list
    - The node returns a partial state update (no crash, graph continues)
    - The `completed_nodes` list is NOT updated (node did not complete)

    Independent nodes that run after the failed node continue normally.
    The `conflict_resolution` node handles missing `raw_*_facts` entries
    by treating them as empty collections.

    Args:
        node_name: The human-readable node name for error messages.

    Returns:
        Decorator function.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(state: ResearchState) -> dict[str, Any]:
            try:
                return func(state)
            except Exception as exc:
                error_msg = f"[{node_name}] Node failed: {type(exc).__name__}: {exc}"
                logger.error(error_msg)
                # Return minimal state update so graph continues
                return {
                    "data_collection_errors": [error_msg],
                    "pipeline_errors": [],
                    # completed_nodes intentionally NOT set — node did not succeed
                }

        return wrapper

    return decorator
