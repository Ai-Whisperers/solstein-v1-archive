import json
import logging
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from ..config import get_settings
from ..domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    ConfidenceLevel,
    FinancialMetric,
    ThreatLevel,
)
from ..analytics.confidence_weighting import populate_signal_confidences
from .metric_contract import normalize_financial_payload

logger = logging.getLogger(__name__)


class CompetitorDataLoader:
    """Load competitor data from JSON files and convert to domain entities.

    DEPRECATED: This loader is being consolidated. For new code, use UnifiedCompanyLoader
    from solstein.data.unified_loader which provides enriched data with conflict resolution.
    """

    def __init__(self, data_dir: Path | None = None):
        import warnings

        warnings.warn(
            "CompetitorDataLoader is deprecated. Use UnifiedCompanyLoader from "
            "solstein.data.unified_loader for enriched data with conflict resolution.",
            DeprecationWarning,
            stacklevel=2,
        )
        settings = get_settings()
        self.data_dir = data_dir or Path(settings.data.data_dir)
        self._cache: dict[str, list[Company]] = {}

    def load_companies(self, limit: int | None = None) -> list[Company]:
        """Load all companies from data directory."""
        cache_key = f"companies_{limit}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        companies = []

        # Try to load from the main competitor data JSON
        json_path = self.data_dir / "competitor_data.json"

        if not json_path.exists():
            error_msg = f"Critical error: Competitor data not found at {json_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        companies.extend(self._load_from_json(json_path, limit))

        if limit:
            companies = companies[:limit]

        self._cache[cache_key] = companies
        return companies

    def load_from_json(self, json_path: Path, limit: int | None = None) -> list[Company]:
        """Load companies from scored JSON file (e.g., from pipeline output)."""
        return self._load_from_json(json_path, limit)

    def _load_from_json(self, json_path: Path, limit: int | None = None) -> list[Company]:
        """Load companies from JSON file."""
        try:
            with open(json_path) as f:
                data = json.load(f)

            competitors = data.get("competitors", [])
            if limit:
                competitors = competitors[:limit]

            companies = []
            for i, comp in enumerate(competitors):
                try:
                    company = self._convert_to_domain_company(comp, i)
                    companies.append(company)
                except Exception as e:
                    logger.warning(f"Error converting competitor {i}: {e}")
                    continue

            logger.info(f"Loaded {len(companies)} companies from {json_path}")
            return companies

        except Exception as e:
            logger.error(f"Error loading JSON from {json_path}: {e}")
            return []

    def _convert_to_domain_company(self, raw_data: dict[str, Any], index: int) -> Company:
        """Convert raw JSON data to Company domain entity."""
        company_name = raw_data.get("company_name") or raw_data.get("name") or f"Company {index}"
        folder = raw_data.get("folder", f"company-{index}")

        # Extract revenue timeline
        revenue_data = raw_data.get("revenue", {})
        if isinstance(revenue_data, dict):
            timeline = revenue_data.get("timeline", [])
            cagr_3yr = revenue_data.get("cagr_3yr_pct")
            cagr_5yr = revenue_data.get("cagr_5yr_pct")
        else:
            timeline = []
            cagr_3yr = raw_data.get("revenue_cagr_3yr")
            cagr_5yr = raw_data.get("revenue_cagr_5yr")

        latest_revenue = None
        latest_growth = None
        revenue_confidence = ConfidenceLevel.UNKNOWN

        if timeline:
            latest = timeline[0]
            latest_revenue = latest.get("eur_millions")
            latest_growth = latest.get("yoy_growth_pct")
            revenue_confidence = self._convert_confidence(latest.get("confidence"))
        elif isinstance(revenue_data, (int, float)):
            latest_revenue = float(revenue_data)
            growth_rate = raw_data.get("growth_rate")
            if isinstance(growth_rate, (int, float)):
                latest_growth = float(growth_rate)
            revenue_confidence = ConfidenceLevel.CONFIRMED

        # Get CAGR from data
        # Calculate CAGR from timeline if not provided
        calculated_cagr_3yr = cagr_3yr
        if not calculated_cagr_3yr and timeline and len(timeline) >= 2:
            try:
                # Get revenue from 3 years ago (or earliest available)
                years_back = min(3, len(timeline))
                if years_back >= 2:
                    current_rev = timeline[0].get("eur_millions", 0)
                    past_rev = timeline[years_back - 1].get("eur_millions", 0)
                    if current_rev and past_rev and past_rev > 0:
                        calculated_cagr_3yr = ((current_rev / past_rev) ** (1 / years_back) - 1) * 100
            except (ZeroDivisionError, ValueError) as e:
                logger.debug(f"Could not calculate 3-year CAGR from timeline: {e}")

        # Extract profitability
        profitability_data = raw_data.get("profitability", {})
        if isinstance(profitability_data, dict):
            ebitda_margin = profitability_data.get("ebitda_margin_pct")
            recurring_rev_pct = profitability_data.get("recurring_revenue_pct")
            rev_per_employee = profitability_data.get("revenue_per_employee_eur_k")
            raw_metrics = profitability_data.get("raw_metrics", {})
        else:
            ebitda_margin = None
            recurring_rev_pct = None
            rev_per_employee = None
            raw_metrics = {}

        # Extract profit margin from raw_metrics - multiple strategies
        profit_margin = None
        if raw_metrics:
            # Strategy 1: Direct numeric value
            for key, value in raw_metrics.items():
                if "margin" in key.lower() and isinstance(value, (int, float)):
                    profit_margin = float(value)
                    break

            # Strategy 2: Parse string like "0.7% margin" or "33.7%"
            if not profit_margin:
                for key, value in raw_metrics.items():
                    if "margin" in key.lower() and isinstance(value, str):
                        # Try to extract percentage
                        match = re.search(r"([\d.]+)\s*%", value)
                        if match:
                            profit_margin = float(match.group(1))
                            break
                        # Try plain number
                        match = re.search(r"([\d.]+)", value)
                        if match:
                            val = float(match.group(1))
                            # If value > 100, it's likely absolute, not percentage
                            if val <= 100:
                                profit_margin = val
                                break

            # Strategy 3: Calculate from net profit and revenue
            if not profit_margin:
                net_profit = None
                net_revenue_key = None
                for key in raw_metrics.keys():
                    if "net profit" in key.lower() and "(fy" in key.lower():
                        net_profit = raw_metrics[key]
                        # Try to find corresponding revenue
                        for rev_key in raw_metrics.keys():
                            if "revenue" in rev_key.lower() or "sales" in rev_key.lower():
                                net_revenue_key = rev_key
                                break
                        break

                if net_profit and net_revenue_key:
                    try:
                        # Parse net profit
                        np_match = re.search(r"([\d.]+)", str(net_profit))
                        if np_match:
                            np_val = float(np_match.group(1))
                            # Convert if needed (DKK, GBP, etc.)
                            if "dkk" in str(net_profit).lower():
                                np_val *= 0.134
                            elif "gbp" in str(net_profit).lower():
                                np_val *= 1.18

                            # Parse revenue
                            rev_match = re.search(r"([\d.]+)", str(raw_metrics[net_revenue_key]))
                            if rev_match:
                                rev_val = float(rev_match.group(1))
                                if "dkk" in str(raw_metrics[net_revenue_key]).lower():
                                    rev_val *= 0.134
                                elif "gbp" in str(raw_metrics[net_revenue_key]).lower():
                                    rev_val *= 1.18

                                if rev_val > 0:
                                    profit_margin = (np_val / rev_val) * 100
                    except (ValueError, TypeError, KeyError, ZeroDivisionError) as e:
                        logger.debug(f"Could not parse profit margin: {e}")

        # Fallback: check root-level profit_margin (Ivan's flat format)
        if profit_margin is None:
            root_pm = raw_data.get("profit_margin")
            if isinstance(root_pm, (int, float)):
                # If < 1, assume it's a ratio (0.15 = 15%), convert to percentage
                profit_margin = root_pm * 100 if root_pm < 1 else root_pm
        # Extract funding - handle both nested and flat formats
        funding_data = raw_data.get("funding", {})
        if isinstance(funding_data, dict) and funding_data:
            # Original nested format
            funding_rounds = funding_data.get("rounds", [])
            total_raised_text = funding_data.get("total_raised_text", "")
            latest_valuation_text = funding_data.get("latest_valuation_text", "")
            lead_investors = funding_data.get("lead_investors", [])
            war_chest = funding_data.get("war_chest_signals")
            total_funding_eur = self._parse_funding_amount(total_raised_text)
            latest_valuation_eur = self._parse_valuation(latest_valuation_text)
        else:
            # Flat format: funding_raised, valuation at root level
            funding_rounds = raw_data.get("funding_rounds", [])
            lead_investors = raw_data.get("lead_investors", [])
            war_chest = raw_data.get("war_chest_signals")
            # Direct numeric values
            total_funding_eur = raw_data.get("funding_raised")
            latest_valuation_eur = raw_data.get("valuation")

        # Extract employees - handle both dict and direct int formats
        employees_data = raw_data.get("employees", {})
        if isinstance(employees_data, (int, float)):
            # Ivan's simplified format: "employees": 150
            employee_count = int(employees_data)
            employee_cagr = raw_data.get("employee_cagr_pct")
            open_positions = raw_data.get("open_positions")
        elif isinstance(employees_data, dict):
            # Original nested format: {"latest_headcount": 150, ...}
            employee_count_raw = employees_data.get("latest_headcount")
            employee_count = int(employee_count_raw) if employee_count_raw else None
            employee_cagr = employees_data.get("employee_cagr_pct")
            open_positions = employees_data.get("open_positions")
        else:
            employee_count = None
            employee_cagr = None
            open_positions = None

        # Extract AI capabilities - handle both nested and flat formats
        ai_data = raw_data.get("ai", {})
        if isinstance(ai_data, dict) and ai_data:
            # Original nested format
            ai_score = ai_data.get("ai_score")
            ai_signal_level = ai_data.get("signal_level")
            ai_capabilities = ai_data.get("key_capabilities")
            ai_in_production = ai_data.get("in_production")
        else:
            # Flat format: ai_score, ai_maturity_score at root level
            ai_score = raw_data.get("ai_score") or raw_data.get("ai_maturity_score")
            ai_signal_level = raw_data.get("ai_signal_level")
            ai_capabilities = raw_data.get("ai_key_capabilities")
            ai_in_production = raw_data.get("ai_in_production")

        # Extract scorecard - handle both nested and flat formats
        scorecard = raw_data.get("scorecard", {})
        if isinstance(scorecard, dict) and scorecard:
            dimensions = scorecard.get("dimensions", {})
            composite_score = scorecard.get("composite_score", 5)
            classification = scorecard.get("classification")
        else:
            # Flat format: classification at root level
            dimensions = {}
            composite_score = raw_data.get("composite_score", 5)
            classification = raw_data.get("classification")

        # Extract SaaS score for fallback AI maturity determination
        saas_score = dimensions.get("SaaS Maturity", {}).get("score", 5)

        # Determine AI maturity from string field first, then scorecard
        ai_maturity_str = raw_data.get("ai_maturity", "").strip().lower()
        has_ai_derivation_signal = any(
            [
                bool(ai_maturity_str),
                ai_signal_level is not None,
                bool(ai_capabilities),
                ai_in_production is not None,
            ]
        )
        if ai_maturity_str:
            # Map string values to enum
            if ai_maturity_str in ("strong", "advanced", "mature"):
                ai_maturity = AIMaturity.STRONG
            elif ai_maturity_str in ("moderate", "intermediate", "developing"):
                ai_maturity = AIMaturity.MODERATE
            else:  # "low", "emerging", "minimal", etc.
                ai_maturity = AIMaturity.LOW
        else:
            # Fall back to numeric scoring
            if ai_score is not None:
                if ai_score >= 8:
                    ai_maturity = AIMaturity.STRONG
                elif ai_score >= 5:
                    ai_maturity = AIMaturity.MODERATE
                else:
                    ai_maturity = AIMaturity.LOW
            else:
                if saas_score >= 8:
                    ai_maturity = AIMaturity.STRONG
                elif saas_score >= 5:
                    ai_maturity = AIMaturity.MODERATE
                else:
                    ai_maturity = AIMaturity.LOW

        # Determine threat level from composite score
        if composite_score >= 8:
            threat_level = ThreatLevel.HIGH
        elif composite_score >= 6:
            threat_level = ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.LOW

        normalized_financials = normalize_financial_payload(
            {
                "revenue": latest_revenue,
                "growth_rate": latest_growth,
                "profit_margin": profit_margin,
                "funding_raised": total_funding_eur,
                "valuation": latest_valuation_eur,
            }
        )
        latest_revenue = normalized_financials["revenue"]
        latest_growth = normalized_financials["growth_rate"]
        profit_margin = normalized_financials["profit_margin"]
        total_funding_eur = normalized_financials["funding_raised"]
        latest_valuation_eur = normalized_financials["valuation"]

        financial = FinancialMetric(
            revenue=latest_revenue,
            revenue_confidence=revenue_confidence,
            growth_rate=latest_growth,
            growth_confidence=ConfidenceLevel.ESTIMATED if latest_growth is not None else ConfidenceLevel.UNKNOWN,
            employees=employee_count,
            employees_confidence=ConfidenceLevel.CONFIRMED if employee_count is not None else ConfidenceLevel.UNKNOWN,
            profit_margin=profit_margin,
            margin_confidence=ConfidenceLevel.CONFIRMED if profit_margin is not None else ConfidenceLevel.UNKNOWN,
            ebitda_margin=ebitda_margin,
            recurring_revenue_pct=recurring_rev_pct,
            funding_raised=total_funding_eur,
            funding_confidence=ConfidenceLevel.ESTIMATED if total_funding_eur is not None else ConfidenceLevel.UNKNOWN,
            valuation=latest_valuation_eur,
            valuation_confidence=ConfidenceLevel.ESTIMATED
            if latest_valuation_eur is not None
            else ConfidenceLevel.UNKNOWN,
        )

        # Determine tier based on revenue
        tier = self._determine_tier(latest_revenue)

        if ai_score is None and has_ai_derivation_signal:
            ai_score_by_maturity = {
                AIMaturity.STRONG: 8.0,
                AIMaturity.MODERATE: 6.0,
                AIMaturity.LOW: 3.0,
                AIMaturity.NONE: 1.0,
            }
            ai_score = ai_score_by_maturity.get(ai_maturity, 1.0)

        # Build confidence scores dictionary from raw confidence fields
        # Convert string confidence levels to numeric scores
        confidence_level_map = {
            'confirmed': 1.0,
            'high': 0.9,
            'strong': 0.85,
            'medium': 0.6,
            'moderate': 0.5,
            'low': 0.3,
            'weak': 0.2,
            'estimated': 0.5,
            'unknown': 0.0,
        }

        def convert_confidence(value):
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                return confidence_level_map.get(value.lower(), 0.5)
            return 0.0

        def extract_revenue_confidences(revenue_data):
            """Extract confidence levels from revenue timeline entries."""
            confidences = {}
            if not isinstance(revenue_data, dict):
                return confidences
            timeline = revenue_data.get("timeline", [])
            for entry in timeline:
                if isinstance(entry, dict):
                    year = entry.get("year")
                    confidence = entry.get("confidence")
                    if year and confidence:
                        confidences[f"revenue_{year}"] = convert_confidence(confidence)
            return confidences

        confidence_scores = {}
        # Add revenue timeline confidences
        revenue_confidences = extract_revenue_confidences(raw_data.get("revenue", {}))
        confidence_scores.update(revenue_confidences)

        if raw_data.get("classification_confidence"):
            confidence_scores["classification"] = convert_confidence(raw_data["classification_confidence"])
        if raw_data.get("ai_confidence"):
            confidence_scores["ai_score"] = convert_confidence(raw_data["ai_confidence"])
        if raw_data.get("employees_confidence"):
            confidence_scores["employees"] = convert_confidence(raw_data["employees_confidence"])
        if raw_data.get("funding_confidence"):
            confidence_scores["funding"] = convert_confidence(raw_data["funding_confidence"])
        if raw_data.get("valuation_confidence"):
            confidence_scores["valuation"] = convert_confidence(raw_data["valuation_confidence"])

        # Build metric sources dictionary from raw source fields
        metric_sources = {}
        if raw_data.get("employees_source"):
            metric_sources["employees"] = [raw_data["employees_source"]]
        if raw_data.get("ai_source"):
            metric_sources["ai_score"] = [raw_data["ai_source"]]
        if raw_data.get("funding_source"):
            metric_sources["funding"] = [raw_data["funding_source"]]
        if raw_data.get("valuation_source"):
            metric_sources["valuation"] = [raw_data["valuation_source"]]
        # Add profitability source if available
        profitability_data = raw_data.get("profitability", {})
        if isinstance(profitability_data, dict):
            if profitability_data.get("source"):
                metric_sources["profitability"] = [profitability_data["source"]]

        # Build enrichment quality metrics
        enrichment_quality_metrics = {}
        if raw_data.get("data_quality_score") is not None:
            enrichment_quality_metrics["data_quality_score"] = raw_data["data_quality_score"]
        if raw_data.get("enrichment_source_count") is not None:
            enrichment_quality_metrics["source_count"] = raw_data["enrichment_source_count"]

        # Convert source_links from objects to strings
        source_links = []
        raw_source_links = raw_data.get("source_links", [])
        for link in raw_source_links:
            if isinstance(link, dict) and link.get("source"):
                source_links.append(link["source"])
            elif isinstance(link, str):
                source_links.append(link)

        # Create company profile
        company = Company(
            id=folder.lower().replace(" ", "-").replace("/", "-"),
            name=company_name,
            industry=raw_data.get("industry", "Energy Software"),
            description=raw_data.get("description", "Competitor in energy software market"),
            website=raw_data.get("website"),
            headquarters=raw_data.get("country") or self._estimate_headquarters(folder),
            founded_year=raw_data.get("founded_year"),
            tier=tier,
            threat_level=threat_level,
            ai_maturity=ai_maturity,
            saas_maturity=int(saas_score) if saas_score else 1,
            tech_stack=[],
            financials=financial,
            geographic_presence=self._extract_geographic_presence(raw_data),
            key_customers=[],
            last_updated=datetime.now(timezone.utc),
            data_source="SolStein Competitive Intelligence",
            # Scores
            composite_score=composite_score,
            classification=classification,
            confidence_scores=confidence_scores,
            # Comprehensive data
            revenue_timeline=timeline,
            revenue_cagr_3yr=calculated_cagr_3yr if calculated_cagr_3yr else cagr_3yr,
            revenue_cagr_5yr=cagr_5yr,
            profit_margin=profit_margin,
            ebitda_margin=ebitda_margin,
            recurring_revenue_pct=recurring_rev_pct,
            revenue_per_employee_eur_k=rev_per_employee,
            profitability_raw_metrics=raw_metrics,
            funding_rounds=funding_rounds,
            total_funding_raised_eur=total_funding_eur,
            latest_valuation_eur=latest_valuation_eur,
            lead_investors=lead_investors,
            funding_war_chest=war_chest,
            employee_count=employee_count,
            employee_cagr_3yr=employee_cagr,
            open_positions=open_positions,
            ai_score=float(ai_score) if ai_score is not None else None,
            ai_signal_level=ai_signal_level,
            ai_key_capabilities=ai_capabilities,
            ai_in_production=ai_in_production,
            data_availability=raw_data.get("data_availability"),
            # EPIC-004: Preserve quality and source metadata
            metric_sources=metric_sources,
            enrichment_quality_metrics=enrichment_quality_metrics,
            source_links=source_links,
            enrichment_source_count=raw_data.get("enrichment_source_count", 0),
            data_quality_tier="high" if raw_data.get("data_quality_score", 0) >= 0.7 else "medium" if raw_data.get("data_quality_score", 0) >= 0.4 else "low",
        )

        # EPIC-007: Populate signal_confidences from financial metric confidence levels
        company = populate_signal_confidences(company)

        return company

    def _parse_funding_amount(self, text: str | None) -> float | None:
        """Parse funding amount from text like '$1.0B', 'EUR 400M', '~£3.8B', etc."""
        if not text:
            return None

        text = text.upper()

        # Check for bootstrapped/no funding
        if any(
            x in text
            for x in [
                "BOOTSTRAPPED",
                "ZERO EXTERNAL",
                "€0 ",
                "EUR 0 (",
                "EUR 0.0",
                "NOT APPLICABLE",
                "N/A (",
                "NO EXTERNAL",
                "SELF-FUNDED",
                "UNFUNDED",
            ]
        ):
            return 0.0

        currency_mult = self._detect_currency_multiplier(text)
        if currency_mult is None:
            return None

        explicit_match = re.search(r"(EUR|USD|GBP|A\$|AUD|£|\$)\s*([\d.,]+)\s*(B|BN|BILLION|M|MLN|MILLION)", text)
        if explicit_match:
            amount = self._parse_numeric_value(explicit_match.group(2))
            if amount is not None:
                mag = explicit_match.group(3)
                magnitude = 1_000_000_000 if mag.startswith("B") else 1_000_000
                rate = self._detect_currency_multiplier(explicit_match.group(1))
                if rate is not None:
                    return amount * magnitude * rate

        # Patterns: (regex, multiplier_key)
        patterns = [
            (r"~\$?\s*([\d.]+)\s*BILLION", "BILLION"),
            (r"~\$?\s*([\d.]+)\s*B\b", "BILLION"),
            (r"\$\s*([\d.]+)\s*B", "BILLION"),
            (r"EUR\s*([\d.]+)\s*BILLION", "BILLION"),
            (r"EUR\s*([\d.]+)\s*B\b", "BILLION"),
            (r"([\d.]+)\s*BILLION", "BILLION"),
            (r"~\$?\s*([\d.]+)\s*M\b", "MILLION"),
            (r"\$\s*([\d.]+)\s*M\b", "MILLION"),
            (r"EUR\s*([\d.]+)\s*M\b", "MILLION"),
            (r"GBP\s*([\d.]+)\s*M\b", "MILLION"),
            (r"NOK\s*([\d.]+)\s*B\b", "BILLION"),
            (r"DKK\s*([\d.]+)\s*B\b", "BILLION"),
            (r"DKK\s*([\d.]+)\s*M\b", "MILLION"),
            (r"AUD\s*([\d.]+)\s*M\b", "MILLION"),
        ]

        magnitude = {"BILLION": 1_000_000_000, "MILLION": 1_000_000}

        for pattern, mag_key in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    amount = self._parse_numeric_value(match.group(1))
                    if amount is None:
                        continue
                    return amount * magnitude[mag_key] * currency_mult
                except (ValueError, KeyError):
                    continue
        return None

    def _parse_valuation(self, text: str | None) -> float | None:
        """Parse valuation from text like '$8.65B', 'EUR 1.5 billion', market cap."""
        if not text:
            return None

        text = text.upper()

        currency_mult = self._detect_currency_multiplier(text)
        if currency_mult is None:
            return None

        explicit_match = re.search(r"(EUR|USD|GBP|A\$|AUD|£|\$)\s*([\d.,]+)\s*(B|BN|BILLION|M|MLN|MILLION)", text)
        if explicit_match:
            amount = self._parse_numeric_value(explicit_match.group(2))
            if amount is not None:
                mag = explicit_match.group(3)
                magnitude = 1_000_000_000 if mag.startswith("B") else 1_000_000
                rate = self._detect_currency_multiplier(explicit_match.group(1))
                if rate is not None:
                    return amount * magnitude * rate

        # Check for no valuation
        if any(
            x in text
            for x in [
                "UNDISCLOSED",
                "UNKNOWN",
                "NOT APPLICABLE",
                "NO EXTERNAL",
                "NONE",
            ]
        ):
            return None

        # Handle ranges like "EUR 30-60M" - use midpoint
        range_match = re.search(r"(EUR|\$|USD|GBP)\s*([\d.]+)\s*[-–]\s*([\d.]+)\s*(M|B)", text)
        if range_match:
            try:
                curr = range_match.group(1)
                low = self._parse_numeric_value(range_match.group(2))
                high = self._parse_numeric_value(range_match.group(3))
                if low is None or high is None:
                    return None
                mag = range_match.group(4)
                midpoint = (low + high) / 2
                mult = 1_000_000 if mag == "M" else 1_000_000_000
                rate = self._detect_currency_multiplier(curr) or currency_mult
                return midpoint * mult * rate
            except (ValueError, AttributeError) as e:
                logger.debug(f"Could not parse valuation range: {e}")

        # Extract market cap / enterprise value
        if "MARKET CAP" in text or "ENTERPRISE VALUE" in text:
            patterns_to_try = [
                r"(EUR|USD|\$|GBP|£|A\$|AUD)\s*([\d.]+)\s*(B|BN|BILLION)",
                r"(EUR|USD|\$|GBP|£|A\$|AUD)\s*([\d.]+)\s*(M|MLN|MILLION)",
            ]
            for pattern in patterns_to_try:
                match = re.search(pattern, text)
                if match:
                    try:
                        curr = match.group(1)
                        amount = self._parse_numeric_value(match.group(2))
                        if amount is None:
                            continue
                        mag = match.group(3)
                        mult = 1_000_000 if mag.startswith("M") else 1_000_000_000
                        rate = self._detect_currency_multiplier(curr) or currency_mult
                        return amount * mult * rate
                    except (ValueError, TypeError, AttributeError) as e:
                        logger.debug(f"Could not parse market cap: {e}")
                        continue

        patterns = [
            (r"~\$?\s*([\d.]+)\s*BILLION", "BILLION"),
            (r"~\$?\s*([\d.]+)\s*B\b", "BILLION"),
            (r"\$\s*([\d.]+)\s*B\b", "BILLION"),
            (r"EUR\s*([\d.]+)\s*BILLION", "BILLION"),
            (r"EUR\s*([\d.]+)\s*B\b", "BILLION"),
            (r"([\d.]+)\s*BILLION", "BILLION"),
            (r"~\$?\s*([\d.]+)\s*M\b", "MILLION"),
            (r"\$\s*([\d.]+)\s*M\b", "MILLION"),
            (r"EUR\s*([\d.]+)\s*M\b", "MILLION"),
            (r"GBP\s*([\d.]+)\s*M\b", "MILLION"),
            (r"£\s*([\d.]+)\s*M\b", "MILLION"),
        ]

        magnitude = {"BILLION": 1_000_000_000, "MILLION": 1_000_000}

        for pattern, mag_key in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    amount = self._parse_numeric_value(match.group(1))
                    if amount is None:
                        continue
                    return amount * magnitude[mag_key] * currency_mult
                except (ValueError, KeyError):
                    continue
        return None

    def _detect_currency_multiplier(self, text: str) -> float | None:
        currency_mult = [
            ("A$", 0.60),
            ("AUD", 0.60),
            ("USD", 1.0),
            ("$", 1.0),
            ("EUR", 1.0),
            ("€", 1.0),
            ("GBP", 1.18),
            ("£", 1.18),
            ("NOK", 0.085),
            ("DKK", 0.134),
        ]
        for token, rate in currency_mult:
            if token in text:
                return rate
        return None

    def _parse_numeric_value(self, raw: str) -> float | None:
        cleaned = raw.replace(",", "").strip()
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None

    def _convert_confidence(self, confidence_str: str | None) -> ConfidenceLevel:
        """Convert string confidence to ConfidenceLevel enum."""
        if not confidence_str:
            return ConfidenceLevel.UNKNOWN

        confidence_str = confidence_str.lower()
        if "confirm" in confidence_str:
            return ConfidenceLevel.CONFIRMED
        elif "estimate" in confidence_str:
            return ConfidenceLevel.ESTIMATED
        else:
            return ConfidenceLevel.UNKNOWN

    def _determine_tier(self, revenue: float | None) -> CompanyTier:
        """Determine company tier based on revenue."""
        if revenue is None:
            return CompanyTier.TIER_4

        if revenue >= 1000:  # >= €1B
            return CompanyTier.TIER_1
        elif revenue >= 100:  # >= €100M
            return CompanyTier.TIER_2
        elif revenue >= 10:  # >= €10M
            return CompanyTier.TIER_3
        else:
            return CompanyTier.TIER_4

    def _estimate_headquarters(self, folder: str) -> str | None:
        """Estimate headquarters based on folder name."""
        folder_lower = folder.lower()

        if "uk" in folder_lower or "british" in folder_lower:
            return "United Kingdom"
        elif "german" in folder_lower or "deutsch" in folder_lower:
            return "Germany"
        elif "french" in folder_lower or "france" in folder_lower:
            return "France"
        elif "norway" in folder_lower or "norwegian" in folder_lower:
            return "Norway"
        elif "spain" in folder_lower or "spanish" in folder_lower:
            return "Spain"
        elif "poland" in folder_lower or "polish" in folder_lower:
            return "Poland"
        elif "swiss" in folder_lower or "switzerland" in folder_lower:
            return "Switzerland"
        else:
            return "Europe"

    def _extract_geographic_presence(self, raw_data: dict[str, Any]) -> list[str]:
        """Extract geographic presence from raw data.

        Handles both nested format ({"geographic": {"major_offices": [...]}}) and
        flat format ({"geographic_presence": ["Germany", "France"]}).
        Returns a list of countries/regions. If geographic data is not available,
        returns an empty list (will be overridden by Markdown data if available).
        """
        # Check for flat format first (Ivan's simplified JSON)
        flat_presence = raw_data.get("geographic_presence")
        if isinstance(flat_presence, list) and flat_presence:
            return flat_presence

        # Original nested format
        geographic = raw_data.get("geographic", {})

        if not geographic or not isinstance(geographic, dict):
            return []

        # If major_offices are available, extract countries from them
        major_offices = geographic.get("major_offices", [])
        if major_offices:
            # Return first 3 offices as proxy for countries
            return major_offices[:3]

        # If headquarters is available, use it
        headquarters = geographic.get("headquarters")
        if headquarters:
            return [headquarters]

        # Default: return empty list (don't default to 'Europe')
        return []

    def clear_cache(self) -> None:
        """Clear the data cache."""
        self._cache.clear()
        logger.debug("Cleared data cache")


# Global instance for easy import
loader = CompetitorDataLoader()


class BondYieldData:
    """Container for bond yield time series data."""

    def __init__(self, yields: pd.DataFrame | None = None):
        self.yields = pd.DataFrame() if yields is None else yields

    def get_yield(self, as_of: datetime | date) -> float | None:
        """Get bond yield for a specific date."""
        if isinstance(as_of, date):
            as_of = datetime.combine(as_of, datetime.min.time())

        if as_of not in self.yields.index:
            return None

        yield_value = self.yields.loc[as_of, "DGS10"]

        if pd.isna(yield_value):
            return None

        return float(yield_value)

    def get_latest_yield(self) -> float | None:
        """Get the most recent bond yield."""
        if self.yields.empty:
            return None

        latest = self.yields["DGS10"].dropna()

        if latest.empty:
            return None

        return float(latest.iloc[-1])


class BondYieldLoader:
    """Loader for 10-year US Treasury bond yields."""

    DEFAULT_DATA_PATH = Path(__file__).parent.parent.parent.parent / "data" / "bond_yield.csv"

    def __init__(self, data_path: Path | None = None):
        self.data_path = data_path or self.DEFAULT_DATA_PATH

    def load(self) -> BondYieldData:
        """Load bond yield data from CSV."""
        if not self.data_path.exists():
            logger.warning(f"Bond yield data not found at {self.data_path}")
            return BondYieldData()

        df = pd.read_csv(self.data_path, parse_dates=["observation_date"])
        df.set_index("observation_date", inplace=True)
        df.sort_index(inplace=True)

        return BondYieldData(yields=df)


class SP500MembershipData:
    """Container for S&P 500 membership data."""

    def __init__(self, memberships: dict[str, dict[str, Any]] | None = None):
        self.memberships = memberships or {}

    def is_member(self, ticker: str, as_of: date) -> bool:
        membership = self.memberships.get(ticker)

        if not membership:
            return False

        date_added = membership.get("date_added")
        date_removed = membership.get("date_removed")

        if date_added is None:
            return False

        if as_of < date_added:
            return False

        if date_removed is not None and as_of >= date_removed:
            return False

        return True


class SP500MembershipLoader:
    """Loader for S&P 500 membership history."""

    DEFAULT_DATA_PATH = Path(__file__).parent.parent.parent.parent / "data" / "snp_500_add_removal_dates.csv"

    def __init__(self, data_path: Path | None = None):
        self.data_path = data_path or self.DEFAULT_DATA_PATH

    def load(self) -> SP500MembershipData:
        """Load S&P 500 membership data from CSV."""
        if not self.data_path.exists():
            logger.warning(f"S&P 500 membership data not found at {self.data_path}")
            return SP500MembershipData()

        df = pd.read_csv(self.data_path)

        memberships = {}

        for _, row in df.iterrows():
            ticker = row["Ticker"]

            date_added = None
            if pd.notna(row["Date_Added"]).item() and str(row["Date_Added"]) != "NA":
                date_added = pd.to_datetime(row["Date_Added"]).item().date()

            date_removed = None
            if pd.notna(row["Date_Removed"]).item() and str(row["Date_Removed"]) != "NA":
                date_removed = pd.to_datetime(row["Date_Removed"]).item().date()

            memberships[ticker] = {
                "date_added": date_added,
                "date_removed": date_removed,
            }

        logger.info(f"Loaded S&P 500 membership data for {len(memberships)} tickers")

        return SP500MembershipData(memberships=memberships)
