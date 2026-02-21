"""Base class for all data gathering agents.

Provides common interface, error handling, and data model support.
"""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from ..domain.models import AggregatedFact, RawDataSource, DataSourceType


class AgentTaskResult(BaseModel):
    """Result returned by a specialist agent."""

    agent_name: str
    source_type: DataSourceType
    success: bool
    raw_sources: list[RawDataSource] = Field(default_factory=list)
    extracted_facts: list[AggregatedFact] = Field(default_factory=list)
    execution_time_seconds: float = 0.0
    error_message: str | None = None
    coverage_gaps: list[str] = Field(default_factory=list)


class BaseDataGatheringAgent(ABC):
    """Base class for all data gathering agents.

    Each specialist agent (GitHub, Web Search, etc.) inherits from this
    and implements the gather() method to collect data from its source.
    """

    def __init__(self, agent_name: str, source_type: DataSourceType):
        """Initialize agent.

        Args:
            agent_name: Human-readable name (e.g., "GitHubAgent", "WebSearchAgent")
            source_type: Which DataSourceType this agent handles
        """
        self.agent_name = agent_name
        self.source_type = source_type
        self.logger = logger.bind(agent=agent_name)

    @abstractmethod
    async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
        """Gather data about a company from this agent's source.

        Must be implemented by subclasses.

        Args:
            company_name: Name of company to research
            context: Additional context (market, industry, known_info, etc.)

        Returns:
            AgentTaskResult with raw sources and extracted facts
        """
        pass

    def _create_raw_source(
        self,
        raw_content: str | dict,
        source_name: str,
        url: str | None = None,
        publication_date: datetime | None = None,
        confidence: float = 0.8,
        relevance_score: float = 0.8,
        metadata: dict | None = None,
        extraction_method: str | None = None,
    ) -> RawDataSource:
        """Create a RawDataSource record."""
        return RawDataSource(
            source_type=self.source_type,
            source_name=source_name,
            raw_content=raw_content,
            url=url,
            retrieval_timestamp=datetime.now(UTC),
            publication_date=publication_date,
            confidence=confidence,
            relevance_score=relevance_score,
            metadata=metadata or {},
            extraction_method=extraction_method,
        )

    def _create_fact(
        self,
        fact_type: str,
        value: Any,
        confidence: float = 0.8,
        year: int | None = None,
        sources_used: list[str] | None = None,
        source_credibility_scores: dict[str, float] | None = None,
        reasoning: str | None = None,
    ) -> AggregatedFact:
        """Create an AggregatedFact record."""
        return AggregatedFact(
            fact_type=fact_type,
            value=value,
            confidence=confidence,
            year=year,
            sources_used=sources_used or [],
            source_credibility_scores=source_credibility_scores or {},
            verification_notes=reasoning,
        )

    def log_info(self, message: str, **kwargs) -> None:
        """Log info message with agent context."""
        self.logger.info(message, **kwargs)

    def log_warning(self, message: str, **kwargs) -> None:
        """Log warning message with agent context."""
        self.logger.warning(message, **kwargs)

    def log_error(self, message: str, **kwargs) -> None:
        """Log error message with agent context."""
        self.logger.error(message, **kwargs)
