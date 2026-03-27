"""Due Diligence Engine — orchestrates the full DD workflow (STORY-147).

The engine coordinates red-flag detection, competitive positioning,
checklist generation, and investment memo assembly into a single
:class:`DDReport`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from .checklist import build_checklist
from .models import (
    CompetitivePosition,
    DDReport,
    InvestmentMemo,
    RedFlagSeverity,
)
from .red_flags import detect_red_flags

if TYPE_CHECKING:
    from collections.abc import Sequence

    from solstein.domain.models import Company


class DueDiligenceEngine:
    """Orchestrates AI-readiness-aware due diligence analysis.

    Usage::

        engine = DueDiligenceEngine()
        report = engine.run(target=company, peers=[peer1, peer2])
    """

    def run(
        self,
        target: Company,
        peers: Sequence[Company] | None = None,
    ) -> DDReport:
        """Execute a full due diligence assessment.

        Args:
            target: The company being evaluated.
            peers: Optional peer companies for competitive positioning.

        Returns:
            Assembled DDReport with all components.
        """
        logger.info("[DD] Starting due diligence for {}", target.name)

        # 1. Red flag scan
        red_flags = detect_red_flags(target)
        logger.info("[DD] Detected {} red flags for {}", len(red_flags), target.name)

        # 2. Competitive positioning
        competitive = self._position_against_peers(target, peers or [])

        # 3. Checklist
        checklist = build_checklist(target)
        auto_count = sum(1 for c in checklist if c.auto_assessed)
        logger.info("[DD] Checklist: {}/{} items auto-assessed", auto_count, len(checklist))

        # 4. Investment memo
        memo = self._build_memo(target, red_flags, competitive)

        # 5. Assess data quality
        quality = self._assess_quality(target, checklist)

        report = DDReport(
            target_name=target.name,
            red_flags=red_flags,
            competitive_position=competitive,
            checklist=checklist,
            investment_memo=memo,
            data_sources_used=self._identify_sources(target),
            assessment_quality=quality,
        )
        logger.info("[DD] Report complete for {} (quality: {})", target.name, quality)
        return report

    # -- competitive positioning --------------------------------------------

    @staticmethod
    def _position_against_peers(
        target: Company,
        peers: Sequence[Company],
    ) -> CompetitivePosition | None:
        """Rank target against peers on AI score."""
        if not peers:
            return None

        target_score = getattr(target, "ai_score", None)
        scored: list[tuple[str, float]] = []

        if target_score is not None:
            scored.append((target.name, target_score))

        for p in peers:
            p_score = getattr(p, "ai_score", None)
            if p_score is not None:
                scored.append((p.name, p_score))

        if len(scored) < 2:
            return None

        # Sort descending by score
        scored.sort(key=lambda x: x[1], reverse=True)
        target_rank = next(
            (i + 1 for i, (name, _) in enumerate(scored) if name == target.name),
            len(scored),
        )
        percentile = (1.0 - (target_rank - 1) / max(1, len(scored) - 1)) * 100

        # Positioning label
        if percentile >= 80:
            positioning = "leader"
        elif percentile >= 60:
            positioning = "above_average"
        elif percentile >= 40:
            positioning = "average"
        elif percentile >= 20:
            positioning = "below_average"
        else:
            positioning = "laggard"

        peer_avg = sum(s for _, s in scored if _ != target.name) / max(1, len(scored) - 1)

        return CompetitivePosition(
            target_name=target.name,
            peer_count=len(peers),
            target_ai_score=target_score,
            peer_avg_ai_score=round(peer_avg, 2),
            target_rank=target_rank,
            percentile=round(percentile, 1),
            positioning=positioning,
            peer_scores=[(n, s) for n, s in scored if n != target.name],
        )

    # -- investment memo ----------------------------------------------------

    @staticmethod
    def _build_memo(
        target: Company,
        red_flags: list,
        competitive: CompetitivePosition | None,
    ) -> InvestmentMemo:
        """Assemble a structured investment memo from DD findings."""
        critical = [f for f in red_flags if f.severity == RedFlagSeverity.CRITICAL]
        high = [f for f in red_flags if f.severity == RedFlagSeverity.HIGH]

        # Executive summary
        ai_maturity = str(getattr(target, "ai_maturity", "unknown"))
        ai_score = getattr(target, "ai_score", None)
        score_text = f"{ai_score}/10" if ai_score is not None else "N/A"

        exec_summary = (
            f"{target.name} is an energy software company "
            f"with AI maturity '{ai_maturity}' (score: {score_text}). "
        )
        if critical:
            exec_summary += (
                f"CRITICAL: {len(critical)} critical red flag(s) require immediate attention. "
            )
        if high:
            exec_summary += f"{len(high)} high-severity risk(s) identified. "

        # AI readiness section
        ai_summary = f"AI maturity: {ai_maturity}. AI score: {score_text}. "
        if competitive:
            ai_summary += (
                f"Ranked #{competitive.target_rank} of {competitive.peer_count + 1} "
                f"peers ({competitive.positioning}). "
            )

        # Recommendation
        if critical:
            recommendation = (
                "PROCEED WITH CAUTION: Critical red flags must be resolved "
                "before investment commitment."
            )
        elif len(high) >= 2:
            recommendation = (
                "CONDITIONAL PROCEED: Multiple high-severity risks require "
                "mitigation plan as condition of investment."
            )
        elif high:
            recommendation = (
                "PROCEED: One high-severity risk identified — include in "
                "100-day plan."
            )
        else:
            recommendation = "PROCEED: No critical risks identified."

        return InvestmentMemo(
            target_name=target.name,
            executive_summary=exec_summary,
            ai_readiness_summary=ai_summary,
            ai_readiness_score=ai_score,
            ai_readiness_tier=ai_maturity,
            red_flag_count=len(red_flags),
            critical_flags=[f.title for f in critical],
            competitive_summary=(
                f"Positioned as '{competitive.positioning}' among peers"
                if competitive else "No peer comparison available"
            ),
            recommendation=recommendation,
        )

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _identify_sources(company: Company) -> list[str]:
        """List data sources used for this company."""
        sources: list[str] = []
        if company.revenue is not None:
            sources.append("revenue_data")
        if getattr(company, "ai_score", None) is not None:
            sources.append("ai_scoring")
        if getattr(company, "tech_stack", []):
            sources.append("tech_stack_analysis")
        if company.growth_rate is not None:
            sources.append("growth_metrics")
        if getattr(company, "funding_raised", None) or getattr(company, "funding", None):
            sources.append("funding_data")
        return sources

    @staticmethod
    def _assess_quality(
        target: Company,
        checklist: list,
    ) -> str:
        """Determine assessment quality based on data availability."""
        auto_count = sum(1 for c in checklist if c.auto_assessed)
        total = len(checklist)
        if total == 0:
            return "limited"
        ratio = auto_count / total
        if ratio >= 0.5:
            return "comprehensive"
        if ratio >= 0.25:
            return "standard"
        return "limited"
