"""Trading Platform & Digital Infrastructure Assessment (STORY-151, EPIC-039).

Evaluates energy company trading platform maturity and digital infrastructure:

- **Trading platform maturity**: algorithmic trading, market access, risk mgmt
- **Digital infrastructure**: cloud adoption, API maturity, data architecture
- **Integration readiness**: interoperability, standards compliance, scalability

The composite score (0-100) feeds into the company's energy sector assessment
alongside compliance (STORY-149) and market forecasting (STORY-150).

Usage::

    from solstein.analytics.energy_trading_infrastructure import (
        TradingInfrastructureScorer,
    )
    scorer = TradingInfrastructureScorer()
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


class PlatformMaturity(str, Enum):
    """Trading platform maturity level."""

    ADVANCED = "advanced"  # Algorithmic, multi-market, real-time
    INTERMEDIATE = "intermediate"  # Electronic trading, single market
    BASIC = "basic"  # Manual/bilateral trading
    UNKNOWN = "unknown"


class InfrastructureTier(str, Enum):
    """Digital infrastructure tier."""

    CLOUD_NATIVE = "cloud_native"  # Full cloud, microservices, CI/CD
    HYBRID = "hybrid"  # Mix of cloud and on-premise
    LEGACY = "legacy"  # On-premise, monolithic
    UNKNOWN = "unknown"


@dataclass
class InfrastructureSignal:
    """A single infrastructure-related signal."""

    category: str  # "trading", "cloud", "api", "data", "integration"
    name: str
    maturity: str  # "advanced", "intermediate", "basic"
    details: str = ""


@dataclass
class TradingInfrastructureResult:
    """Result of trading infrastructure assessment."""

    # Scores (0-100)
    trading_platform_score: float
    digital_infrastructure_score: float
    integration_readiness_score: float
    composite_score: float

    # Classification
    platform_maturity: PlatformMaturity
    infrastructure_tier: InfrastructureTier

    # Details
    signals: list[InfrastructureSignal] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    breakdown: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Keyword lookups
# ---------------------------------------------------------------------------

_TRADING_KEYWORDS = frozenset(
    {
        "algorithmic trading",
        "algo trading",
        "automated trading",
        "energy trading",
        "power trading",
        "commodity trading",
        "market making",
        "hedging",
        "derivatives",
        "etrm",
        "ctrm",  # Energy/Commodity Trading Risk Management
    }
)

_MARKET_ACCESS_KEYWORDS = frozenset(
    {
        "epex",
        "nord pool",
        "entsoe",
        "wholesale market",
        "balancing market",
        "intraday",
        "day-ahead",
        "futures",
        "otc",
        "bilateral",
        "exchange",
    }
)

_RISK_MGMT_KEYWORDS = frozenset(
    {
        "var",
        "value at risk",
        "risk management",
        "position management",
        "credit risk",
        "market risk",
        "counterparty",
        "collateral",
        "margin",
    }
)

_CLOUD_KEYWORDS = frozenset(
    {
        "aws",
        "azure",
        "gcp",
        "cloud",
        "kubernetes",
        "docker",
        "serverless",
        "lambda",
        "cloud-native",
    }
)

_API_KEYWORDS = frozenset(
    {
        "api",
        "rest",
        "graphql",
        "grpc",
        "webhook",
        "api gateway",
        "microservices",
        "event-driven",
    }
)

_DATA_ARCH_KEYWORDS = frozenset(
    {
        "data lake",
        "data warehouse",
        "data mesh",
        "data pipeline",
        "streaming",
        "kafka",
        "real-time data",
        "time series",
        "snowflake",
        "databricks",
        "spark",
    }
)

_INTEGRATION_KEYWORDS = frozenset(
    {
        "iec 61968",
        "cim",
        "iec 62325",
        "entsoe",
        "openapi",
        "interoperability",
        "standard protocol",
        "edi",
        "xml",
        "json api",
    }
)

_SECURITY_INFRA_KEYWORDS = frozenset(
    {
        "zero trust",
        "sso",
        "oauth",
        "mfa",
        "encryption",
        "waf",
        "siem",
        "soc",
    }
)


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------


class TradingInfrastructureScorer:
    """Score energy company trading platform and digital infrastructure."""

    def score(self, company: Company) -> TradingInfrastructureResult:
        """Run full trading infrastructure assessment on *company*."""
        logger.info("[TradingInfra] Scoring {}", company.name)

        tech_stack = [s.lower() for s in getattr(company, "tech_stack", [])]
        notes = (getattr(company, "notes", "") or "").lower()
        description = (getattr(company, "description", "") or "").lower()
        text_corpus = f"{notes} {description} {' '.join(tech_stack)}"

        signals: list[InfrastructureSignal] = []
        trading = self._score_trading_platform(text_corpus, signals)
        infra = self._score_digital_infrastructure(
            text_corpus,
            tech_stack,
            company,
            signals,
        )
        integration = self._score_integration_readiness(text_corpus, signals)

        composite = (trading * 0.35) + (infra * 0.40) + (integration * 0.25)
        platform_mat = _classify_platform_maturity(trading)
        infra_tier = _classify_infrastructure_tier(infra, tech_stack)

        strengths = _identify_strengths(trading, infra, integration)
        gaps = _identify_gaps(trading, infra, integration, platform_mat)
        recommendations = _build_recommendations(gaps, platform_mat, infra_tier)

        result = TradingInfrastructureResult(
            trading_platform_score=round(trading, 1),
            digital_infrastructure_score=round(infra, 1),
            integration_readiness_score=round(integration, 1),
            composite_score=round(composite, 1),
            platform_maturity=platform_mat,
            infrastructure_tier=infra_tier,
            signals=signals,
            strengths=strengths,
            gaps=gaps,
            recommendations=recommendations,
            breakdown={
                "trading_weight": 0.35,
                "infrastructure_weight": 0.40,
                "integration_weight": 0.25,
                "trading_keywords_found": sum(1 for s in signals if s.category == "trading"),
                "cloud_keywords_found": sum(1 for s in signals if s.category == "cloud"),
            },
        )
        logger.info(
            "[TradingInfra] {} scored {:.1f} ({}, {})",
            company.name,
            composite,
            platform_mat.value,
            infra_tier.value,
        )
        return result

    # -- dimension scorers --------------------------------------------------

    @staticmethod
    def _score_trading_platform(
        text: str,
        signals: list[InfrastructureSignal],
    ) -> float:
        """Score trading platform maturity."""
        score = 25.0  # Baseline

        # Algorithmic / automated trading
        trading_count = sum(1 for kw in _TRADING_KEYWORDS if kw in text)
        if trading_count >= 2:
            score += 25.0
            signals.append(
                InfrastructureSignal(
                    "trading",
                    "Algorithmic Trading",
                    "advanced",
                    f"Detected {trading_count} trading platform indicators",
                )
            )
        elif trading_count >= 1:
            score += 12.0
            signals.append(
                InfrastructureSignal(
                    "trading",
                    "Electronic Trading",
                    "intermediate",
                    "Trading platform capability detected",
                )
            )

        # Market access breadth
        market_count = sum(1 for kw in _MARKET_ACCESS_KEYWORDS if kw in text)
        if market_count >= 3:
            score += 20.0
            signals.append(
                InfrastructureSignal(
                    "trading",
                    "Multi-Market Access",
                    "advanced",
                    f"Access to {market_count} market types detected",
                )
            )
        elif market_count >= 1:
            score += 10.0

        # Risk management
        risk_count = sum(1 for kw in _RISK_MGMT_KEYWORDS if kw in text)
        if risk_count >= 2:
            score += 15.0
            signals.append(
                InfrastructureSignal(
                    "trading",
                    "Risk Management",
                    "advanced",
                    "Comprehensive risk management detected",
                )
            )
        elif risk_count >= 1:
            score += 8.0

        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_digital_infrastructure(
        text: str,
        tech_stack: list[str],
        company: Company,
        signals: list[InfrastructureSignal],
    ) -> float:
        """Score digital infrastructure maturity."""
        score = 25.0  # Baseline

        # Cloud adoption
        cloud_count = sum(1 for kw in _CLOUD_KEYWORDS if kw in text)
        cloud_in_stack = sum(1 for t in tech_stack if t in {"aws", "azure", "gcp", "kubernetes", "docker"})
        total_cloud = cloud_count + cloud_in_stack
        if total_cloud >= 3:
            score += 25.0
            signals.append(
                InfrastructureSignal(
                    "cloud",
                    "Cloud-Native",
                    "advanced",
                    f"Strong cloud adoption ({total_cloud} indicators)",
                )
            )
        elif total_cloud >= 1:
            score += 12.0
            signals.append(
                InfrastructureSignal(
                    "cloud",
                    "Cloud Adoption",
                    "intermediate",
                    "Cloud infrastructure detected",
                )
            )

        # API maturity
        api_count = sum(1 for kw in _API_KEYWORDS if kw in text)
        if api_count >= 3:
            score += 20.0
            signals.append(
                InfrastructureSignal(
                    "api",
                    "API-First Architecture",
                    "advanced",
                    f"Strong API maturity ({api_count} indicators)",
                )
            )
        elif api_count >= 1:
            score += 10.0

        # Data architecture
        data_count = sum(1 for kw in _DATA_ARCH_KEYWORDS if kw in text)
        data_in_stack = sum(1 for t in tech_stack if t in {"kafka", "spark", "snowflake", "databricks"})
        total_data = data_count + data_in_stack
        if total_data >= 3:
            score += 20.0
            signals.append(
                InfrastructureSignal(
                    "data",
                    "Modern Data Architecture",
                    "advanced",
                    f"Advanced data infrastructure ({total_data} indicators)",
                )
            )
        elif total_data >= 1:
            score += 10.0

        # SaaS maturity
        saas = getattr(company, "saas_maturity", 1)
        if saas >= 7:
            score += 10.0
        elif saas >= 4:
            score += 5.0

        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_integration_readiness(
        text: str,
        signals: list[InfrastructureSignal],
    ) -> float:
        """Score integration and interoperability readiness."""
        score = 30.0  # Baseline

        # Standards compliance
        std_count = sum(1 for kw in _INTEGRATION_KEYWORDS if kw in text)
        if std_count >= 3:
            score += 30.0
            signals.append(
                InfrastructureSignal(
                    "integration",
                    "Standards Compliance",
                    "advanced",
                    f"Strong standards adherence ({std_count} standards detected)",
                )
            )
        elif std_count >= 1:
            score += 15.0
            signals.append(
                InfrastructureSignal(
                    "integration",
                    "Partial Standards",
                    "intermediate",
                    "Some integration standards detected",
                )
            )

        # Security infrastructure
        sec_count = sum(1 for kw in _SECURITY_INFRA_KEYWORDS if kw in text)
        if sec_count >= 3:
            score += 25.0
            signals.append(
                InfrastructureSignal(
                    "integration",
                    "Security Infrastructure",
                    "advanced",
                    f"Robust security posture ({sec_count} security measures)",
                )
            )
        elif sec_count >= 1:
            score += 12.0

        return max(0.0, min(100.0, score))


# ---------------------------------------------------------------------------
# Classification and recommendations (module-level)
# ---------------------------------------------------------------------------


def _classify_platform_maturity(trading_score: float) -> PlatformMaturity:
    """Map trading score to platform maturity level."""
    if trading_score >= 65:
        return PlatformMaturity.ADVANCED
    if trading_score >= 40:
        return PlatformMaturity.INTERMEDIATE
    if trading_score > 25:
        return PlatformMaturity.BASIC
    return PlatformMaturity.UNKNOWN


def _classify_infrastructure_tier(
    infra_score: float,
    tech_stack: list[str],
) -> InfrastructureTier:
    """Map infrastructure score to tier."""
    cloud_tech = {"aws", "azure", "gcp", "kubernetes", "docker"}
    has_cloud = any(t in cloud_tech for t in tech_stack)

    if infra_score >= 70:
        return InfrastructureTier.CLOUD_NATIVE
    if infra_score >= 45 or has_cloud:
        return InfrastructureTier.HYBRID
    if infra_score > 25:
        return InfrastructureTier.LEGACY
    return InfrastructureTier.UNKNOWN


def _identify_strengths(
    trading: float,
    infra: float,
    integration: float,
) -> list[str]:
    """Identify infrastructure strengths."""
    strengths: list[str] = []
    if trading >= 65:
        strengths.append("Advanced trading platform with algorithmic capabilities")
    if infra >= 65:
        strengths.append("Modern cloud-native digital infrastructure")
    if integration >= 65:
        strengths.append("Strong integration readiness with standards compliance")
    return strengths


def _identify_gaps(
    trading: float,
    infra: float,
    integration: float,
    platform: PlatformMaturity,
) -> list[str]:
    """Identify infrastructure gaps."""
    gaps: list[str] = []
    if trading < 40:
        gaps.append("Limited trading platform — manual or no electronic trading")
    if infra < 40:
        gaps.append("Legacy digital infrastructure — limited cloud or API adoption")
    if integration < 40:
        gaps.append("Poor integration readiness — missing standards compliance")
    if platform in (PlatformMaturity.BASIC, PlatformMaturity.UNKNOWN):
        gaps.append("Trading platform maturity insufficient for modern markets")
    return gaps


def _build_recommendations(
    gaps: list[str],
    platform: PlatformMaturity,
    tier: InfrastructureTier,
) -> list[str]:
    """Generate actionable recommendations."""
    recs: list[str] = []
    for gap in gaps:
        if "trading platform" in gap.lower() and "limited" in gap.lower():
            recs.append("Implement electronic trading capabilities; evaluate ETRM solutions")
        elif "legacy digital" in gap.lower():
            recs.append("Develop cloud migration roadmap; prioritize API-first architecture")
        elif "integration readiness" in gap.lower():
            recs.append("Adopt energy industry standards (IEC 61968/CIM); implement standard APIs")
        elif "maturity insufficient" in gap.lower():
            recs.append("Invest in trading technology modernization programme")

    if not recs and platform != PlatformMaturity.ADVANCED:
        recs.append("Continue platform evolution; explore algorithmic trading capabilities")
    if not recs and tier != InfrastructureTier.CLOUD_NATIVE:
        recs.append("Evaluate cloud-native architecture migration for improved scalability")
    return recs
