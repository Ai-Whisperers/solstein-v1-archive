"""Energy sector intelligence module (EPIC-039).

Provides energy-specific scoring adjustments and sector classification for
companies operating in the energy transition, oil & gas, renewables,
cleantech, and utilities markets.

Usage::

    from solstein.analytics.energy_sector import EnergySectorAnalyzer

    analyzer = EnergySectorAnalyzer()
    result = analyzer.analyze(company)
    print(result.sector_class, result.transition_score)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from solstein.domain.models import Company


class EnergySubSector(StrEnum):
    RENEWABLES = "renewables"
    OIL_AND_GAS = "oil_and_gas"
    CLEANTECH = "cleantech"
    UTILITIES = "utilities"
    ENERGY_TECH = "energy_tech"
    STORAGE = "energy_storage"
    NUCLEAR = "nuclear"
    UNKNOWN = "unknown"


# Keywords used to auto-classify companies into energy sub-sectors
_SUBSECTOR_KEYWORDS: dict[EnergySubSector, list[str]] = {
    EnergySubSector.RENEWABLES: ["solar", "wind", "renewable", "photovoltaic", "hydro", "geothermal"],
    EnergySubSector.OIL_AND_GAS: ["oil", "gas", "petroleum", "lng", "upstream", "midstream", "downstream"],
    EnergySubSector.CLEANTECH: ["cleantech", "clean energy", "green tech", "carbon capture", "net zero"],
    EnergySubSector.UTILITIES: ["utility", "utilities", "grid", "transmission", "distribution", "electricity"],
    EnergySubSector.ENERGY_TECH: ["energy management", "smart grid", "demand response", "energy efficiency"],
    EnergySubSector.STORAGE: ["battery storage", "energy storage", "ess", "bess", "flow battery"],
    EnergySubSector.NUCLEAR: ["nuclear", "fission", "fusion", "smr", "small modular reactor"],
}

# ESG / transition alignment multipliers per sub-sector
_TRANSITION_MULTIPLIER: dict[EnergySubSector, float] = {
    EnergySubSector.RENEWABLES: 1.4,
    EnergySubSector.CLEANTECH: 1.3,
    EnergySubSector.STORAGE: 1.3,
    EnergySubSector.ENERGY_TECH: 1.2,
    EnergySubSector.UTILITIES: 1.0,
    EnergySubSector.NUCLEAR: 0.9,
    EnergySubSector.OIL_AND_GAS: 0.7,
    EnergySubSector.UNKNOWN: 1.0,
}


@dataclass
class EnergySectorResult:
    """Analysis result for an energy-sector company.

    Attributes:
        sub_sector: Classified energy sub-sector.
        transition_score: Energy-transition alignment score (0–10).
        composite_adjusted: Original composite score adjusted for sector context.
        flags: Notable observations for this company.
    """

    sub_sector: EnergySubSector
    transition_score: float
    composite_adjusted: float
    flags: list[str] = field(default_factory=list)


class EnergySectorAnalyzer:
    """Energy-specific scoring and classification for PE/VC deal sourcing."""

    def analyze(self, company: Company) -> EnergySectorResult:
        """Classify and score an energy-sector company.

        Args:
            company: Company domain object.

        Returns:
            EnergySectorResult with sub-sector, transition score, adjusted composite.
        """
        sub_sector = self._classify_subsector(company)
        transition_score = self._transition_score(company, sub_sector)
        multiplier = _TRANSITION_MULTIPLIER[sub_sector]
        base_composite: float = getattr(company, "composite_score", 5.0) or 5.0
        composite_adjusted = round(min(10.0, base_composite * multiplier), 2)
        flags = self._flags(company, sub_sector, transition_score)

        return EnergySectorResult(
            sub_sector=sub_sector,
            transition_score=transition_score,
            composite_adjusted=composite_adjusted,
            flags=flags,
        )

    def _classify_subsector(self, c: Company) -> EnergySubSector:
        text = " ".join(
            filter(
                None,
                [
                    getattr(c, "name", ""),
                    getattr(c, "description", ""),
                    getattr(c, "industry", ""),
                ],
            )
        ).lower()

        for sector, keywords in _SUBSECTOR_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return sector
        return EnergySubSector.UNKNOWN

    def _transition_score(self, c: Company, sub_sector: EnergySubSector) -> float:
        base = _TRANSITION_MULTIPLIER[sub_sector] * 5.0  # 0-7 range
        growth: float = 0.0
        fin = getattr(c, "financials", None)
        if fin and getattr(fin, "growth_rate", None):
            growth = min(fin.growth_rate / 20.0, 2.0)  # max +2 from growth
        return round(min(10.0, max(0.0, base + growth)), 2)

    def _flags(
        self,
        c: Company,
        sub_sector: EnergySubSector,
        transition_score: float,
    ) -> list[str]:
        flags: list[str] = []
        if sub_sector == EnergySubSector.OIL_AND_GAS:
            flags.append("Traditional fossil-fuel exposure — ESG alignment risk")
        if transition_score >= 8.0:
            flags.append("Strong energy-transition alignment — high ESG suitability")
        funding: float = getattr(c, "total_funding_raised_eur", 0.0) or 0.0
        if funding > 50_000_000 and sub_sector in (EnergySubSector.RENEWABLES, EnergySubSector.CLEANTECH):
            flags.append("Well-funded cleantech/renewable — strong deal candidate")
        return flags or ["No specific energy sector flags"]
