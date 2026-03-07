"""Logic fusion workflow node.

EPIC-022: Extracted from CoordinatorAgent for modularity.
"""

from datetime import datetime, timezone
from typing import Any

from ...domain.models import AggregatedFact
from .base import WorkflowNode


class LogicFusionNode(WorkflowNode):
    """Aggregate facts from agent results."""

    @property
    def name(self) -> str:
        return "logic_fusion"

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute logic fusion node.

        Args:
            state: Workflow state with agent_results

        Returns:
            Updated state with aggregated_facts
        """
        agent_results = state.get("agent_results", [])

        aggregated_facts = []
        for result in agent_results:
            for fact in result.extracted_facts:
                aggregated_facts.append(
                    AggregatedFact(
                        company_name=result.company_name,
                        field=fact.field,
                        value=fact.value,
                        unit=fact.unit,
                        confidence=fact.confidence,
                        sources=fact.sources,
                        extraction_method=fact.extraction_method,
                        extracted_at=datetime.now(timezone.utc),
                    )
                )

        self.logger.info(f"Aura | Stage: Logic Fusion | Aggregated {len(aggregated_facts)} facts")

        return {"aggregated_facts": aggregated_facts}
