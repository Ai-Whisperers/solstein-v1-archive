"""
Test script to verify financial health scoring works correctly.

Usage:
    python scripts/test_financial_scoring.py
"""

import sys

sys.path.insert(0, "src")

from solstein.analytics.scorers.financial_health import FinancialHealthScorer
from solstein.domain.models import FinancialMetric


def test_revenue_scoring():
    """Test that different revenue levels produce different scores."""
    print("Testing Revenue Scoring...")
    print("=" * 60)

    scorer = FinancialHealthScorer()

    test_cases = [
        ("Small (€0.5M)", 0.5),
        ("Medium (€5M)", 5.0),
        ("Large (€50M)", 50.0),
        ("Very Large (€150M)", 150.0),
    ]

    scores = []
    for name, revenue in test_cases:
        financials = FinancialMetric(revenue=revenue)
        score, explanation = scorer.score(financials)
        scores.append(score)
        print(f"{name:20} Revenue: €{revenue:6.1f}M -> Score: {score:.2f}")

    # Check variance
    variance = max(scores) - min(scores)
    print(f"\nScore variance: {variance:.2f}")

    if variance > 2.0:
        print("✅ PASS: Scores vary appropriately")
        return True
    else:
        print("❌ FAIL: Scores don't vary enough")
        return False


def test_profitability_scoring():
    """Test that profit margins affect scoring."""
    print("\n\nTesting Profitability Scoring...")
    print("=" * 60)

    scorer = FinancialHealthScorer()

    test_cases = [
        ("Negative (-5%)", -5.0),
        ("Low (5%)", 5.0),
        ("Medium (12%)", 12.0),
        ("High (25%)", 25.0),
    ]

    scores = []
    for name, margin in test_cases:
        financials = FinancialMetric(
            revenue=10.0,  # €10M revenue
            profit_margin=margin,
        )
        score, explanation = scorer.score(financials)
        scores.append(score)
        print(f"{name:20} Margin: {margin:6.1f}% -> Score: {score:.2f}")

    variance = max(scores) - min(scores)
    print(f"\nScore variance: {variance:.2f}")

    if variance > 1.0:
        print("✅ PASS: Profitability affects scores")
        return True
    else:
        print("❌ FAIL: Profitability doesn't affect scores enough")
        return False


def test_efficiency_scoring():
    """Test revenue per employee calculation."""
    print("\n\nTesting Efficiency Scoring...")
    print("=" * 60)

    scorer = FinancialHealthScorer()

    # Company with €10M revenue, 100 employees = €100K per employee
    financials = FinancialMetric(revenue=10.0, employees=100)
    score, explanation = scorer.score(financials)
    print(f"€10M revenue, 100 employees -> Score: {score:.2f}")

    # Company with €10M revenue, 10 employees = €1M per employee (very efficient)
    financials = FinancialMetric(revenue=10.0, employees=10)
    score2, explanation2 = scorer.score(financials)
    print(f"€10M revenue, 10 employees -> Score: {score2:.2f}")

    if score2 > score:
        print("✅ PASS: Higher efficiency = higher score")
        return True
    else:
        print("❌ FAIL: Efficiency not properly calculated")
        return False


def test_all_companies_scenario():
    """Simulate the real scenario with 199 companies."""
    print("\n\nSimulating Real Scenario (199 companies)...")
    print("=" * 60)

    scorer = FinancialHealthScorer()

    # Simulate 199 companies with varying financials
    import random

    random.seed(42)  # For reproducibility

    scores = []
    for i in range(199):
        revenue = random.uniform(0.5, 200.0)  # €0.5M to €200M
        margin = random.uniform(-10.0, 30.0)  # -10% to 30%
        employees = random.randint(5, 500)

        financials = FinancialMetric(revenue=revenue, profit_margin=margin, employees=employees)

        score, _ = scorer.score(financials)
        scores.append(score)

    # Analyze results
    min_score = min(scores)
    max_score = max(scores)
    avg_score = sum(scores) / len(scores)
    variance = max_score - min_score

    print(f"Min score: {min_score:.2f}")
    print(f"Max score: {max_score:.2f}")
    print(f"Avg score: {avg_score:.2f}")
    print(f"Variance:  {variance:.2f}")

    # Count how many at each level
    low = sum(1 for s in scores if s < 4.0)
    medium = sum(1 for s in scores if 4.0 <= s < 7.0)
    high = sum(1 for s in scores if s >= 7.0)

    print("\nDistribution:")
    print(f"  Low (<4):    {low} companies ({low / 199 * 100:.1f}%)")
    print(f"  Medium (4-7): {medium} companies ({medium / 199 * 100:.1f}%)")
    print(f"  High (>=7):   {high} companies ({high / 199 * 100:.1f}%)")

    if variance > 2.0:
        print("\n✅ PASS: Good score distribution")
        return True
    else:
        print("\n❌ FAIL: Scores too similar")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Financial Health Scoring Tests")
    print("=" * 60)

    results = []
    results.append(("Revenue Scoring", test_revenue_scoring()))
    results.append(("Profitability Scoring", test_profitability_scoring()))
    results.append(("Efficiency Scoring", test_efficiency_scoring()))
    results.append(("Real Scenario", test_all_companies_scenario()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:30} {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n🎉 All tests passed! Financial scoring is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Review the scoring logic.")
        sys.exit(1)
