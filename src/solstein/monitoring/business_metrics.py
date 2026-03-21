"""Business metrics collection and dashboard utilities.

EPIC-026 Story 2: Collects business metrics for dashboard display including:
- Company intelligence metrics
- Research pipeline metrics
- API usage metrics
- Export activity metrics
- LLM usage metrics
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.infrastructure.database_models import (
    CompanyRecord,
    ResearchRunRecord,
    ScoringRecord,
)


@dataclass
class CompanyMetrics:
    """Company intelligence metrics."""

    total: int = 0
    by_classification: dict[str, int] = field(default_factory=dict)
    by_tier: dict[str, int] = field(default_factory=dict)
    enrichment_success_rate: float = 0.0
    avg_data_quality: float = 0.0
    processed_per_hour: float = 0.0


@dataclass
class ResearchMetrics:
    """Research pipeline metrics."""

    runs_per_day: float = 0.0
    avg_duration_minutes: float = 0.0
    success_rate: float = 0.0
    failure_rate: float = 0.0
    stage_metrics: dict[str, dict[str, float]] = field(default_factory=dict)


@dataclass
class ExportMetrics:
    """Export activity metrics."""

    total_generated: int = 0
    by_format: dict[str, int] = field(default_factory=dict)
    success_rate: float = 0.0
    avg_export_time_seconds: float = 0.0


@dataclass
class LLMMetrics:
    """LLM usage metrics."""

    total_tokens: dict[str, int] = field(default_factory=dict)  # by provider
    total_cost_usd: float = 0.0
    by_model: dict[str, dict[str, Any]] = field(default_factory=dict)
    cache_hit_rate: float = 0.0
    provider_availability: dict[str, bool] = field(default_factory=dict)


@dataclass
class BusinessDashboard:
    """Complete business metrics dashboard."""

    timestamp: datetime = field(default_factory=datetime.utcnow)
    companies: CompanyMetrics = field(default_factory=CompanyMetrics)
    research: ResearchMetrics = field(default_factory=ResearchMetrics)
    exports: ExportMetrics = field(default_factory=ExportMetrics)
    llm: LLMMetrics = field(default_factory=LLMMetrics)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "companies": {
                "total": self.companies.total,
                "by_classification": self.companies.by_classification,
                "by_tier": self.companies.by_tier,
                "enrichment_success_rate": round(self.companies.enrichment_success_rate, 2),
                "avg_data_quality": round(self.companies.avg_data_quality, 2),
                "processed_per_hour": round(self.companies.processed_per_hour, 2),
            },
            "research": {
                "runs_per_day": round(self.research.runs_per_day, 2),
                "avg_duration_minutes": round(self.research.avg_duration_minutes, 2),
                "success_rate": round(self.research.success_rate, 2),
                "failure_rate": round(self.research.failure_rate, 2),
                "stage_metrics": self.research.stage_metrics,
            },
            "exports": {
                "total_generated": self.exports.total_generated,
                "by_format": self.exports.by_format,
                "success_rate": round(self.exports.success_rate, 2),
                "avg_export_time_seconds": round(self.exports.avg_export_time_seconds, 2),
            },
            "llm": {
                "total_tokens": self.llm.total_tokens,
                "total_cost_usd": round(self.llm.total_cost_usd, 2),
                "by_model": self.llm.by_model,
                "cache_hit_rate": round(self.llm.cache_hit_rate, 2),
                "provider_availability": self.llm.provider_availability,
            },
        }


class BusinessMetricsCollector:
    """Collector for business metrics."""

    def __init__(self, session: AsyncSession):
        """Initialize collector.

        Args:
            session: Database session.
        """
        self.session = session

    async def collect_company_metrics(self) -> CompanyMetrics:
        """Collect company intelligence metrics.

        Returns:
            CompanyMetrics with current counts and rates.
        """
        # Total count
        result = await self.session.execute(select(func.count()).select_from(CompanyRecord))
        total = result.scalar() or 0

        # By classification
        result = await self.session.execute(
            select(CompanyRecord.classification, func.count()).group_by(CompanyRecord.classification)
        )
        by_classification = {row[0] or "unknown": row[1] for row in result.fetchall()}

        # By tier
        result = await self.session.execute(select(CompanyRecord.tier, func.count()).group_by(CompanyRecord.tier))
        by_tier = {row[0] or "unknown": row[1] for row in result.fetchall()}

        # Average data quality score
        result = await self.session.execute(select(func.avg(CompanyRecord.ai_score)))
        avg_quality = result.scalar() or 0.0

        # Companies processed in last hour (enrichment_updated_at)
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        result = await self.session.execute(
            select(func.count()).select_from(CompanyRecord).where(CompanyRecord.last_updated >= one_hour_ago)
        )
        processed_last_hour = result.scalar() or 0

        return CompanyMetrics(
            total=total,
            by_classification=by_classification,
            by_tier=by_tier,
            enrichment_success_rate=0.0,  # Would need enrichment log table
            avg_data_quality=float(avg_quality),
            processed_per_hour=processed_last_hour,
        )

    async def collect_research_metrics(self) -> ResearchMetrics:
        """Collect research pipeline metrics.

        Returns:
            ResearchMetrics with pipeline statistics.
        """
        # Runs per day (last 24 hours)
        one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        result = await self.session.execute(
            select(func.count()).select_from(ResearchRunRecord).where(ResearchRunRecord.started_at >= one_day_ago)
        )
        runs_last_day = result.scalar() or 0

        # Success/failure rates
        result = await self.session.execute(
            select(ResearchRunRecord.status, func.count())
            .where(ResearchRunRecord.started_at >= one_day_ago)
            .group_by(ResearchRunRecord.status)
        )
        status_counts = {row[0]: row[1] for row in result.fetchall()}
        total = sum(status_counts.values()) or 1

        success_rate = status_counts.get("completed", 0) / total * 100
        failure_rate = status_counts.get("failed", 0) / total * 100

        # Average duration
        result = await self.session.execute(
            select(func.avg(func.extract("epoch", ResearchRunRecord.completed_at - ResearchRunRecord.started_at)))
            .where(ResearchRunRecord.completed_at.isnot(None))
            .where(ResearchRunRecord.started_at >= one_day_ago)
        )
        avg_duration_seconds = result.scalar() or 0
        avg_duration_minutes = avg_duration_seconds / 60

        return ResearchMetrics(
            runs_per_day=runs_last_day,
            avg_duration_minutes=float(avg_duration_minutes),
            success_rate=success_rate,
            failure_rate=failure_rate,
            stage_metrics={},  # Would need stage-level tracking
        )

    async def collect_export_metrics(self) -> ExportMetrics:
        """Collect export activity metrics.

        Returns:
            ExportMetrics with export statistics.
        """
        # This would need an export log table
        # Returning placeholder for now
        return ExportMetrics(
            total_generated=0,
            by_format={},
            success_rate=0.0,
            avg_export_time_seconds=0.0,
        )

    async def collect_llm_metrics(self) -> LLMMetrics:
        """Collect LLM usage metrics.

        Returns:
            LLMMetrics with usage statistics.
        """
        # This would need LLM usage tracking table
        # Returning placeholder for now
        return LLMMetrics(
            total_tokens={},
            total_cost_usd=0.0,
            by_model={},
            cache_hit_rate=0.0,
            provider_availability={},
        )

    async def collect_all(self) -> BusinessDashboard:
        """Collect all business metrics.

        Returns:
            BusinessDashboard with all metrics.
        """
        return BusinessDashboard(
            companies=await self.collect_company_metrics(),
            research=await self.collect_research_metrics(),
            exports=await self.collect_export_metrics(),
            llm=await self.collect_llm_metrics(),
        )


# Grafana dashboard as code
GRAFANA_DASHBOARD_TEMPLATE = {
    "dashboard": {
        "title": "Solstein Business Metrics",
        "tags": ["business", "solstein"],
        "timezone": "utc",
        "refresh": "5s",
        "panels": [
            {
                "id": 1,
                "title": "Total Companies",
                "type": "stat",
                "targets": [
                    {
                        "expr": "companies_total",
                        "legendFormat": "{{classification}} - {{tier}}",
                    }
                ],
                "fieldConfig": {
                    "defaults": {"unit": "short"},
                },
            },
            {
                "id": 2,
                "title": "Companies Processed (1h)",
                "type": "stat",
                "targets": [
                    {
                        "expr": "companies_processed_per_hour",
                    }
                ],
            },
            {
                "id": 3,
                "title": "Research Runs (24h)",
                "type": "stat",
                "targets": [
                    {
                        "expr": "research_runs_total",
                    }
                ],
            },
            {
                "id": 4,
                "title": "Research Success Rate",
                "type": "gauge",
                "targets": [
                    {
                        "expr": "research_success_rate",
                    }
                ],
                "fieldConfig": {
                    "defaults": {"unit": "percent", "min": 0, "max": 100},
                },
            },
            {
                "id": 5,
                "title": "LLM Daily Cost",
                "type": "stat",
                "targets": [
                    {
                        "expr": "increase(llm_cost_dollars_total[24h])",
                        "legendFormat": "{{provider}} - {{model}}",
                    }
                ],
                "fieldConfig": {
                    "defaults": {"unit": "currencyUSD"},
                },
            },
            {
                "id": 6,
                "title": "LLM Cache Hit Rate",
                "type": "stat",
                "targets": [
                    {
                        "expr": "llm_cache_hit_rate",
                    }
                ],
                "fieldConfig": {
                    "defaults": {"unit": "percent", "min": 0, "max": 100},
                },
            },
            {
                "id": 7,
                "title": "Reports Generated",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(reports_generated_total[5m])",
                        "legendFormat": "{{format}}",
                    }
                ],
            },
            {
                "id": 8,
                "title": "Data Quality Score",
                "type": "heatmap",
                "targets": [
                    {
                        "expr": "data_quality_score_bucket",
                    }
                ],
            },
        ],
    }
}
