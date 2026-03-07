"""Base class for workflow nodes.

EPIC-022: Extracted from CoordinatorAgent for modularity.
"""

from abc import ABC, abstractmethod
from typing import Any

from loguru import logger


class WorkflowNode(ABC):
    """Base class for LangGraph workflow nodes.

    Each node in the coordinator workflow is implemented as a separate
    class for modularity and testability.
    """

    def __init__(self):
        self.logger = logger.bind(node=self.name)

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this workflow node."""
        pass

    @abstractmethod
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute the workflow node.

        Args:
            state: Current workflow state

        Returns:
            Updated state dictionary
        """
        pass
