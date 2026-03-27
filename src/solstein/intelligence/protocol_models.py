"""Market protocol mapping models for Epic 4."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ProtocolType(Enum):
    BALANCING = "balancing"
    CAPACITY_MARKET = "capacity_market"
    DAY_AHEAD = "day_ahead"
    INTRADAY = "intraday"
    FORWARD = "forward"
    SETTLEMENT = "settlement"
    METERING = "metering"
    GRID_CONNECTION = "grid_connection"


class MarketMaturity(Enum):
    MATURE = "mature"
    DEVELOPING = "developing"
    EMERGING = "emerging"
    RESTRICTED = "restricted"


@dataclass
class MarketProtocol:
    protocol_name: str
    protocol_type: ProtocolType
    country_code: str
    country_name: str
    operator: str
    description: str = ""
    entry_requirements: list[str] = field(default_factory=list)
    technical_standards: list[str] = field(default_factory=list)
    maturity: MarketMaturity = MarketMaturity.MATURE


@dataclass
class ProtocolPresence:
    protocol: MarketProtocol
    is_active: bool
    entry_date: str | None = None
    capabilities_used: list[str] = field(default_factory=list)
    evidence_source: str = ""


@dataclass
class MarketPresence:
    country_code: str
    country_name: str
    protocols: list[ProtocolPresence] = field(default_factory=list)
    market_maturity: MarketMaturity = MarketMaturity.MATURE
    market_share_estimate: str | None = None
    competitive_intensity: str = "medium"
    entry_barriers: list[str] = field(default_factory=list)
    local_partners: list[str] = field(default_factory=list)


@dataclass
class ProtocolMap:
    company_name: str
    markets: list[MarketPresence] = field(default_factory=list)

    total_countries: int = 0
    total_protocols: int = 0
    primary_markets: list[str] = field(default_factory=list)
    emerging_markets: list[str] = field(default_factory=list)

    geographic_diversification_score: float = 0.0
    protocol_complexity_score: float = 0.0

    market_entry_strategy: str = ""
    regulatory_risks: list[str] = field(default_factory=list)
    expansion_opportunities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "company_name": self.company_name,
            "total_countries": self.total_countries,
            "total_protocols": self.total_protocols,
            "primary_markets": self.primary_markets,
            "emerging_markets": self.emerging_markets,
            "geographic_diversification_score": self.geographic_diversification_score,
            "protocol_complexity_score": self.protocol_complexity_score,
            "market_entry_strategy": self.market_entry_strategy,
            "regulatory_risks": self.regulatory_risks,
            "expansion_opportunities": self.expansion_opportunities,
            "markets": [
                {
                    "country": m.country_name,
                    "code": m.country_code,
                    "maturity": m.market_maturity.value,
                    "protocols": [
                        {
                            "name": p.protocol.protocol_name,
                            "type": p.protocol.protocol_type.value,
                            "active": p.is_active,
                        }
                        for p in m.protocols
                    ],
                }
                for m in self.markets
            ],
        }


EU_ENERGY_PROTOCOLS = {
    "DE": [
        MarketProtocol("Regelenergie", ProtocolType.BALANCING, "DE", "Germany", "TSO Consortium"),
        MarketProtocol("spot market", ProtocolType.DAY_AHEAD, "DE", "Germany", "EPEX SPOT"),
        MarketProtocol("Intraday Continuous", ProtocolType.INTRADAY, "DE", "Germany", "EPEX SPOT"),
        MarketProtocol("SRL", ProtocolType.BALANCING, "DE", "Germany", "Regelleistung"),
    ],
    "GB": [
        MarketProtocol("BM", ProtocolType.BALANCING, "GB", "United Kingdom", "National Grid ESO"),
        MarketProtocol("BRP Settlement", ProtocolType.SETTLEMENT, "GB", "United Kingdom", "ELEXON"),
        MarketProtocol("Capacity Market", ProtocolType.CAPACITY_MARKET, "GB", "United Kingdom", "National Grid"),
    ],
    "NL": [
        MarketProtocol("Tennet Balancing", ProtocolType.BALANCING, "NL", "Netherlands", "Tennet"),
        MarketProtocol("EPEX NL", ProtocolType.DAY_AHEAD, "NL", "Netherlands", "EPEX SPOT"),
    ],
    "FR": [
        MarketProtocol("RTE Balancing", ProtocolType.BALANCING, "FR", "France", "RTE"),
        MarketProtocol("EPEX FR", ProtocolType.DAY_AHEAD, "FR", "France", "EPEX SPOT"),
    ],
    "BE": [
        MarketProtocol("Elia Balancing", ProtocolType.BALANCING, "BE", "Belgium", "Elia"),
        MarketProtocol("EPEX BE", ProtocolType.DAY_AHEAD, "BE", "Belgium", "EPEX SPOT"),
    ],
    "DK": [
        MarketProtocol("Energinet Balancing", ProtocolType.BALANCING, "DK", "Denmark", "Energinet"),
        MarketProtocol("Nord Pool DK", ProtocolType.DAY_AHEAD, "DK", "Denmark", "Nord Pool"),
    ],
    "NO": [
        MarketProtocol("Statnett Balancing", ProtocolType.BALANCING, "NO", "Norway", "Statnett"),
        MarketProtocol("Nord Pool NO", ProtocolType.DAY_AHEAD, "NO", "Norway", "Nord Pool"),
    ],
    "SE": [
        MarketProtocol("Svk Balancing", ProtocolType.BALANCING, "SE", "Sweden", "Svenska Kraftnat"),
        MarketProtocol("Nord Pool SE", ProtocolType.DAY_AHEAD, "SE", "Sweden", "Nord Pool"),
    ],
}
