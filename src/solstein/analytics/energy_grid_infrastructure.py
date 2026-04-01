"""Grid Integration & Smart Infrastructure Scoring (STORY-152, EPIC-039).

Evaluates energy company grid integration capabilities and smart
infrastructure readiness:

- **Grid connectivity**: DER management, grid-edge intelligence, V2G
- **Smart infrastructure**: IoT/sensors, digital twins, predictive maintenance
- **Decentralization readiness**: microgrid, peer-to-peer, prosumer platforms

The composite score (0-100) completes the energy sector assessment suite
alongside compliance (149), market (150), and trading infrastructure (151).

Usage::

    from solstein.analytics.energy_grid_infrastructure import (
        GridInfrastructureScorer,
    )
    scorer = GridInfrastructureScorer()
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


class GridReadiness(str, Enum):
    """Grid integration readiness level."""

    ADVANCED = "advanced"  # Full DER/microgrid/V2G capabilities
    DEVELOPING = "developing"  # Partial grid-edge intelligence
    BASIC = "basic"  # Traditional grid connection only
    UNKNOWN = "unknown"


class SmartInfraLevel(str, Enum):
    """Smart infrastructure maturity level."""

    INTELLIGENT = "intelligent"  # AI-driven, digital twins, predictive
    CONNECTED = "connected"  # IoT sensors, basic monitoring
    TRADITIONAL = "traditional"  # Manual/legacy infrastructure
    UNKNOWN = "unknown"


@dataclass
class GridSignal:
    """A single grid infrastructure signal."""

    category: str  # "grid", "smart", "decentralization"
    name: str
    maturity: str  # "advanced", "developing", "basic"
    details: str = ""


@dataclass
class GridInfrastructureResult:
    """Result of grid infrastructure assessment."""

    # Scores (0-100)
    grid_connectivity_score: float
    smart_infrastructure_score: float
    decentralization_score: float
    composite_score: float

    # Classification
    grid_readiness: GridReadiness
    smart_infra_level: SmartInfraLevel

    # Details
    signals: list[GridSignal] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    breakdown: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Keyword lookups
# ---------------------------------------------------------------------------

_GRID_CONNECTIVITY_KEYWORDS = frozenset(
    {
        "der management",
        "distributed energy resource",
        "grid-edge",
        "grid edge",
        "v2g",
        "vehicle-to-grid",
        "grid integration",
        "frequency regulation",
        "voltage regulation",
        "power quality",
        "grid stability",
        "ancillary services",
    }
)

_DER_KEYWORDS = frozenset(
    {
        "solar inverter",
        "battery inverter",
        "charge controller",
        "power electronics",
        "grid-tied",
        "islanding",
        "net metering",
        "feed-in",
        "curtailment",
    }
)

_SMART_INFRA_KEYWORDS = frozenset(
    {
        "iot",
        "sensor",
        "smart meter",
        "smart sensor",
        "edge computing",
        "fog computing",
        "embedded",
        "telemetry",
        "remote monitoring",
        "condition monitoring",
    }
)

_DIGITAL_TWIN_KEYWORDS = frozenset(
    {
        "digital twin",
        "simulation",
        "virtual model",
        "predictive maintenance",
        "predictive analytics",
        "asset performance",
        "apm",
    }
)

_AI_GRID_KEYWORDS = frozenset(
    {
        "machine learning",
        "neural network",
        "reinforcement learning",
        "optimization",
        "load forecasting",
        "generation forecasting",
        "anomaly detection",
        "fault detection",
    }
)

_MICROGRID_KEYWORDS = frozenset(
    {
        "microgrid",
        "mini-grid",
        "off-grid",
        "island mode",
        "islanded",
        "community energy",
    }
)

_P2P_KEYWORDS = frozenset(
    {
        "peer-to-peer",
        "p2p energy",
        "prosumer",
        "energy marketplace",
        "blockchain energy",
        "local energy market",
        "energy community",
    }
)

_VPP_KEYWORDS = frozenset(
    {
        "virtual power plant",
        "vpp",
        "aggregation",
        "demand response",
        "flexibility",
        "ancillary",
        "balancing",
        "frequency response",
    }
)


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------


class GridInfrastructureScorer:
    """Score energy company grid integration and smart infrastructure."""

    def score(self, company: Company) -> GridInfrastructureResult:
        """Run full grid infrastructure assessment on *company*."""
        logger.info("[GridInfra] Scoring {}", company.name)

        tech_stack = [s.lower() for s in getattr(company, "tech_stack", [])]
        notes = (getattr(company, "notes", "") or "").lower()
        description = (getattr(company, "description", "") or "").lower()
        text_corpus = f"{notes} {description} {' '.join(tech_stack)}"

        signals: list[GridSignal] = []
        grid = self._score_grid_connectivity(text_corpus, signals)
        smart = self._score_smart_infrastructure(text_corpus, company, signals)
        decentralization = self._score_decentralization(text_corpus, signals)

        composite = (grid * 0.35) + (smart * 0.35) + (decentralization * 0.30)
        grid_ready = _classify_grid_readiness(grid, decentralization)
        smart_level = _classify_smart_level(smart)

        capabilities = _identify_capabilities(grid, smart, decentralization)
        gaps = _identify_gaps(grid, smart, decentralization)
        recommendations = _build_recommendations(gaps, grid_ready, smart_level)

        result = GridInfrastructureResult(
            grid_connectivity_score=round(grid, 1),
            smart_infrastructure_score=round(smart, 1),
            decentralization_score=round(decentralization, 1),
            composite_score=round(composite, 1),
            grid_readiness=grid_ready,
            smart_infra_level=smart_level,
            signals=signals,
            capabilities=capabilities,
            gaps=gaps,
            recommendations=recommendations,
            breakdown={
                "grid_weight": 0.35,
                "smart_weight": 0.35,
                "decentralization_weight": 0.30,
                "grid_signals": sum(1 for s in signals if s.category == "grid"),
                "smart_signals": sum(1 for s in signals if s.category == "smart"),
                "decentralization_signals": sum(1 for s in signals if s.category == "decentralization"),
            },
        )
        logger.info(
            "[GridInfra] {} scored {:.1f} ({}, {})",
            company.name,
            composite,
            grid_ready.value,
            smart_level.value,
        )
        return result

    # -- dimension scorers --------------------------------------------------

    @staticmethod
    def _score_grid_connectivity(
        text: str,
        signals: list[GridSignal],
    ) -> float:
        """Score grid connectivity and DER management capabilities."""
        score = 25.0  # Baseline

        # Grid connectivity
        grid_count = sum(1 for kw in _GRID_CONNECTIVITY_KEYWORDS if kw in text)
        if grid_count >= 3:
            score += 25.0
            signals.append(
                GridSignal(
                    "grid",
                    "Advanced Grid Integration",
                    "advanced",
                    f"Detected {grid_count} grid connectivity capabilities",
                )
            )
        elif grid_count >= 1:
            score += 12.0
            signals.append(
                GridSignal(
                    "grid",
                    "Basic Grid Integration",
                    "developing",
                    "Grid connectivity capabilities detected",
                )
            )

        # DER capabilities
        der_count = sum(1 for kw in _DER_KEYWORDS if kw in text)
        if der_count >= 2:
            score += 20.0
            signals.append(
                GridSignal(
                    "grid",
                    "DER Management",
                    "advanced",
                    f"Detected {der_count} DER management capabilities",
                )
            )
        elif der_count >= 1:
            score += 10.0

        # VPP capabilities
        vpp_count = sum(1 for kw in _VPP_KEYWORDS if kw in text)
        if vpp_count >= 2:
            score += 20.0
            signals.append(
                GridSignal(
                    "grid",
                    "Virtual Power Plant",
                    "advanced",
                    f"VPP/aggregation capabilities ({vpp_count} indicators)",
                )
            )
        elif vpp_count >= 1:
            score += 10.0

        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_smart_infrastructure(
        text: str,
        company: Company,
        signals: list[GridSignal],
    ) -> float:
        """Score smart infrastructure maturity."""
        score = 25.0  # Baseline

        # IoT/sensor layer
        iot_count = sum(1 for kw in _SMART_INFRA_KEYWORDS if kw in text)
        if iot_count >= 3:
            score += 25.0
            signals.append(
                GridSignal(
                    "smart",
                    "IoT Infrastructure",
                    "advanced",
                    f"Strong IoT/sensor layer ({iot_count} indicators)",
                )
            )
        elif iot_count >= 1:
            score += 12.0
            signals.append(
                GridSignal(
                    "smart",
                    "Basic Monitoring",
                    "developing",
                    "Monitoring capabilities detected",
                )
            )

        # Digital twins and predictive
        twin_count = sum(1 for kw in _DIGITAL_TWIN_KEYWORDS if kw in text)
        if twin_count >= 2:
            score += 20.0
            signals.append(
                GridSignal(
                    "smart",
                    "Digital Twin / Predictive",
                    "advanced",
                    f"Digital twin or predictive capabilities ({twin_count})",
                )
            )
        elif twin_count >= 1:
            score += 10.0

        # AI/ML for grid
        ai_count = sum(1 for kw in _AI_GRID_KEYWORDS if kw in text)
        if ai_count >= 2:
            score += 20.0
            signals.append(
                GridSignal(
                    "smart",
                    "AI-Driven Grid",
                    "advanced",
                    f"AI/ML grid capabilities ({ai_count} indicators)",
                )
            )
        elif ai_count >= 1:
            score += 10.0

        # Company AI maturity
        ai_maturity = str(getattr(company, "ai_maturity", "") or "").lower()
        if ai_maturity in ("strong", "very strong"):
            score += 10.0

        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_decentralization(
        text: str,
        signals: list[GridSignal],
    ) -> float:
        """Score decentralization readiness."""
        score = 25.0  # Baseline

        # Microgrid
        micro_count = sum(1 for kw in _MICROGRID_KEYWORDS if kw in text)
        if micro_count >= 2:
            score += 25.0
            signals.append(
                GridSignal(
                    "decentralization",
                    "Microgrid Capability",
                    "advanced",
                    f"Microgrid capabilities ({micro_count} indicators)",
                )
            )
        elif micro_count >= 1:
            score += 12.0
            signals.append(
                GridSignal(
                    "decentralization",
                    "Microgrid Interest",
                    "developing",
                    "Microgrid capability detected",
                )
            )

        # P2P / prosumer
        p2p_count = sum(1 for kw in _P2P_KEYWORDS if kw in text)
        if p2p_count >= 2:
            score += 25.0
            signals.append(
                GridSignal(
                    "decentralization",
                    "P2P Energy Trading",
                    "advanced",
                    f"Peer-to-peer energy capabilities ({p2p_count})",
                )
            )
        elif p2p_count >= 1:
            score += 12.0

        # VPP (also contributes to decentralization)
        vpp_count = sum(1 for kw in _VPP_KEYWORDS if kw in text)
        if vpp_count >= 1:
            score += 15.0

        return max(0.0, min(100.0, score))


# ---------------------------------------------------------------------------
# Classification and recommendations (module-level)
# ---------------------------------------------------------------------------


def _classify_grid_readiness(
    grid_score: float,
    decentralization: float,
) -> GridReadiness:
    """Map scores to grid readiness level."""
    combined = (grid_score + decentralization) / 2.0
    if combined >= 60:
        return GridReadiness.ADVANCED
    if combined >= 35:
        return GridReadiness.DEVELOPING
    if combined > 25:
        return GridReadiness.BASIC
    return GridReadiness.UNKNOWN


def _classify_smart_level(smart_score: float) -> SmartInfraLevel:
    """Map smart infrastructure score to level."""
    if smart_score >= 65:
        return SmartInfraLevel.INTELLIGENT
    if smart_score >= 40:
        return SmartInfraLevel.CONNECTED
    if smart_score > 25:
        return SmartInfraLevel.TRADITIONAL
    return SmartInfraLevel.UNKNOWN


def _identify_capabilities(
    grid: float,
    smart: float,
    decentralization: float,
) -> list[str]:
    """Identify infrastructure capabilities."""
    caps: list[str] = []
    if grid >= 60:
        caps.append("Advanced grid integration with DER management")
    if smart >= 60:
        caps.append("Intelligent infrastructure with AI-driven analytics")
    if decentralization >= 60:
        caps.append("Decentralization-ready with microgrid/P2P capabilities")
    return caps


def _identify_gaps(
    grid: float,
    smart: float,
    decentralization: float,
) -> list[str]:
    """Identify infrastructure gaps."""
    gaps: list[str] = []
    if grid < 40:
        gaps.append("Limited grid connectivity — no DER management or VPP")
    if smart < 40:
        gaps.append("Traditional infrastructure — no IoT, digital twins, or AI")
    if decentralization < 40:
        gaps.append("No decentralization capabilities — missing microgrid/P2P")
    return gaps


def _build_recommendations(
    gaps: list[str],
    grid_ready: GridReadiness,
    smart_level: SmartInfraLevel,
) -> list[str]:
    """Generate actionable recommendations."""
    recs: list[str] = []
    for gap in gaps:
        if "grid connectivity" in gap.lower():
            recs.append("Develop DER management and grid-edge intelligence capabilities")
        elif "traditional infrastructure" in gap.lower():
            recs.append("Invest in IoT sensor layer and predictive maintenance; explore digital twin technology")
        elif "decentralization" in gap.lower():
            recs.append("Explore microgrid and virtual power plant solutions for decentralized energy management")

    if not recs and grid_ready != GridReadiness.ADVANCED:
        recs.append("Continue grid modernization; explore V2G and advanced DER aggregation")
    if not recs and smart_level != SmartInfraLevel.INTELLIGENT:
        recs.append("Evaluate AI-driven grid optimization and digital twin deployment")
    return recs
