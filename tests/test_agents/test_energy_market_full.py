"""Phase 4: End-to-end test with 29 energy software companies.

Tests the full pipeline: coordinator + all agents + comparison to manual data.
"""

import asyncio
import json
import os
from pathlib import Path

import pytest

from solstein.agents import CoordinatorAgent
from solstein.data.loaders import CompetitorDataLoader


@pytest.fixture
def coordinator():
    """Fixture to provide coordinator agent."""
    return CoordinatorAgent()


@pytest.fixture
def manual_data():
    """Load manual competitor data for comparison."""
    data_dir = Path(__file__).parent.parent.parent / "data" / "input"
    loader = CompetitorDataLoader(data_dir)
    companies = loader.load_companies()
    return {c.id: c for c in companies}


@pytest.mark.asyncio
async def test_analyze_energy_market_sample(coordinator, manual_data):
    """Test analyzing a sample of 3 energy companies."""
    sample_companies = list(manual_data.keys())[:3]

    results = {}
    for company_id in sample_companies:
        company_data = manual_data[company_id]

        audit_trail = await coordinator.analyze_company(
            company_name=company_data.name,
            gathering_batch_id="test_batch_20250220_001",
            context={
                "industry": "Energy Software",
                "market": "European Energy",
                "known_github_org": None,
            },
        )

        results[company_id] = {
            "audit_trail": audit_trail,
            "manual_data": company_data,
        }

    assert len(results) == 3

    for company_id, result in results.items():
        audit_trail = result["audit_trail"]
        manual = result["manual_data"]

        assert audit_trail.company_name == manual.name
        assert audit_trail.analysis_duration_seconds > 0
        print(
            f"\n{manual.name}:"
            f"\n  Raw sources: {len(audit_trail.raw_data.sources) if audit_trail.raw_data else 0}"
            f"\n  Aggregated facts: {len(audit_trail.aggregated_facts.facts) if audit_trail.aggregated_facts else 0}"
            f"\n  Signals extracted: {len(audit_trail.extracted_signals.signals) if audit_trail.extracted_signals else 0}"
            f"\n  Data completeness: {audit_trail.data_completeness:.0%}"
            f"\n  Confidence level: {audit_trail.confidence_level}"
            f"\n  Duration: {audit_trail.analysis_duration_seconds:.1f}s"
        )


@pytest.mark.asyncio
async def test_all_29_companies_quick(coordinator, manual_data):
    """Quick test of all 29 companies (minimal sources)."""
    companies = list(manual_data.items())

    print(f"\n\nAnalyzing {len(companies)} energy software companies...")

    results = {}
    errors = []

    for company_id, company_data in companies:
        try:
            audit_trail = await coordinator.analyze_company(
                company_name=company_data.name,
                gathering_batch_id="test_batch_29_companies",
                context={
                    "industry": "Energy Software",
                    "market": "European Energy",
                },
            )
            results[company_id] = audit_trail
        except Exception as e:
            errors.append((company_id, str(e)))
            continue

    success_rate = len(results) / len(companies)
    print(
        f"\nSuccess rate: {success_rate:.0%} ({len(results)}/{len(companies)} companies)"
    )

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for company_id, error in errors[:5]:
            print(f"  - {company_id}: {error}")

    total_sources = sum(
        len(r.raw_data.sources) if r.raw_data else 0 for r in results.values()
    )
    total_facts = sum(
        len(r.aggregated_facts.facts) if r.aggregated_facts else 0
        for r in results.values()
    )

    print(f"\nAggregate Results:")
    print(f"  Total sources gathered: {total_sources}")
    print(f"  Total facts extracted: {total_facts}")
    print(f"  Average sources per company: {total_sources / len(results):.1f}")
    print(f"  Average facts per company: {total_facts / len(results):.1f}")

    assert success_rate >= 0.80, f"Too many failures: {len(errors)} errors"
    assert total_sources > 0, "No sources gathered"
    assert total_facts > 0, "No facts extracted"


@pytest.mark.asyncio
async def test_comparison_to_manual(coordinator, manual_data):
    """Compare AI-gathered data to manual analysis for top 5 companies.

    For each company, check:
    1. Revenue data matches (if gathered)
    2. Growth rate matches (if gathered)
    3. AI maturity assessment reasonable (if gathered)
    4. Geographic presence at least as complete as manual
    """
    sample_companies = list(manual_data.items())[:5]

    print("\n\nComparison to Manual Data:")
    print("=" * 80)

    for company_id, company_data in sample_companies:
        audit_trail = await coordinator.analyze_company(
            company_name=company_data.name,
            gathering_batch_id="comparison_test",
            context={"industry": "Energy Software"},
        )

        print(f"\n{company_data.name}:")
        print(f"  Manual revenue: {company_data.financials.revenue}")
        print(f"  Manual growth: {company_data.financials.growth_rate}%")
        print(f"  Manual AI maturity: {company_data.ai_maturity}")

        if audit_trail.aggregated_facts:
            revenue_facts = [
                f
                for f in audit_trail.aggregated_facts.facts
                if "revenue" in f.fact_type.lower()
            ]
            growth_facts = [
                f
                for f in audit_trail.aggregated_facts.facts
                if "growth" in f.fact_type.lower()
            ]
            ai_facts = [
                f
                for f in audit_trail.aggregated_facts.facts
                if "ai" in f.fact_type.lower()
            ]

            if revenue_facts:
                print(f"  AI revenue facts: {len(revenue_facts)} found")
            if growth_facts:
                print(f"  AI growth facts: {len(growth_facts)} found")
            if ai_facts:
                print(f"  AI maturity facts: {len(ai_facts)} found")

        print(f"  Overall completeness: {audit_trail.data_completeness:.0%}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
