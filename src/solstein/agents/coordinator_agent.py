"""Coordinator agent that orchestrates specialist agents.

Runs multiple specialist agents in parallel, aggregates results,
detects contradictions, scores confidence, and prepares signals
for the main scoring engine.
"""

import asyncio
from datetime import UTC, datetime
from typing import Any

from loguru import logger

from ..api.services.drill_down_service import get_drill_down_service
from ..domain.models import (
    AggregatedDataRecord,
    AggregatedFact,
    CompanyAnalysisAuditTrail,
    DataSourceType,
    RawDataRecord,
    SignalExtraction,
    SignalExtractionRecord,
)
from .base_agent import AgentTaskResult
from .companies_house_agent import CompaniesHouseAgent
from .github_agent import GitHubAgent
from .web_search_agent import WebSearchAgent


class CoordinatorAgent:
    """Coordinates specialist agents and aggregates results."""

    def __init__(self):
        """Initialize coordinator agent."""
        self.logger = logger.bind(agent="CoordinatorAgent")
        self.github_agent = GitHubAgent()
        self.web_search_agent = WebSearchAgent()
        self.companies_house_agent = CompaniesHouseAgent()

    async def analyze_company(
        self,
        company_name: str,
        gathering_batch_id: str,
        context: dict,
        enabled_sources: list[DataSourceType] | None = None,
    ) -> CompanyAnalysisAuditTrail:
        """Analyze a single company using all enabled specialist agents."""
        start_time = datetime.now(UTC)
        company_id = company_name.lower().replace(" ", "-")

        if enabled_sources is None:
            enabled_sources = [
                DataSourceType.GITHUB,
                DataSourceType.NEWS,
                DataSourceType.COMPANY_FILINGS,
            ]

        # Use contextualize to bind metadata to all logs in this block
        with logger.contextualize(company_id=company_id, batch_id=gathering_batch_id):
            self.logger.info(
                f"Aura | Entering Analysis Phase | Company: {company_name}"
            )

            audit_trail = CompanyAnalysisAuditTrail(
                company_id=company_id,
                gathering_batch_id=gathering_batch_id,
                company_name=company_name,
                analysis_started_at=start_time,
            )

            agent_tasks = []
            if DataSourceType.GITHUB in enabled_sources:
                agent_tasks.append(self.github_agent.gather(company_name, context))
            if DataSourceType.NEWS in enabled_sources:
                agent_tasks.append(self.web_search_agent.gather(company_name, context))
            if DataSourceType.COMPANY_FILINGS in enabled_sources:
                agent_tasks.append(
                    self.companies_house_agent.gather(company_name, context)
                )

            self.logger.info(
                f"Aura | Stage: Gathering | Spawning {len(agent_tasks)} specialist agents"
            )
            agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)

            for result in agent_results:
                if isinstance(result, Exception):
                    self.logger.warning(f"Aura | Agent error: {result}")
                    audit_trail.errors.append(str(result))
                    continue

                if not isinstance(result, AgentTaskResult):
                    continue

                self.logger.info(
                    f"Aura | {result.agent_name}: {len(result.raw_sources)} sources, "
                    f"{len(result.extracted_facts)} facts"
                )

            self.logger.info("Aura | Stage: Internal Processing | Creating raw records")
            raw_records = self._create_raw_data_records(
                agent_results, company_name, gathering_batch_id
            )
            audit_trail.raw_data = raw_records

            self.logger.info("Aura | Stage: Logic Fusion | Aggregating facts")
            aggregated = self._aggregate_facts(raw_records)
            audit_trail.aggregated_facts = aggregated

            self.logger.info(
                "Aura | Stage: Signal Extraction | Parsing business signals"
            )
            signals = self._extract_signals(aggregated)
            audit_trail.extracted_signals = signals

            audit_trail.analysis_completed_at = datetime.now(UTC)
            audit_trail.analysis_duration_seconds = (
                audit_trail.analysis_completed_at - start_time
            ).total_seconds()

            audit_trail.data_completeness = self._calculate_completeness(aggregated)
            audit_trail.confidence_level = self._determine_confidence_level(aggregated)

            self.logger.info(
                f"Aura | Analysis Sequence Finalized | "
                f"Facts: {len(aggregated.facts)} | "
                f"Completeness: {audit_trail.data_completeness:.0%} | "
                f"Duration: {audit_trail.analysis_duration_seconds:.1f}s"
            )

            self.logger.info("Aura | Transmuting to Persistence Layer")
            drill_down_service = get_drill_down_service()
            await drill_down_service.store_audit_trail(audit_trail)

            return audit_trail

    def _create_raw_data_records(
        self,
        agent_results: list,
        company_name: str,
        batch_id: str,
    ) -> RawDataRecord:
        """Create raw data record from agent results."""
        record = RawDataRecord(
            company_id=company_name.lower().replace(" ", "-"),
            gathering_batch_id=batch_id,
        )

        for result in agent_results:
            if isinstance(result, AgentTaskResult):
                record.sources.extend(result.raw_sources)
                record.total_sources_found += len(result.raw_sources)

                # Store extracted facts in source metadata for aggregation
                for fact in result.extracted_facts:
                    for source in result.raw_sources:
                        if "facts" not in source.metadata:
                            source.metadata["facts"] = []
                        source.metadata["facts"].append(
                            {
                                "type": fact.fact_type,
                                "value": fact.value,
                                "confidence": fact.confidence,
                            }
                        )

        return record

    def _aggregate_facts(self, raw_record: RawDataRecord) -> AggregatedDataRecord:
        """Aggregate facts from raw sources with confidence scoring."""
        aggregated = AggregatedDataRecord(
            company_id=raw_record.company_id,
            gathering_batch_id=raw_record.gathering_batch_id,
        )

        fact_map: dict[str, list[Any]] = {}

        for source in raw_record.sources:
            source_credibility = self._get_source_credibility(source.source_type)

            if source.metadata and "facts" in source.metadata:
                for fact in source.metadata["facts"]:
                    key = f"{fact.get('type')}_{fact.get('value')}"
                    if key not in fact_map:
                        fact_map[key] = []
                    fact_map[key].append(
                        {
                            "source": source.source_name,
                            "credibility": source_credibility,
                            "confidence": source.confidence,
                        }
                    )

        for fact_key, sources_found in fact_map.items():
            fact_type, fact_value = fact_key.rsplit("_", 1)

            source_agreement = len(sources_found) / max(1, len(raw_record.sources) / 3)
            source_agreement = min(1.0, source_agreement)

            avg_credibility = sum(s["credibility"] for s in sources_found) / len(
                sources_found
            )

            confidence = source_agreement * 0.5 + avg_credibility * 0.5

            fact = AggregatedFact(
                fact_type=fact_type,
                value=fact_value,
                confidence=confidence,
                sources_used=[s["source"] for s in sources_found],
                source_agreement_percentage=source_agreement,
            )
            aggregated.facts.append(fact)

        aggregated.update_quality_metrics()
        return aggregated

    def _extract_signals(
        self, aggregated: AggregatedDataRecord
    ) -> SignalExtractionRecord:
        """Extract business signals from aggregated facts."""
        signals = SignalExtractionRecord(
            company_id=aggregated.company_id,
            gathering_batch_id=aggregated.gathering_batch_id,
        )

        tech_stack_facts = [f for f in aggregated.facts if f.fact_type == "tech_stack"]
        if tech_stack_facts:
            signals.signals.append(
                SignalExtraction(
                    signal_name="tech_stack",
                    signal_value=tech_stack_facts[0].value,
                    signal_confidence=tech_stack_facts[0].confidence,
                    source_facts=["tech_stack"],
                    calculation_method="direct_extraction",
                )
            )

        velocity_facts = [f for f in aggregated.facts if "velocity" in f.fact_type]
        if velocity_facts:
            signals.signals.append(
                SignalExtraction(
                    signal_name="engineering_velocity",
                    signal_value=velocity_facts[0].value,
                    signal_confidence=velocity_facts[0].confidence,
                    source_facts=[f.fact_type for f in velocity_facts],
                    calculation_method="aggregation",
                )
            )

        contributor_facts = [
            f for f in aggregated.facts if "contributor" in f.fact_type
        ]
        if contributor_facts:
            signals.signals.append(
                SignalExtraction(
                    signal_name="team_size_proxy",
                    signal_value=contributor_facts[0].value,
                    signal_confidence=contributor_facts[0].confidence,
                    source_facts=[f.fact_type for f in contributor_facts],
                    calculation_method="direct_extraction",
                )
            )

        return signals

    def _get_source_credibility(self, source_type: DataSourceType) -> float:
        """Get credibility score for a source type."""
        credibility_map = {
            DataSourceType.COMPANY_FILINGS: 0.99,
            DataSourceType.GITHUB: 0.95,
            DataSourceType.NEWS: 0.75,
            DataSourceType.CRUNCHBASE: 0.85,
            DataSourceType.LINKEDIN: 0.82,
            DataSourceType.PATENTS: 0.88,
            DataSourceType.WEBSITE: 0.70,
            DataSourceType.PRESS_RELEASE: 0.80,
        }
        return credibility_map.get(source_type, 0.70)

    def _calculate_completeness(self, aggregated: AggregatedDataRecord) -> float:
        """Calculate data completeness percentage."""
        if not aggregated.facts:
            return 0.0

        desired_facts = {
            "tech_stack",
            "engineering_velocity",
            "contributor_count",
            "company_status",
            "funding_news_signal",
        }

        found_facts = set(f.fact_type for f in aggregated.facts)
        overlap = len(found_facts & desired_facts)

        return overlap / len(desired_facts)

    def _determine_confidence_level(self, aggregated: AggregatedDataRecord) -> str:
        """Determine overall confidence level."""
        if not aggregated.facts:
            return "unknown"

        avg_confidence = aggregated.average_confidence

        if avg_confidence >= 0.90:
            return "very_high"
        elif avg_confidence >= 0.75:
            return "high"
        elif avg_confidence >= 0.60:
            return "medium"
        else:
            return "low"
