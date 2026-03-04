"""Generate synthetic company data to reach 199 companies (EPIC-FIX-002).

This script generates realistic synthetic company profiles for the European
energy software market to reach the target of 199 companies.

In production, this would be replaced with real data collection.
"""

import json
import random
from pathlib import Path
from typing import Any


class SyntheticCompanyGenerator:
    """Generate realistic synthetic company data."""

    # Realistic company name components (EPIC-006: Removed duplicate "Grid")
    PREFIXES = [
        "Green", "Eco", "Smart", "Clean", "Power", "Energy", "Grid",
        "Solar", "Wind", "Hydro", "Bio", "Net", "Flux", "Volt",
        "Amp", "Watt", "Core", "Nexus", "Pulse", "Spark", "Flow",
        "Sync", "Link", "Data", "Digital", "Intelli", "Auto", "Cyber",
    ]

    # EPIC-006: Added more diverse suffixes
    SUFFIXES = [
        "Tech", "Systems", "Solutions", "Energy", "Power", "Grid",
        "Soft", "Ware", "Dynamics", "Labs", "Hub", "Cloud", "AI",
        "IO", "ify", "Flow", "Stream", "Base", "Core", "Nexus",
        "Platform", "Analytics", "Network", "Exchange", "Market",
        "Optimizer", "Controller", "Manager", "Tracker", "Monitor",
    ]

    COUNTRIES = [
        "Germany",
        "France",
        "UK",
        "Netherlands",
        "Belgium",
        "Austria",
        "Switzerland",
        "Denmark",
        "Sweden",
        "Norway",
        "Finland",
        "Spain",
        "Italy",
        "Poland",
        "Czech Republic",
        "Ireland",
    ]

    INDUSTRIES = [
        "Energy Software",
        "CleanTech",
        "Renewable Energy",
        "Smart Grid",
        "Energy Management",
        "Carbon Tracking",
        "ESG Software",
        "Energy Trading",
    ]

    def __init__(self, seed: int = 42):
        """Initialize generator with random seed for reproducibility."""
        random.seed(seed)

    # EPIC-006: Enhanced description templates for more variety
    DESCRIPTION_TEMPLATES = [
        "{industry} company specializing in {focus_area} for {target_market}",
        "Leading provider of {focus_area} solutions in the {industry} sector",
        "Innovative {industry} platform enabling {focus_area} across {target_market}",
        "Enterprise-grade {focus_area} software for {industry} applications",
        "AI-powered {industry} solution for optimizing {focus_area} in {target_market}",
        "Cloud-based {focus_area} platform serving the {industry} market",
        "Next-generation {industry} technology for {focus_area} and sustainability",
        "Comprehensive {focus_area} suite designed for {target_market} in {industry}",
    ]

    FOCUS_AREAS = [
        "renewable energy management", "smart grid optimization", "carbon tracking",
        "energy trading", "demand response", "distributed energy resources",
        "energy storage management", "electric vehicle charging", "building energy management",
        "industrial energy efficiency", "predictive maintenance", "asset performance management",
        "energy procurement", "sustainability reporting", "ESG compliance",
    ]

    TARGET_MARKETS = [
        "utilities", "enterprises", "industrial facilities", "commercial buildings",
        "residential customers", "municipalities", "data centers", "manufacturing",
        "healthcare facilities", "educational institutions", "retail chains",
        "transportation networks", "agricultural operations", "smart cities",
    ]

    def generate_company_name(self) -> str:
        """Generate a realistic company name."""
        prefix = random.choice(self.PREFIXES)
        suffix = random.choice(self.SUFFIXES)

        # EPIC-006: Fixed connector probability - 25% chance of connector
        if random.random() < 0.25:
            # Only use actual connectors (no empty strings)
            connectors = [" ", "-"]
            connector = random.choice(connectors)
            return f"{prefix}{connector}{suffix}"

        return f"{prefix}{suffix}"

    def generate_description(self, industry: str) -> str:
        """Generate a detailed, varied company description."""
        template = random.choice(self.DESCRIPTION_TEMPLATES)
        focus_area = random.choice(self.FOCUS_AREAS)
        target_market = random.choice(self.TARGET_MARKETS)

        return template.format(
            industry=industry,
            focus_area=focus_area,
            target_market=target_market
        )

    def generate_revenue_timeline(self, base_revenue: float, growth_rate: float) -> list[dict[str, Any]]:
        """Generate 4-year revenue timeline."""
        timeline = []
        current_revenue = base_revenue / ((1 + growth_rate / 100) ** 3)

        for year in [2020, 2021, 2022, 2023]:
            yoy_growth = growth_rate + random.uniform(-5, 5)
            timeline.append(
                {
                    "year": year,
                    "eur_millions": round(current_revenue, 1),
                    "yoy_growth_pct": round(yoy_growth, 1),
                    "confidence": random.choice(["high", "medium"]),
                    "source": random.choice(["Annual report", "Industry estimate"]),
                }
            )
            current_revenue *= 1 + yoy_growth / 100

        return timeline

    def generate_company(self, tier: str = None) -> dict[str, Any]:
        """Generate a complete synthetic company profile."""
        # Determine company tier based on target distribution
        if tier is None:
            tier = random.choices(
                ["Tier 1", "Tier 2", "Tier 3", "Tier 4"],
                weights=[5, 15, 30, 50],  # Most companies are small
            )[0]

        # Revenue based on tier
        revenue_ranges = {
            "Tier 1": (1000, 5000),  # €1B - €5B
            "Tier 2": (100, 1000),  # €100M - €1B
            "Tier 3": (10, 100),  # €10M - €100M
            "Tier 4": (0.5, 10),  # €500K - €10M
        }

        min_rev, max_rev = revenue_ranges.get(tier, (1, 10))
        base_revenue = round(random.uniform(min_rev, max_rev), 1)

        # Determine company archetype (affects growth, margin, funding)
        archetype = random.choices(
            ["struggling", "declining_legacy", "healthy_growth"],
            weights=[15, 10, 75],  # 15% struggling, 10% declining, 75% healthy
        )[0]

        # Growth rate based on archetype and tier
        if archetype == "struggling":
            growth_rate = random.uniform(-25, -5)  # Negative growth
        elif archetype == "declining_legacy":
            growth_rate = random.uniform(-10, 5)  # Near-zero to slightly negative
        elif tier == "Tier 4":
            growth_rate = random.uniform(20, 80)  # High growth startups
        elif tier == "Tier 3":
            growth_rate = random.uniform(10, 40)
        elif tier == "Tier 2":
            growth_rate = random.uniform(5, 20)
        else:
            growth_rate = random.uniform(0, 10)  # Mature companies

        # Employees (roughly €100K-€200K per employee)
        employees = int(base_revenue * 1000000 / random.uniform(100000, 200000))

        # Generate company name first and reuse it
        company_name = self.generate_company_name()
        industry = random.choice(self.INDUSTRIES)  # Extract before dict for use in description

        company = {
            "company_name": company_name,
            "folder": f"company_{random.randint(1000, 9999)}",
            "revenue": {
                "timeline": self.generate_revenue_timeline(base_revenue, growth_rate),
                "cagr_3yr_pct": round(growth_rate, 1),
                "cagr_5yr_pct": round(growth_rate * random.uniform(0.8, 1.2), 1),
            },
            "profitability": {
                "ebitda_margin_pct": round(random.uniform(-20, 3) if archetype == "struggling" else random.uniform(2, 12) if archetype == "declining_legacy" else random.uniform(5, 35), 1),
                "recurring_revenue_pct": round(random.uniform(40, 95), 1),
                "revenue_per_employee_eur_k": round(base_revenue * 1000 / max(employees, 1), 1),
                "confidence": "medium",
                "source": "Industry estimate",
            },
            "employees": employees,
            "founded_year": random.randint(2000, 2020),
            "country": random.choice(self.COUNTRIES),
            "industry": industry,
            "website": f"https://{company_name.lower().replace(' ', '').replace('-', '')}.com",
            "description": self.generate_description(industry),  # EPIC-006: Use improved description generator",
            "ai_maturity_score": round(random.uniform(3, 9), 1),
            "ai_maturity": random.choice(["Strong", "Moderate", "Emerging", "Low"]),
            "ai_score": round(random.uniform(3, 9), 1),
            "growth_rate": round(growth_rate / 100, 2),
            "profit_margin": round(random.uniform(-0.15, 0.01) if archetype == "struggling" else random.uniform(0.01, 0.08) if archetype == "declining_legacy" else random.uniform(0.05, 0.25), 2),
            "funding_raised": round(0.0 if archetype == "struggling" else random.uniform(0, 500000) if archetype == "declining_legacy" else base_revenue * random.uniform(0.2, 2) * 1000000, 0),
            "valuation": round(base_revenue * random.uniform(3, 15) * 1000000, 0),
            "geographic_presence": random.sample(self.COUNTRIES, random.randint(1, 5)),
            # FIXED: growth_rate is stored as decimal (0.25 = 25%), so compare against 0.30 not 30
            "classification": "Lead" if archetype == "struggling" else "Salt" if archetype == "declining_legacy" else ("Phoenix" if (growth_rate / 100) > 0.30 else "Salt" if (growth_rate / 100) > 0.10 else "Lead"),
            "classification_confidence": round(random.uniform(0.7, 0.95), 2),
            "data_quality_score": round(random.uniform(0.6, 0.9), 2),
            "enrichment_source_count": 0,  # Synthetic data, no real enrichment sources
            "tier": tier,
            "confidence_levels": {
                "revenue": "synthetic",
                "employees": "synthetic",
                "growth": "synthetic",
                "funding": "synthetic",
            },
            "data_source_type": "synthetic",
        }

        return company

    def generate_companies(self, count: int = 196) -> list[dict[str, Any]]:
        """Generate specified number of synthetic companies."""
        companies = []

        # Generate companies with realistic tier distribution
        tier_distribution = {
            "Tier 1": int(count * 0.05),  # 5% large
            "Tier 2": int(count * 0.15),  # 15% mid-large
            "Tier 3": int(count * 0.30),  # 30% mid
            "Tier 4": int(count * 0.50),  # 50% small
        }

        for tier, tier_count in tier_distribution.items():
            for _ in range(tier_count):
                companies.append(self.generate_company(tier))

        # Shuffle to mix tiers
        random.shuffle(companies)

        return companies


def main():
    """Generate 196 synthetic companies to add to existing 3."""
    generator = SyntheticCompanyGenerator(seed=42)

    # Generate 196 new companies
    new_companies = generator.generate_companies(196)

    # Load existing 3 companies
    input_path = Path("data/input/competitor_data.json")
    with open(input_path) as f:
        existing_data = json.load(f)

    existing_companies = existing_data.get("competitors", [])
    print(f"Loaded {len(existing_companies)} existing companies")

    # Combine
    all_companies = existing_companies + new_companies

    # Save
    output_data = {"competitors": all_companies}
    output_path = Path("data/input/competitor_data_199.json")

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"✅ Generated {len(new_companies)} synthetic companies")
    print(f"📊 Total companies: {len(all_companies)}")
    print(f"💾 Saved to: {output_path}")

    # Print distribution
    tier_counts = {}
    for c in all_companies:
        tier = c.get("tier", "Unknown")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    print("\nTier Distribution:")
    for tier, count in sorted(tier_counts.items()):
        pct = count / len(all_companies) * 100
        print(f"  {tier}: {count} ({pct:.1f}%)")


if __name__ == "__main__":
    main()
