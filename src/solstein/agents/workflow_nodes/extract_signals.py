"""Extract signals workflow node.

EPIC-022: Extracted from CoordinatorAgent for modularity.
"""

from datetime import datetime, timezone
from typing import Any

from ...analytics.signals.base import SignalCategory
from ...domain.models import SignalExtraction
from .base import WorkflowNode


class ExtractSignalsNode(WorkflowNode):
    """Extract business signals from aggregated facts."""

    @property
    def name(self) -> str:
        return "extract_signals"

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute extract signals node.

        Args:
            state: Workflow state with aggregated_facts

        Returns:
            Updated state with extracted_signals
        """
        aggregated_facts = state.get("aggregated_facts", [])

        extracted_signals = []
        for fact in aggregated_facts:
            signal = self._fact_to_signal(fact)
            if signal:
                extracted_signals.append(signal)

        self.logger.info(f"Aura | Stage: Signal Extraction | Extracted {len(extracted_signals)} signals")

        return {"extracted_signals": extracted_signals}

    def _fact_to_signal(self, fact: Any) -> SignalExtraction | None:
        """Convert aggregated fact to business signal.

        Args:
            fact: AggregatedFact object

        Returns:
            SignalExtraction or None
        """
        # Map fact fields to signal categories
        category_map = {
            "revenue": SignalCategory.FINANCIAL,
            "growth_rate": SignalCategory.GROWTH,
            "employees": SignalCategory.HIRING,
            "funding": SignalCategory.FINANCIAL,
            "valuation": SignalCategory.FINANCIAL,
            "ai_maturity": SignalCategory.TECHNICAL,
            "saas_maturity": SignalCategory.TECHNICAL,
        }

        category = category_map.get(fact.field, SignalCategory.OPERATIONAL)

        return SignalExtraction(
            company_name=fact.company_name,
            signal_name=fact.field,
            signal_category=category,
            signal_value=str(fact.value),
            confidence=fact.confidence,
            evidence_sources=fact.sources,
            extracted_at=datetime.now(timezone.utc),
        )
