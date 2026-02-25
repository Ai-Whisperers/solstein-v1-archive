#!/usr/bin/env python3
"""
Continuous Market Discovery System
Discovers companies until market coverage is complete
"""

import json
import sys
from pathlib import Path
from typing import Set, List, Dict

sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger


class ContinuousMarketDiscovery:
    """
    Discovers companies continuously using multiple sources
    Stops only when we've covered the market (diminishing returns)
    """

    def __init__(self):
        self.discovered_companies: Dict[str, dict] = {}
        self.known_names: Set[str] = set()
        self.iteration = 0
        self.max_iterations = 20  # Safety limit
        self.convergence_threshold = 5  # Stop if <5 new companies found in iteration

    def load_existing_database(self):
        """Load companies we already have."""
        try:
            with open("data/input/competitor_data.json", "r") as f:
                db = json.load(f)

            for company in db["competitors"]:
                name = company.get("company_name", "").lower()
                self.known_names.add(name)
                self.discovered_companies[name] = company

            logger.info(f"Loaded {len(self.discovered_companies)} existing companies")
        except Exception as e:
            logger.warning(f"Could not load existing database: {e}")

    def discover_from_static_catalogs(self) -> List[dict]:
        """Source 1: All static catalogs in discovery.py"""
        from solstein.research.discovery import _catalog_for_market

        new_companies = []

        # Try multiple market variations
        markets = [
            "dutch energy software",
            "european energy software",
            "energy utility software",
            "grid software",
            "energy trading platform",
            "renewable energy software",
        ]

        for market in markets:
            try:
                catalog = _catalog_for_market(market)
                for company in catalog:
                    name = company.get("name", "").lower()
                    if name and name not in self.known_names:
                        new_companies.append(
                            {
                                "company_name": company["name"],
                                "ticker": company.get("ticker"),
                                "industry": company.get("industry", "Energy Software"),
                                "region": company.get("region", "Unknown"),
                                "tags": company.get("tags", []),
                                "source": f"static_catalog_{market}",
                                "discovery_iteration": self.iteration,
                            }
                        )
            except Exception as e:
                logger.debug(f"Catalog {market} not found: {e}")

        return new_companies

    def discover_from_competitor_references(self) -> List[dict]:
        """Source 2: Find companies mentioned as competitors in existing data."""
        new_companies = []

        # Look for competitor mentions in existing companies
        for company in self.discovered_companies.values():
            # Check various fields that might mention competitors
            fields_to_check = [
                company.get("description", ""),
                company.get("data_availability", ""),
                str(company.get("tags", [])),
            ]

            # Extract potential company names (capitalized words)
            for field in fields_to_check:
                if not field:
                    continue
                # Simple heuristic: look for capitalized phrases
                words = field.split()
                for i, word in enumerate(words):
                    if word[0].isupper() and len(word) > 2:
                        potential_name = word
                        # Could be multi-word
                        if i + 1 < len(words) and words[i + 1][0].isupper():
                            potential_name += " " + words[i + 1]

                        name_lower = potential_name.lower()
                        if name_lower not in self.known_names and len(potential_name) > 3:
                            # This is a candidate - add for verification
                            pass  # Would need more sophisticated NLP here

        return new_companies

    def discover_from_market_segments(self) -> List[dict]:
        """Source 3: Systematic segment coverage."""

        # Comprehensive list of energy software segments
        segments = {
            "trading_risk": [
                "Trayport",
                " Brady",
                "OpenLink",
                "Aspect",
                "Allegro",
                "FIS Energy",
                "ICE",
                "EEX",
                "Nord Pool",
                "EPEX Spot",
            ],
            "grid_management": [
                "AutoGrid",
                "Opus One",
                "Smarter Grid Solutions",
                "Camus",
                "Virtual Peaker",
                "Siemens Grid Software",
                "GE GridOS",
            ],
            "billing_crm": [
                "Salesforce Energy",
                "Oracle Utilities",
                "SAP IS-U",
                "Gentrack",
                "Fluentgrid",
                "Itineris",
                "Silver Spring",
            ],
            "ev_charging": [
                "ChargePoint",
                "EVBox",
                "Wallbox",
                "Pod Point",
                "EO Charging",
                "InstaVolt",
                "IONITY",
                "Fastned",
                "Allego",
                "Tesla Supercharger",
                "FLO",
                "Greenlots",
                "SemaConnect",
                "OpConnect",
            ],
            "energy_retails": [
                "Octopus Energy",
                "Ovo Energy",
                "Bulb",
                "Pure Planet",
                "Green Network Energy",
                "Utility Warehouse",
                "Together Energy",
            ],
            "flexibility_demand_response": [
                "Limejump",
                "Kaluza",
                "GridBeyond",
                "Open Energi",
                "Moixa",
                "Sonnen",
                "Tesla Autobidder",
                "Fluence Mosaic",
                "Wartsila",
            ],
            "metering_data": [
                "Itron",
                "Landis+Gyr",
                "Sensus",
                "Aclara",
                "Honeywell",
                "Kamstrup",
                "Diehl",
                "Zenner",
                "Apator",
            ],
            "asset_management": [
                "Infor EAM",
                "IBM Maximo",
                "SAP EAM",
                "AssetWorks",
                "Dude Solutions",
                "Fiix",
                "UpKeep",
                "Hippo CMMS",
            ],
            "renewable_management": [
                "Atonix",
                "Power Factors",
                "AlsoEnergy",
                "LocusView",
                "GE Digital Renewable Energy",
                "Siemens Renewable",
            ],
            "carbon_offset": [
                "Patch",
                "Wren",
                " Cloverly",
                "Pachama",
                "Sylvera",
                "Carbon Engineering",
                "Climeworks",
                "CarbonCure",
            ],
        }

        new_companies = []

        for segment_name, company_list in segments.items():
            for company_name in company_list:
                name_lower = company_name.lower()
                if name_lower not in self.known_names:
                    new_companies.append(
                        {
                            "company_name": company_name,
                            "ticker": None,
                            "industry": f"Energy Software - {segment_name}",
                            "region": "Global",
                            "tags": [segment_name, "energy", "software"],
                            "source": f"market_segment_{segment_name}",
                            "discovery_iteration": self.iteration,
                        }
                    )

        return new_companies

    def discover_from_geographic_expansion(self) -> List[dict]:
        """Source 4: Geographic markets we haven't covered well."""

        # Major European energy markets
        geographic_targets = {
            "France": ["RTE", "Enedis", "TotalEnergies Digital", "EDF Pulse"],
            "Germany": ["TenneT Germany", "TransnetBW", "Amprion", "50Hertz"],
            "Spain": ["REE", "Endesa", "Iberdrola Digital", "Naturgy"],
            "Italy": ["Terna", "Enel X", "Snam", "Eni Plenitude"],
            "Nordics": ["Statnett", "Fingrid", "Energinet", "Svenska Kraftnät"],
            "Benelux": ["Elia", "Tennet NL", "Enexis", "Liander"],
            "Eastern Europe": ["CEZ", "PGE", "Enea", "Tauron"],
        }

        new_companies = []

        for region, companies in geographic_targets.items():
            for company_name in companies:
                name_lower = company_name.lower()
                if name_lower not in self.known_names:
                    new_companies.append(
                        {
                            "company_name": company_name,
                            "ticker": None,
                            "industry": "Energy Software",
                            "region": region,
                            "tags": ["utility", "grid", region.lower()],
                            "source": f"geographic_{region}",
                            "discovery_iteration": self.iteration,
                        }
                    )

        return new_companies

    def deduplicate_and_filter(self, candidates: List[dict]) -> List[dict]:
        """Remove duplicates and filter out invalid entries."""
        seen = set()
        filtered = []

        for candidate in candidates:
            name = candidate.get("company_name", "").lower().strip()

            # Skip if already known
            if name in self.known_names or name in seen:
                continue

            # Skip if too short or generic
            if len(name) < 3 or name in ["the", "and", "for"]:
                continue

            # Skip if already in database (fuzzy match)
            is_duplicate = False
            for known in self.known_names:
                # Check if names are similar
                if name in known or known in name:
                    is_duplicate = True
                    break

            if not is_duplicate:
                seen.add(name)
                filtered.append(candidate)

        return filtered

    def should_stop_discovery(self, new_found: int) -> bool:
        """Determine if we've covered the market."""

        # Stop conditions:
        # 1. No new companies found
        if new_found == 0:
            logger.info("No new companies found - market coverage appears complete")
            return True

        # 2. Very few new companies (diminishing returns)
        if new_found < self.convergence_threshold:
            logger.info(f"Only {new_found} new companies found (<{self.convergence_threshold} threshold)")
            logger.info("Discovery has reached diminishing returns")
            return True

        # 3. Max iterations reached (safety)
        if self.iteration >= self.max_iterations:
            logger.warning(f"Max iterations ({self.max_iterations}) reached")
            return True

        return False

    def add_to_database(self, companies: List[dict]):
        """Add newly discovered companies to our tracking."""
        for company in companies:
            name = company.get("company_name", "").lower()
            self.known_names.add(name)
            self.discovered_companies[name] = company

    def run_continuous_discovery(self):
        """Main discovery loop - continues until market is covered."""

        logger.info("=" * 70)
        logger.info("CONTINUOUS MARKET DISCOVERY")
        logger.info("Discovering until market coverage is complete...")
        logger.info("=" * 70)

        # Load existing
        self.load_existing_database()
        initial_count = len(self.discovered_companies)

        discovery_history = []

        while self.iteration < self.max_iterations:
            self.iteration += 1

            logger.info(f"\n--- Discovery Iteration {self.iteration} ---")

            all_new_candidates = []

            # Run all discovery sources
            sources = [
                ("Static Catalogs", self.discover_from_static_catalogs),
                ("Competitor References", self.discover_from_competitor_references),
                ("Market Segments", self.discover_from_market_segments),
                ("Geographic Expansion", self.discover_from_geographic_expansion),
            ]

            for source_name, source_func in sources:
                try:
                    candidates = source_func()
                    if candidates:
                        logger.info(f"  {source_name}: {len(candidates)} candidates")
                        all_new_candidates.extend(candidates)
                except Exception as e:
                    logger.error(f"  {source_name} failed: {e}")

            # Deduplicate
            new_companies = self.deduplicate_and_filter(all_new_candidates)

            # Add to database
            self.add_to_database(new_companies)

            # Record
            discovery_history.append(
                {"iteration": self.iteration, "new_found": len(new_companies), "total": len(self.discovered_companies)}
            )

            logger.info(f"New companies this iteration: {len(new_companies)}")
            logger.info(f"Total discovered: {len(self.discovered_companies)}")

            # Check stopping criteria
            if self.should_stop_discovery(len(new_companies)):
                break

        # Summary
        final_count = len(self.discovered_companies)
        newly_discovered = final_count - initial_count

        logger.info("\n" + "=" * 70)
        logger.info("DISCOVERY COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Initial companies: {initial_count}")
        logger.info(f"Newly discovered: {newly_discovered}")
        logger.info(f"Total in database: {final_count}")
        logger.info(f"Iterations run: {self.iteration}")

        return list(self.discovered_companies.values()), discovery_history


def main():
    """Run continuous discovery."""
    discoverer = ContinuousMarketDiscovery()
    companies, history = discoverer.run_continuous_discovery()

    # Save discovery log
    with open("data/output/discovery_log.json", "w") as f:
        json.dump(
            {
                "total_companies": len(companies),
                "iterations": history,
                "companies": [{k: v for k, v in c.items() if k != "scorecard"} for c in companies],
            },
            f,
            indent=2,
        )

    logger.info(f"\nDiscovery log saved to: data/output/discovery_log.json")

    return companies


if __name__ == "__main__":
    main()
