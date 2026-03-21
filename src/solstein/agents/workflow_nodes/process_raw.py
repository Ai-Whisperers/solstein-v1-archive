"""Process raw data workflow node.

EPIC-022: Extracted from CoordinatorAgent for modularity.
"""

from datetime import datetime, timezone
from typing import Any

from ...domain.models import RawDataSource
from .base import WorkflowNode


class ProcessRawNode(WorkflowNode):
    """Process raw data from agent results."""

    @property
    def name(self) -> str:
        return "process_raw"

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute process raw node.

        Args:
            state: Workflow state with agent_results

        Returns:
            Updated state with raw_data_records
        """
        agent_results = state.get("agent_results", [])

        raw_data_records = []
        for result in agent_results:
            for source in result.raw_sources:
                # source is already a RawDataSource; pass through directly,
                # preserving existing metadata and adding agent_name context.
                if isinstance(source, RawDataSource):
                    raw_data_records.append(source)
                else:
                    # Legacy path: source is a raw dict or legacy object
                    raw_data_records.append(
                        RawDataSource(
                            source_type=getattr(source, "source_type", "unknown"),
                            source_name=getattr(source, "source_name", str(source)),
                            raw_content=getattr(source, "raw_content", ""),
                            retrieval_timestamp=datetime.now(timezone.utc),
                        )
                    )

        self.logger.info(f"Aura | Stage: Processing | Created {len(raw_data_records)} raw data records")

        return {"raw_data_records": raw_data_records}
