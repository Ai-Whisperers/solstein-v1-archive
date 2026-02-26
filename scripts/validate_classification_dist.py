#!/usr/bin/env python3
"""
Task 19: Validate Classification Distribution

Validates that the classification distribution across all 199 companies
is balanced and within expected ranges:
- Phoenix: 15-25%
- Salt: 60-70%
- Lead: 10-20%
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from solstein.analytics.scoring import GrowthScorer
from solstein.data.unified_loader import UnifiedCompanyLoader


@dataclass
class ClassificationStats:
    """Statistics for classification distribution."""
    total_companies: int
    phoenix_count: int
    salt_count: int
    lead_count: int
    phoenix_pct: float
    salt_pct: float
    lead_pct: float
    phoenix_in_range: bool
    salt_in_range: bool
    lead_in_range: bool
    all_in_range: bool
    boundary_cases: list[dict]


def validate_classification_distribution() -> ClassificationStats:
    """
    Validate classification distribution across all companies.

    Returns:
        ClassificationStats with distribution analysis
    """
    print("Loading all companies...")
    loader = UnifiedCompanyLoader()
    companies = loader.load_unified_companies()
    print(f"Loaded {len(companies)} companies")

    # Score all companies
    scorer = GrowthScorer()
    scored_companies = []

    print("Scoring all companies...")
    for i, company in enumerate(companies):
        if (i + 1) % 50 == 0:
            print(f"  Scored {i + 1}/{len(companies)}")

        company_copy = company.model_copy(deep=True)
        scored = scorer.calculate_scores(company_copy)
        scored_companies.append(scored)

    # Count classifications
    phoenix_companies = [c for c in scored_companies if c.classification == "Phoenix"]
    salt_companies = [c for c in scored_companies if c.classification == "Salt"]
    lead_companies = [c for c in scored_companies if c.classification == "Lead"]

    total = len(scored_companies)
    phoenix_count = len(phoenix_companies)
    salt_count = len(salt_companies)
    lead_count = len(lead_companies)

    phoenix_pct = (phoenix_count / total) * 100 if total > 0 else 0
    salt_pct = (salt_count / total) * 100 if total > 0 else 0
    lead_pct = (lead_count / total) * 100 if total > 0 else 0

    # Check ranges
    phoenix_in_range = 15 <= phoenix_pct <= 25
    salt_in_range = 60 <= salt_pct <= 70
    lead_in_range = 10 <= lead_pct <= 20
    all_in_range = phoenix_in_range and salt_in_range and lead_in_range

    # Find boundary cases (companies near classification boundaries)
    boundary_cases = []
    for company in scored_companies:
        # Phoenix boundary: 7.0
        if 6.8 <= company.composite_score <= 7.2:
            boundary_cases.append({
                "name": company.name,
                "score": company.composite_score,
                "classification": company.classification,
                "reason": "Near Phoenix/Salt boundary (7.0)"
            })
        # Salt/Lead boundary: 4.0
        elif 3.8 <= company.composite_score <= 4.2:
            boundary_cases.append({
                "name": company.name,
                "score": company.composite_score,
                "classification": company.classification,
                "reason": "Near Salt/Lead boundary (4.0)"
            })

    stats = ClassificationStats(
        total_companies=total,
        phoenix_count=phoenix_count,
        salt_count=salt_count,
        lead_count=lead_count,
        phoenix_pct=round(phoenix_pct, 2),
        salt_pct=round(salt_pct, 2),
        lead_pct=round(lead_pct, 2),
        phoenix_in_range=phoenix_in_range,
        salt_in_range=salt_in_range,
        lead_in_range=lead_in_range,
        all_in_range=all_in_range,
        boundary_cases=boundary_cases
    )

    return stats


def print_report(stats: ClassificationStats) -> None:
    """Print human-readable report."""
    print("\n" + "="*70)
    print("CLASSIFICATION DISTRIBUTION VALIDATION REPORT")
    print("="*70)

    print(f"\nTotal Companies Scored: {stats.total_companies}")
    print("\nDistribution:")
    print(f"  Phoenix: {stats.phoenix_count:3d} ({stats.phoenix_pct:5.1f}%) - Target: 15-25% {'✓' if stats.phoenix_in_range else '✗'}")
    print(f"  Salt:    {stats.salt_count:3d} ({stats.salt_pct:5.1f}%) - Target: 60-70% {'✓' if stats.salt_in_range else '✗'}")
    print(f"  Lead:    {stats.lead_count:3d} ({stats.lead_pct:5.1f}%) - Target: 10-20% {'✓' if stats.lead_in_range else '✗'}")

    print(f"\nOverall Status: {'✓ PASS' if stats.all_in_range else '✗ FAIL'}")

    if stats.boundary_cases:
        print(f"\nBoundary Cases ({len(stats.boundary_cases)} companies near classification thresholds):")
        for case in stats.boundary_cases[:10]:  # Show first 10
            print(f"  - {case['name']}: {case['score']:.2f} ({case['classification']}) - {case['reason']}")
        if len(stats.boundary_cases) > 10:
            print(f"  ... and {len(stats.boundary_cases) - 10} more")

    print("\n" + "="*70)


def save_evidence(stats: ClassificationStats, output_path: Path = None) -> Path:
    """Save evidence to JSON file."""
    if output_path is None:
        output_path = Path(".sisyphus/evidence/task-19-classification-dist.json")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(asdict(stats), f, indent=2)

    print(f"\nEvidence saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    stats = validate_classification_distribution()
    print_report(stats)
    save_evidence(stats)

    # Exit with appropriate code
    exit(0 if stats.all_in_range else 1)
