"""Energy Market Forecasting & Demand Scoring Module (STORY-150, EPIC-039).

Assesses energy company positioning relative to market demand trends:

- **Market alignment**: how well the company's offerings match demand growth areas
- **Demand resilience**: revenue stability and diversification across demand segments
- **Forecasting capability**: internal data/analytics maturity for demand prediction

The final market demand score (0-100) feeds into the company's overall
energy sector assessment alongside compliance (STORY-149) and infrastructure scores.

Usage::

    from solstein.analytics.energy_market_forecasting import EnergyMarketScorer
    scorer = EnergyMarketScorer()
    result = scorer.score(company)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from loguru import logger

if TYPE_CHECKING:
    from solstein.domain.models import Company


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class MarketPositioning(str, Enum):
    """Company positioning relative to energy market trends."""

    LEADER = "leader"  # Aligned with high-growth segments
    ALIGNED = "aligned"  # Good alignment with market trends
    TRANSITIONING = "transitioning"  # Moving toward growth segments
    MISALIGNED = "misaligned"  # Focused on declining segments
    UNKNOWN = "unknown"


class DemandSegment(str, Enum):
    """Energy demand segments for alignment scoring."""

    RENEWABLES_INTEGRATION = "renewables_integration"
    GRID_MODERNIZATION = "grid_modernization"
    ENERGY_STORAGE = "energy_storage"
    EV_INFRASTRUCTURE = "ev_infrastructure"
    DISTRIBUTED_ENERGY = "distributed_energy"
    CARBON_MANAGEMENT = "carbon_management"
    DEMAND_RESPONSE = "demand_response"
    TRADITIONAL_GENERATION = "traditional_generation"


@dataclass
class MarketSignal:
    """A single market-related signal."""

    segment: str
    name: str
    strength: str  # "strong", "moderate", "weak"
    trend: str  # "growing", "stable", "declining"
    details: str = ""


@dataclass
class EnergyMarketResult:
    """Result of energy market forecasting assessment."""

    # Scores (0-100)
    market_alignment_score: float
    demand_resilience_score: float
    forecasting_capability_score: float
    composite_score: float

    # Classification
    market_positioning: MarketPositioning
    primary_segments: list[DemandSegment] = field(default_factory=list)

    # Details
    signals: list[MarketSignal] = field(default_factory=list)
    growth_factors: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    breakdown: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Segment keyword lookups
# ---------------------------------------------------------------------------

_SEGMENT_KEYWORDS: dict[DemandSegment, frozenset[str]] = {
    DemandSegment.RENEWABLES_INTEGRATION: frozenset(
        {
            "solar",
            "wind",
            "renewable",
            "photovoltaic",
            "geothermal",
            "renewable integration",
            "green energy",
        }
    ),
    DemandSegment.GRID_MODERNIZATION: frozenset(
        {
            "smart grid",
            "grid modernization",
            "amr",
            "ami",
            "grid analytics",
            "distribution automation",
            "adms",
        }
    ),
    DemandSegment.ENERGY_STORAGE: frozenset(
        {
            "battery",
            "energy storage",
            "ess",
            "bess",
            "flow battery",
            "pumped hydro",
            "thermal storage",
        }
    ),
    DemandSegment.EV_INFRASTRUCTURE: frozenset(
        {
            "ev charging",
            "electric vehicle",
            "evse",
            "charging station",
            "v2g",
            "vehicle-to-grid",
        }
    ),
    DemandSegment.DISTRIBUTED_ENERGY: frozenset(
        {
            "distributed energy",
            "der",
            "microgrid",
            "virtual power plant",
            "prosumer",
            "behind-the-meter",
        }
    ),
    DemandSegment.CARBON_MANAGEMENT: frozenset(
        {
            "carbon capture",
            "carbon trading",
            "carbon offset",
            "emissions",
            "net zero",
            "decarbonization",
            "carbon management",
        }
    ),
    DemandSegment.DEMAND_RESPONSE: frozenset(
        {
            "demand response",
            "load management",
            "load shifting",
            "peak shaving",
            "flexibility market",
        }
    ),
    DemandSegment.TRADITIONAL_GENERATION: frozenset(
        {
            "coal",
            "natural gas generation",
            "fossil fuel",
            "thermal plant",
            "combined cycle",
        }
    ),
}

# Growth trend weights per segment (higher = faster growing market)
_SEGMENT_GROWTH: dict[DemandSegment, float] = {
    DemandSegment.RENEWABLES_INTEGRATION: 1.4,
    DemandSegment.GRID_MODERNIZATION: 1.3,
    DemandSegment.ENERGY_STORAGE: 1.5,
    DemandSegment.EV_INFRASTRUCTURE: 1.5,
    DemandSegment.DISTRIBUTED_ENERGY: 1.3,
    DemandSegment.CARBON_MANAGEMENT: 1.2,
    DemandSegment.DEMAND_RESPONSE: 1.1,
    DemandSegment.TRADITIONAL_GENERATION: 0.6,  # Declining segment
}

_FORECASTING_KEYWORDS = frozenset(
    {
        "machine learning",
        "predictive",
        "forecasting",
        "analytics",
        "data-driven",
        "ai-powered",
        "time series",
        "demand prediction",
        "load forecasting",
        "price forecasting",
    }
)

_DIVERSIFICATION_KEYWORDS = frozenset(
    {
        "multi-market",
        "diversified",
        "cross-border",
        "international",
        "multiple segments",
        "portfolio",
    }
)


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------


class EnergyMarketScorer:
    """Score energy company market positioning and demand alignment."""

    def score(self, company: Company) -> EnergyMarketResult:
        """Run full market forecasting assessment on *company*."""
        logger.info("[MarketForecast] Scoring {}", company.name)

        tech_stack = [s.lower() for s in getattr(company, "tech_stack", [])]
        notes = (getattr(company, "notes", "") or "").lower()
        description = (getattr(company, "description", "") or "").lower()
        text_corpus = f"{notes} {description} {' '.join(tech_stack)}"

        signals: list[MarketSignal] = []
        segments = self._detect_segments(text_corpus, signals)

        alignment = self._score_market_alignment(segments, signals)
        resilience = self._score_demand_resilience(
            segments,
            text_corpus,
            company,
            signals,
        )
        forecasting = self._score_forecasting_capability(
            text_corpus,
            company,
            signals,
        )

        composite = (alignment * 0.40) + (resilience * 0.30) + (forecasting * 0.30)
        positioning = _classify_positioning(composite, segments)

        growth_factors = _identify_growth_factors(segments)
        risk_factors = _identify_risk_factors(
            alignment,
            resilience,
            forecasting,
            segments,
        )
        recommendations = _build_recommendations(risk_factors, positioning)

        result = EnergyMarketResult(
            market_alignment_score=round(alignment, 1),
            demand_resilience_score=round(resilience, 1),
            forecasting_capability_score=round(forecasting, 1),
            composite_score=round(composite, 1),
            market_positioning=positioning,
            primary_segments=segments,
            signals=signals,
            growth_factors=growth_factors,
            risk_factors=risk_factors,
            recommendations=recommendations,
            breakdown={
                "alignment_weight": 0.40,
                "resilience_weight": 0.30,
                "forecasting_weight": 0.30,
                "segment_count": len(segments),
                "growth_segment_count": sum(1 for s in segments if _SEGMENT_GROWTH.get(s, 1.0) > 1.0),
            },
        )
        logger.info(
            "[MarketForecast] {} scored {:.1f} ({})",
            company.name,
            composite,
            positioning.value,
        )
        return result

    # -- dimension scorers --------------------------------------------------

    @staticmethod
    def _detect_segments(
        text: str,
        signals: list[MarketSignal],
    ) -> list[DemandSegment]:
        """Detect which demand segments the company operates in."""
        found: list[DemandSegment] = []
        for segment, keywords in _SEGMENT_KEYWORDS.items():
            matched = [kw for kw in keywords if kw in text]
            if matched:
                found.append(segment)
                growth = _SEGMENT_GROWTH.get(segment, 1.0)
                trend = "growing" if growth > 1.0 else ("declining" if growth < 1.0 else "stable")
                signals.append(
                    MarketSignal(
                        segment=segment.value,
                        name=segment.value.replace("_", " ").title(),
                        strength="strong" if len(matched) >= 2 else "moderate",
                        trend=trend,
                        details=f"Matched keywords: {', '.join(matched[:3])}",
                    )
                )
        return found

    @staticmethod
    def _score_market_alignment(
        segments: list[DemandSegment],
        signals: list[MarketSignal],
    ) -> float:
        """Score how well the company aligns with high-growth segments."""
        if not segments:
            return 30.0  # Baseline for unknown alignment

        growth_sum = sum(_SEGMENT_GROWTH.get(s, 1.0) for s in segments)
        avg_growth = growth_sum / len(segments)

        # Base score from average growth alignment
        score = 40.0 + (avg_growth - 1.0) * 80.0  # 1.0 = 40, 1.5 = 80

        # Bonus for being in multiple growth segments
        growth_segments = [s for s in segments if _SEGMENT_GROWTH.get(s, 1.0) > 1.0]
        score += min(20.0, len(growth_segments) * 7.0)

        # Penalty for traditional/declining segments
        declining = [s for s in segments if _SEGMENT_GROWTH.get(s, 1.0) < 1.0]
        if declining:
            score -= 15.0
            for seg in declining:
                signals.append(
                    MarketSignal(
                        segment=seg.value,
                        name="Declining Segment",
                        strength="weak",
                        trend="declining",
                        details=f"Exposure to declining segment: {seg.value}",
                    )
                )

        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_demand_resilience(
        segments: list[DemandSegment],
        text: str,
        company: Company,
        signals: list[MarketSignal],
    ) -> float:
        """Score revenue resilience and demand diversification."""
        score = 40.0  # Baseline

        # Segment diversification
        if len(segments) >= 3:
            score += 20.0
            signals.append(
                MarketSignal(
                    segment="diversification",
                    name="Multi-Segment Presence",
                    strength="strong",
                    trend="stable",
                    details=f"Active in {len(segments)} demand segments",
                )
            )
        elif len(segments) >= 2:
            score += 10.0

        # Diversification keywords
        div_count = sum(1 for kw in _DIVERSIFICATION_KEYWORDS if kw in text)
        score += min(15.0, div_count * 8.0)

        # Revenue stability from growth rate
        growth = getattr(company, "growth_rate", None)
        if growth is not None:
            if growth > 15:
                score += 15.0
            elif growth > 5:
                score += 8.0
            elif growth < 0:
                score -= 15.0

        # SaaS/recurring revenue model
        saas = getattr(company, "saas_maturity", 1)
        if saas >= 7:
            score += 10.0
        elif saas >= 4:
            score += 5.0

        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_forecasting_capability(
        text: str,
        company: Company,
        signals: list[MarketSignal],
    ) -> float:
        """Score internal forecasting and analytics capability."""
        score = 30.0  # Baseline

        # Forecasting/analytics keywords
        forecast_count = sum(1 for kw in _FORECASTING_KEYWORDS if kw in text)
        if forecast_count >= 3:
            score += 30.0
            signals.append(
                MarketSignal(
                    segment="forecasting",
                    name="Advanced Forecasting",
                    strength="strong",
                    trend="growing",
                    details=f"Detected {forecast_count} forecasting capabilities",
                )
            )
        elif forecast_count >= 1:
            score += 15.0
            signals.append(
                MarketSignal(
                    segment="forecasting",
                    name="Basic Forecasting",
                    strength="moderate",
                    trend="stable",
                    details=f"Detected {forecast_count} forecasting capabilities",
                )
            )

        # AI maturity contributes to forecasting capability
        ai_maturity = str(getattr(company, "ai_maturity", "") or "").lower()
        if ai_maturity in ("strong", "very strong"):
            score += 20.0
        elif ai_maturity == "moderate":
            score += 10.0

        # Tech stack modernity
        tech_stack = [s.lower() for s in getattr(company, "tech_stack", [])]
        analytics_tech = {"python", "tensorflow", "pytorch", "spark", "databricks", "snowflake"}
        analytics_count = sum(1 for t in tech_stack if t in analytics_tech)
        score += min(15.0, analytics_count * 5.0)

        return max(0.0, min(100.0, score))


# ---------------------------------------------------------------------------
# Classification and recommendations (module-level to keep class under 300 lines)
# ---------------------------------------------------------------------------


def _classify_positioning(
    composite: float,
    segments: list[DemandSegment],
) -> MarketPositioning:
    """Map composite score and segments to market positioning."""
    if not segments:
        return MarketPositioning.UNKNOWN

    has_declining = any(_SEGMENT_GROWTH.get(s, 1.0) < 1.0 for s in segments)
    has_growing = any(_SEGMENT_GROWTH.get(s, 1.0) > 1.2 for s in segments)

    if composite >= 70:
        return MarketPositioning.LEADER
    if composite >= 55:
        return MarketPositioning.ALIGNED
    if has_growing and has_declining:
        return MarketPositioning.TRANSITIONING
    if composite >= 40:
        return MarketPositioning.TRANSITIONING
    return MarketPositioning.MISALIGNED


def _identify_growth_factors(segments: list[DemandSegment]) -> list[str]:
    """Identify market growth factors from detected segments."""
    factors: list[str] = []
    for seg in segments:
        growth = _SEGMENT_GROWTH.get(seg, 1.0)
        if growth >= 1.4:
            factors.append(f"High-growth segment: {seg.value.replace('_', ' ')} (growth multiplier {growth}x)")
        elif growth >= 1.2:
            factors.append(f"Growing segment: {seg.value.replace('_', ' ')} (growth multiplier {growth}x)")
    return factors


def _identify_risk_factors(
    alignment: float,
    resilience: float,
    forecasting: float,
    segments: list[DemandSegment],
) -> list[str]:
    """Identify market risk factors."""
    factors: list[str] = []
    if alignment < 40:
        factors.append("Poor market alignment — company not positioned in growth segments")
    if resilience < 40:
        factors.append("Low demand resilience — limited diversification or declining revenue")
    if forecasting < 40:
        factors.append("Weak forecasting capability — limited analytics or AI maturity")
    declining = [s for s in segments if _SEGMENT_GROWTH.get(s, 1.0) < 1.0]
    if declining:
        names = ", ".join(s.value.replace("_", " ") for s in declining)
        factors.append(f"Exposure to declining segments: {names}")
    if not segments:
        factors.append("No identifiable energy demand segments detected")
    return factors


def _build_recommendations(
    risk_factors: list[str],
    positioning: MarketPositioning,
) -> list[str]:
    """Generate actionable recommendations."""
    recs: list[str] = []
    for factor in risk_factors:
        if "alignment" in factor.lower():
            recs.append("Pivot product roadmap toward high-growth segments (renewables, storage, EV infrastructure)")
        elif "resilience" in factor.lower():
            recs.append("Diversify revenue across multiple demand segments to reduce concentration risk")
        elif "forecasting" in factor.lower():
            recs.append("Invest in predictive analytics and AI capabilities for demand forecasting")
        elif "declining" in factor.lower():
            recs.append("Develop transition strategy away from declining segments toward growth areas")
        elif "no identifiable" in factor.lower():
            recs.append("Clarify energy market positioning and identify target demand segments")

    if not recs and positioning != MarketPositioning.LEADER:
        recs.append("Continue strengthening market position; explore adjacent growth segments")
    return recs
