"""Market protocol mapper for Epic 4."""

from __future__ import annotations

import re
from typing import Optional

from .protocol_models import (
    EU_ENERGY_PROTOCOLS,
    MarketMaturity,
    MarketPresence,
    ProtocolMap,
    ProtocolPresence,
    ProtocolType,
)


COUNTRY_PATTERNS = {
    "DE": ["germany", "german", "deutschland", "berlin", "munich", "hamburg"],
    "GB": ["united kingdom", "uk", "britain", "british", "england", "london"],
    "NL": ["netherlands", "dutch", "holland", "amsterdam", "rotterdam"],
    "FR": ["france", "french", "paris", "lyon", "marseille"],
    "BE": ["belgium", "belgian", "brussels", "antwerp"],
    "DK": ["denmark", "danish", "copenhagen", "energinet"],
    "NO": ["norway", "norwegian", "oslo", "statnett", "nord pool"],
    "SE": ["sweden", "swedish", "stockholm", "svenska kraftnat"],
    "ES": ["spain", "spanish", "madrid", "barcelona", "iberdrola"],
    "IT": ["italy", "italian", "milan", "rome", "enel"],
    "PL": ["poland", "polish", "warsaw", "pse"],
    "AT": ["austria", "austrian", "vienna", "apg"],
    "CH": ["switzerland", "swiss", "zurich", "swissgrid"],
    "FI": ["finland", "finnish", "helsinki", "fingrid"],
    "IE": ["ireland", "irish", "dublin", "eirgrid"],
    "PT": ["portugal", "portuguese", "lisbon", "ren"],
    "CZ": ["czech republic", "czechia", "prague", "ceps"],
    "HU": ["hungary", "hungarian", "budapest", "mavir"],
    "RO": ["romania", "romanian", "bucharest", "transelectrica"],
    "GR": ["greece", "greek", "athens", "admie"],
}

PROTOCOL_SIGNALS = {
    ProtocolType.BALANCING: [
        "balancing",
        "regelenergie",
        "ancillary services",
        "frequency response",
        "reserve",
        "regulation",
        "grid stability",
        "system services",
    ],
    ProtocolType.DAY_AHEAD: [
        "day-ahead",
        "spot market",
        "epex",
        "nord pool",
        "wholesale market",
        "day ahead",
        "spot price",
        "market clearing",
    ],
    ProtocolType.INTRADAY: [
        "intraday",
        "continuous trading",
        "intraday market",
        "within-day",
    ],
    ProtocolType.CAPACITY_MARKET: [
        "capacity market",
        "capacity auction",
        "reliability option",
        "capacity remuneration",
        "strategic reserve",
    ],
    ProtocolType.SETTLEMENT: [
        "settlement",
        "imbalance",
        "brp",
        "balance responsible",
        "metering",
        "data collection",
        "conciliation",
    ],
}

ENERGY_KEYWORDS = [
    "energy",
    "electricity",
    "power",
    "grid",
    "renewable",
    "solar",
    "wind",
    "battery",
    "storage",
    "flexibility",
    "demand response",
    "virtual power",
    "vpp",
    "aggregation",
    "trading",
    "market",
    "utility",
]


class ProtocolMapper:
    def __init__(self):
        self.country_patterns = COUNTRY_PATTERNS
        self.protocol_signals = PROTOCOL_SIGNALS
        self.energy_keywords = ENERGY_KEYWORDS
        self.known_protocols = EU_ENERGY_PROTOCOLS

    def analyze(
        self,
        company_name: str,
        company_description: str = "",
        headquarters: str = "",
        recent_news: list[str] | None = None,
    ) -> ProtocolMap:
        protocol_map = ProtocolMap(company_name=company_name)

        all_text = self._combine_text_sources(company_description, headquarters, recent_news)

        detected_countries = self._detect_countries(all_text)

        markets = []
        for country_code in detected_countries:
            market = self._analyze_market_presence(
                country_code,
                all_text,
                company_name,
            )
            if market:
                markets.append(market)

        if not markets and headquarters:
            hq_country = self._detect_country_from_hq(headquarters)
            if hq_country:
                market = self._analyze_market_presence(hq_country, all_text, company_name)
                if market:
                    markets.append(market)

        protocol_map.markets = markets
        protocol_map = self._calculate_metrics(protocol_map)
        protocol_map = self._generate_strategy(protocol_map)
        protocol_map = self._identify_risks(protocol_map)

        return protocol_map

    def _combine_text_sources(
        self,
        description: str,
        headquarters: str,
        news: list[str] | None,
    ) -> str:
        parts = [description.lower(), headquarters.lower()]
        if news:
            parts.extend(n.lower() for n in news if isinstance(n, str))
        return " ".join(parts)

    def _detect_countries(self, text: str) -> list[str]:
        detected = set()

        for country_code, patterns in self.country_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    detected.add(country_code)
                    break

        return list(detected)

    def _detect_country_from_hq(self, headquarters: str) -> Optional[str]:
        text = headquarters.lower()

        country_mappings = {
            "germany": "DE",
            "uk": "GB",
            "united kingdom": "GB",
            "netherlands": "NL",
            "france": "FR",
            "belgium": "BE",
            "denmark": "DK",
            "norway": "NO",
            "sweden": "SE",
            "spain": "ES",
            "italy": "IT",
            "ireland": "IE",
            "finland": "FI",
            "poland": "PL",
            "austria": "AT",
            "switzerland": "CH",
            "portugal": "PT",
        }

        for name, code in country_mappings.items():
            if name in text:
                return code

        for country_code, patterns in self.country_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return country_code

        return None

    def _analyze_market_presence(
        self,
        country_code: str,
        text: str,
        company_name: str,
    ) -> Optional[MarketPresence]:
        country_name = self._get_country_name(country_code)

        protocols = self.known_protocols.get(country_code, [])
        if not protocols:
            return None

        protocol_presences = []
        for protocol in protocols:
            is_active = self._detect_protocol_usage(text, protocol)
            presence = ProtocolPresence(
                protocol=protocol,
                is_active=is_active,
                evidence_source="description" if is_active else "",
            )
            protocol_presences.append(presence)

        if not any(p.is_active for p in protocol_presences):
            protocol_presences[0].is_active = True

        market = MarketPresence(
            country_code=country_code,
            country_name=country_name,
            protocols=protocol_presences,
        )

        market.market_maturity = self._assess_market_maturity(country_code)

        return market

    def _get_country_name(self, country_code: str) -> str:
        names = {
            "DE": "Germany",
            "GB": "United Kingdom",
            "NL": "Netherlands",
            "FR": "France",
            "BE": "Belgium",
            "DK": "Denmark",
            "NO": "Norway",
            "SE": "Sweden",
            "ES": "Spain",
            "IT": "Italy",
            "IE": "Ireland",
            "FI": "Finland",
            "PL": "Poland",
            "AT": "Austria",
            "CH": "Switzerland",
            "PT": "Portugal",
            "CZ": "Czech Republic",
            "HU": "Hungary",
            "RO": "Romania",
            "GR": "Greece",
        }
        return names.get(country_code, country_code)

    def _detect_protocol_usage(self, text: str, protocol) -> bool:
        protocol_name_lower = protocol.protocol_name.lower()
        protocol_operator_lower = protocol.operator.lower()

        if protocol_name_lower in text or protocol_operator_lower in text:
            return True

        protocol_type_signals = self.protocol_signals.get(protocol.protocol_type, [])
        country_signals = self.country_patterns.get(protocol.country_code, [])

        type_mentions = sum(1 for signal in protocol_type_signals if signal in text)
        country_mentions = sum(1 for signal in country_signals if signal in text)

        if type_mentions > 0 and country_mentions > 0:
            return True

        return False

    def _assess_market_maturity(self, country_code: str) -> MarketMaturity:
        mature = {"DE", "GB", "NL", "FR", "BE", "DK", "NO", "SE", "CH", "AT"}
        developing = {"ES", "IT", "IE", "FI", "PL", "PT", "CZ"}

        if country_code in mature:
            return MarketMaturity.MATURE
        elif country_code in developing:
            return MarketMaturity.DEVELOPING
        else:
            return MarketMaturity.EMERGING

    def _calculate_metrics(self, protocol_map: ProtocolMap) -> ProtocolMap:
        protocol_map.total_countries = len(protocol_map.markets)

        total_protocols = sum(len(m.protocols) for m in protocol_map.markets)
        protocol_map.total_protocols = total_protocols

        primary = []
        emerging = []

        for market in protocol_map.markets:
            if market.market_maturity == MarketMaturity.MATURE:
                primary.append(market.country_name)
            elif market.market_maturity == MarketMaturity.EMERGING:
                emerging.append(market.country_name)

        protocol_map.primary_markets = primary
        protocol_map.emerging_markets = emerging

        if protocol_map.total_countries > 0:
            diversification = min(1.0, protocol_map.total_countries / 10.0)
            protocol_map.geographic_diversification_score = round(diversification * 10, 1)

        if protocol_map.total_protocols > 0:
            avg_protocols_per_country = protocol_map.total_protocols / protocol_map.total_countries
            complexity = min(1.0, avg_protocols_per_country / 5.0)
            protocol_map.protocol_complexity_score = round(complexity * 10, 1)

        return protocol_map

    def _generate_strategy(self, protocol_map: ProtocolMap) -> ProtocolMap:
        if protocol_map.total_countries == 0:
            protocol_map.market_entry_strategy = "No clear market presence detected."
            return protocol_map

        parts = []

        if protocol_map.total_countries == 1:
            parts.append(
                f"Single-market focus in {protocol_map.markets[0].country_name}. "
                f"Deep specialization strategy with concentrated regulatory expertise."
            )
        elif protocol_map.total_countries <= 3:
            markets_str = ", ".join(m.country_name for m in protocol_map.markets)
            parts.append(
                f"Regional focus across {markets_str}. "
                f"Selective expansion strategy targeting culturally and regulatorily similar markets."
            )
        else:
            parts.append(
                f"Multi-market presence across {protocol_map.total_countries} countries. "
                f"Diversified strategy spreads regulatory risk across jurisdictions."
            )

        if protocol_map.primary_markets and len(protocol_map.primary_markets) >= 2:
            parts.append(
                f"Established presence in mature markets ({', '.join(protocol_map.primary_markets[:2])}) "
                f"provides stable revenue base."
            )

        if protocol_map.emerging_markets:
            parts.append(
                f"Exposure to emerging markets ({', '.join(protocol_map.emerging_markets)}) "
                f"offers growth potential with higher regulatory uncertainty."
            )

        opportunities = []

        if protocol_map.total_countries < 3:
            opportunities.append("Expand to neighboring markets with similar protocols")

        if protocol_map.geographic_diversification_score < 5:
            opportunities.append("Geographic diversification to reduce single-market risk")

        missing_mature = set(["Germany", "United Kingdom", "Netherlands"]) - set(protocol_map.primary_markets)
        if missing_mature:
            opportunities.append(f"Consider entry to major market: {', '.join(missing_mature)}")

        protocol_map.expansion_opportunities = opportunities[:3]
        protocol_map.market_entry_strategy = " ".join(parts)

        return protocol_map

    def _identify_risks(self, protocol_map: ProtocolMap) -> ProtocolMap:
        risks = []

        if protocol_map.total_countries == 1:
            risks.append("Single-market concentration creates regulatory dependency risk")

        if protocol_map.total_countries > 5:
            risks.append("Multi-jurisdictional complexity increases compliance overhead")

        emerging_count = sum(1 for m in protocol_map.markets if m.market_maturity == MarketMaturity.EMERGING)
        if emerging_count > 2:
            risks.append("Heavy exposure to emerging markets with evolving regulations")

        if not any(m.market_maturity == MarketMaturity.MATURE for m in protocol_map.markets):
            risks.append("No presence in mature markets limits access to established liquidity pools")

        if protocol_map.protocol_complexity_score > 7:
            risks.append("High protocol complexity requires significant technical integration")

        protocol_map.regulatory_risks = risks[:4]
        return protocol_map
