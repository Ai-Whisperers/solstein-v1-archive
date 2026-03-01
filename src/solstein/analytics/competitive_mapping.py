"""Competitive mapping module (EPIC-042).

Builds a competitive landscape map from a universe of companies,
identifying clusters, positioning gaps, and head-to-head rivalries.

Usage::

    from solstein.analytics.competitive_mapping import CompetitiveMapper

    mapper = CompetitiveMapper()
    landscape = mapper.map(companies, reference_company=stripe)
    print(landscape.direct_competitors)
    print(landscape.positioning_gap)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Sequence

from solstein.domain.models import Company


class CompetitiveRelation(StrEnum):
    DIRECT = "direct"  # Same market, similar size, overlapping product
    ADJACENT = "adjacent"  # Same sector, different product focus
    ASPIRATIONAL = "aspirational"  # Similar profile but larger/more mature
    DISTANT = "distant"  # Minimal overlap


@dataclass
class CompetitorEntry:
    """A single competitor in the landscape map.

    Attributes:
        company: The competitor Company object.
        relation: Nature of competition with the reference company.
        overlap_score: Similarity score 0–1 (higher = more direct competition).
        threat_rationale: Why this company is (or is not) a threat.
    """

    company: Company
    relation: CompetitiveRelation
    overlap_score: float
    threat_rationale: str


@dataclass
class CompetitiveLandscape:
    """Output of ``CompetitiveMapper.map()``.

    Attributes:
        reference: The reference company being mapped against.
        direct_competitors: Companies classified as DIRECT competitors.
        adjacent_players: Companies classified as ADJACENT.
        aspirational_peers: Larger companies the reference could evolve toward.
        positioning_gap: Identified white-space opportunities in the landscape.
        differentiation_factors: Dimensions where the reference stands out.
    """

    reference: Company
    direct_competitors: list[CompetitorEntry] = field(default_factory=list)
    adjacent_players: list[CompetitorEntry] = field(default_factory=list)
    aspirational_peers: list[CompetitorEntry] = field(default_factory=list)
    positioning_gap: str = ""
    differentiation_factors: list[str] = field(default_factory=list)


class CompetitiveMapper:
    """Maps a company's competitive position within a universe of peers."""

    def map(
        self,
        universe: Sequence[Company],
        reference_company: Company,
        top_n: int = 10,
    ) -> CompetitiveLandscape:
        """Build a competitive landscape map.

        Args:
            universe: All companies to consider as potential competitors.
            reference_company: The target company being analysed.
            top_n: Maximum number of entries per relation tier.

        Returns:
            CompetitiveLandscape with classified competitors and insights.
        """
        landscape = CompetitiveLandscape(reference=reference_company)

        ref_industry = getattr(reference_company, "industry", "") or ""
        ref_score: float = getattr(reference_company, "composite_score", 5.0) or 5.0
        ref_revenue: float = self._revenue(reference_company)

        entries: list[CompetitorEntry] = []
        for company in universe:
            if company.name == reference_company.name:
                continue
            relation, overlap = self._classify(company, reference_company, ref_industry, ref_score, ref_revenue)
            rationale = self._rationale(company, relation, overlap)
            entries.append(
                CompetitorEntry(
                    company=company,
                    relation=relation,
                    overlap_score=round(overlap, 3),
                    threat_rationale=rationale,
                )
            )

        # Sort by overlap descending
        entries.sort(key=lambda e: e.overlap_score, reverse=True)

        landscape.direct_competitors = [e for e in entries if e.relation == CompetitiveRelation.DIRECT][:top_n]
        landscape.adjacent_players = [e for e in entries if e.relation == CompetitiveRelation.ADJACENT][:top_n]
        landscape.aspirational_peers = [e for e in entries if e.relation == CompetitiveRelation.ASPIRATIONAL][:top_n]
        landscape.positioning_gap = self._positioning_gap(reference_company, entries)
        landscape.differentiation_factors = self._differentiation_factors(reference_company, entries)

        return landscape

    def _revenue(self, c: Company) -> float:
        fin = getattr(c, "financials", None)
        if fin:
            return getattr(fin, "revenue", 0.0) or 0.0
        return 0.0

    def _classify(
        self,
        competitor: Company,
        reference: Company,
        ref_industry: str,
        ref_score: float,
        ref_revenue: float,
    ) -> tuple[CompetitiveRelation, float]:
        comp_industry = getattr(competitor, "industry", "") or ""
        comp_score: float = getattr(competitor, "composite_score", 5.0) or 5.0
        comp_revenue = self._revenue(competitor)

        # Industry match
        industry_match = 1.0 if comp_industry.lower() == ref_industry.lower() else 0.3
        # Score proximity (closer = more direct)
        score_diff = abs(comp_score - ref_score)
        score_match = max(0.0, 1.0 - score_diff / 10.0)
        # Revenue proximity
        if ref_revenue > 0 and comp_revenue > 0:
            rev_ratio = min(ref_revenue, comp_revenue) / max(ref_revenue, comp_revenue)
        else:
            rev_ratio = 0.5

        overlap = round((industry_match * 0.5 + score_match * 0.3 + rev_ratio * 0.2), 3)

        if industry_match > 0.8 and overlap > 0.7:
            relation = CompetitiveRelation.DIRECT
        elif industry_match > 0.5 or overlap > 0.5:
            if comp_score > ref_score + 2.0:
                relation = CompetitiveRelation.ASPIRATIONAL
            else:
                relation = CompetitiveRelation.ADJACENT
        else:
            relation = CompetitiveRelation.DISTANT

        return relation, overlap

    def _rationale(self, c: Company, relation: CompetitiveRelation, overlap: float) -> str:
        tier = getattr(c, "tier", None)
        tier_str = tier.value if hasattr(tier, "value") else str(tier) if tier else "unknown"
        return f"{relation.value.title()} competitor (overlap={overlap:.0%}). Tier: {tier_str}."

    def _positioning_gap(self, ref: Company, entries: list[CompetitorEntry]) -> str:
        direct_count = sum(1 for e in entries if e.relation == CompetitiveRelation.DIRECT)
        if direct_count == 0:
            return f"{ref.name} operates in a largely uncrowded segment — limited direct competition identified."
        elif direct_count > 10:
            return f"Highly contested space with {direct_count} direct competitors — differentiation is critical."
        else:
            return f"{direct_count} direct competitors identified — moderate market density."

    def _differentiation_factors(self, ref: Company, entries: list[CompetitorEntry]) -> list[str]:
        factors: list[str] = []
        ref_ai: float = getattr(ref, "ai_score", 0.0) or 0.0
        if ref_ai >= 7.0:
            factors.append("Above-average AI maturity vs. competitive set")
        ref_growth_fin = getattr(ref, "financials", None)
        ref_growth = getattr(ref_growth_fin, "growth_rate", 0.0) if ref_growth_fin else 0.0
        if ref_growth >= 20.0:
            factors.append(f"High growth rate ({ref_growth:.0f}%) relative to peers")
        return factors or ["No significant differentiation factors detected vs. competitive set."]
