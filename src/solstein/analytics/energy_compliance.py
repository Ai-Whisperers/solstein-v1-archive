"""Energy Compliance & Control Intelligence Module (STORY-149, EPIC-039).

Adds energy-sector-specific compliance scoring dimensions:

- **Regulatory compliance**: certifications, audit history, violation record
- **Control system sophistication**: SCADA/DMS, automation level, cyber posture
- **Regulatory change exposure**: how exposed is the company to upcoming changes

The final compliance risk level (High / Medium / Low) feeds into the
company's overall scoring and DD workflow.

Usage::

    from solstein.analytics.energy_compliance import EnergyComplianceScorer
    scorer = EnergyComplianceScorer()
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

class ComplianceRisk(str, Enum):
    """Overall compliance risk level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ControlSystemTier(str, Enum):
    """Control system sophistication tier."""

    ADVANCED = "advanced"      # Modern SCADA/DMS, full automation, strong cyber
    STANDARD = "standard"      # Basic SCADA, partial automation
    LEGACY = "legacy"          # Manual/legacy control systems
    UNKNOWN = "unknown"


@dataclass
class ComplianceSignal:
    """A single compliance-related signal."""

    category: str  # "certification", "violation", "audit", "regulation"
    name: str
    status: str  # "active", "expired", "pending", "violation"
    impact: str  # "positive", "negative", "neutral"
    details: str = ""


@dataclass
class EnergyComplianceResult:
    """Result of energy compliance assessment."""

    # Scores (0-100)
    regulatory_score: float
    control_system_score: float
    change_exposure_score: float
    composite_score: float

    # Classification
    compliance_risk: ComplianceRisk
    control_tier: ControlSystemTier

    # Details
    signals: list[ComplianceSignal] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    breakdown: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Certification and keyword lookups
# ---------------------------------------------------------------------------

_POSITIVE_CERTS = frozenset({
    "iso 27001", "iso 9001", "iso 14001", "iso 50001",
    "soc 2", "soc2", "nerc cip", "iec 62351", "iec 61850",
    "gdpr compliant", "entso-e certified",
})

_NEGATIVE_KEYWORDS = frozenset({
    "violation", "fine", "penalty", "non-compliant",
    "audit failure", "breach", "incident",
})

_SCADA_KEYWORDS = frozenset({
    "scada", "dms", "ems", "adms", "derms", "ot security",
})

_AUTOMATION_KEYWORDS = frozenset({
    "automated", "real-time", "self-healing", "auto-restore",
    "smart grid", "digital twin",
})

_CYBER_KEYWORDS = frozenset({
    "iec 62351", "nerc cip", "ot security", "soc 2", "soc2",
    "penetration testing", "zero trust",
})


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------

class EnergyComplianceScorer:
    """Score energy company compliance posture from available signals."""

    def score(self, company: Company) -> EnergyComplianceResult:
        """Run full compliance assessment on *company*."""
        logger.info("[Compliance] Scoring {}", company.name)

        tech_stack = [s.lower() for s in getattr(company, "tech_stack", [])]
        notes = (getattr(company, "notes", "") or "").lower()
        description = (getattr(company, "description", "") or "").lower()
        text_corpus = f"{notes} {description} {' '.join(tech_stack)}"

        signals: list[ComplianceSignal] = []
        reg_score = self._score_regulatory(text_corpus, signals)
        ctrl_score, ctrl_tier = self._score_control_systems(tech_stack, text_corpus, signals)
        exposure_score = self._score_change_exposure(text_corpus, company, signals)

        composite = (reg_score * 0.40) + (ctrl_score * 0.35) + (exposure_score * 0.25)
        risk = self._classify_risk(composite)

        risk_factors = self._identify_risk_factors(reg_score, ctrl_score, exposure_score, ctrl_tier)
        recommendations = self._build_recommendations(risk_factors, ctrl_tier)

        result = EnergyComplianceResult(
            regulatory_score=round(reg_score, 1),
            control_system_score=round(ctrl_score, 1),
            change_exposure_score=round(exposure_score, 1),
            composite_score=round(composite, 1),
            compliance_risk=risk,
            control_tier=ctrl_tier,
            signals=signals,
            risk_factors=risk_factors,
            recommendations=recommendations,
            breakdown={
                "regulatory_weight": 0.40,
                "control_system_weight": 0.35,
                "change_exposure_weight": 0.25,
                "cert_count": sum(1 for s in signals if s.category == "certification"),
                "violation_count": sum(1 for s in signals if s.status == "violation"),
            },
        )
        logger.info("[Compliance] {} scored {:.1f} ({})", company.name, composite, risk.value)
        return result

    # -- dimension scorers --------------------------------------------------

    @staticmethod
    def _score_regulatory(text: str, signals: list[ComplianceSignal]) -> float:
        """Score regulatory compliance from certifications and violations."""
        score = 50.0  # Baseline

        # Positive: certifications
        cert_count = 0
        for cert in _POSITIVE_CERTS:
            if cert in text:
                cert_count += 1
                signals.append(ComplianceSignal(
                    "certification", cert.upper(), "active", "positive",
                    f"Certification '{cert}' detected in company profile",
                ))
        score += min(30.0, cert_count * 10.0)

        # Negative: violations
        violation_count = 0
        for kw in _NEGATIVE_KEYWORDS:
            if kw in text:
                violation_count += 1
                signals.append(ComplianceSignal(
                    "violation", kw, "violation", "negative",
                    f"Negative keyword '{kw}' detected",
                ))
        score -= min(40.0, violation_count * 15.0)

        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_control_systems(
        tech_stack: list[str],
        text: str,
        signals: list[ComplianceSignal],
    ) -> tuple[float, ControlSystemTier]:
        """Score control system sophistication."""
        score = 30.0  # Baseline: assume basic

        scada_present = any(kw in text for kw in _SCADA_KEYWORDS)
        automation_present = any(kw in text for kw in _AUTOMATION_KEYWORDS)
        cyber_present = any(kw in text for kw in _CYBER_KEYWORDS)

        if scada_present:
            score += 20.0
            signals.append(ComplianceSignal(
                "control_system", "SCADA/DMS", "active", "positive",
                "Control system technology detected",
            ))

        if automation_present:
            score += 20.0
            signals.append(ComplianceSignal(
                "control_system", "Automation", "active", "positive",
                "Automation capabilities detected",
            ))

        if cyber_present:
            score += 15.0
            signals.append(ComplianceSignal(
                "control_system", "OT Security", "active", "positive",
                "OT/cyber security measures detected",
            ))

        # Determine tier
        if score >= 70:
            tier = ControlSystemTier.ADVANCED
        elif score >= 45 or scada_present or automation_present:
            tier = ControlSystemTier.STANDARD
        else:
            tier = ControlSystemTier.UNKNOWN

        return min(100.0, score), tier

    @staticmethod
    def _score_change_exposure(
        text: str,
        company: Company,
        signals: list[ComplianceSignal],
    ) -> float:
        """Score exposure to regulatory changes.

        Higher score = better prepared for upcoming changes.
        """
        score = 50.0  # Baseline

        # SaaS maturity indicates adaptability
        saas = getattr(company, "saas_maturity", 1)
        if saas >= 7:
            score += 20.0
        elif saas >= 4:
            score += 10.0
        else:
            score -= 10.0

        # Modern tech stack = more adaptable
        modern_kw = {"cloud", "api", "microservices", "saas", "platform"}
        modern_count = sum(1 for kw in modern_kw if kw in text)
        score += min(20.0, modern_count * 8.0)

        # Geographic presence may affect regulatory complexity
        geo = getattr(company, "geographic_presence", [])
        if len(geo) > 3:
            score -= 10.0  # Multi-jurisdiction complexity
            signals.append(ComplianceSignal(
                "regulation", "Multi-jurisdiction",
                "pending", "neutral",
                f"Operates in {len(geo)} jurisdictions — increased regulatory complexity",
            ))

        return max(0.0, min(100.0, score))

    # -- classification and recommendations --------------------------------

    @staticmethod
    def _classify_risk(composite: float) -> ComplianceRisk:
        """Map composite score to risk level (higher score = lower risk)."""
        if composite >= 65:
            return ComplianceRisk.LOW
        if composite >= 40:
            return ComplianceRisk.MEDIUM
        return ComplianceRisk.HIGH

    @staticmethod
    def _identify_risk_factors(
        reg: float,
        ctrl: float,
        exposure: float,
        tier: ControlSystemTier,
    ) -> list[str]:
        """Identify specific compliance risk factors."""
        factors: list[str] = []
        if reg < 40:
            factors.append("Low regulatory compliance score — possible certification gaps or violations")
        if ctrl < 40:
            factors.append("Weak control system infrastructure — limited automation or visibility")
        if exposure < 40:
            factors.append("High regulatory change exposure — may struggle with upcoming requirements")
        if tier in (ControlSystemTier.LEGACY, ControlSystemTier.UNKNOWN):
            factors.append("Control system tier unknown or legacy — modernisation needed")
        return factors

    @staticmethod
    def _build_recommendations(
        risk_factors: list[str],
        tier: ControlSystemTier,
    ) -> list[str]:
        """Generate actionable recommendations from risk factors."""
        recs: list[str] = []
        for factor in risk_factors:
            if "certification" in factor.lower():
                recs.append("Pursue ISO 27001/SOC 2 certification within 12 months")
            elif "control system" in factor.lower():
                recs.append("Invest in SCADA/DMS modernisation programme")
            elif "regulatory change" in factor.lower():
                recs.append("Establish regulatory change monitoring process")
            elif "legacy" in factor.lower() or "unknown" in factor.lower():
                recs.append("Commission control system audit and modernisation roadmap")

        if not recs and tier != ControlSystemTier.ADVANCED:
            recs.append("Continue current compliance programme; consider advanced OT security")

        return recs
